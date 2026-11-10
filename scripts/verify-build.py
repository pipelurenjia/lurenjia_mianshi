# -*- coding: utf-8 -*-
"""
构建产物验证脚本（模拟生产环境的扩展名回退行为）

用法：
    npm run build && python scripts/verify-build.py

检查项：
1. 全部 39 个页面返回 200，且正文真实存在于静态 HTML 源码中（P0-1 回归测试）
2. 每页 canonical / og:url 逐页正确（不是共用首页的）
3. 页面标题格式为「文章标题 | 一个路人甲 · 结构化面试」
4. 每页有独立 description，且 og:description 与之相同
5. 每页只有一个 h1；内页 JSON-LD 含 BreadcrumbList 与 Article，首页是 WebSite
6. sitemap 中每个 URL 都有 lastmod，并与 docs/.vitepress/lastmod.json 一致
7. 所有正文内链无死链
8. 所有引用的图片资源存在
9. llms.txt / llms-full.txt / robots.txt / sitemap.xml 可访问
10. 侧栏「一个路人甲原创问答」是独立分组，紧挨在「资料与课程」之前，链接仍是 /practice/original-qa-*，且不在「练习方法」下
11. 首页「内容目录」覆盖全部侧栏链接；llms 索引使用同一栏目名
"""

import json
import os
import re
import sys
import threading
import urllib.error
import urllib.request
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SITE = "https://yigelurenjia.com"
SITE_DESCRIPTION = (
    "免费、系统、实战的结构化面试自学知识体系。"
    "从零基础到上岸的完整学习路径，包含布点法、观点展开法、问答笔记法等原创方法论，"
    "覆盖综合分析、组织管理、应急应变等各类题型。"
)
TITLE_SUFFIX = " | 一个路人甲 · 结构化面试"
HOME_TITLE = "一个路人甲 · 结构化面试原创学习体系 | 免费自学资料"
PORT = 4173
# 侧栏分组与首页目录必须同时指向这些既有网址
ORIGINAL_QA_GROUP = "一个路人甲原创问答"
ORIGINAL_QA_LINKS = ["/practice/original-qa-01", "/practice/original-qa-02"]

EXPECTED = [
    "/",
    "/guide/start-here", "/guide/guerrilla", "/guide/emergency", "/guide/choose-class",
    "/method/point-method", "/method/expand", "/method/point-expand", "/method/breadth-depth",
    "/method/concrete", "/method/break-homogenization", "/method/improve-depth", "/method/practice-macro",
    "/question-types/comprehensive", "/question-types/organization", "/question-types/emergency",
    "/question-types/relationship", "/question-types/simulation", "/question-types/attitude-viewpoint",
    "/question-types/impromptu-speech", "/question-types/allegory", "/question-types/research",
    "/practice/review", "/practice/practice-methods", "/practice/note-taking-deep",
    "/practice/repeat-deep", "/practice/practice-with-others",
    # 原创问答：侧栏独立分组，网址仍在 /practice/ 下，不要改成新路径
    "/practice/original-qa-01", "/practice/original-qa-02",
    "/expression/stop-words", "/expression/spoken-style", "/expression/fluency",
    "/mindset/nervous", "/mindset/anxiety", "/mindset/pace",
    "/mindset/study-fatigue", "/mindset/mindset",
    "/guide/resources",
    "/experience/picks",
]


