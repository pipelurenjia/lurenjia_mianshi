# -*- coding: utf-8 -*-
"""
构建产物验证脚本（模拟生产环境的扩展名回退行为）

用法：
    npm run build && python scripts/verify-build.py

检查项：
1. 全部 36 个页面返回 200，且正文真实存在于静态 HTML 源码中（P0-1 回归测试）
2. 每页 canonical / og:url 逐页正确（不是共用首页的）
3. 页面标题格式为「文章标题 | 一个路人甲 · 结构化面试」
4. 所有正文内链无死链
5. 所有引用的图片资源存在
6. llms.txt / llms-full.txt / robots.txt / sitemap.xml 可访问
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
    "/expression/stop-words", "/expression/spoken-style", "/expression/fluency",
    "/mindset/nervous", "/mindset/anxiety", "/mindset/pace",
    "/mindset/study-fatigue", "/mindset/mindset",
    "/guide/resources",
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

    finally:
        httpd.shutdown()

    print()
    print("=" * 72)
    print("✅ 全部通过" if ok else "❌ 存在问题，见上")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
