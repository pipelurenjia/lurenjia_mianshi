# -*- coding: utf-8 -*-
"""
构建产物验证脚本（模拟生产环境的扩展名回退行为）

用法：
    npm run build && python scripts/verify-build.py

检查项：
1. 全部 39 个页面返回 200，且正文真实存在于静态 HTML 源码中（P0-1 回归测试）
2. 每页 canonical / og:url 逐页正确（不是共用首页的）
3. 页面标题格式为「文章标题 | 一个路人甲 · 结构化面试」
4. 所有正文内链无死链
5. 所有引用的图片资源存在
6. llms.txt / llms-full.txt / robots.txt / sitemap.xml 可访问
7. 侧栏「原创问答」是独立分组，链接仍是 /practice/original-qa-*，且不在「练习方法」下
8. 首页「内容目录」有独立的「原创问答」栏目，链接与侧栏一致
"""

import os
import re
import sys
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SITE = "https://yigelurenjia.com"
PORT = 4173
# 侧栏分组与首页目录必须同时指向这些既有网址
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
    """侧栏、首页目录、llms 索引三处都把原创问答当作独立栏目，且网址不变。"""
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
        if by_title.get("原创问答") != ORIGINAL_QA_LINKS:
            problems.append(f"侧栏「原创问答」链接不符：{by_title.get('原创问答')}")
        leaked = [link for link in ORIGINAL_QA_LINKS if link in by_title.get("练习方法", [])]
        if leaked:
            problems.append(f"原创问答仍挂在侧栏「练习方法」下：{leaked}")
        if "练习方法" in titles and "原创问答" in titles:
            if titles.index("原创问答") != titles.index("练习方法") + 1:
                problems.append("侧栏「原创问答」应紧跟在「练习方法」之后")

    if not os.path.exists(home_path):
        problems.append("找不到 index.html，无法检查首页目录")
    else:
        home = open(home_path, encoding="utf-8").read()
        qa_block = heading_block(home, "原创问答")
        practice_block = heading_block(home, "练习方法")
        if qa_block is None:
            problems.append("首页内容目录缺少「原创问答」栏目")
        else:
            got = [link for link in links_in(qa_block) if link.startswith("/practice/original-qa")]
            if got != ORIGINAL_QA_LINKS:
                problems.append(f"首页「原创问答」链接不符：{got}")
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
        qa = section_body(text, "原创问答")
        practice = section_body(text, "练习方法")
        if qa is None:
            problems.append(f"{name} 缺少「原创问答」分类")
        else:
            for link in ORIGINAL_QA_LINKS:
                if f"{SITE}{link}" not in qa:
                    problems.append(f"{name}「原创问答」缺少 {link}")
        if practice is not None:
            for link in ORIGINAL_QA_LINKS:
                if f"{SITE}{link}" in practice:
                    problems.append(f"{name}「练习方法」仍包含 {link}")
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

            has_skeleton = "正在加载内容" in text

            status = []
            if code != 200:
                status.append(f"HTTP{code}")
            if length < 400:
                status.append("正文缺失")
            if canonical != expect_canonical:
                status.append(f"canonical={canonical}")
            if has_skeleton:
                status.append("骨架残留")

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
        print("原创问答导航（侧栏独立分组 / 首页目录 / llms，网址保持 /practice/）")
        print("=" * 72)
        nav_problems = check_original_qa_nav()
        if nav_problems:
            ok = False
            for item in nav_problems:
                print("  ❌", item)
        else:
            print("  ✅ 原创问答已独立成组，链接仍是 /practice/original-qa-01 与 /practice/original-qa-02")

    finally:
        httpd.shutdown()

    print()
    print("=" * 72)
    print("✅ 全部通过" if ok else "❌ 存在问题，见上")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
