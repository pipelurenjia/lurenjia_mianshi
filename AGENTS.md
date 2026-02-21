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
