import re, json, os

# Keywords by category
cat_keywords = {
    'copper-tube': ['铜管凝汽器', '化学清洗', '缓蚀保护', 'BTA缓蚀剂', '电厂清洗'],
    'condenser': ['凝汽器清洗', '真空度恢复', '化学清洗', '高压水射流', '电厂设备'],
    'power-plant': ['电厂清洗', '凝汽器', '化学清洗', '锅炉清洗', '高压水射流'],
    'heat-exchanger': ['换热器清洗', '化学清洗', '高压水射流', '除垢', '工业设备'],
    'air-cooler': ['空冷器清洗', '高压水射流', '翅片清洗', '工业设备'],
    'boiler': ['锅炉清洗', '化学除垢', '高压水射流', '工业锅炉', '导热油'],
    'pipeline': ['管道清洗', '化学清洗', '高压水射流', 'PIG清管', '工业管道'],
    'reactor': ['反应釜清洗', '化学清洗', '钝化处理', '不锈钢', '化工设备'],
    'central-ac': ['中央空调清洗', '溴化锂机组', '冷却塔清洗', '风机盘管', '维保'],
    'gas-cooler': ['煤气初冷器', '焦化厂', '化学清洗', '焦油垢', '萘垢'],
    'evaporative': ['蒸发式冷凝器', '化学清洗', '高压水射流', '除垢', '镀锌层保护'],
    'thermal-oil': ['导热油清洗', '除焦', '化学清洗', '锅炉', '管道'],
    'chemical': ['化学清洗', '酸洗', '钝化', '缓蚀剂', '工业设备'],
    'organic': ['有机酸', '无机酸', '清洗剂', '化学清洗', 'Sulfamic Acid'],
    'corrosion': ['缓蚀剂', 'BTA', 'MBT', '腐蚀防护', '化学清洗'],
    'sulfamic': ['Sulfamic Acid', '化学清洗', '酸洗', '除垢', '工业清洗'],
    'citric': ['Citric Acid', '有机酸', '化学清洗', '清洗剂', '工业设备'],
    'equipment': ['工业设备清洗', '化学清洗', '高压水射流', '除垢', '维护'],
    'cleaning': ['工业清洗', '化学清洗', '高压水射流', '设备维护', '除垢'],
    'steel': ['钢铁行业', '冷却系统', '化学清洗', '防腐', '工业设备'],
    'pharmaceutical': ['制药行业', 'GMP合规', '设备清洗', '化学清洗', '验证'],
    'food': ['食品行业', 'CIP清洗', '卫生标准', '设备清洗', '化学清洗'],
    'stainless': ['不锈钢清洗', '钝化', '酸洗', '化学清洗', '工业设备'],
    'passivation': ['钝化处理', '不锈钢', '化学清洗', '腐蚀防护', '工业设备'],
    'nanjing': ['南京', '工业清洗', '换热器', '锅炉', '管道'],
    'suzhou': ['苏州', '工业清洗', '管道', '换热器', '化学清洗'],
    'wuxi': ['无锡', '工业清洗', '锅炉', '换热器', '中央空调'],
    'changzhou': ['常州', '工业清洗', '反应釜', '钝化', '化学清洗'],
    'yangzhou': ['扬州', '工业清洗', '设备清洗', '化学清洗', '换热器'],
    'taizhou': ['泰州', '工业清洗', '化学清洗', '换热器', '管道'],
    'nantong': ['南通', '工业清洗', '中央空调', '船舶', '化工设备'],
    'lianyungang': ['连云港', '工业清洗', '石化设备', '化学清洗', '高压水射流'],
    'huai-an': ['淮安', '管道清洗', '化学清洗', '高压水射流', 'CIP清洗'],
    'xuzhou': ['徐州', '换热器清洗', '凝汽器清洗', '工业设备', '化学清洗'],
    'zhenjiang': ['镇江', '化工设备清洗', '工业清洗', '化学清洗', '管道'],
    'regional': ['地域服务', '江苏', '浙江', '上海', '安徽', '工业清洗'],
    'return-parts': ['零件清洗', '重油污', '高压水射流', '化学浸泡', '工业清洗'],
    'double-pipe': ['套管式换热器', '在线清洗', '化学清洗', '换热器', '工业设备'],
    'shell-and-tube': ['列管式换热器', '化学清洗', '结垢机理', '工业设备', '除垢'],
    'floating-head': ['浮头式换热器', '检修清洗', '化学清洗', '工业设备', '除垢'],
    'plate': ['板式换热器', '化学清洗', '高压水射流', '除垢', '工业设备'],
    'spiral-plate': ['螺旋板式换热器', '化学清洗', '除垢', '工业设备', '高压水射流'],
    'various': ['换热器清洗', '化学清洗', '高压水射流', '除垢', '工业设备'],
    'fluoride': ['氟化物', '溴化锂机组', '腔体清洗', '化学清洗', '中央空调'],
    'lithium-bromide': ['溴化锂机组', '中央空调', '维保', '化学清洗', '溶液再生'],
    'hydraulic': ['反渗透设备', '化学清洗', '膜系统', '工业设备', '除垢'],
    'industrial-steam': ['蒸汽锅炉', '化学除垢', '工业锅炉', '清洗技术', '工业设备'],
    'waste-heat': ['余热锅炉', '换热管束', '化学清洗', '工业设备', '除垢'],
    'thermal-oil-boiler': ['导热油锅炉', '管道清洗', '除焦', '化学清洗', '工业设备'],
    'carbon-plant': ['碳素厂', '余热锅炉', '除垢', '化学清洗', '高压水射流'],
    'chemical-group': ['化工厂', '列管式换热器', '化学清洗', '案例', '除垢'],
    'chemical-industry': ['化工行业', '反应釜', '换热器', '化学清洗', '设备清洗'],
    'corrosion-inhibitor': ['缓蚀剂', '腐蚀防护', '化学清洗', '选型指南', '工业设备'],
    'industry-trends': ['工业清洗', '技术趋势', '在线清洗', '绿色清洗剂', 'AI监测'],
    'hcl': ['Sulfamic Acid', 'HCl', '酸洗', '化学清洗', '除垢'],
    'choosing': ['工业清洗服务商', '选择标准', '化学清洗', '设备清洗', '供应商'],
    'equipment-cleaning-cycle': ['清洗周期', '预防性维护', '设备清洗', '化学清洗', '工业设备'],
    'chemical-vs': ['化学清洗', '高压水射流', '对比', '工业清洗', '除垢'],
    'industrial-cleaning-faq': ['工业清洗', '常见问题', 'FAQ', '化学清洗', '设备清洗'],
    'equipment-cleaning-tech': ['工业设备清洗', '技术概述', '化学清洗', '高压水射流', '除垢'],
    'equipment-cleaning-technology': ['工业设备', '定期清洗', '化学清洗', '结垢', '传热效率'],
    'passivation-after': ['钝化处理', '不锈钢', '化学清洗', '腐蚀防护', '工业设备'],
    'cleaning-before': ['新装置', '开车前清扫', '化学清洗', '工业设备', '钝化'],
    'central-air-conditioning': ['中央空调', '化学清洗', '水质稳定', '冷却塔', '维保'],
    'commercial-building': ['商业建筑', '中央空调', '维保方案', '溴化锂', '冷却塔'],
}

