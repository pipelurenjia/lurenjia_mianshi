---
name: skill-snapshot
description: |-
  管理 OpenCode 技能快照：扫描、备份、恢复、列表、对比技能版本。将备份存储在私有 GitHub 仓库中，随时可以恢复到任意版本。Use proactively when user wants to backup, restore, list, or diff skills.
  
  Examples:
  - user: "快照 my-skill" → save current version to GitHub
  - user: "恢复 my-skill 到 v1" → restore skill from snapshot
  - user: "列出所有技能快照" → list all available snapshots
  - user: "哪些技能需要备份" → scan and identify skills needing backup
  - user: "对比 my-skill 当前版本和 v2" → diff between current and snapshot
  - user: "初始化技能快照" → create private GitHub repo for backups
---

# Skill Snapshot

OpenCode 技能快照管理工具：将技能备份到私有 GitHub 仓库，支持版本回退。

## 触发词

- "快照"、"snapshot"、"保存技能"、"备份技能"
- "回退技能"、"恢复技能"、"restore skill"
- "列出快照"、"list snapshots"
- "对比差异"、"diff skill"
- "初始化快照"

## 命令格式

```
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py <command> [args]
```

### 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `scan` | 扫描技能，判断哪些需要备份 | `skill-snapshot scan` |
| `init` | 初始化私有仓库 | `skill-snapshot init` |
| `save <skill> [message]` | 保存快照 | `skill-snapshot save my-skill "添加新功能"` |
| `restore <skill> [version]` | 恢复版本 | `skill-snapshot restore my-skill v2` |
| `list [skill]` | 列出快照 | `skill-snapshot list my-skill` |
| `diff <skill> [version]` | 对比差异 | `skill-snapshot diff my-skill v1` |

## 配置

- **私有仓库**: `skill-snapshots`（自动创建）
- **本地克隆**: `~/.opencode/skill-snapshots/`
- **版本标签**: `<skill-name>/v<n>`（如 `my-skill/v1`）

## 技能位置

OpenCode 技能存储在两个位置：

| 类型 | 路径 |
|------|------|
| 全局技能 | `~/.config/opencode/skills/` |
| 项目技能 | `.opencode/skills/` |

skill-snapshot 会同时扫描这两个位置。

## 忽略规则

scan 命令根据以下规则自动判断哪些技能需要备份：

| 规则 | 跳过原因 |
|------|----------|
| `archive/` 目录 | 归档目录 |
| 符号链接 | 外部安装的技能 |
| `skill-snapshot` | 快照工具本身 |
| 包含 `.git/` | 自带版本控制 |
| 包含 `.venv/` 或 `node_modules/` | 包含大量依赖 |
| 体积 > 10MB | 体积过大 |
| 缺少 `SKILL.md` | 可能不是有效技能 |

## 执行流程

### scan - 扫描技能

扫描所有技能，判断哪些需要备份、哪些应跳过。

执行脚本：
```bash
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py scan
```

输出示例：
```
【需要备份】
  ✓ my-skill (5 files, 68K) [已有: my-skill/v1]
  ○ new-skill (3 files, 12K) [未备份]

【跳过】
  ✗ git-managed-skill - 自带 Git 版本控制
  ✗ external-plugin - 符号链接（外部安装）
```

### init - 初始化

1. 检查 GitHub CLI (`gh`) 是否已安装
2. 检查是否已认证 GitHub 账号
3. 检查私有仓库 `skill-snapshots` 是否存在
4. 如不存在，创建私有仓库
5. 克隆到本地 `~/.opencode/skill-snapshots/`

执行脚本：
```bash
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py init
```

### save - 保存快照

参数：
- `<skill>`: 技能名称（必填）
- `[message]`: 快照说明（可选，默认为时间戳）

流程：
1. 验证技能存在于 skills 目录
2. 确定下一个版本号（检查现有 tags）
3. 复制技能目录到仓库 `~/.config/opencode/skill-snapshots/<skill>/`
4. Git add, commit, tag, push

执行脚本：
```bash
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py save "<skill>" "[message]"
```

### restore - 恢复版本

参数：
- `<skill>`: 技能名称（必填）
- `[version]`: 版本号（可选，默认为最新）

流程：
1. 拉取最新仓库
2. 如未指定版本，列出可用版本让用户选择
3. Checkout 到指定 tag
4. 复制仓库中的技能目录到 skills 目录
5. 切回 main 分支

执行脚本：
```bash
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py restore "<skill>" "[version]"
```

### list - 列出快照

参数：
- `[skill]`: 技能名称（可选，不填则列出所有）

流程：
1. 拉取最新 tags
2. 过滤匹配的 tags
3. 显示版本列表和提交信息

执行脚本：
```bash
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py list "[skill]"
```

### diff - 对比差异

参数：
- `<skill>`: 技能名称（必填）
- `[version]`: 版本号（可选，默认为最新快照）

流程：
1. 提取指定版本的快照
2. 对比当前技能目录与快照
3. 显示差异

执行脚本：
```bash
python .opencode/skills/skill-snapshot/scripts/skill_snapshot.py diff "<skill>" "[version]"
```

## 存储结构

```
~/.opencode/skill-snapshots/          # 本地仓库
├── my-skill/
│   ├── SKILL.md
│   └── scripts/
├── another-skill/
│   └── SKILL.md
└── README.md

GitHub Tags:
├── my-skill/v1
├── my-skill/v2
├── my-skill/v3
└── another-skill/v1
```

## 使用示例

### 场景 1：首次使用

```
用户: 帮我初始化技能快照
AI: [执行 init.py]
```

### 场景 2：修改前保存

```
用户: 我要改 my-skill，先保存一下
AI: [执行 save.py my-skill "修改前备份"]
输出: 已保存快照 my-skill/v3
```

### 场景 3：改坏了回退

```
用户: my-skill 改坏了，退回上一版
AI: [执行 restore.py my-skill v2]
输出: 已恢复到 my-skill/v2
```

### 场景 4：查看历史

```
用户: my-skill 有哪些版本？
AI: [执行 list.py my-skill]
输出:
  v3 - 2025-01-10 - 修改前备份
  v2 - 2025-01-08 - 添加断点续写
  v1 - 2025-01-05 - 初始版本
```

## 注意事项

1. **符号链接跳过**：如 `external-plugin` 等外部安装的技能（符号链接）不支持快照
2. **archive 目录忽略**：不对 archive 目录下的技能做快照
3. **首次使用需 init**：首次使用前需执行 `init` 创建仓库
4. **网络依赖**：save/restore 需要网络连接推送到 GitHub
5. **平台要求**：需要安装 GitHub CLI (`gh`) 并认证
6. **Windows 支持**：脚本使用 Python 编写，跨平台兼容

## 文件结构

```
skill-snapshot/
├── SKILL.md                    # 本文件
└── scripts/
    └── skill_snapshot.py       # 统一的 Python CLI 入口
```
