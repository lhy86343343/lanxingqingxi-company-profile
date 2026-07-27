"""Inject Organization + LocalBusiness + Service schemas into all pages."""
import os, re

# ===== CN SCHEMAS =====
CN_ORG_SCHEMA = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"丹阳市蓝星防腐清洗有限公司","alternateName":"丹阳蓝星清洗","url":"https://www.lanxingqingxi.com","logo":"https://www.lanxingqingxi.com/images/logo.webp","foundingDate":"2001","foundingLocation":"江苏省丹阳市","description":"中国江苏丹阳地区工业清洗领域权威企业，中国工业清洗协会成员单位，20余年专注工业设备化学清洗与高压水射流清洗服务。","address":{"@type":"PostalAddress","streetAddress":"丹北镇埤城洪家埭98号","addressLocality":"丹阳市","addressRegion":"江苏省","postalCode":"212300","addressCountry":"CN"},"telephone":"+8618952832843","email":"luohuiyong@126.com","areaServed":["江苏","浙江","上海","安徽","山东","河南"],"industry":"Industrial Cleaning","knowsAbout":["工业设备化学清洗","高压水射流清洗","换热器清洗","管道清洗","锅炉清洗","中央空调清洗","反应釜清洗","凝汽器清洗","煤气初冷器清洗","蒸发式冷凝器清洗","导热油系统除焦清洗","溴化锂机组维保","冷却水系统处理","设备防腐处理","在线不停车清洗"]}</script>'''

CN_LOCALBUSINESS_SCHEMA = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","alternateName":"丹阳蓝星清洗","description":"丹阳蓝星清洗成立于2001年，位于江苏省丹阳市，是中国工业清洗协会成员单位，专注工业设备化学清洗与高压水射流清洗20余年。","url":"https://www.lanxingqingxi.com","image":"https://www.lanxingqingxi.com/images/logo.webp","foundingDate":"2001","address":{"@type":"PostalAddress","streetAddress":"丹北镇埤城洪家埭98号","addressLocality":"丹阳市","addressRegion":"江苏省","postalCode":"212300","addressCountry":"CN"},"geo":{"@type":"GeoCoordinates","latitude":"31.9564","longitude":"119.7357"},"telephone":"+8618952832843","email":"luohuiyong@126.com","priceRange":"¥","openingHours":"Mo-Su 00:00-23:59","areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"hasCredential":[{"@type":"EducationalOccupationalCredential","name":"中国工业清洗协会会员单位"}],"numberOfEmployees":{"@type":"QuantitativeValue","minValue":20,"maxValue":50}}</script>'''

CN_COMBO = CN_ORG_SCHEMA + '\n' + CN_LOCALBUSINESS_SCHEMA

# ===== EN SCHEMAS =====
EN_ORG_SCHEMA = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Danyang Blue Star Anti-corrosion Cleaning Co., Ltd.","alternateName":"Blue Star Cleaning","url":"https://www.lanxingqingxi.com/en/","logo":"https://www.lanxingqingxi.com/images/logo.webp","foundingDate":"2001","foundingLocation":"Danyang, Jiangsu, China","description":"China Jiangsu Danyang industrial cleaning authority, member of China Industrial Cleaning Association, 20+ years specializing in industrial equipment chemical cleaning and high-pressure water jetting.","address":{"@type":"PostalAddress","streetAddress":"No.98 Hongjiadai, Picheng, Danbei Town","addressLocality":"Danyang","addressRegion":"Jiangsu","postalCode":"212300","addressCountry":"CN"},"telephone":"+8618952832843","email":"luohuiyong@126.com","areaServed":["Jiangsu","Zhejiang","Shanghai","Anhui","Shandong","Henan"],"industry":"Industrial Cleaning","knowsAbout":["Industrial Equipment Chemical Cleaning","High-Pressure Water Jetting","Heat Exchanger Cleaning","Pipeline Cleaning","Boiler Cleaning","Central AC Cleaning","Reactor Cleaning","Condenser Cleaning"]}</script>'''

EN_LOCALBUSINESS_SCHEMA = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","name":"Danyang Blue Star Anti-corrosion Cleaning Co., Ltd.","alternateName":"Blue Star Cleaning","description":"Blue Star Cleaning, founded in 2001, located in Danyang City, Jiangsu Province, is a member of China Industrial Cleaning Association, specializing in industrial equipment chemical cleaning and high-pressure water jetting for over 20 years.","url":"https://www.lanxingqingxi.com/en/","image":"https://www.lanxingqingxi.com/images/logo.webp","foundingDate":"2001","address":{"@type":"PostalAddress","streetAddress":"No.98 Hongjiadai, Picheng, Danbei Town","addressLocality":"Danyang","addressRegion":"Jiangsu","postalCode":"212300","addressCountry":"CN"},"geo":{"@type":"GeoCoordinates","latitude":"31.9564","longitude":"119.7357"},"telephone":"+8618952832843","email":"luohuiyong@126.com","priceRange":"$","openingHours":"Mo-Su 00:00-23:59","areaServed":[{"@type":"State","name":"Jiangsu"},{"@type":"State","name":"Zhejiang"},{"@type":"State","name":"Shanghai"},{"@type":"State","name":"Anhui"},{"@type":"State","name":"Shandong"},{"@type":"State","name":"Henan"}],"hasCredential":[{"@type":"EducationalOccupationalCredential","name":"China Industrial Cleaning Association Member"}],"numberOfEmployees":{"@type":"QuantitativeValue","minValue":20,"maxValue":50}}</script>'''

