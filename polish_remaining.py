# -*- coding: utf-8 -*-
# 精确盘点：git log 已精磨文件 vs 当前文章清单
import subprocess, re, glob

# 1. 收集所有"精磨"相关提交的文件
out = subprocess.run(['git', 'log', '--oneline', '--name-only', '--pretty=format:%h %s'],
                     capture_output=True, text=True).stdout
polished = set()
for line in out.splitlines():
    if not line.strip():
        continue
    if re.match(r'^[0-9a-f]{7} ', line):
        msg = line[8:]
        if re.search(r'精磨|打磨', msg):
            cur = msg
            continue
    if line.strip().endswith('.html') and 'cur' in dir():
        polished.add(line.strip().replace('\\', '/'))

print(f"=== git log 精磨过的 HTML 文件: {len(polished)} ===")

# 2. 当前文章清单
nav = ['blog-list', 'boiler-reactor', 'regional', 'central-ac', 'general-tech',
       'pipeline-membrane', 'industrial-cleaning']
def articles(pat):
    return set(f.replace('\\', '/') for f in glob.glob(pat)
               if not any(n in f for n in nav) and '.git' not in f
               and not f.endswith('/index.html'))

blog = articles('blog/*.html')
knowledge = set(f.replace('\\','/') for f in glob.glob('knowledge/*/*.html') if not f.endswith('index.html'))
enblog = articles('en/blog/*.html')

print(f"blog 文章: {len(blog)} | 其中已精磨: {len(blog & polished)}")
print(f"knowledge 文章: {len(knowledge)} | 其中已精磨: {len(knowledge & polished)}")
print(f"en/blog 文章: {len(enblog)} | 其中已精磨: {len(enblog & polished)}")

# 3. 剩余清单
print("\n=== 剩余未精磨 blog 文章 ===")
for f in sorted(blog - polished):
    print(f"  {f}")
print(f"\n=== 剩余未精磨 knowledge 文章: {len(knowledge - polished)} ===")
for f in sorted(knowledge - polished):
    print(f"  {f}")
print(f"\n=== 剩余未精磨 en/blog: {len(enblog - polished)} ===")
for f in sorted(enblog - polished):
    print(f"  {f}")
