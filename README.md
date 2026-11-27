# Personal Memory & Decision OS

这是一个由 **Git + Markdown + 本地 AI Agent** 共同维护的「个人第二大脑、复盘系统与决策支持库」，按 **LLM Wiki** 模式组织：
raw 层只追加地记录发生了什么，wiki 层由 Agent 编译成按“东西”组织的页面并原地更新，`index.md` 是唯一入口，`log.md` 记每次操作，`memory_status.py` 做 lint 清理孤儿页和过期页。知识编译一次、反复读取，页面数量随概念增长而不是随天数增长。

它的核心目的不是囤积资料，而是建立一个**持续进化的人机协同闭环**：
1. **平时学习与做事** -> 让本地 Agent 随手记录、结构化归档，并关联实际应用。
2. **定期复盘总结** -> 从成败经历中提炼出属于你自己的**个人原则（Principles）**与能力边界。
3. **不确定时做决定** -> 当你纠结犹豫时，Agent 会调取你的「阶段目标 + 个人原则 + 历史决策结果」，帮你识别盲区、权衡利弊并追踪决策后续效果。

---

## 目录导航

| 目录 / 文件 | 作用说明 |
| :--- | :--- |
| [`AGENTS.md`](./AGENTS.md) | **本地 Agent 的工作协议**（自动指导 Agent 如何读写和维护本仓库） |
| [`index.md`](./index.md) | **唯一入口**：所有 wiki 页的目录，一行一页（一句话 + 状态） |
| [`log.md`](./log.md) | 只追加的操作日志：何时因何事改了哪些页 |
| [`profile/context.md`](./profile/context.md) | 个人背景、技能栈、现实约束（精力/时间/资源） |
| [`profile/goals.md`](./profile/goals.md) | 当前阶段的核心目标与「不做清单」 |
| [`profile/principles.md`](./profile/principles.md) | 个人原则库与防踩坑清单（上限 30 条，超了先合并淘汰） |
| `learning/topics/` | wiki 概念页：一个概念 / 机制 / 方法一页，先更新再新建 |
| `decisions/` | wiki 决策页：一个决策一页（ADR），到期回看写回结果 |
| `reviews/daily/` | raw：日常日志，只追加不改写，不入目录 |
| `reviews/weekly/`、`reviews/postmortems/` | wiki 综合页：周复盘与专项复盘，产出回流到原则与概念页 |
| [`inbox/`](./inbox/README.md) | raw：未消化碎片，周复盘时升格、合并或删除 |
| [`templates/`](./templates/) | 标准记录模板，确保长期维护格式统一 |
| [`skills/personal-memory/`](./skills/personal-memory/SKILL.md) | **全局跨目录 Agent Skill**（支持在其他任意项目目录直接召唤维护本库） |
| [`scripts/memory_status.py`](./scripts/memory_status.py) | lint 脚本：到期决策、待消化 inbox、未入 index、坏链接、孤儿页、过期页、原则超限 |
| [`scripts/sync_memory.py`](./scripts/sync_memory.py) | **自动安全扫描 + 一键同步 GitHub 脚本**（自动拦截敏感 Token 并执行 commit & push） |
| [`scripts/install_global.py`](./scripts/install_global.py) | **一键全局安装脚本**：注册全局 Skill、Agent 路由与终端快捷命令 |

---

## 跨目录无感自动沉淀与 GitHub 同步

平时你不需要切回本目录，运行一次全局注册脚本（换电脑或移动仓库目录后重跑一次即可）：

```bash
python3 scripts/install_global.py
```

它会自动完成：
1. 将 `personal-memory` 技能软链接到 `~/.codex-one/skills/`、`~/.claude/skills/` 等本地 Agent 全局技能目录；
2. 在全局 `~/.codex-one/AGENTS.md` 与 `~/.claude/CLAUDE.md` 中启用**跨目录沉淀协议**（当你排查了深度 Bug、梳理了核心架构、拍板了关键方案或完成重要里程碑时，Agent 先写 raw 日志、再更新已有 wiki 页；要新建 wiki 页会先说一句；日常琐碎改动不记）；
3. 在 `~/.zshrc` 中注册环境变量 `$PERSONAL_MEMORY_DIR` 以及三个终端快捷指令：
   - `pmem`：在任意目录一键巡检记忆库状态与到期需回看的决策；
   - `pmem-sync`：手动触发一键提交并同步到 GitHub；
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

## 快速巡检命令（lint）

在终端运行以下命令（或任意目录输入 `pmem`），查看到期决策、待消化 inbox、孤儿页、坏链接、过期页与原则条数：

```bash
python3 scripts/memory_status.py
```
