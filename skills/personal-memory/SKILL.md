---
name: personal-memory
description: 跨目录维护用户的个人记忆库（LLM Wiki 模式：raw 只追加、wiki 页按“东西”组织先更新再新建、index.md 唯一入口、log.md 操作日志）。在任意工作目录中：(1) 当开发/排查任务产出了高价值踩坑经验、架构理解、技术选型拍板或重要阶段进展时，脱敏写入 raw 日志并更新已有 wiki 页，同步到 GitHub；(2) 当用户主动要求记录、做日/周/专项复盘、提炼原则时触发；(3) 当用户纠结犹豫请求辅助做决定时触发。琐碎小改动不触发。
metadata:
  short-description: 跨目录维护个人 LLM Wiki（学习、复盘、决策）并同步 GitHub
---

# Personal Memory Wiki（跨目录技能）

本技能允许本地 Agent 在**任意工程目录**工作时，定位、读取并维护用户的 `personal-memory` Git 仓库。仓库按 LLM Wiki 组织：
`reviews/daily/`、`inbox/` 是 raw 层（只追加）；`profile/`、`learning/topics/`、`decisions/`、`reviews/weekly|postmortems` 是 wiki 层（一个东西一页，原地改写）；`index.md` 是唯一入口；`log.md` 记每次操作。完整规则在 `"$MEMORY_REPO/AGENTS.md"`。

## 1. 定位个人记忆库路径（Repo Discovery）

在任意工作目录触发本技能时，按以下优先级定位 `MEMORY_REPO` 根目录：

1. 环境变量 `$PERSONAL_MEMORY_DIR`（若已设置且存在）；
2. 技能自身所在仓库根目录：解析当前 `SKILL.md` 的真实物理路径（`realpath` 追踪软链接后向上两级目录，即 `<MEMORY_REPO>/skills/personal-memory/SKILL.md` -> `<MEMORY_REPO>`）；
3. 兜底配置文件：`~/.config/personal-memory/repo_path` 中记录的路径。

> **注意**：由于路径可能包含空格（如 `person memory`），所有 Shell / Git 命令中引用路径时**必须加双引号**（例如 `git -C "$MEMORY_REPO" status`）。

## 2. 跨目录工作流规范

确认 `MEMORY_REPO` 后，先读 `"$MEMORY_REPO/index.md"`（必要时读 `AGENTS.md`），并运行 lint 了解现状：

```bash
python3 "$MEMORY_REPO/scripts/memory_status.py"
```

### 场景 A：在其他项目干活时顺手沉淀（Ingest）
1. **脱敏**：只提炼通用技术原理、架构设计与个人经验，**严禁**写入公司密钥、Token、内网地址或敏感业务数据。
2. **先落 raw**：在 `"$MEMORY_REPO/reviews/daily/YYYY-MM-DD.md"` 追加 1~5 行事实，并链接相关 wiki 页。想不清归属的碎片进 `inbox/`。
3. **查 index，更新优先**：在 `index.md` 和 `learning/topics/` 找已有页，有就原地改（补机制、改结论、记新坑、改 `updated`），不要按日期在页尾追加流水。
4. **新建 wiki 页要过门**：它是一个“东西”而非事件、能写出“与用户目标的关联 / 下一步怎么用”、三个月后大概率会搜。三条凑齐才新建，并在回复里先用一句话说明建什么页。模板见 `templates/learning-note.md`。
5. **决策**：用 `templates/decision-record.md` 建 `decisions/YYYY-MM-DD-slug.md`，设 `review_date`。
6. **收尾**：`index.md` 加行或改状态；`log.md` 追加一行；同步。

### 场景 B：周期复盘与原则提炼（Lint）
1. 运行 lint；读 `profile/goals.md`、近 7 天 `reviews/daily/`、`inbox/`、`log.md`。
2. 把 raw 里还没进 wiki 的东西按场景 A 消化；inbox 清空（升格、合并或删除）；冲突与过期页改正或标 `archived`。
3. 生成周复盘（`reviews/weekly/YYYY-WXX.md`）或专项复盘（`reviews/postmortems/YYYY-MM-DD-slug.md`），在 `index.md` 综合页加行。
4. 提炼 1~2 条可复用经验，经用户确认后写入 `profile/principles.md`（上限 30 条，超了先合并淘汰）。

### 场景 C：纠结时辅助决策（Query）
1. **必读基准**：读取 `"$MEMORY_REPO/profile/context.md"`、`goals.md`、`principles.md` 以及 `"$MEMORY_REPO/index.md"` 的决策表（看历史上有没有类似决策与结果）。
2. **结构化把关**：
   - 检查与阶段主线目标的对齐度；
   - 区分「双向门（低成本可逆 -> 快速试错）」与「单向门（高代价不可逆 -> 严控下行风险）」；
   - 对照 `principles.md` 指出潜在盲区（如高估业余精力、过度设计、逃避核心难点）；
   - 给出有明确倾向性的建议。
3. **决策留痕**：使用 `"$MEMORY_REPO/templates/decision-record.md"` 写入 `"$MEMORY_REPO/decisions/YYYY-MM-DD-slug.md"`，设定 `review_date`，更新 `index.md` 并在 `log.md` 追加一行。

## 3. 跨目录 Git 提交与同步

每次修改完记忆库文件后，**不影响用户当前工作目录的 Git 状态**，直接调用内置同步脚本完成安全扫描、提交、rebase 拉取与推送到 GitHub：

```bash
python3 "$MEMORY_REPO/scripts/sync_memory.py" "<type>: <简明中文说明>"
```

- `<type>` 推荐使用：`learn` / `log` / `review` / `decide` / `profile`。
- 同步完成后，在回复末尾用一行简短提示告知用户已同步至 `personal-memory` GitHub 仓库即可，不要喧宾夺主干扰当前开发任务。
