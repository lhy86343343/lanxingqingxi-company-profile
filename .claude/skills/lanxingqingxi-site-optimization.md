---
name: lanxingqingxi-site-optimization
description: "lanxingqingxi.com 全站SEO/GEO/Schema优化技能。覆盖：五大Schema部署、导航一致性、案例增强、GEO实体锚定、Title/Description/H1优化、Article增强、@graph合并、英文版优化、FTP部署。"
version: 1.0.0
---

# lanxingqingxi.com 全站优化技能

## 触发条件

用户提到以下任一关键词时加载此技能：
- "lanxingqingxi" + "优化/修复/检查/Schema/SEO/GEO"
- "蓝星清洗" + "网站/页面/结构化"
- "五大Schema" / "Article Schema" / "Service Schema"
- "案例增强" / "实体锚定" / "GEO关键词"

## 核心架构

- 本地仓库: `C:\Users\lanxi\Desktop\lanxingqingxi-bilingual\lanxingqingxi-company-profile\`
- 线上: `https://www.lanxingqingxi.com/`
- GitHub: `https://github.com/lhy86343343/lanxingqingxi-company-profile`
- 部署: FTP (Hostinger) + GitHub push
- 备份: `lanxingqingxi-backup-20260728_063120.tar.gz`
- Git标签: `backup-20260728-all-fixes`

## FTP 部署

```
Host: 46.202.158.224:21
User: u527534732.lanxingqingxi
Pass: Z2Fva&J6OeB|7S;x
```

上传命令:
```python
import ftplib
ftp = ftplib.FTP()
ftp.connect('46.202.158.224', 21, timeout=30)
ftp.login('u527534732.lanxingqingxi', 'Z2Fva&J6OeB|7S;x')
ftp.cwd('/PATH')
with open('local.html', 'rb') as fh:
    ftp.storbinary('STOR file.html', fh)
ftp.quit()
```

## 五大 Schema 部署标准

### 1. Organization (全站)
```json
{
  "@type": "Organization",
  "@id": "https://www.lanxingqingxi.com/#organization",
  "name": "丹阳市蓝星防腐清洗有限公司",
  "alternateName": "蓝星清洗",
  "url": "https://www.lanxingqingxi.com/",
  "logo": {"@type": "ImageObject", "url": "https://www.lanxingqingxi.com/images/logo.webp"},
  "telephone": "18952832843",
  "address": {"@type": "PostalAddress", "streetAddress": "丹北镇埤城洪家埭98号", "addressLocality": "丹阳市", "addressRegion": "江苏省", "addressCountry": "CN"}
}
```

### 2. LocalBusiness (首页+联系页)
- 含 geo (31.9564, 119.7357)
- 含 openingHoursSpecification
- 含 contactPoint (18952832843)

### 3. Service (服务页)
- 每页1个主Service
- @id 格式: `https://www.lanxingqingxi.com/#service-{name}`
- provider 必须引用 `#organization`
- 首页可放5个Service（总览）
- 含 category + hasOfferCatalog

### 4. Article (博客文章)
- @id: `URL#article`
- image: ImageObject 类型
- author.@id + publisher.@id → `#organization`
- articleSection: "工业设备清洗技术"
- keywords: 5个主题相关词
- mainEntityOfPage: 必填

### 5. FAQPage (首页+服务页)
- 首页12问，服务页10问
- 回答50-150字

## 部署规则

| 页面类型 | Schema组合 |
|---------|-----------|
| 首页 | Organization + LocalBusiness + Service×5 + FAQPage + BreadcrumbList + WebSite |
| 服务页 | Organization + Service + FAQPage + BreadcrumbList |
| 案例页 | Organization + ItemList + BreadcrumbList |
| 文章页 | Organization + Article + BreadcrumbList |

## @graph 合并格式

全站113页已统一为 `@graph` 单块格式:
```json
{"@context":"https://schema.org","@graph":[...]}
```

## GEO 实体锚定

### 首页结构
1. **Hero定位句**: "丹阳市蓝星防腐清洗有限公司是江苏工业清洗领域专业工业设备清洗工程服务商"
2. **四维实体卡片**: 公司/地域/行业/年限
3. **关于蓝星清洗**: 实体介绍框
4. **16城市标签**（服务页）: 江苏/镇江/丹阳/南京/苏州/无锡/常州/扬州/南通/上海/浙江/杭州/宁波/安徽/合肥/山东
5. **热门搜索锚点**: "江苏工业清洗厂家"·"镇江工业清洗公司"等

### EN首页GEO关键词
- Title: `Industrial Cleaning China | Heat Exchanger Cleaning Service | Chemical Cleaning Contractor`
- 四维实体卡片（英文）
- JSON-LD: industry + keywords 字段

## SEO 优化标准

### Title
- 格式: `关键词1_关键词2_关键词3 | 蓝星清洗`
- 50-60字符

### Description
- 150-160字符
- 含电话18952832843

### H1
- 差异化（不与Title完全相同）
- 含核心服务词

### 关键词密度
- 正文需包含: 工业清洗公司/江苏工业清洗/工业设备清洗厂家

## 案例页标准

每个案例必须:
```
案例：客户名+设备+治理
├── 客户：XX企业
├── 设备：规格型号
├── 地点：省市
├── 问题：数据+现象
├── 方案：工艺+参数
└── 结果：3+量化指标
```

## 公司名称统一

✅ 正确: 丹阳市蓝星防腐清洗有限公司
品牌: 蓝星清洗

## 常见修复操作

### 批量JSON逗号修复
```python
fixed = re.sub(r'\"\s*\"', '\",\"', block)
fixed = re.sub(r'\}\s*\"', '},\"', fixed)
```

### 导航一致性修复
```python
content = content.replace('href="index.html#contact"', 'href="contact.html"')
```

### Article Schema批量注入
用 `add_article_schema.py` 模式:
1. 提取标题、日期、图片
2. 构建完整 Article JSON
3. 注入 `</head>` 前

### @graph合并
用 `merge_schema_graph.py` 模式:
1. 提取所有JSON-LD块
2. 合并为 `{"@graph": [...]}`
3. 替换回页面

## 验证清单

- [ ] JSON-LD 0错误
- [ ] @graph 单块格式
- [ ] Organization @id 存在
- [ ] Service provider.@id 引用 #organization
- [ ] Article 含6字段(@id/image/author.@id/publisher.@id/articleSection/keywords)
- [ ] 导航"联系我们"→ contact.html
- [ ] 语言切换指向对应页面
- [ ] Favicon + OG标签完整
- [ ] 百度统计 + GA 均部署
