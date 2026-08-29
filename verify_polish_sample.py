# -*- coding: utf-8 -*-
import re, json

f = 'knowledge/chemical-cleaning/sulfamic-acid.html'
html = open(f, encoding='utf-8').read()
ok = True

def check(name, cond):
    global ok
    print(f"  {'✅' if cond else '❌'} {name}")
    if not cond: ok = False

print(f"文件: {f} ({len(html)} bytes)")
# 1. JSON-LD
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S):
    try:
        d = json.loads(m.group(1))
        types = [n.get('@type') for n in d.get('@graph', [d])]
        print(f"  JSON-LD: ✅ {types}")
        faq = next((n for n in d['@graph'] if n.get('@type') == 'FAQPage'), None)
        if faq: print(f"    FAQPage 问答数: {len(faq['mainEntity'])}")
    except Exception as e:
        print(f"  JSON-LD: ❌ {e}"); ok = False
# 2. 损坏
check("无 ***@type 损坏", '***@type' not in html)
# 3. 日期行
check("无日期行(2026-08-04 · 阅读约3分钟)", '阅读约' not in html and '2026-08-04 ·' not in html)
# 4. 结构元素
for k in ['author-card', 'scroll-std', 'FAQPage', 'GB/T 25146-2010', 'cta-card', 'robots', '罗会永', '25年']:
    check(f"含 {k}", k in html)
# 5. div 平衡
check(f"div 平衡 {html.count('<div')}/{html.count('</div>')}", html.count('<div') == html.count('</div>'))
# 6. 重复百度统计
check("无重复百度统计", html.count('hm.js?bffac') == 1)
# 7. 字数
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
cn = len(re.findall(r'[\u4e00-\u9fff]', body))
print(f"  中文正文: {cn} 字")
check("字数达标(>1200)", cn > 1200)
# 8. 数据限定
for kw in ['挂片试验数据', '表3', '行业经验值', '实验室口径', '以现场实测为准']:
    check(f"数据限定含 {kw}", kw in html)
# 9. 残留旧值
check("无 <0.1g/m²·h 无空格旧格式", '<0.1g/m²·h' not in html)
print("\n" + ("✅ 全部通过" if ok else "⚠️ 有失败项"))
