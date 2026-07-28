"""Fix all schema issues across the site."""
import os, re, json

fixes = {
    'json_commas': 0,
    'add_id': 0,
    'add_org': 0,
    'add_breadcrumb': 0,
}

def fix_json_commas(block):
    """Fix missing commas between JSON properties."""
    # Pattern: "key":"value""key2" -> "key":"value","key2"
    # Pattern: }{"@type" -> },{"@type"
    # Pattern: ]"name" -> ],"name"
    fixed = re.sub(r'\"\s*\"', '","', block)  # Fix adjacent quotes
    fixed = re.sub(r'\}\s*\{', '},{', fixed)   # Fix adjacent objects
    fixed = re.sub(r'\]\s*\"', '],"', fixed)   # Fix array to string
    fixed = re.sub(r'\"\s*\{', '",{', fixed)   # Fix string to object
    return fixed

for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for fname in files:
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)

        for b in blocks:
            try:
                json.loads(b)
            except json.JSONDecodeError:
                # Try to fix commas
                fixed_b = fix_json_commas(b)
                try:
                    json.loads(fixed_b)
                    # Fix worked - apply it
                    content = content.replace(
                        '<script type="application/ld+json">' + b + '</script>',
                        '<script type="application/ld+json">' + fixed_b + '</script>',
                        1
                    )
                    fixes['json_commas'] += 1
                    changed = True
                except:
                    pass  # Can't auto-fix, skip

        if changed:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)

print(f"Fixed JSON commas: {fixes['json_commas']}")

# ===== Phase 2: Add @id to Organization, LocalBusiness, Service schemas =====
# Only fix the two main pages that represent the canonical entity

for fname, id_map in [
    ('index.html', {
        'Organization': 'https://www.lanxingqingxi.com/#organization',
        'LocalBusiness': 'https://www.lanxingqingxi.com/#localbusiness',
    }),
]:
    if not os.path.exists(fname):
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    for b in blocks:
        try:
            d = json.loads(b)
            t = str(d.get('@type', ''))
            for schema_type, new_id in id_map.items():
                if schema_type in t and not d.get('@id'):
                    d['@id'] = new_id
                    new_b = '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
                    old_b = '<script type="application/ld+json">' + b + '</script>'
                    content = content.replace(old_b, new_b, 1)
                    fixes['add_id'] += 1
                    print(f"Added @id={new_id} to {schema_type} in {fname}")
                    break
        except:
            pass

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Added @id: {fixes['add_id']}")

# ===== Phase 3: Add missing Organization schema to pages that lack it =====
org_schema = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","@id":"https://www.lanxingqingxi.com/#organization","name":"丹阳市蓝星防腐清洗有限公司","alternateName":"蓝星清洗","url":"https://www.lanxingqingxi.com","logo":{"@type":"ImageObject","url":"https://www.lanxingqingxi.com/images/logo.webp"},"foundingDate":"2001","description":"专业工业设备清洗工程服务商，中国工业清洗协会成员单位，20余年经验。","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省","addressCountry":"CN"}}</script>'

pages_need_org = [
    'services/heat-exchanger.html', 'services/pipeline.html',
    'services/boiler.html', 'services/central-ac.html',
    'services/condenser.html', 'services/reactor.html',
    'services/gas-cooler.html', 'services/evaporative-condenser.html',
    'cases.html',
]

for fname in pages_need_org:
    if not os.path.exists(fname):
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if Organization already exists
    if '"@type":"Organization"' in content or '"@type": "Organization"' in content:
        continue

    if '</head>' in content:
        content = content.replace('</head>', org_schema + '\n</head>')
        fixes['add_org'] += 1
        print(f"Added Organization to {fname}")

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Added Organization: {fixes['add_org']}")

# ===== Phase 4: Add Breadcrumb to blog articles missing it =====
# Generate breadcrumb for each article
for root, dirs, files in os.walk('blog'):
    for fname in files:
        if not fname.endswith('.html') or fname in ['blog-list.html', 'heat-exchanger.html',
            'central-ac.html', 'boiler-reactor.html', 'pipeline-membrane.html',
            'general-tech.html', 'regional.html']:
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'BreadcrumbList' in content:
            continue

        # Get article title
        title_m = re.search(r'<title>([^<]+)</title>', content)
        title = title_m.group(1).strip() if title_m else fname
        if ' | ' in title:
            title = title.split(' | ')[0]
        if ' — ' in title:
            title = title.split(' — ')[0]

        page_url = f'https://www.lanxingqingxi.com/blog/{fname}'

        bc = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "首页",
                 "item": "https://www.lanxingqingxi.com/"},
                {"@type": "ListItem", "position": 2, "name": "清洗资讯",
                 "item": "https://www.lanxingqingxi.com/blog/blog-list.html"},
                {"@type": "ListItem", "position": 3, "name": title,
                 "item": page_url}
            ]
        }
        bc_str = '<script type="application/ld+json">' + json.dumps(bc, ensure_ascii=False) + '</script>'

        if '</head>' in content:
            content = content.replace('</head>', bc_str + '\n</head>')
            fixes['add_breadcrumb'] += 1

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)

print(f"Added Breadcrumb: {fixes['add_breadcrumb']}")

print()
print("===== FIX SUMMARY =====")
print(f"JSON commas fixed: {fixes['json_commas']}")
print(f"@id added: {fixes['add_id']}")
print(f"Organization added: {fixes['add_org']}")
print(f"Breadcrumb added: {fixes['add_breadcrumb']}")
print("======================")
