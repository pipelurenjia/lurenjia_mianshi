# AGENTS.md - Agentic Coding Guidelines

This repository contains a Docsify-powered documentation site for structured interview preparation materials.

## Project Overview

- **Type**: Static documentation site (Docsify)
- **Language**: Chinese (Simplified)
- **Content**: Markdown files for interview frameworks and skills
- **No build step required**: Changes to `.md` files are auto-refreshed in preview

---

## Commands

### Preview Documentation Locally

```bash
# Serve docsify locally (requires docsify-cli)
docsify serve .

# Or use Python simple server
python -m http.server 3000
```

Then open http://localhost:3000 in browser.

### No Linting/Testing

This is a pure content repository - no JavaScript/TypeScript code, no tests, no linting.

---

## File Structure

```
/
├── index.html          # Docsify entry point
├── _sidebar.md         # Navigation sidebar config
├── _cover.md           # Cover page config
├── framework/          # 面试框架 (Interview frameworks)
│   └── viewpoint.md
│   └── structure.md
├── skills/             # 面试技巧 (Interview skills)
│   ├── talk.md
│   └── review.md
└── AGENTS.md           # This file
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

Sidebar is configured in `_sidebar.md`:
```markdown
- 面试框架
  - [观点展开法](/framework/viewpoint.md)
  - [答题结构](/framework/structure.md)
- 面试技巧
  - [话术技巧](/skills/talk.md)
  - [复盘方法](/skills/review.md)
```

To add new pages:
1. Create `.md` file in appropriate folder
2. Add entry to `_sidebar.md`

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

Custom styles in `index.html`:
- Cover gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Theme: Vue.css from unpkg docsify

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
| Add new article | Create `.md` file, update `_sidebar.md` |
| Fix typo | Edit `.md` file directly |
| Add navigation | Edit `_sidebar.md` |
| Customize theme | Edit `index.html` styles |
| Add search | Docsify search is already enabled |

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
