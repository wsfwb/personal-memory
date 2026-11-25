# Personal Memory & Decision OS

这是一个由 **Git + Markdown + 本地 AI Agent** 共同维护的「个人第二大脑、复盘系统与决策支持库」。

它的核心目的不是囤积资料，而是建立一个**持续进化的人机协同闭环**：
1. **平时学习与做事** -> 让本地 Agent 随手记录、结构化归档，并关联实际应用。
2. **定期复盘总结** -> 从成败经历中提炼出属于你自己的**个人原则（Principles）**与能力边界。
3. **不确定时做决定** -> 当你纠结犹豫时，Agent 会调取你的「阶段目标 + 个人原则 + 历史决策结果」，帮你识别盲区、权衡利弊并追踪决策后续效果。

---

## 目录导航

| 目录 / 文件 | 作用说明 |
| :--- | :--- |
| [`AGENTS.md`](./AGENTS.md) | **本地 Agent 的工作协议**（自动指导 Agent 如何读写和维护本仓库） |
| [`profile/context.md`](./profile/context.md) | 个人背景、技能栈、现实约束（精力/时间/资源） |
| [`profile/goals.md`](./profile/goals.md) | 当前阶段的核心目标与「不做清单」 |
| [`profile/principles.md`](./profile/principles.md) | 个人原则库与防踩坑清单（越用越懂你的核心资产） |
| [`learning/`](./learning/index.md) | 学习笔记与知识地图（追踪从“了解”到“内化实践”的闭环） |
| [`reviews/`](./reviews/index.md) | 日常日志（`daily/`）、周复盘（`weekly/`）与专项复盘（`postmortems/`） |
| [`decisions/`](./decisions/index.md) | 决策档案库（记录关键选择、推理逻辑及到期回看验证结果） |
| [`inbox/`](./inbox/README.md) | 临时收集箱（随手丢进来的未分类想法，定期由 Agent 归档） |
| [`templates/`](./templates/) | 标准记录模板，确保长期维护格式统一 |
| [`skills/personal-memory/`](./skills/personal-memory/SKILL.md) | **全局跨目录 Agent Skill**（支持在其他任意项目目录直接召唤维护本库） |
| [`scripts/memory_status.py`](./scripts/memory_status.py) | 状态巡检脚本：一键查看待归档事项、到期需验证的决策等 |
| [`scripts/install_global.py`](./scripts/install_global.py) | **一键全局安装脚本**：注册全局 Skill、Agent 路由与终端快捷命令 |

---

## 跨目录全局联动（在其他项目干活时也能随时记录与辅助决策）

平时你不需要切回本目录，运行一次全局注册脚本（换电脑或移动仓库目录后重跑一次即可）：

```bash
python3 scripts/install_global.py
```

它会自动完成：
1. 将 `personal-memory` 技能软链接到 `~/.codex-one/skills/`、`~/.claude/skills/` 等本地 Agent 全局技能目录；
2. 在全局 `~/.codex-one/AGENTS.md` 与 `~/.claude/CLAUDE.md` 中注入轻量路径指引；
3. 在 `~/.zshrc` 中注册环境变量 `$PERSONAL_MEMORY_DIR` 以及两个终端快捷指令：
   - `pmem`：在任意目录一键巡检记忆库状态与到期需回看的决策；
   - `pmem-cd`：在任意目录一键跳回记忆库。

**跨目录使用示例（当你在其他业务代码仓库工作时）：**
> - *“刚刚排查出来的这个并发死锁问题很有代表性，帮我脱敏整理到个人记忆库的学习笔记里。”*
> - *“今天在这个项目上的推进和卡点帮我记到个人记忆库的今日日志里。”*
> - *“我在纠结这个模块要不要重构，结合我个人记忆库里的阶段目标和防踩坑原则，帮我做个决策分析并记录下来。”*

---

## 日常怎么和本地 Agent 配合使用？

你不需要手动去记忆复杂的模板格式，无论在本目录还是其他工程目录下启动本地 Agent（如 CodexOne / Claude Code 等），直接用自然语言对话即可：

### 1. 初次启动 / 更新画像
> - “帮我完善一下我的个人背景和近期目标，我目前主要在做……”

### 2. 平时学习与日常记录
> - “今天我学了 XXX，核心收获是……，帮我整理到学习库里。”
> - “记一下今天的进展：完成了 A，但在 B 上卡了很久，原因是……”
> - “把这个想法先丢进 inbox，周末复盘再细想：……”

### 3. 周期复盘与提炼原则
> - “帮我做一下这周的周复盘，看看我这周的时间花得值不值，有没有偏离目标。”
> - “今天这件事搞砸了/做得很顺，帮我做个专项复盘，并看看能不能提炼一条原则写进 `principles.md`。”

### 4. 纠结不确定时，辅助做决定
> - “我现在很纠结要不要做 X 还是 Y，背景是……，结合我的目标和以前的原则帮我分析一下怎么选。”
> - “看看有哪些以前做的决定到了回看日期，我们一起来验证一下当时的判断是否准确。”

---

## 快速巡检命令

在终端运行以下命令，可随时查看当前记忆库状态与待回看决策：

```bash
python3 scripts/memory_status.py
```
