import os
import re
from datetime import datetime

ROOT = r"D:\Coding\lurenjia_mianshi"
DOMAIN = "https://yigelurenjia.com"
TODAY = "2026-10-19"

# 从 _sidebar.md 提取真实导航页面（唯一可信来源）
sidebar = open(os.path.join(ROOT, "_sidebar.md"), encoding="utf-8").read()
raw_links = re.findall(r"\[[^\]]*\]\((/[^)]+)\)", sidebar)
links = [l[:-3] if l.endswith(".md") else l for l in raw_links]

pages = []
for link in links:
    rel = link.lstrip("/")
    path = os.path.join(ROOT, rel.replace("/", os.sep) + ".md")
    pages.append((rel, os.path.exists(path)))

# 承接页（侧栏可能已包含，去重）
seen = {r for r, _ in pages}
if "guide/resources" not in seen:
    pages.append(("guide/resources", os.path.exists(os.path.join(ROOT, "guide", "resources.md"))))

# 优先级规则
def priority(route):
    if route in ("guide/start-here",):
        return "1.0"
    if route == "guide/resources":
        return "0.9"
    if route.startswith("guide/"):
        return "0.9"
    if route.startswith("method/"):
        return "0.9"
    if route in ("question-types/comprehensive", "question-types/organization",
                 "question-types/emergency", "question-types/relationship"):
        return "0.8"
    if route.startswith("question-types/"):
        return "0.7"
    if route in ("practice/review",):
        return "0.9"
    if route.startswith("practice/"):
        return "0.8"
    return "0.7"

def lastmod(route):
    path = os.path.join(ROOT, (route + ".md").replace("/", os.sep))
    if not os.path.exists(path):
        return None
    ts = datetime.fromtimestamp(os.path.getmtime(path))
    # 未来时间或异常值统一用今天
    s = ts.strftime("%Y-%m-%d")
    return s if s <= TODAY else TODAY

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
         '  <!-- 首页 -->',
         '  <url>',
         f'    <loc>{DOMAIN}/</loc>',
         '    <changefreq>weekly</changefreq>',
         '    <priority>1.0</priority>',
         f'    <lastmod>{TODAY}</lastmod>',
         '  </url>']

missing = []
for route, exists in pages:
    if not exists:
        missing.append(route)
        continue
    lm = lastmod(route)
    lines += ['  <url>',
              f'    <loc>{DOMAIN}/{route}</loc>',
              '    <changefreq>weekly</changefreq>',
              f'    <priority>{priority(route)}</priority>']
    if lm:
        lines.append(f'    <lastmod>{lm}</lastmod>')
    lines.append('  </url>')

lines.append('</urlset>')
out = os.path.join(ROOT, "sitemap.xml")
open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

print(f"pages written: {len(pages) - len(missing)}")
print(f"missing files: {missing if missing else 'none'}")
