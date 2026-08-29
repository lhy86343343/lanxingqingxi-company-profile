import urllib.request, ssl, re, os
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sitemap = urllib.request.urlopen('https://www.lanxingqingxi.com/sitemap.xml', timeout=30, context=ctx).read().decode('utf-8')
kurls = sorted(set(re.findall(r'https://www\.lanxingqingxi\.com/knowledge/[^<]+\.html', sitemap)))
print(f'knowledge 页面: {len(kurls)}')

ok = fail = 0
old_hits = []
for u in kurls:
    rel = u.replace('https://www.lanxingqingxi.com/', '')
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    try:
        t = urllib.request.urlopen(u, timeout=30, context=ctx).read().decode('utf-8')
        open(rel, 'w', encoding='utf-8').write(t)
        ok += 1
        olds = re.findall(r'20[+余]?年|二十余年|20\+ ?years|20 Years|20 years', t)
        if olds:
            old_hits.append((rel, len(olds)))
    except Exception as e:
        fail += 1
        print(f'ERR {rel}: {e}')

print(f'拉取: {ok} 成功, {fail} 失败')
print(f'含 20年系: {len(old_hits)} 个文件')
for rel, n in old_hits:
    print(f'  {rel}: {n} 处')
