# -*- coding: utf-8 -*-
"""
生成 AI 抓取入口文件：
  - llms.txt      摘要索引（llmstxt.org 规范）
  - llms-full.txt 全站正文完整合集（Markdown 原文）

用法：
    python scripts/gen-llms.py

说明：
- 内容直接从各目录下的 .md 源文件读取，与网站正文同源，改完文章重跑一次即可。
- 分类与顺序与 _sidebar.md 保持一致，首页（README.md）排在最前。
- 每条目的简介为手工撰写，勿改成自动抓取（正文里的引用块多是示例，抓出来会错）。
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")   # VitePress srcDir，正文都在这里
SITE = "https://yigelurenjia.com"

SUMMARY = (
    "一个免费、系统、实战的结构化面试自学知识体系。"
    "教的是底层思维方法而不是固定套路，覆盖布点法、观点展开法、问答笔记法、"
    "复述法、游击战法等原创方法论，以及综合分析、组织管理、应急应变、人际关系等各类题型。"
)

# (分类, 路由, 侧栏标题, 一句话简介)
PAGES = [
    ("入门指南", "guide/start-here", "从零开始怎么学",
     "按「完全小白 / 学了但混乱 / 能答但质量不高」三种状态分流，给出各自的学习路径与周期"),
    ("入门指南", "guide/guerrilla", "游击战法：快速入门",
     "不纠结一城一地得失，先用 2-3 小时了解题型就大量开练，边打边学"),
    ("入门指南", "guide/emergency", "上考场急救包",
     "只剩几天就要面试时的应急策略，帮你撑住场面"),
    ("入门指南", "guide/choose-class", "面试班选择指南",
     "报班还是自学、怎么挑面试班的决策参考"),

    ("答题方法论", "method/point-method", "布点法：如何快速破题",
     "拿到题先找一条逻辑主线，在主线上布 2-3 个要点，每个再展开 2-3 个小点"),
    ("答题方法论", "method/expand", "观点展开：怎么说清楚",
     "框架有了但展不开时，用广度法与深度法把一个观点说清楚"),
    ("答题方法论", "method/point-expand", "观点展开法：完整版",
     "观点展开法的完整汇编，核心讲观点要明确犀利、答完再找补体现周全"),
    ("答题方法论", "method/breadth-depth", "广度深度：展不开怎么办",
     "广度拓展拆成组成部分，深度挖掘追问为什么与怎么办"),
    ("答题方法论", "method/concrete", "化虚为实：避免车轱辘话",
     "把抽象、空泛的表述落到具体事例与动作上，不再翻来覆去"),
    ("答题方法论", "method/break-homogenization", "答题同质化怎么破",
     "大家答得都差不多时怎么出彩：加宏观视角、用生活例子、形成自己的角度"),
    ("答题方法论", "method/improve-depth", "提高深度：洞察事物内在联系",
     "深度不是堆术语套官话，而是看到别人看不到的联系，附刻意练习路径"),
    ("答题方法论", "method/practice-macro", "宏观练习：大量答题把握规律",
     "见题少就会觉得每题都是新题，答得多了才能建立题型框架，附答疑"),

    ("题型专训", "question-types/comprehensive", "综合分析题",
     "最常见也最能体现思维深度的题型，是什么→为什么→怎么办"),
    ("题型专训", "question-types/organization", "组织管理题",
     "考察计划组织协调能力，关键是流程清晰、重点突出"),
    ("题型专训", "question-types/emergency", "应急应变题",
     "考察突发情况处理能力，关键是快、准、稳"),
    ("题型专训", "question-types/relationship", "人际关系题",
     "考察处理人际关系的能力，关键是理解、沟通、改进"),
    ("题型专训", "question-types/simulation", "情景模拟题",
     "代入角色现场模拟说话，关键是真实自然"),
    ("题型专训", "question-types/attitude-viewpoint", "态度观点题怎么答",
     "用「来龙去脉」法破题，不再没思路"),
    ("题型专训", "question-types/impromptu-speech", "即兴演讲题怎么答",
     "即兴演讲不是考表演是考思路，忘记演讲正常答题"),
    ("题型专训", "question-types/allegory", "漫画名言哲理题",
     "先讲清漫画/名言的道理，再结合社会现象或态度观点，转化为综合分析题作答"),
    ("题型专训", "question-types/research", "调研类题目",
     "调研类题目的解题方法，先理解调研目的再设计内容"),

    ("练习方法", "practice/review", "复盘方法论",
     "复盘不是重做：复盘思路对不对、亮点在哪、问题在哪，分浅复盘与深复盘"),
    ("练习方法", "practice/practice-methods", "高效练习方法",
     "关键词输出法、限时思考法与练习量建议"),
    ("练习方法", "practice/note-taking-deep", "问答笔记法详解",
     "积累思路最有效的方法：提炼问题与要点，遮住答案复述"),
    ("练习方法", "practice/repeat-deep", "复述法详解",
     "背诵是低效的，合上材料用自己的话讲出来才是真掌握"),
    ("练习方法", "practice/practice-with-others", "对练方法",
     "一个人练和对练效果完全不同，讲怎么组织高效对练"),

    ("表达能力", "expression/stop-words", "口头语消除训练",
     "接受停顿、放慢语速、录音复盘，系统消除「嗯、那个、就是」"),
    ("表达能力", "expression/spoken-style", "口语化表达",
     "答题不是念稿子，是说人话"),
    ("表达能力", "expression/fluency", "流畅性训练",
     "先想后说、一次只说一件事，解决卡顿"),

    ("心态调整", "mindset/nervous", "考场紧张怎么办",
     "紧张是正常的，重要的是学会与紧张共处，附压力脱敏训练"),
    ("心态调整", "mindset/anxiety", "焦虑缓解方法",
     "备考焦虑是正常的，关键是学会与焦虑共处"),
    ("心态调整", "mindset/pace", "备考节奏把控",
     "备考是马拉松不是短跑，讲不同阶段的节奏安排"),
    ("心态调整", "mindset/study-fatigue", "备考厌学怎么办",
     "学着学着不想学了怎么办，帮你调整状态继续前进"),
    ("心态调整", "mindset/mindset", "心态答疑：坚持还是放弃",
     "关于坚持还是放弃、要不要休息、什么时候该精雕细琢的答疑"),

    ("资料与课程", "guide/resources", "配套资料与视频课",
     "作者整理的系统化补充内容：视频课与文字资料合集（网站本体全部免费）"),
]

HOMEPAGE = ("index", "站点总览：核心价值、学习路径与完整目录")


def read_md(route):
    path = os.path.join(DOCS, route + ".md")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_title_body(text):
    """拆出第一个 H1 作为标题，其余作为正文。"""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return line[2:].strip(), "\n".join(lines[i + 1:]).strip()
    return None, text.strip()


def main():
    # ---------- llms.txt：摘要索引 ----------
    idx = [
        "# 一个路人甲 · 结构化面试原创学习体系",
        "",
        f"> {SUMMARY}",
        "",
        "- 作者：路人甲（自学面试 93 分上岸）",
        f"- 站点：{SITE}",
        "- 许可：CC BY-NC-SA 4.0",
        "- 内容全部免费开放，无付费墙",
        f"- 完整正文合集：{SITE}/llms-full.txt",
        "",
        "## 适合谁",
        "",
        "- 零基础小白：不知道从哪里开始",
        "- 进阶提升者：能答题但质量不高",
        "- 自学党：不想报班或报班没效果",
        "- 时间紧迫者：几天就要面试",
        "",
        "## 核心方法论",
        "",
        "- **布点法**：一道题先找逻辑主线，布 2-3 个要点，每个要点再展开 2-3 个小点",
        "- **观点展开法**：广度拓展（拆成组成部分）+ 深度挖掘（追问为什么、怎么办）",
        "- **问答笔记法**：阅读时提炼问题与要点，复习时遮住答案复述，形成输入-输出闭环",
        "- **复述法**：合上材料用自己的话讲出来，能讲出来才是真掌握",
        "- **游击战法**：边打边学、大量练习，不纠结一城一地得失",
        "",
        "## 推荐起始页面",
        "",
        "- 新手入门 → /guide/start-here",
        "- 快速了解方法论 → /method/point-method",
        "- 时间紧迫 → /guide/emergency",
        "",
        "## 全部内容",
        "",
    ]

    current = None
    for section, route, nav_title, desc in PAGES:
        if section != current:
            idx.append(f"### {section}")
            idx.append("")
            current = section
        idx.append(f"- [{nav_title}]({SITE}/{route})：{desc}")
    idx.append("")
    idx.extend([
        "## 配套资料与课程",
        "",
        "网站内容全部免费。如需更系统的整理，作者在小红书店铺提供付费资料与视频课：",
        "",
        f"- 资料与视频课介绍：{SITE}/guide/resources",
        "- 结构化面试视频课（主推）：方法论 + 四大题型 + 讲义与思维导图，共 237 分钟",
        "- 文字资料合集：《答题思维总结》约 3 万字 +《答题示例（逐字稿）》32 题 2.7 万字",
        "- 获取方式：小红书搜索 `pipelurenjia`（昵称：一个路人甲（自学面试上岸）），或扫码进店",
        "",
        "---",
        "",
        "✅",
        "我是路人甲",
        "原创结构化面试自学资料体系",
        "重剑无锋 大道至简",
        "希望每个人都可以通过自学上岸",
        "✅",
        "",
    ])
    index_text = "\n".join(idx)

    # ---------- llms-full.txt：正文合集 ----------
    full = [
        "# 一个路人甲 · 结构化面试原创学习体系",
        "",
        f"> {SUMMARY}",
        "",
        "本文件是站点全部正文的完整合集（Markdown 原文），供 AI 系统与检索代理直接读取。",
        "网站正文由 JavaScript 渲染，不执行 JS 的抓取器请直接读取本文件或 /llms.txt。",
        "",
        "- 作者：路人甲（自学面试 93 分上岸）",
        f"- 站点：{SITE}",
        "- 许可：CC BY-NC-SA 4.0",
        "- 说明：网站内容全部免费开放，付费资料与课程为可选补充",
        "",
        "---",
        "",
        "## 目录",
        "",
        f"- [首页]({SITE}/)：{HOMEPAGE[1]}",
    ]
    current = None
    for section, route, nav_title, desc in PAGES:
        if section != current:
            full.append("")
            full.append(f"### {section}")
            current = section
        full.append(f"- [{nav_title}]({SITE}/{route})：{desc}")
    full.extend(["", "---", ""])

    # 首页正文
    text = read_md(HOMEPAGE[0])
    if text:
        title, body = split_title_body(text)
        full.append(f"# 首页 · {title}")
        full.append("")
        full.append(f"来源：{SITE}/")
        full.append("")
        full.append(body)
        full.extend(["", "---", ""])

    # 各页正文
    for section, route, nav_title, desc in PAGES:
        text = read_md(route)
        if not text:
            print(f"  [跳过] 找不到 {route}.md")
            continue
        title, body = split_title_body(text)
        full.append(f"# {title}")
        full.append("")
        full.append(f"来源：{SITE}/{route}")
        full.append("")
        full.append(body)
        full.extend(["", "---", ""])

    full_text = "\n".join(full).rstrip() + "\n"

    public = os.path.join(DOCS, "public")
    os.makedirs(public, exist_ok=True)
    with open(os.path.join(public, "llms.txt"), "w", encoding="utf-8", newline="") as f:
        f.write(index_text)
    with open(os.path.join(public, "llms-full.txt"), "w", encoding="utf-8", newline="") as f:
        f.write(full_text)

    print(f"llms.txt      : {len(index_text):>7} 字符")
    print(f"llms-full.txt : {len(full_text):>7} 字符")
    print(f"收录页面      : {len(PAGES) + 1} 篇（含首页）")


if __name__ == "__main__":
    main()
