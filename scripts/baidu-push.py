#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""百度「普通收录」URL 批量推送（支持断点续跑）

用法：
    python scripts/baidu-push.py --list                 # 只导出 URL 列表（手动提交用）
    python scripts/baidu-push.py --limit 10             # 按配额推 10 条
    python scripts/baidu-push.py --token xxx --limit 10 # 直接指定密钥

断点续跑机制：
    已推送成功的 URL 会写进 project-progress/baidu-pushed.txt，
    下次运行自动跳过。所以断电、关机、中途失败都不会重复推送，
    也不会漏推——直接重跑即可。

配额：
    百度每天只给 10 条左右，且北京时间 0 点重置。
    当天配额用尽会返回 over quota，脚本按「正常结束」处理（退出码 0），
    定时任务不会误报失败，第二天接着推。

密钥：
    优先读 --token，其次读环境变量 BAIDU_TOKEN，
    再其次读 %USERPROFILE%\\.workbuddy\\secrets\\baidu-token.txt。
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITEMAP = ROOT / "dist" / "sitemap.xml"
STATE = ROOT / "project-progress" / "baidu-pushed.txt"
LOG = ROOT / "project-progress" / "baidu-push.log"
TOKEN_FILE = Path.home() / ".workbuddy" / "secrets" / "baidu-token.txt"
SITE = "https://yigelurenjia.com"

# 配额只有 10 条/天，按「总入口 → 转化页 → 搜索量大的题型页」排序先推这些。
# 没列出的页面排在后面，按 sitemap 原顺序。
PRIORITY = [
    "/",
    "/guide/start-here",
    "/guide/resources",
    "/guide/guerrilla",
    "/guide/emergency",
    "/method/point-method",
    "/method/expand",
    "/question-types/comprehensive",
    "/question-types/organization",
    "/question-types/emergency",
    "/question-types/relationship",
    "/guide/choose-class",
]


def log(msg):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_sitemap(xml_text):
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(xml_text)
    return [loc.text.strip() for loc in root.findall(".//sm:loc", ns) if loc.text]


def read_urls():
    """优先读线上 sitemap（这样新发布的文章能自动纳入），
    线上取不到再退回本地构建产物，最后退回扫 docs 源文件。"""
    urls, source = None, None

    try:
        req = urllib.request.Request(
            f"{SITE}/sitemap.xml", headers={"User-Agent": "baidu-push/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            urls, source = parse_sitemap(resp.read().decode("utf-8")), "线上 sitemap"
    except Exception as e:
        log(f"⚠️ 线上 sitemap 取不到（{type(e).__name__}），改用本地 {SITEMAP.name}")

    if urls is None and SITEMAP.exists():
        urls, source = parse_sitemap(SITEMAP.read_text(encoding="utf-8")), "本地 sitemap"

    if urls is None:
        log(f"⚠️ 本地也没有 {SITEMAP}，回退为扫描 docs/ 源文件（URL 可能与线上有出入）")
        docs = ROOT / "docs"
        urls = []
        for md in sorted(docs.rglob("*.md")):
            if ".vitepress" in md.parts:
                continue
            rel = md.relative_to(docs).with_suffix("").as_posix()
            rel = "" if rel == "index" else rel
            rel = rel[: -len("/index")] if rel.endswith("/index") else rel
            urls.append(f"{SITE}/{rel}" if rel else SITE + "/")
        source = "docs"

    bad = [u for u in urls if not u.startswith(SITE + "/")]
    if bad:
        log(f"⚠️ 跳过 {len(bad)} 条非 {SITE} 的地址：{bad[:3]}")
    urls = [u for u in urls if u.startswith(SITE + "/")]
    log(f"URL 来源：{source}，共 {len(urls)} 条")
    return urls


def load_state():
    if not STATE.exists():
        return set()
    return {line.strip() for line in STATE.read_text(encoding="utf-8").splitlines() if line.strip()}


def save_state(urls):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with STATE.open("a", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")


def resolve_token(cli_token):
    if cli_token:
        return cli_token
    env = os.environ.get("BAIDU_TOKEN")
    if env:
        return env.strip()
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    return None


def push(urls, token):
    # ⚠️ 不要用 urllib.parse.urlencode：它会把 https:// 编码成 https%3A%2F%2F，
    # 百度解析不出站点，直接返回 400 {"message":"site init fail"}。
    endpoint = f"http://data.zz.baidu.com/urls?site={SITE}&token={token}"
    body = "\n".join(urls).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=body, headers={"Content-Type": "text/plain"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="只导出 URL 列表")
    ap.add_argument("--token", default=None, help="准入密钥")
    ap.add_argument("--all", action="store_true", help="忽略已推送记录，全量重推")
    ap.add_argument("--limit", type=int, default=0, help="本次最多推几条（吃配额）")
    args = ap.parse_args()

    urls = read_urls()

    if args.list:
        out = ROOT / "project-progress" / "baidu-urls.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(urls), encoding="utf-8")
        log(f"已导出 {len(urls)} 条到 {out}（手动提交用）")
        return 0

    done = set() if args.all else load_state()
    todo = [u for u in urls if u not in done]
    order = {SITE + p: i for i, p in enumerate(PRIORITY)}
    todo.sort(key=lambda u: (order.get(u, len(PRIORITY)), u))

    log(f"进度：已完成 {len(urls) - len(todo)}/{len(urls)}" + ("（全量模式）" if args.all else ""))
    if not todo:
        log("✅ 全部推送完成，无需再跑")
        return 0

    if args.limit:
        todo = todo[: args.limit]

    token = resolve_token(args.token)
    if not token:
        log("❌ 没有可用密钥：请设置环境变量 BAIDU_TOKEN，或写入 " + str(TOKEN_FILE))
        return 1

    try:
        result = push(todo, token)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "ignore")
        msg = ""
        try:
            msg = json.loads(raw).get("message", "")
        except Exception:
            pass
        if "quota" in msg.lower():
            log(f"今日配额已用尽（{msg}），本次推 0 条，明天自动继续")
            return 0
        if e.code == 401:
            log(f"❌ 密钥无效或站点不匹配：{raw}（site 必须是已验证的 {SITE}）")
        else:
            log(f"❌ 推送失败 HTTP {e.code}：{raw}")
        return 1
    except Exception as e:  # 断网、超时等
        log(f"❌ 网络异常：{type(e).__name__}: {e}")
        return 1

    log("百度返回：" + json.dumps(result, ensure_ascii=False))

    ok = result.get("success", 0)
    if ok:
        save_state(todo[:ok])
        log(f"✅ 成功 {ok} 条，今日剩余配额 {result.get('remain', '未知')}，进度 {len(urls) - len(todo) + ok}/{len(urls)}")
    else:
        log("本次没有成功推送的 URL")

    for key, label in (("not_same_site", "域名不匹配"), ("not_valid", "非法 URL")):
        if result.get(key):
            log(f"⚠️ {label}：{result[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
