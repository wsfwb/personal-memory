---
id: DEC-20261127-02
title: 记忆库改用 LLM Wiki 模式（raw / wiki / index / log / lint）
date: 2026-11-27
status: decided
reversibility: two-way-door
review_date: 2026-12-27
tags: [architecture, agent-memory, productivity]
---

# 决策记录：记忆库改用 LLM Wiki 模式

## 1. 背景、核心诉求与现实约束
- **要解决的真正问题**：初版协议是“任意目录任务结束自动写 topics / decisions / daily”，写入自动、读取手动、没有淘汰。Agent 判断“高价值”时偏向多写，按天堆文件，几十篇后 index 会变成没人翻的目录，维护一堆没用的记忆。
- **关键约束**：仍要零运维（Git + Markdown），仍要跨目录可用；不能为了整洁增加记录负担。
- **与 goals 的对齐**：目标 3（跑通个人记忆与决策系统）；同时记忆分层、写入策略、淘汰与检索本身就是目标 2（Agent 记忆 / 上下文工程）的核心课题，拿自己的仓库做实验场。

## 2. 备选方案评估

| 方案 | 预期收益 | 最坏情况 | 机会成本 |
| :--- | :--- | :--- | :--- |
| **A. LLM Wiki（采用）**：raw 只追加；wiki 页按“东西”组织、先更新再新建；根 `index.md` 唯一入口；`log.md` 操作日志；lint 查孤儿 / 过期 / 坏链 / 超限 | 页面数量随概念数增长而非随天数增长；每次 ingest 让已有页更准；lint 把“值不值得留”的判断挪到事后 | 规则太多 Agent 不遵守，退化成原样 | 改写 AGENTS.md、脚本、索引，约半天 |
| B. 只提高写入门槛 + inbox 先行 | 改动最小 | 没有 index/log/lint，噪音只是延后到 inbox 里堆 | 低 |
| C. 引入向量库 / Mem0 类工具 | 检索强 | 违背 11-25 决策与“不做工具链过度折腾”；数据量根本不需要 | 高 |
| 维持现状 | 0 | 一个月后 index 失效、重复页增多 | 复盘时要花时间清理 |

## 3. 原则与盲区检查
- 符合“先最小闭环再优化”：目录不大动，只换规则和入口，`rg` 足以检索。
- 风险在“规则多了没人遵守”：所以把能自动化的放进 `memory_status.py`，模型只负责判断矛盾与归档。

## 4. 最终决定与核心假设
- **最终选择**：方案 A。具体：`reviews/daily/`、`inbox/` 为 raw 层；`profile/`、`learning/topics/`、`decisions/`、`reviews/weekly|postmortems` 为 wiki 层；合并三个子 index 为根 `index.md`；新增 `log.md`；`memory_status.py` 升级为 lint；`principles.md` 上限 30 条；跨目录自动沉淀默认只写 raw 和更新已有页，新建 wiki 页需先说明。
- **核心假设**：wiki 页数量按概念增长，一个月内 topics 不超过 15 页且没有重复主题；lint 每周跑一次能在 5 分钟内处理完。
- **什么信号说明选错了**：index 里出现同一主题两页以上；raw 连续两周没有被 ingest 进任何 wiki 页；用户觉得规则重到不想记。

## 5. 到期回看验证（2026-12-27）
- **实际回看日期**：
- **结果评估**：
- **认知复盘**：

## 参考
- 来源讨论：[2026-11-27 日常记录](../reviews/daily/2026-11-27.md)
- 前序决策：[个人记忆与决策系统技术选型](./2026-11-25-memory-system-architecture.md)
- 模式来源：Karpathy “LLM Wiki” 笔记（raw sources → LLM 维护的 wiki → index + log → lint），以及 MemGPT 分层记忆、Zettelkasten fleeting → permanent 的提炼流程
