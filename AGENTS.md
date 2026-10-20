# AGENTS.md - Agentic Coding Guidelines

This repository contains a **VitePress**-powered documentation site for structured interview preparation materials.

> 2026-10 已从 Docsify 迁移到 VitePress。原因：Docsify 是纯客户端渲染，正文要等 JS 运行时才拉取，百度、GPTBot、ClaudeBot 等不执行 JS 的爬虫读到的是只有 41 个字的空壳。VitePress 是静态站点生成（SSG），每页输出完整静态 HTML。

## Project Overview

- **Type**: Static documentation site (VitePress · SSG)
- **Language**: Chinese (Simplified)
- **Content**: Markdown files for interview frameworks and skills
- **Build required**: `npm run build` → 产物输出到 `dist/`

---

## Commands

```bash
npm install      # 安装依赖
npm run dev      # 本地预览（http://localhost:5173）
npm run build    # 构建到 dist/
npm run preview  # 预览构建产物
npm run llms     # 重新生成 llms.txt / llms-full.txt
```

### 构建后验证（含 P0-1 回归测试）

```bash
npm run build && python scripts/verify-build.py
```

该脚本会逐个请求全部 36 个页面，确认正文真实存在于静态 HTML 源码中、canonical/og:url 逐页正确、内链与图片无缺失。

---

## File Structure

```
/
├── docs/                    # VitePress 源目录（srcDir）
│   ├── .vitepress/
│   │   ├── config.mjs         # 标题、导航、侧栏、head、sitemap
│   │   └── theme/
│   │       ├── index.mjs       # 自定义插件（放大 / 埋点 / 换页上报）
│   │       ├── FooterCta.vue  # 全站文末引流块
│   │       └── custom.css      # lrj- 引流组件样式
│   ├── index.md              # 首页（hero + 内容索引）
│   ├── guide/                 # 入门指南 + 资料与课程承接页
│   ├── method/                # 答题方法论
│   ├── question-types/        # 题型专训
│   ├── practice/              # 练习方法
│   ├── expression/            # 表达能力
│   ├── mindset/               # 心态调整
│   └── public/                # 静态资源（原样拷到站点根）
│       ├── assets/img/        # 引流组件用图
│       ├── favicon.ico
│       ├── robots.txt
│       ├── llms.txt
│       └── llms-full.txt
├── scripts/
│   ├── gen-llms.py           # 生成 llms.txt / llms-full.txt
│   └── verify-build.py       # 构建产物验证（36 页回归）
├── notes/                     # 原始笔记素材
├── 内容素材/                   # 501 篇小红书素材（未挂导航）
└── AGENTS.md                  # 本文件
```

---

## Content Guidelines

### Language
- **All content must be in Simplified Chinese**
- Use Chinese punctuation:，。、！？；：
- Consistent terminology throughout

### Markdown Conventions

1. **Headers**: Use `#` for titles, `##` for sections, `###` for subsections
2. **Emphasis**: Use `**bold**` for emphasis, `*italic*` for subtle notes
3. **Lists**: Use `-` for unordered lists, `1.` for ordered lists
4. **Checkboxes**: Use `- [ ]` for unchecked, `- [x]` for checked

### Content Structure

- Each file should have a clear title (`# Title`)
- Use horizontal rules `---` to separate major sections
- End signature blocks with `✅` separator:
```
✅
我是路人甲
原创结构化面试自学资料体系
重剑无锋 大道至简
希望每个人都可以通过自学上岸
✅
```

### Naming Conventions

- Files: lowercase with hyphens (e.g., `viewpoint.md`, `talk-skills.md`)
- Folder names: Chinese (e.g., `framework/`, `skills/`)
- Navigation: Use descriptive Chinese titles

### Writing Style

1. **Tone**: Professional but approachable
2. **Length**: Substantial content per article (500-2000 characters)
3. **Structure**: Clear problem-solution format
4. **Examples**: Include concrete examples where helpful

---

## Navigation Configuration

Sidebar is configured in `docs/.vitepress/config.mjs` under `themeConfig.sidebar`:
```js
{
  text: '我是小白',
  items: [
    { text: '从零开始怎么学', link: '/guide/start-here' }
  ]
}
```

To add new pages:
1. Create `.md` file in the appropriate folder under `docs/`
2. Add an entry to `themeConfig.sidebar` in `config.mjs`
3. Re-run `npm run llms` to refresh the AI entry files

---

## Adding New Content

### New Category/Folder
1. Create folder (e.g., `theory/`)
2. Add files to folder
3. Update `_sidebar.md` with new section

### New Article
1. Create `.md` file in existing folder
2. Use consistent header format
3. Add to `_sidebar.md` navigation

---

## Theme Customization

**站点框架**：VitePress（2026-10 从 Docsify 迁移）。配置文件 `docs/.vitepress/config.mjs`。

**品牌色规范**：
- 品牌绿：`#348f6b`（按钮、价格、强调色统一用这个）
- Hero 文字：`#2d5a47`，副文字 `#4a6b5c`
- 原封面渐变：`linear-gradient(315deg, #B3B8FE 0%, #D4DCD7 50%, #F2FCB4 100%)`（迁移后作为首页 hero 视觉参考）

