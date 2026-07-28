"""Merge multiple JSON-LD blocks into single @graph block per page."""
import re, json, os

def merge_blocks_to_graph(html):
    """Extract all JSON-LD blocks, merge into one @graph block."""
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)

    graph = []
    for b in blocks:
        try:
            d = json.loads(b)
            # Handle @graph already present
            if '@graph' in d:
                graph.extend(d['@graph'])
            elif isinstance(d, dict):
                graph.append(d)
            elif isinstance(d, list):
                graph.extend(d)
        except json.JSONDecodeError:
            print(f'  WARNING: skipping broken JSON block')
            continue

    if not graph:
        return html, 0

    # Build merged block
    merged = {
        "@context": "https://schema.org",
        "@graph": graph
    }
    merged_tag = '<script type="application/ld+json">' + json.dumps(merged, ensure_ascii=False) + '</script>'

    # Remove all existing JSON-LD blocks
    for b in blocks:
        old_tag = '<script type="application/ld+json">' + b + '</script>'
        html = html.replace(old_tag, '', 1)

    # Insert merged block before </head>
    if '</head>' in html:
        html = html.replace('</head>', merged_tag + '\n</head>')
    else:
        # Insert before </body>
        html = html.replace('</body>', merged_tag + '\n</body>')

    return html, len(graph)

# Pages to merge
pages = [
    'index.html',
    'about.html',
    'services.html',
    'tech.html',
    'cases.html',
    'faq.html',
    'contact.html',
    'certificates.html',
    'privacy.html',
]

# Add service subpages
for root, dirs, files in os.walk('services'):
    for f in files:
        if f.endswith('.html'):
            pages.append(os.path.join(root, f))

# Add tech subpages
for f in ['tech/thermal-oil-decoking.html', 'tech/high-pressure-water-jetting.html']:
    if os.path.exists(f):
        pages.append(f)

# Add blog articles
for root, dirs, files in os.walk('blog'):
    for f in files:
        if f.endswith('.html'):
            pages.append(os.path.join(root, f))

# Add EN pages
for root, dirs, files in os.walk('en'):
    if '.git' in root: continue
    for f in files:
        if f.endswith('.html'):
            pages.append(os.path.join(root, f))

total_merged = 0
total_items = 0

for fname in pages:
    if not os.path.exists(fname):
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count original blocks
    old_blocks = len(re.findall(r'<script type="application/ld\+json">', content))
    if old_blocks <= 1:
        continue  # Only 1 block, no merging needed

    new_content, graph_size = merge_blocks_to_graph(content)

    if graph_size > 0:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(new_content)
        total_merged += 1
        total_items += graph_size
        if total_merged <= 5 or total_merged % 20 == 0:
            print(f'Merged: {fname} ({old_blocks} blocks -> 1 @graph with {graph_size} items)')

print(f'\nTotal: {total_merged} pages merged, {total_items} schema items in @graph blocks')

# Verify no JSON errors
import os as _os
errors = 0
for root, dirs, files in _os.walk('.'):
    if '.git' in root: continue
    for f in files:
        if not f.endswith('.html'): continue
        fpath = _os.path.join(root, f)
        with open(fpath, 'r', encoding='utf-8') as f:
            c = f.read()
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', c, re.DOTALL):
            try: json.loads(b)
            except: errors += 1
print(f'JSON errors after merge: {errors}')
