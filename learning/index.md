# 学习库与知识地图（Learning Index）

> 状态说明：`learning`（学习理解中） | `to-practice`（已理解待实践） | `internalized`（已实践内化）

| 日期 | 主题笔记 | 所属领域 | 当前状态 | 核心收获 / 下一步行动 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-25 | [Skill 自进化闭环（Skill Loop）架构设计与工程模式](./topics/skill-self-evolution-loop-architecture.md) | AI Agent / Skill 自进化 | `learning` | 厘清「确定性代码编排 + 最小化 Coding Agent 职责（仅 Develop/Execute）」的 7 步自动迭代架构与无头隔离避坑要点；下一步重点调研 Coding Agent 与通用 Agent 在开发阶段的差异 |
| 2026-11-26 | [Coding Agent 与通用 Agent 的区别（按层比较，基于源码核查）](./topics/coding-agent-vs-general-agent-design-differences.md) | AI Agent 架构 / Coding Agent | `learning` | 经 OpenCode、Codex CLI、OpenClaw、Hermes 源码核查：执行内核已趋同，区别在运行契约（触发、工作单元、工作区语义、状态、完成语义、信任边界）；模型适配属于"模型 + harness"组合；记录了早先版本中不成立的说法 |
| 2026-11-27 | [Skill Loop 中只换 develop agent 的实测（同模型 Opus 5.5）](./topics/skill-loop-develop-agent-benchmark.md) | AI Agent / Skill 自进化 | `learning` | 同模型同输入下各 agent 改动方向一致、单轮分数差 7–10 分，耗时差 6–12 倍；评测单次噪声约 8 分；记录了压缩摘要放 assistant 角色被模型不认、上下文窗口配小、用量统计偏低、Codex 对非 OpenAI 模型名依赖模型目录等坑 |
- [学术论文 Rebuttal 审校防反驳清单](./topics/academic-rebuttal-audit.md) — Prompt/Schema 实证口径对齐、原论文指标核验与跨审稿人逻辑自洽原则