default_kw = ['工业设备清洗', '化学清洗', '高压水射流', '换热器清洗', '丹阳蓝星清洗']

fixed = 0
for root, dirs, files in os.walk('blog'):
    for fname in files:
        if not fname.endswith('.html') or fname in ['blog-list.html','heat-exchanger.html',
            'central-ac.html','boiler-reactor.html','pipeline-membrane.html','general-tech.html','regional.html']:
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find Article in @graph
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        if not blocks:
            continue

        changed = False
        for b in blocks:
            try:
                d = json.loads(b)
                items = d.get('@graph', [d])

                for item in items:
                    t = str(item.get('@type',''))
                    if 'Article' not in t and 'BlogPosting' not in t:
                        continue

                    page_url = f'https://www.lanxingqingxi.com/blog/{fname}'

                    # @id
                    if not item.get('@id'):
                        item['@id'] = page_url + '#article'
                        changed = True

                    # image as ImageObject
                    img = item.get('image','')
                    if isinstance(img, str) and img:
                        item['image'] = {"@type": "ImageObject", "url": img}
                        changed = True
                    elif not img:
                        item['image'] = {"@type": "ImageObject", "url": "https://www.lanxingqingxi.com/images/og-image.jpg"}
                        changed = True

                    # author.@id
                    if 'author' in item and isinstance(item['author'], dict):
                        if not item['author'].get('@id'):
                            item['author']['@id'] = 'https://www.lanxingqingxi.com/#organization'
                            changed = True

                    # publisher.@id
                    if 'publisher' in item and isinstance(item['publisher'], dict):
                        if not item['publisher'].get('@id'):
                            item['publisher']['@id'] = 'https://www.lanxingqingxi.com/#organization'
                            changed = True

                    # articleSection
                    if not item.get('articleSection'):
                        item['articleSection'] = '工业设备清洗技术'
                        changed = True

                    # keywords - match by filename pattern
                    if not item.get('keywords'):
                        kw = default_kw
                        for pattern, kws in cat_keywords.items():
                            if pattern in fname.lower():
                                kw = kws
                                break
                        item['keywords'] = kw
                        changed = True

                if changed:
                    new_block = json.dumps(d, ensure_ascii=False)
                    old_tag = '<script type="application/ld+json">' + b + '</script>'
                    new_tag = '<script type="application/ld+json">' + new_block + '</script>'
                    if old_tag in content:
                        content = content.replace(old_tag, new_tag, 1)
                        fixed += 1
                        print(f'Fixed: {fname}')
                    break
            except:
                pass

        if changed:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)

print(f'\nTotal fixed: {fixed} articles')

# Verify
has_id = has_imgobj = has_auth_id = has_pub_id = has_section = has_kw = 0
total = 0
for root, dirs, files in os.walk('blog'):
    for f in files:
        if not f.endswith('.html') or f in ['blog-list.html','heat-exchanger.html','central-ac.html','boiler-reactor.html','pipeline-membrane.html','general-tech.html','regional.html']:
            continue
        total += 1
        with open(os.path.join(root, f), 'r', encoding='utf-8') as fh:
            html = fh.read()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for b in blocks:
            try:
                d = json.loads(b)
                for item in d.get('@graph', [d]):
                    if 'Article' in str(item.get('@type','')) or 'BlogPosting' in str(item.get('@type','')):
                        if item.get('@id'): has_id += 1
                        if isinstance(item.get('image'), dict): has_imgobj += 1
                        auth = item.get('author',{})
                        if isinstance(auth, dict) and auth.get('@id'): has_auth_id += 1
                        pub = item.get('publisher',{})
                        if isinstance(pub, dict) and pub.get('@id'): has_pub_id += 1
                        if item.get('articleSection'): has_section += 1
                        if item.get('keywords'): has_kw += 1
                        break
            except: pass

print(f'Total articles: {total}')
print(f'@id: {has_id}/{total}  image(ImageObject): {has_imgobj}/{total}')
print(f'author.@id: {has_auth_id}/{total}  publisher.@id: {has_pub_id}/{total}')
print(f'articleSection: {has_section}/{total}  keywords: {has_kw}/{total}')
