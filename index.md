# 知识索引（Index）

> 这是整个记忆库的唯一入口与目录页。Agent 每次会话先读本文件，再按需打开具体页面。
> 每个 wiki 页在这里只占一行：一句话说清这页讲什么、现在处于什么状态。raw 层（`reviews/daily/`、`inbox/`）不入目录，按日期直接查。
> 规则见 [AGENTS.md](./AGENTS.md)。操作记录见 [log.md](./log.md)。

## 核心页（Profile，每次会话必读）

| 页面 | 一句话 | 更新 |
| :--- | :--- | :--- |
| [context](./profile/context.md) | 后端 + AI Agent 方向工程师，处于切入核心项目前的蓄力期；决策时重点看“能否加深 Agent/后端硬实力或更快切入核心项目” | 2026-11-25 |
| [goals](./profile/goals.md) | 本季度三件事：切入核心链路、Agent + 后端体系化沉淀、跑通个人记忆与决策系统；不做清单：碎片 AI 噱头、工具链过度折腾、只收藏不消化 | 2026-11-25 |
| [principles](./profile/principles.md) | 单向门/双向门、机会成本、先最小闭环；学习必须回答“解决我什么问题”；破局期原则 | 2026-11-25 |

## 概念与机制页（Topics）

状态：`learning`（理解中） | `to-practice`（已理解待实践） | `internalized`（已实践内化） | `archived`（过期归档）

| 页面 | 领域 | 状态 | 一句话 | 更新 |
| :--- | :--- | :--- | :--- | :--- |
| [Skill 自进化闭环架构](./learning/topics/skill-self-evolution-loop-architecture.md) | AI Agent / Skill Loop | `learning` | 确定性步骤全归编排代码，Coding Agent 只负责 Develop/Execute 的 7 步自动迭代架构；无头隔离避坑；模型侧三个上限（窗口 / 输出含思考 / 超时）按后端能力和 skill 体积配 | 2026-11-27 |
| [Coding Agent 与通用 Agent 的区别](./learning/topics/coding-agent-vs-general-agent-design-differences.md) | AI Agent 架构 | `learning` | 源码核查 OpenCode/Codex/OpenClaw/Hermes：执行内核趋同，差别在运行契约（触发、工作单元、工作区、状态、完成语义、信任边界） | 2026-11-26 |
| [Skill Loop 只换 develop agent 的实测](./learning/topics/skill-loop-develop-agent-benchmark.md) | AI Agent / Skill Loop | `learning` | 同模型下 agent 差别在效率与稳定性而非改动方向；评测噪声约 8 分，比较前先测噪声；换判官会改变排序 | 2026-11-27 |
| [学术 Rebuttal 审校防反驳清单](./learning/topics/academic-rebuttal-audit.md) | 研究方法 | `to-practice` | 绝不编造超出原文 Prompt/公式的事后动机；Prompt/Schema 口径对齐、原论文指标核验、跨审稿人逻辑自洽 | 2026-11-26 |

## 决策页（Decisions）

状态：`proposed`（分析中） | `decided`（已拍板执行） | `reviewed`（已到期回看）

| 日期 | 页面 | 状态 | 最终选择 | 回看日期 | 回看结果 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-11-25 | [个人记忆与决策系统技术选型](./decisions/2026-11-25-memory-system-architecture.md) | `decided` | Git + Markdown + 本地 Agent，暂不引入数据库或前端 | 2026-12-25 | 待验证 |
| 2026-11-25 | [ARR 论文 Rebuttal 实验与口径策略](./decisions/2026-11-25-arr-rebuttal-strategy.md) | `decided` | 零新增 API 成本挖掘 12 组缓存做统计检验与对照基线，只送强正向证据 | 2026-12-15 | 待验证 |
| 2026-11-27 | [skill 自进化框架的网页层：复用 CLI 的薄壳](./decisions/2026-11-27-skill-autodev-web-thin-shell.md) | `decided` | 标准库 http.server + 原生 JS；建任务调 CLI 函数、跑循环起子进程、进度读流水线落盘文件，不另建服务和状态存储 | 2026-12-27 | 待验证 |
| 2026-11-27 | [记忆库改用 LLM Wiki 模式](./decisions/2026-11-27-llm-wiki-memory-model.md) | `decided` | raw/wiki 分层、单一 index、操作 log、lint 巡检；wiki 页按“东西”组织先更新再新建，原则条数设上限 | 2026-12-27 | 待验证 |

## 综合页（Syntheses：周复盘 / 专项复盘）

- 暂无。周复盘写入 `reviews/weekly/YYYY-WXX.md`，专项复盘写入 `reviews/postmortems/YYYY-MM-DD-slug.md`，建好后在此加一行。

## Raw 层（不入目录，按日期查）

- 日常日志：`reviews/daily/YYYY-MM-DD.md`（最近：2026-11-25、11-26、11-27）
- 收集箱：`inbox/`
