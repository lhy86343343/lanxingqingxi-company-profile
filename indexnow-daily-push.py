# -*- coding: utf-8 -*-
"""
每日定时推送脚本（不发布文章时保持收录活跃）
- Bing IndexNow：核心页面 + 轮换 10 篇文章，每日推送
- 百度收录：每日推送 10 条（token 配额内）
- 轮换游标存于 state 文件，7 天覆盖全部文章
用法：python indexnow-daily-push.py
"""
import json, re, os, sys, time, ssl, urllib.request, urllib.error

INDEXNOW_KEY = "e3bf16ace05d90779509e8a7cd9cafaf"
INDEXNOW_HOST = "www.lanxingqingxi.com"
KEY_LOCATION = f"https://{INDEXNOW_HOST}/{INDEXNOW_KEY}.txt"
BAIDU_TOKEN = "1GlE6vJ24jiZHDlU"
BAIDU_SITE = "https://www.lanxingqingxi.com"
SITEMAP = "https://www.lanxingqingxi.com/sitemap.xml"
DAILY = 10  # 每日推送文章数

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indexnow-state.json")

# 百度 data.zz.baidu.com 证书 SNI 不匹配，用非严格验证
_BAIDU_CTX = ssl.create_default_context()
_BAIDU_CTX.check_hostname = False
_BAIDU_CTX.verify_mode = ssl.CERT_NONE

# 核心页面（每天必推）
CORE_URLS = [
    "https://www.lanxingqingxi.com/",
    "https://www.lanxingqingxi.com/services.html",
    "https://www.lanxingqingxi.com/services/chemical-cleaning.html",
    "https://www.lanxingqingxi.com/services/high-pressure-water-jetting.html",
    "https://www.lanxingqingxi.com/services/boiler.html",
    "https://www.lanxingqingxi.com/services/condenser.html",
    "https://www.lanxingqingxi.com/services/heat-exchanger.html",
    "https://www.lanxingqingxi.com/services/reactor.html",
    "https://www.lanxingqingxi.com/tools/scaling-diagnosis.html",
    "https://www.lanxingqingxi.com/tools/maintenance-cycle.html",
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "identity"})
    return urllib.request.urlopen(req, timeout=30).read().decode(errors="replace")


def get_sitemap_urls():
    xml = fetch(SITEMAP)
    urls = re.findall(r"<loc>(.*?)</loc>", xml)
    # 只保留主站 www URL，去重，排除 EN 变体（/en/）
    out = []
    seen = set()
    for u in urls:
        u = u.strip()
        if INDEXNOW_HOST not in u or "/en/" in u:
            continue
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    # 文章类 = 非核心（/blog/ 或非服务/工具）
    return out


def push_indexnow(urls):
    """批量推送到 Bing IndexNow，返回 (状态码, 成功数)"""
    body = json.dumps({
        "host": INDEXNOW_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode()
    req = urllib.request.Request("https://www.bing.com/indexnow", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return r.status, len(urls)
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception as e:
        return 0, 0


def push_baidu(urls):
    """推送百度收录（每行一个 URL）"""
    body = "\n".join(urls).encode()
    url = f"https://data.zz.baidu.com/urls?site={BAIDU_SITE}&token={BAIDU_TOKEN}"
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "text/plain"})
    try:
        r = urllib.request.urlopen(req, timeout=30, context=_BAIDU_CTX)
        resp = json.loads(r.read().decode())
        return resp.get("success", 0), resp.get("remain", 0)
    except urllib.error.HTTPError as e:
        return 0, 0
    except Exception as e:
        return 0, 0


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"cursor": 0, "last": ""}


def save_state(state):
    state["last"] = time.strftime("%Y-%m-%d %H:%M")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    try:
        all_urls = get_sitemap_urls()
    except Exception as e:
        print(f"❌ sitemap 抓取失败: {e}")
        sys.exit(1)

    # 排除核心页面
    core_set = set(CORE_URLS)
    articles = [u for u in all_urls if u not in core_set]
    if not articles:
        print("⚠️ 无文章 URL，仅推送核心页面")
        articles = []

    state = load_state()
    cursor = state.get("cursor", 0)

    # 轮换取 10 篇
    picked = []
    if articles:
        n = len(articles)
        for i in range(min(DAILY, n)):
            picked.append(articles[(cursor + i) % n])
        state["cursor"] = (cursor + DAILY) % n

    # Bing IndexNow：核心 + 轮换文章
    push_list = CORE_URLS + picked
    st, ok = push_indexnow(push_list)
    in_result = f"IndexNow {st} ({ok}/{len(push_list)}条)" if st in (200, 202) else f"IndexNow 失败({st})"

    # 百度：仅文章 10 条
    bd_success, bd_remain = push_baidu(picked) if picked else (0, 0)
    bd_result = f"百度 {bd_success}条成功, 今日剩余 {bd_remain}"

    save_state(state)

    # 输出报告
    print(f"📤 每日定时推送 [{time.strftime('%Y-%m-%d %H:%M')}]")
    print(f"   文章总数: {len(articles)} | 今日轮换: {len(picked)} | 游标: {state['cursor']}")
    print(f"   {in_result} | {bd_result}")
    if picked:
        print(f"   今日推送示例: {picked[0]}")
    # 失败时输出错误明细（供排查）
    if st not in (200, 202):
        print(f"   ⚠️ IndexNow 返回 {st}，请检查 key 是否有效")


if __name__ == "__main__":
    main()
