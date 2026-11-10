# -*- coding: utf-8 -*-
"""
把每个正文页的 git 作者时间写入 docs/.vitepress/lastmod.json。

VitePress 自己也会跑 git log 来填 sitemap lastmod。Cloudflare Pages 若浅克隆，
所有文件都会变成同一次提交的时间，Google 和必应会逐渐不相信这个字段。

- 仓库历史完整时：按各文件最后一次提交重写 json。
- 浅克隆或没有 git 时：保留已提交的 json，不用当前构建时间覆盖。

用法：
    python3 scripts/gen-lastmod.py
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, ".vitepress", "lastmod.json")


def run(args):
    return subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def is_shallow():
    proc = run(["git", "rev-parse", "--is-shallow-repository"])
    if proc.returncode != 0:
        return True
    return proc.stdout.strip() == "true"


def route_for(rel_md):
    rel = rel_md.replace("\\", "/")
    if rel == "index.md":
        return "/"
    if rel.endswith("/index.md"):
        rel = rel[: -len("index.md")].rstrip("/")
    elif rel.endswith(".md"):
        rel = rel[:-3]
    if not rel.startswith("/"):
        rel = "/" + rel
    return rel or "/"


def pages():
    found = []
    for dirpath, dirnames, filenames in os.walk(DOCS):
        dirnames[:] = [name for name in dirnames if name != ".vitepress"]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, DOCS).replace("\\", "/")
            found.append(rel)
    return sorted(found)


def main():
    if is_shallow():
        print("git 历史不完整，保留已有 lastmod.json")
        return 0

    data = {}
    for rel in pages():
        proc = run(["git", "log", "-1", "--format=%aI", "--", os.path.join("docs", rel)])
        iso = proc.stdout.strip()
        if proc.returncode != 0 or not iso:
            print(f"  [跳过] 没有提交时间: docs/{rel}", file=sys.stderr)
            continue
        data[route_for(rel)] = iso

    if not data:
        print("没有写入任何页面时间", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"lastmod.json : {len(data)} 页")
    return 0


if __name__ == "__main__":
    sys.exit(main())
