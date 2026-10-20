# 一个路人甲 · 结构化面试原创学习体系

> **免费、系统、实战** — 从零基础到上岸的完整学习路径。打破机构套路，重构思维框架。

在线站点：<https://yigelurenjia.com>

---

## 项目类型

静态文档站，由 **VitePress** 构建（2026-10 从 Docsify 迁移完成）。

迁移原因：Docsify 为纯客户端渲染，正文要等 JS 运行时才拉取，非 JS 爬虫（百度、GPTBot、ClaudeBot 等）读到的是只有 41 个字的空壳。VitePress 为静态站点生成（SSG），每页都是完整的静态 HTML。

---

## 常用命令

```bash
npm install          # 安装依赖
npm run dev          # 本地预览（默认 http://localhost:5173）
npm run build        # 构建，产物输出到 dist/
npm run preview      # 预览构建产物
npm run llms         # 重新生成 llms.txt / llms-full.txt
```

---

## 目录结构

```
/
├── docs/                    ← VitePress 源目录（srcDir）
│   ├── .vitepress/
│   │   ├── config.mjs        站点配置：标题、导航、侧栏、head、sitemap
│   │   └── theme/
│   │       ├── index.mjs    自定义插件（放大/埋点/换页上报）
│   │       ├── FooterCta.vue 全站文末引流块
│   │       └── custom.css    lrj- 引流组件样式
│   ├── index.md              首页（hero + 内容索引）
│   ├── guide/                入门指南 + 资料与课程
│   ├── method/               答题方法论
│   ├── question-types/       题型专训
│   ├── practice/             练习方法
│   ├── expression/           表达能力
│   ├── mindset/              心态调整
│   └── public/               静态资源（原样拷贝到站点根目录）
│       ├── assets/img/       图片
│       ├── favicon.ico
│       ├── robots.txt
│       ├── llms.txt          AI 抓取入口（摘要索引）
│       └── llms-full.txt      AI 抓取入口（全站正文合集）
├── scripts/
│   ├── gen-llms.py           生成 llms.txt / llms-full.txt
│   └── verify-build.py       构建产物验证（36 页全量回归）
├── notes/                    未发布的原始笔记素材
├── 内容素材/                  501 篇小红书原始素材（未挂导航，版权待确认）
└── skills/                   Agent 技能包（与站点无关）
```

---

## 部署（Cloudflare Pages）

| 配置项 | 值 |
|---|---|
| Build command | `npm run build` |
| Build output directory | `dist` |

⚠️ **必须关闭 SPA 回退**：Docsify 时代需要把所有未知路径回退到 `index.html`，迁移后必须关掉，否则 404 会被兜成首页，且 `dist/404.html` 不会生效。

⚠️ **Bots 设置需核对**：Cloudflare → Bots，确认未拦截 GPTBot / ClaudeBot / anthropic-ai / CCBot / Bytespider（实测这批曾被 403）。

---

## 内容维护

1. 在 `docs/` 对应分类下新增或修改 `.md`
2. 新页面需同步两处：
   - `docs/.vitepress/config.mjs` 的 `sidebar`（否则导航里找不到）
   - 跑一次 `npm run llms` 更新 AI 入口文件
3. `npm run build && python scripts/verify-build.py` 验证无死链

---

## 引流组件约定

转化相关组件统一使用 `lrj-` 前缀，样式集中在 `docs/.vitepress/theme/custom.css`，改动需保守——倾向"重排顺序"而非"隐藏元素"。

| 类名 | 用途 |
|------|------|
| `.lrj-hero` / `.lrj-grid` / `.lrj-card` | 承接页主推卡与商品卡 |
| `.lrj-bundle` | 资料合集横向大卡 |
| `.lrj-buy` / `.lrj-qr-card` | 二维码转化区 |
| `.lrj-copy` | 口令一键复制 |
| `.lrj-stats` / `.lrj-quote-card` / `.lrj-wall` | 好评数据条、引言卡、截图墙 |
| `.lrj-side-card` | 侧栏常驻「关于我」卡片 |
| `.lrj-footer-cta` | 全站文末引流块 |

---

## 许可

本作品采用 CC BY-NC-SA 4.0 许可证进行许可。
版权所有 © 2026 路人甲
