# -*- coding: utf-8 -*-
"""
全站标准引用校验脚本 check_standards.py (2026-08-31)
对照权威标准表扫描所有 .html，揪出：废止版残留 / 标准号错名 / 缺年份 / 缺/T / 误引
权威数据唯一来源：site-config/standards.json（与 .hermes/desktop-attachments/std-data-summary.md 一致）
用法:
  python check_standards.py            # 扫本地仓库
  python check_standards.py --online   # 扫线上全站（sitemap 权威清单）
有残留 exit 1；全绿 exit 0
"""
import json, os, re, sys, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = ('mainsite-work', '.git', '.hermes', '__pycache__', 'dl957_online_fix', 'knowledge-backup')
SKIP_FILE = ('backup-', '.bak')

# ---------- 权威标准表（唯一数据源：site-config/standards.json） ----------
_CFG = os.path.join(BASE, 'site-config', 'standards.json')
with open(_CFG, 'r', encoding='utf-8') as _f:
    _S = json.load(_f)

STANDARDS = {k: v['full_name'] for k, v in _S['standards'].items()}
# 标准号前缀 → 版本年份（缺年份检测用；key 为编号前缀如 'GB/T 25146'）
_YEARS = {}
for _k in STANDARDS:
    if '-' in _k:
        _num, _yr = _k.rsplit('-', 1)
        _YEARS[_num] = _yr

# ---------- 违规规则：(名称, 正则或子串, 修复建议) ----------
def _mk_rules(cfg):
    rules = []
    bans = cfg.get('banned', [])
    for b in bans:
        # 36542 误引 / 旧版残留（含年份编号）
        m = re.search(r'(\d{5}(?:-\d{4})?)', b)
        if m:
            num = m.group(1)
            rules.append((f'{num} 误引/旧版', re.compile(re.escape(num)),
                          f'{num} 已被替代或为误引（见 site-config/standards.json），改用现行标准'))
        else:
            rules.append((f'旧名禁用「{b}」', b, f'改用现行标准全名（见 site-config/standards.json）'))
    # 26135 错名：被当安全规范
    rules.append(('26135 错名', re.compile(r'26135[《\s]{0,2}高压水射流'),
                  '26135=《高压清洗机》产品标准；安全规范=GB/T 26148-2025'))
    rules.append(('26135 错名作业', re.compile(r'26135[^《\-]{0,4}作业标准'), '26135 无「作业标准」之名'))
    # 缺 /T
    for num in ('25146', '26148', '26135'):
        rules.append((f'{num} 缺/T', re.compile(fr'GB {num}'), f'→ GB/T {num}'))
    # 缺年份（带斜杠的标准号后未跟 -YYYY）
    for num, year in _YEARS.items():
        rules.append((f'{num} 缺年份', re.compile(re.escape(num) + r'(?!-)'), f'→ {num}（现行版）'))
    # DL/T 957 旧名（速查表明确：勿写《电力设备化学清洗导则》）
    rules.append(('957 旧名', 'DL/T 957《电力设备化学清洗导则》',
                  '→ DL/T 957-2017《火力发电厂凝汽器化学清洗及成膜导则》'))
    # 变体
    rules.append(('957 无空格变体', re.compile(r'DLT ?957|DL/T957'), '统一为 DL/T 957-2017'))
    # 名称含「安全作业」旧表述（26148 旧名）
    rules.append(('26148 旧名', '高压水射流安全作业规范', '→ 高压水射流清洗作业安全规范'))
    return rules

RULES = _mk_rules(_S)

def scan_text(text, fname):
    issues = []
    for name, pat, fix in RULES:
        if isinstance(pat, str):
            if pat in text:
                issues.append((name, fix))
        else:
            if pat.search(text):
                issues.append((name, fix))
    return issues

def scan_local():
    total_issues = 0
    for root, dirs, names in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in names:
            if not f.endswith('.html') or f.startswith(SKIP_FILE) or '.bak' in f:
                continue
            p = os.path.join(root, f)
            try:
                text = open(p, 'rb').read().decode('utf-8', 'ignore')
            except Exception:
                continue
            issues = scan_text(text, f)
            if issues:
                rel = os.path.relpath(p, BASE).replace('\\', '/')
                total_issues += len(issues)
                for name, fix in issues:
                    print(f'  [{rel}] {name}: {fix}')
    return total_issues

def scan_online():
    import concurrent.futures
    r = subprocess.run(['curl', '-sL', '--max-time', '30', 'https://www.lanxingqingxi.com/sitemap.xml'],
                       capture_output=True, text=True, timeout=40)
    urls = sorted(set(re.findall(r'<loc>([^<]+)</loc>', r.stdout)))
    urls = [u for u in urls if u.endswith('.html')]
    total = 0
    def check_one(url):
        try:
            r2 = subprocess.run(['curl', '-sL', '--max-time', '15', url + '?nc=1'], capture_output=True, timeout=20)
            text = r2.stdout.decode('utf-8', 'ignore')
        except Exception:
            return (url, [('下载失败', '')])
        return (url, scan_text(text, url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for url, issues in ex.map(check_one, urls):
            if issues:
                total += len(issues)
                for name, fix in issues:
                    print(f'  [{url}] {name}: {fix}')
    return total

if __name__ == '__main__':
    online = '--online' in sys.argv
    print(f'标准引用校验（{"线上全站" if online else "本地仓库"}）...')
    n = scan_online() if online else scan_local()
    if n == 0:
        print('✅ 标准引用校验通过，无残留')
        sys.exit(0)
    else:
        print(f'❌ 发现 {n} 处问题，见上方清单')
        sys.exit(1)
