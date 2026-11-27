# Skill 自进化闭环（Skill Loop）架构设计与工程模式

- **日期**：2026-11-25
- **领域**：AI Agent 工程 / Skill 自动迭代闭环 / Coding Agent
- **状态**：`learning`

## 1. 核心设计思想：确定性编排 + 最小化 Agent 职责

在将「改 Skill → 自测 → 整理问题 → 再改」自动化为多轮闭环（Skill Loop）时，最关键的架构边界是**区分确定性代码与非确定性模型判断**：

- **确定性步骤全部交给编排代码（Workflow Orchestrator）**：
  上下文拼装、静态规范检查（Lint）、版本快照与 Diff 生成、打包、测试沙箱调度、从 JSON 事件流提取客观事实、账单/Token 统计、停止条件判定、断点续跑（每步落盘状态文件）。
- **Coding Agent 仅承担两项需要推理判断的任务**：
  1. **Develop（开发/修改）**：读取需求、人工反馈、上轮自测事实与轨迹，修改目标 Skill，并按约定 Schema 将结构化改动说明写入结果文件（如 `result.json`）。
  2. **Execute（无头自测执行）**：在全新隔离的会话与工作目录中，像真实线上环境一样加载该 Skill 并执行测试用例。

## 2. 单轮循环的 7 步标准流水线

1. **Prepare（准备上下文）**：确定基线版本（`latest` 最新版，或接入评测后的 `best` 最高分版防退化），将需求、人工反馈、上轮反馈摘要、上轮逐条用例 `transcript.md`、历史尝试记录放入隔离工作目录。
2. **Develop（Agent 开发）**：按固定优先级（人工反馈 > 报错/未触发 > 产物缺失/错误 > 效率与措辞）修改 Skill，禁止针对单条用例写死特判；输出结构化结果文件（若缺失则复用同一会话补写）。
3. **Lint（静态检查与自修复）**：校验 `SKILL.md` frontmatter、引用脚本存在性、Python/Shell 语法、JSON 合法性及敏感凭证泄露；失败时优先接续原开发会话（`-s session_id`）最多修复 N 次，仍不过则提前终止本轮。
4. **Snapshot（版本快照）**：落盘 `versions/vNNN/`、`diff.patch` 及标准发布包。
5. **Selftest（隔离自测与事实提取）**：每条用例在独立配置与工作目录并发执行；**不让模型自我总结跑得好不好**，而是由代码直接解析 JSON 事件流提取客观事实（是否加载/触发 Skill、工具退出码、脚本报错、输出文件、步数与 Token）并生成可读 `transcript.md`。
6. **Evaluate（可插拔评测接口）**：通过标准输入/输出 JSON 解耦外部评测器（规则脚本或 LLM-as-a-Judge），输出总分 `score`、是否达标 `pass` 及逐条评语，驱动 `best` 基线回退与自动停机。
7. **Finalize（归档与报告）**：汇总本轮报告、更新全局状态与累计 Token 账本，即使提前终止也保证执行。

## 3. 无头调用开源 Coding Agent（如 OpenCode）的工程避坑清单

- **环境与上下文完全隔离**：
  - 每次调用独立指定 `XDG_CONFIG_HOME` / `XDG_DATA_HOME` / `XDG_CACHE_HOME` / `TMPDIR`，禁用全局外部 Skill 与自动更新，避免宿主个人配置污染被测环境。
  - **向上递归读取规则文件陷阱**：许多 Coding Agent 会沿父目录向上查找 `AGENTS.md` 直至 Git 根目录；因此临时开发目录和每条测试工作目录都必须先执行 `git init` 阻断向上穿透。
- **无头守护与进程清理**：
  - 传入 Prompt 后必须立即关闭 `stdin`，否则部分 CLI 会阻塞等待标准输入而不输出任何事件。
  - 禁用问答工具（无人值守无法回答）与子 Agent 工具（防止子会话 Token 漏记账）。
  - 超时或收到 `SIGTERM` 时必须按**进程组（Process Group）**清理，防止 Agent 派生的后台脚本残留。
- **离线/受限网络依赖陷阱**：
  - 确保 `ripgrep (rg)` 预置在 `PATH` 中，避免 CLI 启动时尝试联网下载导致超时卡死。
  - 留意 CLI 后台静默拉取插件依赖（如 `npm install` 导致单次运行膨胀数十 MB），必要时通过预置目录或配置跳过。
- **模型侧三个上限要按"后端实际能力 + skill 体积"配，默认值会在大 skill 上连环失败**（2026-11-27 本机实跑：同一轮 develop 三次各撞一个）：
  - 上下文窗口：告诉 agent 的窗口要 ≥ 网关真实能收的量。配小了 agent 临近窗口就压缩会话，OpenCode 把摘要放在 assistant 角色，Opus 5.5 不认、停下不写结果文件（评审 agent 读大产物时最先撞到）。
  - 单次输出上限：思考（reasoning）token 也算输出。配 16384 时模型想得多的一步以 `finish_reason=length` 被截断，整步作废；按模型允许的上限给（如 64000）。
  - 单次调用超时：默认 40 分钟只够小 skill。600 KB、3000 行脚本的 skill，OpenCode 一轮 develop 实测约 3.5 小时、150 次调用；超时被杀后没有中途断点，重跑从头读。超时要按 skill 体积定，并且**在开跑前**定好，跑一半改配置救不了当前进程。
  - 这三项都做成配置项（框架默认 + 本机覆盖文件），不要写死在生成 agent 配置的代码里。
- **上游中断时续会话，不要整步重跑**：大请求（20–30 万 token）下网关偶发 `api_error` / 流断开，OpenCode 遇到直接退出不重试；一轮 develop 要 3 小时，整步重跑等于白扔两小时。对策：agent 调用层识别瞬时错误（api_error、流断开、5xx，排除 Session not found），用会话 id 续接原会话并给一句"上游中断了，接着做、不要重读"，上限 2 次；实测续上后模型直接从第 12 个 edit 往下做。前提是 harness 的会话落盘可续（OpenCode `-s`），不可续的 agent 只能靠缩短单步或分阶段落盘。
- **网关兼容性先用 curl 验流式再接 agent**：本机 OneAPI 桥在 chat/completions 流末尾追加一个非标准 `response.completed` 事件，非流式请求完全正常，agent 的严格校验（AI SDK）却直接报 Type validation failed。对策是中间加一层过滤代理；排查顺序是「非流式 curl → 流式 curl 看最后几帧 → 再看 agent」，能省掉在 agent 日志里猜的时间。
- **预检要覆盖真实配置**：`setup` 只检查接口能连、runner 能启动，上面这些上限问题要到 develop/evaluate 真跑才暴露；验证新环境时先用小 skill（如 echo-file）把 7 步跑通，再上大 skill，否则一次失败就是 40 分钟到 3 小时。

## 4. 关键待探索问题（下一步切入点）

- **Coding Agent vs. 通用 Agent 在 Develop 阶段的本质差异**：工具集设计（读写补丁、终端试跑验证闭环）、上下文管理、代码理解与自检习惯对 Skill 修改成功率的实际影响。
- **防过拟合与评测对齐**：开发阶段可见用例容易导致隐性过拟合，需在 Evaluate 阶段引入盲测集，并尽量缩小本地 Runner 与线上真实运行环境的系统提示词/工具差异。
