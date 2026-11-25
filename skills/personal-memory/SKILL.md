---
name: personal-memory
description: 跨目录自动沉淀与维护用户的个人记忆库与决策支持系统（Personal Memory & Decision OS）。在任意工作目录中：(1) 当开发/排查任务产出了高价值踩坑经验、架构理解、技术选型拍板或重要阶段进展时，自动脱敏沉淀并同步到 GitHub；(2) 当用户主动要求记录、做日/周/专项复盘、提炼原则时触发；(3) 当用户纠结犹豫请求辅助做决定时触发。琐碎小改动不触发。
metadata:
  short-description: 跨目录自动沉淀个人学习、复盘与决策库并同步 GitHub
---

# Personal Memory & Decision OS（跨目录技能）

本技能允许本地 Agent 在**任意工程目录**工作时，无缝定位、读取并增量维护用户的 `personal-memory` Git 仓库，把日常开发/工作中的实战收获、踩坑复盘与关键抉择沉淀到统一的个人记忆系统中。

## 1. 定位个人记忆库路径（Repo Discovery）

在任意工作目录触发本技能时，按以下优先级定位 `MEMORY_REPO` 根目录：

1. 环境变量 `$PERSONAL_MEMORY_DIR`（若已设置且存在）；
2. 技能自身所在仓库根目录：解析当前 `SKILL.md` 的真实物理路径（`realpath` 追踪软链接后向上两级目录，即 `<MEMORY_REPO>/skills/personal-memory/SKILL.md` -> `<MEMORY_REPO>`）；
3. 兜底配置文件：`~/.config/personal-memory/repo_path` 中记录的路径。

> **注意**：由于路径可能包含空格（如 `person memory`），所有 Shell / Git 命令中引用路径时**必须加双引号**（例如 `git -C "$MEMORY_REPO" status`）。

## 2. 跨目录工作流规范

确认 `MEMORY_REPO` 后，首先阅读 `"$MEMORY_REPO/AGENTS.md"`（或按以下精简协议执行），并运行巡检脚本了解现状：

```bash
python3 "$MEMORY_REPO/scripts/memory_status.py"
```

### 场景 A：在其他项目干活时顺手沉淀（学习 / 踩坑 / 日常进展）
1. **提取当前工程上下文**（脱敏原则）：总结当前项目解决的技术问题、踩坑根因或通用方法论，**严禁**将公司内部密钥、Token、私有连接串或敏感业务数据写入个人记忆库。
2. **归档位置**：
   - 通用技术/方法论收获 -> 新增或更新 `"$MEMORY_REPO/learning/topics/<topic>.md"`（参考 `"$MEMORY_REPO/templates/learning-note.md"`），并更新 `"$MEMORY_REPO/learning/index.md"`。可注明来源项目名以便回溯。
   - 当天推进事项与感悟 -> 创建或追加 `"$MEMORY_REPO/reviews/daily/YYYY-MM-DD.md"`，并确保 `"$MEMORY_REPO/reviews/index.md"` 同步。
   - 临时灵感 -> 写入 `"$MEMORY_REPO/inbox/"`。

### 场景 B：跨目录周期复盘与原则提炼
1. 读取 `"$MEMORY_REPO/profile/goals.md"`、近期 `reviews/daily/` 及 `decisions/`。
2. 生成周复盘（`reviews/weekly/YYYY-WXX.md`）或专项事件复盘（`reviews/postmortems/YYYY-MM-DD-slug.md`）。
3. 提炼 1~2 条可复用的经验教训，经用户确认后写入 `"$MEMORY_REPO/profile/principles.md"`。

### 场景 C：在其他项目或生活中纠结时辅助决策
1. **必读基准**：读取 `"$MEMORY_REPO/profile/context.md"`、`goals.md`、`principles.md` 以及 `"$MEMORY_REPO/decisions/index.md"`。
2. **结构化把关**：
   - 检查与阶段主线目标的对齐度；
   - 区分「双向门（低成本可逆 -> 快速试错）」与「单向门（高代价不可逆 -> 严控下行风险）」；
   - 对照 `principles.md` 指出潜在盲区（如高估业余精力、过度设计、逃避核心难点）；
   - 给出有明确倾向性的建议。
3. **决策留痕**：使用 `"$MEMORY_REPO/templates/decision-record.md"` 写入 `"$MEMORY_REPO/decisions/YYYY-MM-DD-slug.md"`，设定 `review_date`，并更新 `"$MEMORY_REPO/decisions/index.md"`。

## 3. 跨目录 Git 提交与同步

每次修改完记忆库文件后，**不影响用户当前工作目录的 Git 状态**，直接调用内置同步脚本完成安全扫描、提交、rebase 拉取与推送到 GitHub：

```bash
python3 "$MEMORY_REPO/scripts/sync_memory.py" "<type>: <简明中文说明>"
```

- `<type>` 推荐使用：`learn` / `log` / `review` / `decide` / `profile`。
- 同步完成后，在回复末尾用一行简短提示告知用户已同步至 `personal-memory` GitHub 仓库即可，不要喧宾夺主干扰当前开发任务。