### 引流组件（勿随性改动）

转化相关组件统一使用 `lrj-` 前缀，样式集中在 `docs/.vitepress/theme/custom.css`：

| 类名 | 用途 | 位置 |
|------|------|------|
| `.lrj-cover-cta` | 首页底部资料入口 | `docs/index.md` |
| `.lrj-side-card` | 侧栏底部常驻「关于我」卡片 | `docs/.vitepress/config.mjs`（侧栏尾部 HTML） |
| `.lrj-hero` / `.lrj-grid` / `.lrj-card` | 承接页主推卡与商品卡 | `docs/guide/resources.md` |
| `.lrj-quote` | 买家评价引用 | `docs/guide/resources.md` |
| `.lrj-buy` / `.lrj-qr-card` | 二维码转化区 | `docs/guide/resources.md` |
| `.lrj-footer-cta` | 全站文末引流块 | `docs/.vitepress/theme/FooterCta.vue`，经 `doc-after` 插槽注入 |

文末引流块由 `FooterCta.vue` 注入到每个文档页；首页与 `guide/resources` 自动跳过（与 Docsify 时代行为一致）。图片资源在 `docs/public/assets/img/`，原图在仓库根 `assets/img/`（迁移遗留，待清理）。

---

## Git Workflow

```bash
# Create new branch for changes
git checkout -b add-new-article

# Commit changes
git add .
git commit -m "add: 新增XXX文章"

# Push and create PR if needed
git push -u origin add-new-article
```

---

## Common Tasks

| Task | Action |
|------|--------|
| Add new article | Create `.md` under `docs/`, update `config.mjs` sidebar |
| Fix typo | Edit the `.md` file directly |
| Add navigation | Edit `themeConfig.sidebar` in `config.mjs` |
| Customize theme | Edit `docs/.vitepress/theme/custom.css` |
| Update AI entry files | Run `npm run llms` |
| Verify build | Run `npm run build && python scripts/verify-build.py` |

---

## Notes for Agents

- This is a **documentation content** repository, not a code project
- No build pipelines, no CI/CD, no automated tests
- Primary work: creating/editing Markdown content in Chinese
- All paths in markdown should be relative and absolute from root (e.g., `/framework/viewpoint.md`)
- Preview locally to verify changes appear correctly

---

## Available Skills

### 📦 Project Skills (12个)

| Skill Name | 用途 | 触发场景 |
|------------|------|----------|
| **skill-creator** | 创建/更新opencode skills | 创建新技能、更新技能描述、验证技能结构 |
| **skill-snapshot** | 技能快照管理：扫描、备份、恢复、列表、对比 | "快照my-skill"、"恢复技能"、"列出快照" |
| **deep-research** | 深度调研8步法：模糊主题→高质量调研报告 | "深度调研"、"对比分析"、"写调研报告" |
| **evolution-mind** | Agent自我进化思维框架 | 每次任务完成自动触发能力沉淀 |
| **interview-note-expander** | 扩展面试学习要点为完整小红书笔记 | 扩展简短要点为500-800字笔记 |
| **xiaohongshu-product-note** | 生成小红书商品推广笔记 | "写一篇视频课介绍"、"FAQs怎么写" |
| **xiaohongshu-normal-note** | 生成小红书普通教育内容笔记 | "写一篇关于如何提高答题深度的笔记" |
| **interview-qa-extractor** | 从一对一课程转写中提取写作角度和素材 | "帮我从转写中找一些写作角度" |
| **xiaohongshu-title-generator** | 生成小红书爆款标题（8-12个备选） | "帮我生成标题"、"关于答题深度的标题" |
| **xiaohongshu-caption** | 为长图/图片内容生成小红书正文 | "帮我写一段小红书正文" |
| **interview-writer** | 将面试问答/提纲转化为800字+长文 | 扩展短答案为完整文章 |
| **request-letter-generator** | 基于Word模板自动生成内部请示函文档 | "生成请示"、"写请示" |

### 🔧 Built-in Skills (4个)

| Skill Name | 用途 |
|------------|------|
| **playwright** | 浏览器自动化：验证、浏览、截图、测试 |
| **frontend-ui-ux** | 前端UI/UX设计（无需设计稿也能输出惊艳UI） |
| **git-master** | Git操作：atomic commits, rebase/squash, history search |
| **dev-browser** | 浏览器自动化（持久页面状态） |

### 使用示例

```typescript
// 项目skills
skill(name="xiaohongshu-title-generator")

// 通过task加载skills
task(category="writing", load_skills=["xiaohongshu-normal-note"], prompt="写一篇关于答题深度的笔记")
```

### Skills 文件位置

```
skills/
├── deep-research/SKILL.md
├── evolution-mind/SKILL.md
├── interview-note-expander/SKILL.md
├── interview-qa-extractor/SKILL.md
├── interview-writer/SKILL.md
├── request-letter-generator/SKILL.md
├── skill-creator/SKILL.md
├── skill-snapshot/SKILL.md
├── xiaohongshu-caption/SKILL.md
├── xiaohongshu-normal-note/SKILL.md
├── xiaohongshu-product-note/SKILL.md
└── xiaohongshu-title-generator/SKILL.md
```