EN_COMBO = EN_ORG_SCHEMA + '\n' + EN_LOCALBUSINESS_SCHEMA

# ===== SERVICE SCHEMAS (CN) =====
SERVICE_SCHEMAS = {
    'services/heat-exchanger.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"换热器化学清洗","alternateName":"列管式换热器清洗、板式换热器清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供专业换热器化学清洗与高压水射流清洗服务，覆盖列管式、板式、螺旋板式、浮头式换热器除垢，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/pipeline.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"工业管道清洗","alternateName":"管道化学清洗、高压水射流管道清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供化工管道、工艺管道、循环水管道的化学清洗、高压水射流清洗及PIG清管服务，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/central-ac.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"中央空调清洗","alternateName":"溴化锂机组清洗、氟利昂机组清洗、冷却塔清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供溴化锂机组、氟利昂机组、冷却塔及风机盘管的化学清洗与维保服务，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/boiler.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"锅炉化学清洗","alternateName":"蒸汽锅炉清洗、导热油炉清洗、余热锅炉清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供蒸汽锅炉、导热油锅炉、热水锅炉及余热锅炉的化学清洗除垢服务，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/condenser.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"电厂凝汽器清洗","alternateName":"凝汽器化学清洗、凝汽器高压水射流清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供电厂凝汽器、空冷器的高压水射流清洗与化学清洗服务，有效提升真空度和发电效率，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/reactor.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"反应釜清洗","alternateName":"搪瓷反应釜清洗、不锈钢反应釜清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供搪瓷、不锈钢、碳钢反应釜夹套及内壁的专业化学清洗服务，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/gas-cooler.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"煤气初冷器清洗","alternateName":"焦化厂煤气初冷器化学清洗","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供焦化厂横管式、立管式煤气初冷器的专业化学清洗服务，去除焦油垢和萘垢，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',

    'services/evaporative-condenser.html': '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service","name":"蒸发式冷凝器清洗","alternateName":"蒸发冷清洗、镀锌管蒸发冷凝器除垢","provider":{"@type":"LocalBusiness","name":"丹阳市蓝星防腐清洗有限公司","address":{"@type":"PostalAddress","addressLocality":"丹阳市","addressRegion":"江苏省"}},"areaServed":[{"@type":"State","name":"江苏"},{"@type":"State","name":"浙江"},{"@type":"State","name":"上海"},{"@type":"State","name":"安徽"},{"@type":"State","name":"山东"},{"@type":"State","name":"河南"}],"description":"丹阳蓝星清洗提供蒸发式冷凝器化学清洗+高压水射流组合除垢服务，镀锌层保护工艺，20余年工程经验。","serviceType":"IndustrialCleaning","offers":{"@type":"Offer","price":"面议","priceCurrency":"CNY"}}</script>''',
}

# ===== APPLY =====
# Inject Org+LocalBusiness into all pages
cn_pages = [
    'index.html', 'about.html', 'services.html', 'tech.html', 'cases.html',
    'faq.html', 'contact.html', 'certificates.html', 'privacy.html',
    'blog/blog-list.html', 'blog/heat-exchanger.html',
]

en_pages = [
    'en/index.html', 'en/about.html', 'en/services.html', 'en/tech.html',
    'en/cases.html', 'en/contact.html', 'en/certificates.html',
    'en/blog/blog-list.html', 'en/blog/heat-exchanger.html',
]

# Also add to service subpages
cn_service_pages = list(SERVICE_SCHEMAS.keys())

print("=== Injecting Organization + LocalBusiness schemas ===")

# CN pages
for f in cn_pages:
    if not os.path.exists(f):
        print(f"  SKIP {f}: not found")
        continue
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if 'Organization' in content and 'LocalBusiness' in content and '"@type":"LocalBusiness"' in content:
        print(f"  SKIP {f}: schemas already present")
        continue
    # Inject before </head>
    if '</head>' in content:
        content = content.replace('</head>', CN_COMBO + '\n</head>')
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f"  OK: {f}")
    else:
        print(f"  FAIL {f}: no </head>")

# EN pages
for f in en_pages:
    if not os.path.exists(f):
        print(f"  SKIP {f}: not found")
        continue
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    if '"@type":"LocalBusiness"' in content:
        print(f"  SKIP {f}: schemas already present")
        continue
    if '</head>' in content:
        content = content.replace('</head>', EN_COMBO + '\n</head>')
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f"  OK: {f}")

# CN service pages - add Org+LocalBusiness + Service schema
print("\n=== Injecting Service schemas ===")
for f in cn_service_pages:
    if not os.path.exists(f):
        print(f"  SKIP {f}: not found")
        continue
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()

    if '"@type":"Service"' in content:
        print(f"  SKIP {f}: service schema already present")
        continue

    # Add Org+LocalBusiness if not present
    if '"@type":"LocalBusiness"' not in content:
        if '</head>' in content:
            content = content.replace('</head>', CN_COMBO + '\n</head>')

    # Add Service schema
    service_schema = SERVICE_SCHEMAS[f]
    if '</head>' in content:
        content = content.replace('</head>', service_schema + '\n</head>')

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"  OK: {f} (Org+LocalBusiness+Service)")

print("\nDone!")