class Handler(SimpleHTTPRequestHandler):
    """优先精确匹配，再回退 .html（对齐 Cloudflare Pages 行为）"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def translate_path(self, path):
        local = super().translate_path(path)
        if os.path.exists(local):
            return local
        if not local.endswith('.html'):
            for cand in (local + '.html', os.path.join(local, 'index.html')):
                if os.path.exists(cand):
                    return cand
        return local

    def log_message(self, fmt, *args):  # 静音
        pass


def links_in(html):
    found = []
    for href in re.findall(r'href="(/[^"#?]*)"', html or ""):
        href = href.rstrip("/") or "/"
        if href not in found:
            found.append(href)
    return found


def heading_block(html, title):
    """某个 h2/h3 标题之后、下一个同级或更高级标题之前的 HTML。"""
    matched = re.search(
        rf"<h([23])\b[^>]*>\s*{re.escape(title)}(?:\s*<a\b[^>]*>.*?</a>)?\s*</h\1>",
        html,
        re.S,
    )
    if not matched:
        return None
    level = int(matched.group(1))
    rest = html[matched.end():]
    nxt = re.search(rf"<h([1-{level}])\b", rest)
    return rest[:nxt.start()] if nxt else rest


def sidebar_groups(html):
    """解析文档页侧栏，返回 [(分组标题, [站内链接]), ...]。"""
    nav = re.search(r'<nav\b[^>]*\bid="VPSidebarNav"[^>]*>(.*?)</nav>', html, re.S)
    if not nav:
        return None
    groups = []
    # Vue 会把动态 class 写在静态 class 前面，例如 class="no-transition group"
    parts = re.split(r'<div class="[^"]*\bgroup\b[^"]*"[^>]*>', nav.group(1))
    for part in parts[1:]:
        title_match = re.search(r"<h2\b[^>]*>(.*?)</h2>", part, re.S)
        if not title_match:
            continue
        title = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", title_match.group(1)))
        groups.append((title, links_in(part)))
    return groups


def section_body(text, title):
    matched = re.search(rf"^### {re.escape(title)}\s*$", text, re.M)
    if not matched:
        return None
    rest = text[matched.end():]
    nxt = re.search(r"^### ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def check_original_qa_nav():
    """侧栏、首页目录、llms 索引使用同一栏目名，侧栏位于资料与课程之前，网址不变。"""
    problems = []
    review_path = os.path.join(DIST, "practice", "review.html")
    home_path = os.path.join(DIST, "index.html")

    if not os.path.exists(review_path):
        return ["找不到 practice/review.html，无法检查侧栏"]
    groups = sidebar_groups(open(review_path, encoding="utf-8").read())
    if not groups:
        problems.append("侧栏解析失败：practice/review.html 没有 VPSidebarNav")
    else:
        by_title = {title: links for title, links in groups}
        titles = [title for title, _ in groups]
        if by_title.get(ORIGINAL_QA_GROUP) != ORIGINAL_QA_LINKS:
            problems.append(f"侧栏「{ORIGINAL_QA_GROUP}」链接不符：{by_title.get(ORIGINAL_QA_GROUP)}")
        leaked = [link for link in ORIGINAL_QA_LINKS if link in by_title.get("练习方法", [])]
        if leaked:
            problems.append(f"原创问答仍挂在侧栏「练习方法」下：{leaked}")
        if titles[-1:] != ["资料与课程"] or ORIGINAL_QA_GROUP not in titles:
            problems.append(f"侧栏「{ORIGINAL_QA_GROUP}」应紧挨在最后一项「资料与课程」之前")
        elif titles.index(ORIGINAL_QA_GROUP) != len(titles) - 2:
            problems.append(f"侧栏「{ORIGINAL_QA_GROUP}」应是倒数第二项，当前顺序：{titles}")

    if not os.path.exists(home_path):
        problems.append("找不到 index.html，无法检查首页目录")
    else:
        home = open(home_path, encoding="utf-8").read()
        qa_block = heading_block(home, ORIGINAL_QA_GROUP)
        practice_block = heading_block(home, "练习方法")
        if qa_block is None:
            problems.append(f"首页内容目录缺少「{ORIGINAL_QA_GROUP}」栏目")
        else:
            got = [link for link in links_in(qa_block) if link.startswith("/practice/original-qa")]
            if got != ORIGINAL_QA_LINKS:
                problems.append(f"首页「{ORIGINAL_QA_GROUP}」链接不符：{got}")
        if practice_block is not None:
            leaked = [link for link in ORIGINAL_QA_LINKS if link in links_in(practice_block)]
            if leaked:
                problems.append(f"首页「练习方法」仍包含原创问答链接：{leaked}")

    for name in ("llms.txt", "llms-full.txt"):
        path = os.path.join(DIST, name)
        if not os.path.exists(path):
            problems.append(f"找不到 {name}")
            continue
        text = open(path, encoding="utf-8").read()
        qa = section_body(text, ORIGINAL_QA_GROUP)
        practice = section_body(text, "练习方法")
        if qa is None:
            problems.append(f"{name} 缺少「{ORIGINAL_QA_GROUP}」分类")
        else:
            for link in ORIGINAL_QA_LINKS:
                if f"{SITE}{link}" not in qa:
                    problems.append(f"{name}「{ORIGINAL_QA_GROUP}」缺少 {link}")
        if practice is not None:
            for link in ORIGINAL_QA_LINKS:
                if f"{SITE}{link}" in practice:
                    problems.append(f"{name}「练习方法」仍包含 {link}")
    return problems


def meta_content(html, key, attr="name"):
    matched = re.search(
        rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"',
        html,
    )
    return matched.group(1) if matched else ""


def json_ld(html):
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>',
        html,
        re.S,
    )
    parsed = []
    for block in blocks:
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError:
            parsed.append(None)
    return parsed


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def check_home_directory():
    """首页「内容目录」应包含侧栏里的每一个链接。"""
    review_path = os.path.join(DIST, "practice", "review.html")
    home_path = os.path.join(DIST, "index.html")
    problems = []
    if not os.path.exists(review_path) or not os.path.exists(home_path):
        return ["找不到 review.html 或 index.html，无法核对首页目录"]
    groups = sidebar_groups(open(review_path, encoding="utf-8").read()) or []
    sidebar_links = []
    for _, links in groups:
        for link in links:
            if link not in sidebar_links:
                sidebar_links.append(link)
    home = open(home_path, encoding="utf-8").read()
    block = heading_block(home, "内容目录")
    if block is None:
        return ["首页缺少「内容目录」"]
    listed = set(links_in(block))
    missing = [link for link in sidebar_links if link not in listed]
    if missing:
        problems.append("首页内容目录缺少侧栏链接：" + "、".join(missing))
    return problems


def check_sitemap_lastmod():
    path = os.path.join(DIST, "sitemap.xml")
    src = os.path.join(ROOT, "docs", ".vitepress", "lastmod.json")
    problems = []
    if not os.path.exists(path):
        return ["找不到 sitemap.xml"]
    if not os.path.exists(src):
        return ["找不到 docs/.vitepress/lastmod.json"]
    xml = open(path, encoding="utf-8").read()
    expected = json.load(open(src, encoding="utf-8"))
    found = {}
    for loc, lastmod in re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", xml):
        found[loc] = lastmod
    for route in EXPECTED:
        loc = SITE + ("/" if route == "/" else route)
        lastmod = found.get(loc)
        if not lastmod:
            problems.append(f"sitemap 缺少 {loc} 的 lastmod")
            continue
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", lastmod):
            problems.append(f"{loc} 的 lastmod 不是 ISO 8601：{lastmod}")
            continue
        wanted = expected.get(route)
        if not wanted:
            problems.append(f"lastmod.json 缺少 {route}")
            continue
        if parse_time(lastmod) != parse_time(wanted):
            problems.append(f"{loc} lastmod {lastmod} 与记录 {wanted} 不一致")
    return problems


def strip_tags(html: str) -> str:
    t = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style\b[^>]*>.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", "", t)


def main():
    if not os.path.isdir(DIST):
        print(f"❌ 找不到构建产物: {DIST}\n   请先执行 npm run build")
        return 1

    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    base = f"http://127.0.0.1:{PORT}"
    ok = True
    results = []
    descriptions = {}

    try:
        for path in EXPECTED:
            url = base + path
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    code, html = r.status, r.read().decode("utf-8", "ignore")
            except urllib.error.HTTPError as e:
                code, html = e.code, e.read().decode("utf-8", "ignore")
            except Exception as e:
                results.append((path, -1, 0, "ERROR", str(e)))
                ok = False
                continue

            text = strip_tags(html)
            length = len(text)

            m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            canonical = m.group(1) if m else ""
            expect_canonical = SITE + ("/" if path == "/" else path)

            t = re.search(r"<title>(.*?)</title>", html)
            title = t.group(1) if t else ""
            description = meta_content(html, "description")
            og_description = meta_content(html, "og:description", "property")
            og_url = meta_content(html, "og:url", "property")
            h1_count = len(re.findall(r"<h1\b", html))
            ld = json_ld(html)
            ld_text = json.dumps(ld, ensure_ascii=False)

            has_skeleton = "正在加载内容" in text

            status = []
            if code != 200:
                status.append(f"HTTP{code}")
            if length < 400:
                status.append("正文缺失")
            if canonical != expect_canonical:
                status.append(f"canonical={canonical}")
            if og_url != expect_canonical:
                status.append(f"og:url={og_url}")
            if has_skeleton:
                status.append("骨架残留")
            if not description or description == SITE_DESCRIPTION or len(description) < 20:
                status.append("description 缺失或仍是全站介绍")
            elif description in descriptions:
                status.append(f"description 与 {descriptions[description]} 重复")
            else:
                descriptions[description] = path
            if og_description != description:
                status.append("og:description 与 description 不一致")
            if h1_count != 1:
                status.append(f"h1={h1_count}")
            if path == "/":
                if title != HOME_TITLE:
                    status.append(f"title={title}")
                if '"@type": "WebSite"' not in ld_text:
                    status.append("首页缺少 WebSite")
                if "BreadcrumbList" in ld_text:
                    status.append("首页不应有面包屑标记")
            else:
                if not title.endswith(TITLE_SUFFIX):
                    status.append(f"title={title}")
                if '"@type": "BreadcrumbList"' not in ld_text or '"@type": "Article"' not in ld_text:
                    status.append("缺少 Article 或面包屑")
                if '"name": "首页"' not in ld_text:
                    status.append("面包屑缺少首页")

            flag = "✅" if not status else "❌"
            if status:
                ok = False
            results.append((path, code, length, flag, " ".join(status) or "ok"))

        # 输出
        print("=" * 72)
        print("构建产物验证 —— 逐页检查静态 HTML 是否含真实正文")
        print("=" * 72)
        print(f"{'URL':<38}{'码':<5}{'正文字数':>8}  结果")
        print("-" * 72)
        for path, code, length, flag, msg in results:
            print(f"{path:<38}{code:<5}{length:>8}  {flag} {msg}")

        # 死链检查：正文内链
        print()
        print("=" * 72)
        print("内链与图片检查")
        print("=" * 72)
        links = set()
        imgs = set()
        for root, _, files in os.walk(DIST):
            for fn in files:
                if not fn.endswith('.html'):
                    continue
                s = open(os.path.join(root, fn), encoding='utf-8', errors='ignore').read()
                for h in re.findall(r'href="(/[^"#?]*)"', s):
                    if h.startswith('/assets/') or h.endswith('.ico'):
                        continue
                    links.add(h.rstrip('/') or '/')
                for src in re.findall(r'src="(/assets/[^"]+)"', s):
                    imgs.add(src)

        def exists(url_path):
            p = url_path.lstrip('/')
            for cand in (os.path.join(DIST, p), os.path.join(DIST, p + '.html'),
                         os.path.join(DIST, p, 'index.html')):
                if os.path.exists(cand):
                    return True
            return False

        bad_links = sorted(l for l in links if not exists(l))
        bad_imgs = sorted(i for i in imgs if not exists(i))

        print(f"  内链总数 {len(links)}，死链 {len(bad_links)}")
        for b in bad_links:
            print("    ❌", b)
        print(f"  图片总数 {len(imgs)}，缺失 {len(bad_imgs)}")
        for b in bad_imgs:
            print("    ❌", b)

        # 静态资源可达性
        print()
        for p in ['/llms.txt', '/llms-full.txt', '/robots.txt', '/sitemap.xml']:
            ok_path = os.path.exists(os.path.join(DIST, p.lstrip('/')))
            print(f"  {'✅' if ok_path else '❌'} {p}")
            if not ok_path:
                ok = False

        if bad_links or bad_imgs:
            ok = False

        print()
        print("=" * 72)
        print("原创问答导航（侧栏倒数第二 / 首页目录 / llms，网址保持 /practice/）")
        print("=" * 72)
        nav_problems = check_original_qa_nav()
        if nav_problems:
            ok = False
            for item in nav_problems:
                print("  ❌", item)
        else:
            print("  ✅ 「一个路人甲原创问答」紧挨在「资料与课程」之前，链接仍是 /practice/original-qa-01 与 /practice/original-qa-02")

        print()
        print("=" * 72)
        print("首页目录覆盖侧栏 / sitemap lastmod")
        print("=" * 72)
        extra = check_home_directory() + check_sitemap_lastmod()
        if extra:
            ok = False
            for item in extra:
                print("  ❌", item)
        else:
            print("  ✅ 首页目录包含全部侧栏链接，sitemap lastmod 与 lastmod.json 一致")

    finally:
        httpd.shutdown()

    print()
    print("=" * 72)
    print("✅ 全部通过" if ok else "❌ 存在问题，见上")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
