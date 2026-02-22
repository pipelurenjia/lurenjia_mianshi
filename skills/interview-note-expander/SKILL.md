---
name: interview-note-expander
description: |-
  Expand short interview learning outlines/points into full Xiaohongshu notes. Use to transform brief bullet points into polished articles following the "一个路人甲" writing style.

  Examples:
  - user: "背诵是低效的，复述才是高效的" → expand to 500-word note with reasoning and examples
  - user: "答题要有深度，要看内在联系" → expand to method explanation note
  - user: "框架有了但展开不了怎么办" → expand to problem-solution note
  - user: "面试要刻意练习" → expand to practical method note
---

# 面试笔记要点扩展

## 任务
将用户给出的简短要点、提纲或关键词，扩展成完整的、结构清晰的小红书笔记。

## 输入形式
用户可能提供：
- 一个核心观点
- 几个要点/提纲
- 问答形式的提纲
- 某个问题的回答要点

## 输出形式
完整的markdown笔记，包含：
- 吸引人的开头
- 逻辑清晰的主体
- 结尾总结+固定格式

## 素材库位置
详见 `references/素材库索引.md`

## 写作风格（必须严格遵守）
详见 `references/风格指南.md`

### 固定结尾格式（普通笔记必须包含）
详见 `references/风格指南.md`

### 商品笔记结尾
- 售后服务承诺
- 购买方式/链接

## 扩展方法

### 1. 观点深化法
- 提炼核心观点
- 解释为什么（给出理由）
- 举例说明（可以是案例或场景）
- 给出建议或方法

### 2. 问题展开法
- 引入问题/痛点
- 分析问题原因
- 提供解决方案
- 总结要点

### 3. 对比分析法
- 引入两个概念
- 对比分析差异
- 给出适用场景
- 提出建议

### 4. 步骤讲解法
- 引入方法/技巧
- 分步骤说明
- 每步要点解释
- 总结注意事项

## 输出要求

### 篇幅
- 核心观点扩展：500-800字
- 方法讲解：800-1200字
- 问答扩展：300-500字/问

### 格式
- 使用markdown格式
- 适当使用emoji（✅、💡、🔥等）
- 段落之间有空行
- 关键句子可以加粗
- 分点用1. 2. 3. 或第一、第二、第三

## 生成流程

1. **理解要点**：明确用户提供的核心观点或提纲
2. **确定类型**：判断是普通笔记还是商品笔记
3. **选择方法**：根据内容选择扩展方法
4. **素材补充**：从资料库中寻找相关素材补充
5. **风格匹配**：按照风格要求生成内容
6. **检查结尾**：确保包含正确的结尾格式

## 注意事项
- 扩展不是简单凑字数，而是有逻辑地丰富内容
- 保持"一个路人甲"的简洁风格
- 不要添加无关的废话
- 观点要有深度，不要表面
- 例子要贴切，不要生硬
