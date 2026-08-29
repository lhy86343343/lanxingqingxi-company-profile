# -*- coding: utf-8 -*-
# 精磨存量盘点：全站文章 + 批量痕迹特征
import re, glob, os

def scan(dir_pat, exclude):
    files = sorted(glob.glob(dir_pat, recursive=True))
    return [f for f in files if not any(e in f for e in exclude) and '.git' not in f]

# 排除分类/导航页
nav = ['blog-list', 'boiler-reactor', 'regional', 'heat-exchanger.html', 'central-ac', 'general-tech',
       'equipment.html', 'pipeline-membrane', 'industrial-cleaning.html']
blog = scan('blog/*.html', nav + ['mainsite-work'])
knowledge = scan('knowledge/*/*.html', ['index.html', 'mainsite-work'])
enblog = scan('en/blog/*.html', nav)

print(f"blog 文章: {len(blog)}")
print(f"knowledge 文章: {len(knowledge)}")
print(f"en/blog 文章: {len(enblog)}")

# 批量痕迹特征
print("\n=== 批量痕迹特征 ===")
# 1. subtitle 日期行（08-04 批量）
d1 = [f for f in blog + knowledge if re.search(r'subtitle[^>]*>.*20\d\d[-/]\d{1,2}[-/]\d{1,2}', open(f, encoding='utf-8', errors='ignore').read())]
print(f"subtitle 日期行: {len(d1)} 文件")
# 2. "阅读约X分钟"（模板化）
d2 = [f for f in blog + knowledge if '阅读约' in open(f, encoding='utf-8', errors='ignore').read()]
print(f"'阅读约X分钟': {len(d2)} 文件")
# 3. 无作者（文章末无"丹阳蓝星清洗 罗会永"）
d3 = [f for f in blog + knowledge if '罗会永' not in open(f, encoding='utf-8', errors='ignore').read()]
print(f"无作者署名: {len(d3)} 文件")
# 4. 无 FAQPage（AI抓取友好缺口）
d4 = [f for f in blog + knowledge if 'FAQPage' not in open(f, encoding='utf-8', errors='ignore').read()]
print(f"无FAQPage: {len(d4)} 文件")
# 5. 裸数据（无任何限定词的效果承诺密度）—— 抽查前几篇统计"≥95%/可达/保证/100%/零损伤"
import collections
top = collections.Counter()
for f in blog + knowledge:
    html = open(f, encoding='utf-8', errors='ignore').read()
    n = len(re.findall(r'可达|保证|零损伤|100%|确保|稳定在|恢复至设计值', html))
    top[f] = n
print("\n效果承诺密度 Top 15（潜在过度承诺）：")
for f, n in top.most_common(15):
    print(f"  {n:3d}  {f}")

# 输出全量清单（供分批）
print("\n=== 全量清单 ===")
for f in blog: print(f"B\t{f}")
for f in knowledge: print(f"K\t{f}")
for f in enblog: print(f"E\t{f}")
