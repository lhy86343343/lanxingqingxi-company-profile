import os, re, json
from datetime import date

today = '2026-07-28'
default_image = 'https://www.lanxingqingxi.com/images/og-image.jpg'

blog_dir = 'blog'
fixed_missing = 0
fixed_image = 0

for fname in sorted(os.listdir(blog_dir)):
    if not fname.endswith('.html') or fname in ['blog-list.html', 'heat-exchanger.html',
        'central-ac.html', 'boiler-reactor.html', 'pipeline-membrane.html',
        'general-tech.html', 'regional.html']:
        continue

    fpath = os.path.join(blog_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title for headline
    title_m = re.search(r'<title>([^<]+)</title>', content)
    headline = title_m.group(1).strip() if title_m else fname.replace('.html', '')
    # Clean pipe-suffix brand
    if ' | ' in headline:
        headline = headline.split(' | ')[0]
    if ' — ' in headline:
        headline = headline.split(' — ')[0]

    # Extract date
    date_m = re.search(r'datePublished["\s:]+(\d{4}-\d{2}-\d{2})', content)
    pub_date = date_m.group(1) if date_m else today

    # Extract existing image
    img_m = re.search(r'og:image["\s]+content="([^"]+)"', content)
    article_image = img_m.group(1) if img_m else default_image

    # Check existing schemas
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    has_article = False
    has_image_in_article = False

    for b in blocks:
        try:
            d = json.loads(b)
            t = str(d.get('@type', ''))
            if 'Article' in t or 'BlogPosting' in t:
                has_article = True
                if d.get('image'):
                    has_image_in_article = True
                break
        except:
            pass

    if not has_article:
        # Build Article schema
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": headline,
            "author": {"@type": "Person", "name": "丹阳蓝星清洗 罗会永"},
            "datePublished": pub_date,
            "dateModified": pub_date,
            "image": article_image,
            "publisher": {"@type": "Organization", "name": "丹阳市蓝星防腐清洗有限公司",
                         "logo": {"@type": "ImageObject", "url": "https://www.lanxingqingxi.com/images/logo.webp"}}
        }
        schema_str = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>'

        if '</head>' in content:
            content = content.replace('</head>', schema_str + '\n</head>')
            fixed_missing += 1
            print(f'ADDED: {fname}')
    elif not has_image_in_article:
        # Find the Article block and add image
        for i, b in enumerate(blocks):
            try:
                d = json.loads(b)
                t = str(d.get('@type', ''))
                if 'Article' in t or 'BlogPosting' in t:
                    d['image'] = article_image
                    new_block = '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
                    content = content.replace(
                        '<script type="application/ld+json">' + b + '</script>',
                        new_block, 1)
                    fixed_image += 1
                    print(f'IMAGE: {fname}')
                    break
            except:
                pass

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print(f'\nDone: {fixed_missing} articles added, {fixed_image} images fixed')
