# Coding Agent 与通用 Agent 的区别（按层比较，基于 2026-11 源码核查）

- **日期**：2026-11-26（本版替换同日早先版本，早先版本的多条结论经源码核查不成立）
- **领域**：AI Agent 架构 / Coding Agent / Harness 设计
- **状态**：`learning`
- **样本**：coding agent 取 OpenCode v1.19.6、Codex CLI；通用 agent 取 OpenClaw 2026.11.10、Hermes Agent（main），DeerFlow 2.0 作旁证

## 1. 核心结论

1. **架构层没有类别差异。** 两者都是"模型 + harness"。按"能否做到"无法区分，任何能力都能通过加工具或改配置获得。
2. **执行内核已经趋同。** 主流开源实现都有 shell 执行、带容错的文件编辑、SKILL.md 格式的 skill、上下文压缩。OpenClaw 还能把整轮执行交给 Codex app-server，相当于直接把 coding agent 当执行内核。
3. **区别在运行契约**，即默认配置按哪种用法设计：

| 维度 | Coding agent | 通用 agent |
| :--- | :--- | :--- |
| 触发 | 开发者或流水线按任务调用（TUI、`run --format json`、`exec --json`） | 常驻网关，由消息渠道、定时任务、webhook 触发 |
| 工作单元 | 一个任务一个会话 | 服务某个人或团队的长期会话流 |
| 工作区语义 | 用户的仓库，是被修改的对象 | agent 自己的家目录，存放人格、用户画像、记忆 |
| 状态 | 工作区文件和 git | 记忆和会话库（embedding、FTS 检索） |
| 完成语义 | 工程验证（lint、typecheck、测试） | 结果送达渠道 |
| 信任边界 | 工作区沙箱加命令审批 | 请求人身份加渠道策略 |

4. 这些差异的共同来源是**服务对象和工作单元**。它们都是默认值，可以配置，两类产品也在互相吸收（OpenCode 可由 GitHub 评论和定时任务触发，Codex 桌面版有定时任务和记忆）。

## 2. 经核查不成立的说法（避免再犯）

- "通用 agent 的编辑工具简陋"：Hermes `tools/fuzzy_match.py` 的 9 级策略与 OpenCode `edit.ts` 的 9 个匹配器有 8 种同名；Hermes 还有语法检查、LSP 诊断，覆写前要求完整读过文件。
- "coding agent 强制先读后改"：取决于实现。OpenCode 1.19.6 只在工具描述里要求，代码没有检查。
- "通用 agent 遇错就停下问人"：OpenClaw 系统提示词的 Execution Bias 要求持续到完成或受阻，交付前验证。
- "只有 coding agent 贴合模型后训练的工具格式"：OpenClaw 同样提供 apply_patch，并按模型家族注入提示词。
- "测试时关掉 coding agent 的 edit/write 就能防止它绕过被测脚本"：bash 仍然能写文件；如果线上宿主也有这些工具，关掉反而造成假阴性。测试环境应与线上宿主的工具、提示词、模型对齐。

## 3. 模型与 harness 的适配

- OpenAI Codex 提示指南：模型按 apply_patch 格式训练，工具名、参数、输出越贴近训练分布效果越好。
- DeepSeek-V4.1-Flash 模型卡：同一模型在 8 个 coding harness 上，DeepSWE 从 65.5（OpenCode）到 74.2（只有 bash 的 mini-SWE），Terminal-Bench 2.1 从 84.1 到 90.6。
- SWE-agent（2024，GPT-4 Turbo）：专门设计的 ACI 比只用 shell 多解决 10.7 个百分点，编辑时做语法检查贡献 3.0 个百分点。
- 结论：适配是"模型 + harness"组合的属性，工具最多的 harness 不一定最好，需要按组合实测。

## 4. 方法论收获

- 做技术对比先分层（模型 / 执行内核 / 运行契约 / 产品外层），再逐层比较；把框架通用能力当成类别区别是常见错误。
- 用"能否做到"区分同构系统，必然被反例推翻；应比较默认值和设计重心。
- 每条结论回到源码或官方文档核对，并记录版本或 commit；开源 agent 迭代很快，二手印象容易过时。

## 5. 用于 skill 自动开发流水线时（补充）

- 没有对比证据表明 coding agent 在 skill 开发上效果更好；跨 harness 的公开数据只比较了 coding agent 之间。
- 通用 agent 也提供面向 CI 的单次无头模式：OpenClaw `openclaw agent exec`（临时状态目录、`--isolated`、`--json` 最终汇总），Hermes `hermes chat --oneshot --format stream-json`（逐次工具调用事件，`--safe-mode` 关闭个人配置、记忆、插件、MCP）。
- OpenCode 做隔离反而要手工拼（XDG 目录、`OPENCODE_DISABLE_*`、git init 挡 AGENTS.md、占位 node_modules），"coding agent 配置更省事"不成立。
- 真正影响集成的是事件粒度：OpenCode 有逐步 token（`step_finish`）和逐次工具调用；Hermes 工具输出截断 5000 字符、token 只在最终 result；OpenClaw `agent exec` 只有最终汇总。
- 要得出明确结论，需要同模型、同任务集的对照实验，用流水线现有的 lint 和 selftest 判定结果。
