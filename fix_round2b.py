# -*- coding: utf-8 -*-
# round2 补丁：工具 JS 垢型 rate 对照表3 修正 + 名称/说明补硫酸盐
import re

FIX = [
    ('tools/scaling-diagnosis.html',
     "name: '硅酸盐难溶垢', score: 2, rate: '≥95%'",
     "name: '硫酸盐/硅酸盐难溶垢', score: 2, rate: '≥85%'",
     '硫酸盐/硅酸盐垢 rate 95→85（表3）'),
    ('tools/scaling-diagnosis.html',
     "name: '菌藻生物粘泥', score: 2, rate: '≥97%'",
     "name: '菌藻生物粘泥（其他垢型）', score: 2, rate: '≥85%'",
     '菌藻粘泥 rate 97→85（表3 其他垢型）'),
    ('tools/scaling-diagnosis.html',
     '灰白坚硬 → 硅酸盐垢',
     '黄白/灰白坚硬 → 硫酸盐/硅酸盐垢',
     '颜色提示补硫酸盐'),
    ('tools/scaling-diagnosis.html',
     "chemNote: '硅酸盐垢致密难溶",
     "chemNote: '硫酸盐/硅酸盐垢致密难溶",
     'chemNote补硫酸盐'),
    ('blog/scale-diagnosis-tool.html',
     '硅酸盐难溶垢需复合碱煮转化',
     '硅酸盐/硫酸盐难溶垢需复合碱煮转化',
     '工具介绍文补硫酸盐'),
]

for f, old, new, desc in FIX:
    html = open(f, encoding='utf-8', errors='ignore').read()
    c = html.count(old)
    if c:
        html = html.replace(old, new)
        open(f, 'w', encoding='utf-8').write(html)
        print(f"✅ {desc} ×{c} -> {f}")
    else:
        print(f"⚠️ 未命中: {desc} -> {f}")

# 校验：工具 rate 对照表3
print("\n=== 校验 ===")
html = open('tools/scaling-diagnosis.html', encoding='utf-8', errors='ignore').read()
for m in re.finditer(r"name: '([^']+)', score: (\d), rate: '([^']+)'", html):
    name, score, rate = m.group(1), m.group(2), m.group(3)
    ok = (rate == '≥85%' and ('硫酸盐' in name or '其他垢型' in name)) or \
         (rate in ('≥95%', '≥96%', '≥97%', '≥98%', '≥98.5%') and '硫酸盐' not in name and '其他垢型' not in name)
    print(f"  {'✅' if ok else '❌'} {name} | rate {rate}")
