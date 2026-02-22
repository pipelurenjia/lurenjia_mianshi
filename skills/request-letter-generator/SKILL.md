---
name: request-letter-generator
description: |
  基于 Word 模板自动生成内部请示函文档
  
  Triggers when user mentions:
  - "生成请示"
  - "写请示"
  - "创建请示文档"
  - "基于模板生成请示"
---

基于 Word 模板快速生成标准化的内部请示函文档。

## 功能

- 使用预设模板保持格式一致
- 自动替换函号、标题、正文、日期等关键内容
- 保持原有字体和排版格式
- 自动处理日期格式（支持"今天"）
- 支持生成 PDF 文件（需安装转换工具）

## Quick Usage (Already Configured)

### 通过命令行使用

```bash
python .opencode/skills/request-letter-generator/scripts/generate.py \
  --title "支付网红见面会餐饮费用" \
  --content "为加强和当地网红的联系，涵养社会人脉，我办拟于近期组织在我办事处举办冷餐会，需要购买餐食800瑞士法郎。该款项拟从当地活动项目列支。" \
  --number "8"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--title` | 事项标题（必填） | - |
| `--content` | 正文内容（必填） | - |
| `--number` | 函号（必填） | - |
| `--date` | 落款日期 | 今天 |
| `--agent` | 经办人姓名 | 游洋洋 |
| `--template` | 模板文件路径 | 请示函_模板.docx |
| `--output` | 输出文件路径 | 自动生成 |
| `--pdf` | 生成 PDF 文件（可选） | 不生成 |

### 在 Python 中使用

```python
from scripts.generate import generate_request_letter

result = generate_request_letter(
    title="支付网红见面会餐饮费用",
    content="为加强和当地网红的联系...",
    letter_number="8",
    date="今天",
    agent="游洋洋"
)
print(f"文档已生成：{result}")
```

## 模板要求

模板应为标准的请示函 Word 文档，包含：
- 文头（Logo + 标题）
- 函号位置
- 标题位置
- 正文位置
- 落款位置
- 第二页审批表格

## Common Gotchas

- ✅ **模板已内置**：`请示函_模板.docx` 和 `image1.jpeg` 已包含在 skill 中
- 正文内容会自动应用首行缩进
- 日期支持"今天"或"YYYY年MM月DD日"格式
- 标题使用**黑体**，正文使用**仿宋_GB2312**
- PDF 转换支持：docx2pdf（推荐）、LibreOffice、unoconv

## 📦 包含的文件

Skill 已包含完整模板：
- `请示函_模板.docx` - 标准请示函 Word 模板
- `image1.jpeg` - 文头徽标图片

## 🚚 迁移到其他电脑

只需复制整个 skill 文件夹即可：
```bash
.opencode/skills/request-letter-generator/
```

无需额外配置，模板已内置！

## First-Time Setup (If Not Configured)

1. 确保已安装依赖：
   ```bash
   pip install python-docx
   ```

2. （可选）如需生成 PDF，安装以下任一工具：
   ```bash
   pip install docx2pdf
   # 或
   # 安装 LibreOffice: https://www.libreoffice.org/
   ```

3. （可选）如需自定义模板，可替换 `请示函_模板.docx`

## 示例

生成一个简单的请示：
```bash
python scripts/generate.py \
  --title "购买办公用品" \
  --content "为满足日常办公需要，拟购买打印机一台，预算3000元。该款项拟从办公经费列支。" \
  --number "15" \
  --agent "张三"
```
