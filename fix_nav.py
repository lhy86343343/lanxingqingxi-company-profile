# -*- coding: utf-8 -*-
# 导航修复：公司简介→数字化在线评估(calc/)，执行标准导航项删除（仅footer之前区域）
# 用法: python fix_nav.py --dry | python fix_nav.py
import sys, re, glob

exclude = ['.git', 'mainsite-work', 'landing', 'backup', 'knowledge-backup', 'hx_live', 'online_index']
files = [f for f in glob.glob('**/*.html', recursive=True)
         if not any(e in f for e in exclude)]

NEW_LINK = '<a href="https://www.lanxingqingxi.com/calc/" target="_blank" rel="noopener" style="color:#0066cc;font-weight:700">数字化在线评估</a>'

def fix_nav(html):
    """只处理 <footer 之前的部分（导航区）；footer 内保留公司简介链接"""
    ft_idx = html.find('<footer')
    head_part = html if ft_idx == -1 else html[:ft_idx]
    rest = '' if ft_idx == -1 else html[ft_idx:]

    # 公司简介 → 数字化在线评估（3 种 href + active 变体）
    for href in ['about.html', '/about.html', '../about.html']:
        head_part = re.sub(rf'<a[^>]*href="{re.escape(href)}"[^>]*>公司简介</a>', NEW_LINK, head_part)
    # 执行标准导航项 → 删除
    for href in ['certificates.html', '/certificates.html', '../certificates.html']:
        head_part = re.sub(rf'<a[^>]*href="{re.escape(href)}"[^>]*>执行标准</a>', '', head_part)
    return head_part + rest

dry = '--dry' in sys.argv
changed = []
for f in files:
    html = open(f, encoding='utf-8', errors='ignore').read()
    orig = html
    html2 = fix_nav(html)
    if html2 != orig:
        # 校验：导航区无公司简介/执行标准链接残留（页面标题/meta 里的公司简介属正常）
        ft = html2.find('<footer')
        nav_part = html2 if ft == -1 else html2[:ft]
        assert not re.search(r'<a[^>]*>公司简介</a>', nav_part), f"{f}: 导航残留公司简介链接"
        assert not re.search(r'<a[^>]*>执行标准</a>', nav_part), f"{f}: 导航残留执行标准链接"
        changed.append(f)
        if not dry:
            open(f, 'w', encoding='utf-8', errors='ignore').write(html2)

print(f"{'DRY-RUN' if dry else '执行'} 修改: {len(changed)} 页")
for f in changed:
    print(f"  {f}")
