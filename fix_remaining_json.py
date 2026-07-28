import os, re, json

fixed = 0
for root, dirs, files in os.walk('.'):
    if '.git' in root: continue
    for fname in files:
        if not fname.endswith('.html'): continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        changed = False
        for b in blocks:
            # Check if this block has escaped quotes
            has_escaped = False
            for c in b:
                if c == chr(92):  # backslash
                    has_escaped = True
                    break
            if not has_escaped:
                continue

            try:
                json.loads(b)
                continue
            except:
                pass

            # Unescape
            fixed_b = b.replace('\\"', '"')
            try:
                json.loads(fixed_b)
                old_tag = '<script type="application/ld+json">' + b + '</script>'
                new_tag = '<script type="application/ld+json">' + fixed_b + '</script>'
                if old_tag in content:
                    content = content.replace(old_tag, new_tag, 1)
                    fixed += 1
                    changed = True
            except:
                pass

        if changed:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)

print(f'Fixed escaped-quote blocks: {fixed}')

# Fix en/blog files with completely broken schemas
for fname in ['en/blog/blog-list.html', 'en/blog/nantong-industrial-equipment-central-ac-cleaning.html']:
    if not os.path.exists(fname): continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove broken JSON-LD
    content = re.sub(r'<script type="application/ld\+json">.*?</script>', '', content, flags=re.DOTALL)

    # Add fresh schemas
    org = {"@context":"https://schema.org","@type":"Organization",
        "name":"Danyang Blue Star Anti-corrosion Cleaning Co., Ltd.",
        "alternateName":"Blue Star Cleaning",
        "url":"https://www.lanxingqingxi.com/en/",
        "logo":{"@type":"ImageObject","url":"https://www.lanxingqingxi.com/images/logo.webp"}}
    lb = {"@context":"https://schema.org","@type":"LocalBusiness",
        "name":"Danyang Blue Star Anti-corrosion Cleaning Co., Ltd.",
        "address":{"@type":"PostalAddress","addressLocality":"Danyang","addressRegion":"Jiangsu","addressCountry":"CN"},
        "url":"https://www.lanxingqingxi.com/en/"}

    schemas = '<script type="application/ld+json">' + json.dumps(org, ensure_ascii=False) + '</script>\n'
    schemas += '<script type="application/ld+json">' + json.dumps(lb, ensure_ascii=False) + '</script>'

    if '</head>' in content:
        content = content.replace('</head>', schemas + '\n</head>')
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed += 2
        print(f'Regenerated schemas for {fname}')

# Final count
errors = 0
for root, dirs, files in os.walk('.'):
    if '.git' in root: continue
    for f in files:
        if not f.endswith('.html'): continue
        with open(os.path.join(root, f), 'r', encoding='utf-8') as fh:
            content = fh.read()
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL):
            try: json.loads(b)
            except: errors += 1
print(f'Remaining JSON errors: {errors}')
