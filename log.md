# 操作日志（Log）

> 只追加、不改写。每次 ingest / query 落页 / lint 整理 记一行，格式：
> `- YYYY-MM-DD | <op> | <来源或触发> | 改动页面（新建 + / 更新 ~ / 归档 x）`
> 作用：知道“什么时候因为什么改了哪些页”，lint 据此判断哪些 raw 还没被消化。细节看 `git log`。

- 2026-11-25 | init | 建仓 | + profile/context, + profile/goals, + profile/principles, + decisions/memory-system-architecture, + decisions/arr-rebuttal-strategy, + topics/skill-self-evolution-loop-architecture, + topics/academic-rebuttal-audit
- 2026-11-26 | ingest | ARR Rebuttal 补充实验定稿 | ~ topics/academic-rebuttal-audit, raw daily/2026-11-26
- 2026-11-26 | ingest | 源码核查 OpenCode/Codex/OpenClaw/Hermes | + topics/coding-agent-vs-general-agent-design-differences（替换同日早先版本）
- 2026-11-27 | ingest | skill loop 换 develop agent 对照实验 | + topics/skill-loop-develop-agent-benchmark, ~ 同页多次补坑（判官配错、缓存统计、Hermes 压缩失败）
- 2026-11-27 | ingest | skill 自进化框架网页层 | + decisions/skill-autodev-web-thin-shell, raw daily/2026-11-27
- 2026-11-27 | restructure | 讨论“记忆会不会越积越多” | 改用 LLM Wiki 模式：+ index.md（合并 learning/decisions/reviews 三个子索引）, + log.md, ~ AGENTS.md, ~ scripts/memory_status.py（升级为 lint）, + decisions/llm-wiki-memory-model
