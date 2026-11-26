# Coding Agent 与通用 Agent 的核心架构差异与应用场景边界

- **日期**：2026-11-26
- **领域**：AI Agent 架构 / Coding Agent / 工具接口设计（ACI）
- **状态**：`to-practice`

## 1. 本质抽象差异：会话流驱动 vs. 工作区状态闭环驱动

| 维度 | 通用 Agent（General Agent） | Coding Agent（软件工程 Agent） |
| :--- | :--- | :--- |
| **核心任务模型** | `User Query -> API/MCP/RAG -> Final Response` | `Explore (Read/Grep) -> Surgical Edit (Patch) -> Verify (Bash/Test) -> Iterate` |
| **状态持久化中心** | 对话上下文（Message History）与外部数据库/记忆检索 | 本地文件系统（File Tree）、Git 工作区与进程状态 |
| **文件修改原语（ACI）** | 粗粒度 `write_file`（整文件覆盖）或外部 API 调用 | 专用 **ACI（Agent-Computer Interface）**：带行号分页 `read`、唯一块匹配 `edit` / `apply_patch`、`glob`、`ripgrep` |
| **执行与验证心智** | 偏单向交付（工具返回成功即倾向于回复用户） | 内建测试驱动本能（关注 `stdout`/`stderr`、`exit_code`、语法检查，不跑通不轻言结束） |
| **上下文工程重心** | 摘要记忆、实体抽取、RAG 向量召回 | 严格保持前缀稳定以最大化 **Prompt Caching 命中率**、长工具输出折叠截断、超窗 Compaction |
| **无头自动化编排** | 多为同步 HTTP 接口或对话 UI | 原生支持 CLI 无头运行（`--format json` 事件流）、按 Session ID 断点接续修复（`-s`）、环境变量级沙箱隔离 |

## 2. 为什么涉及「配置 + 脚本 + 规范文档」的迭代必须用 Coding Agent？

1. **防止整文件重写的退化灾难**：通用 Agent 全量重写几百行文档或脚本时，极易漏删既有边界条件、破坏格式或偷懒省略代码；Coding Agent 的 `edit/patch` 工具从机制上强制模型做**最小增量修改（Minimal Diff）**。
2. **沙箱实跑的负反馈闭环**：处理文件编码、CLI 参数解析、边界脏数据等问题时，只有真正在临时目录造数据跑一遍脚本、看到非零退出码和 Traceback，模型才能精准修正。
3. **长轨迹下的高性价比缓存复用**：几十步工具调用虽然累计输入 Token 看似高达数十万，但只要保持历史消息前缀不变，90% 以上都能命中 KV Cache，实际推理成本极低。

## 3. 架构设计中的关键陷阱：「测试环境 Coding Agent 过强掩盖缺陷」

当使用 Coding Agent 同时担任**开发者（Developer）**和**测试执行者（Runner）**时，存在严重的**宿主能力错位风险**：
- **原因**：如果目标产物（如 Skill 或插件）最终运行在能力受限的**线上通用 Agent** 中，而离线自测却用能力极强的 **Coding Agent** 去跑——当产物脚本存在小 Bug 或指令模糊时，Coding Agent 会凭借强大的本地工具（`grep`/`edit`/现场写临时脚本）“自救”绕过问题并产出正确结果，造成自测假阳性（False Positive）；上线后通用 Agent 没有自救能力就会直接失败。
- **工程解法**：
  1. **权限与工具集降级对齐**：在测试 Runner 模式中显式裁剪掉线上宿主不存在的高级编码工具（如禁止 `edit`/`write` 源码目录），并注入与线上一致的 System Prompt。
  2. **事件流监控“自救信号”**：在解析测试轨迹事件流时，若发现测试 Agent 读取了工具源码排查报错、或自行编写临时脚本绕过了标准入口，即便最终结果正确，也应判定为健壮性缺陷反馈给下一轮修复。
