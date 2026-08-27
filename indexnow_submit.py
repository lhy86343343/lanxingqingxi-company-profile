import json, re, urllib.request

KEY = "7ba2d74c495e9e04e43dae51b54ebdf7f8dfee3f9715b1a20a74a127ee9b1456"
HOST = "www.lanxingqingxi.com"

# 直接下载 sitemap 提取 URL（避免 /tmp 路径差异）
req = urllib.request.Request(
    "https://www.lanxingqingxi.com/sitemap.xml",
    headers={"User-Agent": "Mozilla/5.0"},
)
xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
urls = re.findall(r"<loc>([^<]+)</loc>", xml)
print(f"从 sitemap 提取 URL 数: {len(urls)}")

payload = {
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": urls,
}

req2 = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
try:
    with urllib.request.urlopen(req2, timeout=90) as f:
        body = f.read().decode("utf-8", "replace")
        print(f"HTTP {f.status}")
        print("响应体:", repr(body[:800]) if body else "(空=成功)")
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}: {e.read().decode('utf-8','replace')[:800]}")
except Exception as e:
    print(f"异常: {e}")
