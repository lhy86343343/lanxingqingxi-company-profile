# -*- coding: utf-8 -*-
# 修复：25个页面 旧豆包floating-contact → 新版ai-chat.js
# 用法: python fix_doubao.py --dry | python fix_doubao.py
import sys, re, glob

FILES = ['about.html','cases.html','certificates.html','contact.html','faq.html','index.html','privacy.html','tech.html',
         'en/about.html','en/cases.html','en/certificates.html','en/contact.html','en/index.html','en/services.html','en/tech.html',
         'services/boiler.html','services/central-ac.html','services/condenser.html','services/evaporative-condenser.html',
         'services/gas-cooler.html','services/heat-exchanger.html','services/pipeline.html','services/reactor.html',
         'tech/high-pressure-water-jetting.html','tech/thermal-oil-decoking.html']

AI_TAG = '\n<!-- AI 智能客服 -->\n<script src="/js/ai-chat.js?v=5" defer></script>\n'

def strip_floating(html):
    """栈匹配删除 <div class="floating-contact"> 完整块"""
    start = html.find('<div class="floating-contact">')
    if start == -1:
        return html, 0
    i = start + len('<div class="floating-contact">')
    depth = 1
    while i < len(html) and depth > 0:
        nxt_open = html.find('<div', i)
        nxt_close = html.find('</div>', i)
        if nxt_close == -1:
            break
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + 4
        else:
            depth -= 1
            i = nxt_close + 6
    return html[:start] + html[i:], i - start

dry = '--dry' in sys.argv
changed = []
for f in FILES:
    html = open(f, encoding='utf-8', errors='ignore').read()
    orig = html
    html2, removed = strip_floating(html)
    assert removed > 0, f"{f}: 未找到floating-contact块"
    # 删除旧返回顶部按钮 + 关联 JS
    html2 = re.sub(
        r'<a href="#" class="back-to-top".*?</a>\s*<script>.*?backTop.*?</script>',
        '\n', html2, flags=re.S)
    # 加新版客服（放 </body> 前）
    if 'ai-chat.js' not in html2:
        html2 = html2.replace('</body>', AI_TAG + '</body>', 1)
    # 残留检查（块删除本身平衡已验证；页面历史 div 失衡与本操作无关）
    assert 'floating-contact' not in html2, f"{f}: 残留floating-contact"
    assert 'doubao' not in html2.lower(), f"{f}: 残留doubao"
    assert 'back-to-top' not in html2, f"{f}: 残留back-to-top"
    if html2 != orig:
        changed.append((f, removed))
        if not dry:
            open(f, 'w', encoding='utf-8', errors='ignore').write(html2)

print(f"{'DRY-RUN' if dry else '执行'} 修改: {len(changed)}/{len(FILES)}")
for f, n in changed:
    print(f"  {f} (删{n}B)")
