---
name: xiaohongshu-product-note
description: |-
  Generate product promotion Xiaohongshu notes for interview learning materials/courses. Use to create sales-focused content that introduces products naturally while providing value.

  Examples:
  - user: "帮我写一篇视频课介绍" → generate course intro with story and value proposition
  - user: "材料合集的FAQs怎么写" → generate Q&A style product explanation
  - user: "一个差评的回应怎么写" → generate response to negative feedback
  - user: "创作历程怎么分享" → generate behind-the-scenes story
---

# 小红书商品笔记生成

## 任务
根据用户给定的主题或商品信息，生成与「一个路人甲」风格一致的小红书商品笔记（带销售性质的内容）。

## 素材库位置
详见 `references/素材库索引.md`

## 商品笔记风格（必须严格遵守）
详见 `references/风格指南.md`

### 核心调性
- **真诚**：不夸大，实事求是
- **低调**：不吹嘘，有自信但不张扬
- **温暖**：像朋友推荐，不强推
- **实在**：强调价值，不玩虚的

### 常见类型及写法

#### 1. 商品介绍型
- 开头：引入痛点或需求
- 中间：介绍商品特点、价值、适用人群
- 结尾：购买方式、售后承诺

#### 2. FAQ型（高频使用）
- 列出常见问题
- 用"问X：...答X：..."格式
- 问题要真实（从答疑中积累）
- 回答要简洁清晰

#### 3. 差评回应型
- 承认问题存在
- 解释原因或背景
- 表明改进态度
- 承诺售后服务

#### 4. 创作历程型
- 个人经历分享
- 创作初心和过程
- 感谢支持
- 未来展望

#### 5. 不推荐购买型（反向营销）
- 明确说明不适合人群
- 真诚建议其他方案
- 反而增加信任感

### 售后服务承诺（常用表达）
- "有任何不满意，随时找我，该改正改正，该退款退款，不含糊"
- "熟悉我的朋友都了解我的售后政策"

### 适用人群描述（常用）
- 小白、进阶、拔高
- 报班、自学
- 公务员、事业单位、遴选、三支一扶等
- 半结构化、结构化小组、教师、税务等（细分）

## 输出要求

### 篇幅
- 短篇商品笔记：300-500字
- 详细介绍：800-1200字
- FAQ类型：可长可短，根据问题数量

### 格式
- 使用markdown格式
- 适当使用emoji
- FAQ使用"问/答"格式
- 段落之间有空行

### 内容原则
详见 `references/风格指南.md`

## 商品素材参考
详见 `references/素材库索引.md`

### 常见卖点
- 100%原创
- 洞察底层逻辑
- 不人云亦云的思考角度
- 实战经验总结
- 好评价："醍醐灌顶"

## 生成流程

1. **明确商品**：确定要推广的商品类型
2. **选择类型**：确定笔记类型（介绍/FAQ/历程等）
3. **素材匹配**：从资料库中提取相关素材
4. **风格匹配**：按照上述风格要求生成内容
5. **检查要素**：确保包含必要的售后承诺和适用人群说明

## 注意事项
- 不要使用"家人们"、"姐妹们"、"必抢"等话术
- 不要过度承诺效果
- 不要贬低竞争对手
- 保持"一个路人甲"的低调真诚风格
- 可以主动说明不适合的人群，反而增加可信度
