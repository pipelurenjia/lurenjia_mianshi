# 主页 Logo 与配色优化计划

## TL;DR

> 将 Logo 添加到首页正中央，并将主页背景改为柔和的绿色渐变，与 Logo 颜色搭配。

**修改文件**：
- `index.html` — 更新 CSS 配色
- `_coverpage.md` — 添加 Logo 并居中显示（需同步更新 index.html 配置）

---

## 需求确认

1. **配色方案**：柔和绿色渐变（与 Logo 的绿色系呼应）
2. **Logo 显示**：居中放置在首页
3. **Logo 嵌入方式**：使用本地 SVG 文件

---

## 实现方案

### 1. 重命名 cover 文件并更新配置

- [ ] 将 `_cover.md` 重命名为 `_coverpage.md`
- [ ] 更新 `index.html` 中 `coverpage: true` 改为 `coverpage: '_coverpage.md'`

### 2. 更新 index.html 的 CSS 样式

- [ ] 将背景色从紫蓝渐变改为柔和绿色渐变
- [ ] 调整标题颜色为深绿色 #2d5a47
- [ ] 调整副标题颜色为灰绿色 #4a6b5c
- [ ] 调整按钮颜色为品牌绿色 #348f6b
- [ ] 更新按钮 hover 效果

### 3. 在 _coverpage.md 添加 Logo

- [ ] 在标题前添加居中的 Logo 图片
- [ ] 设置 Logo 宽度为 200px

---

## 验证步骤

- [ ] 运行 `docsify serve .` 启动本地预览
- [ ] 访问 http://localhost:3000 确认背景为柔和绿色渐变
- [ ] 确认 Logo 居中显示在标题上方
- [ ] 确认文字颜色清晰可读
- [ ] 确认按钮 hover 效果正常

---

## 预期效果

- **背景**：从淡绿(#e3efe8) → 中绿(#c5ddd0) → 稍深的绿(#a8d4c3) 的柔和渐变
- **Logo**：居中显示，与绿色背景和谐搭配
- **文字**：深绿色文字确保在浅色背景上有良好可读性
