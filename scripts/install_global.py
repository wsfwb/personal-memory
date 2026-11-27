#!/usr/bin/env python3
"""
一键全局注册脚本（支持换机重装 / 目录迁移后重新绑定）
作用：
1. 将仓库真实路径写入 ~/.config/personal-memory/repo_path
2. 将 skills/personal-memory 软链接安装到本机常用本地 Agent 的全局 skills 目录：
   - ~/.codex-one/skills/personal-memory
   - ~/.claude/skills/personal-memory
   - ~/.comate/skills/personal-memory (若存在)
3. 在全局 Agent 指令文件（~/.codex-one/AGENTS.md 与 ~/.claude/CLAUDE.md）中幂等地注入轻量跨目录路由说明
4. 在 ~/.zshrc 中幂等地配置 PERSONAL_MEMORY_DIR 环境变量与 `pmem` 快捷命令
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_SRC = REPO_ROOT / "skills" / "personal-memory"
HOME = Path.home()

MARKER_START = "<!-- PERSONAL-MEMORY-OS:START -->"
MARKER_END = "<!-- PERSONAL-MEMORY-OS:END -->"

ZSH_MARKER_START = "# >>> personal-memory-os >>>"
ZSH_MARKER_END = "# <<< personal-memory-os <<<"


def upsert_marked_block(file_path: Path, block: str, start_marker: str, end_marker: str) -> str:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    existing = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    wrapped = f"{start_marker}\n{block.rstrip()}\n{end_marker}\n"

    if start_marker in existing and end_marker in existing:
        before = existing.split(start_marker, 1)[0]
        after = existing.split(end_marker, 1)[1]
        new_text = before.rstrip() + ("\n\n" if before.strip() else "") + wrapped + after.lstrip("\n")
        action = "updated"
    else:
        sep = "\n\n" if existing.strip() else ""
        new_text = existing.rstrip() + sep + wrapped
        action = "added"

    file_path.write_text(new_text, encoding="utf-8")
    return action


def ensure_symlink(src: Path, dst: Path) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        if dst.is_symlink() and dst.resolve() == src.resolve():
            return "already linked"
        if dst.is_symlink():
            dst.unlink()
        else:
            return f"skipped (non-symlink already exists at {dst})"
    os.symlink(src, dst)
    return "linked"


def main() -> None:
    print(f"=== 配置 Personal Memory 全局跨目录支持 ===")
    print(f"记忆库路径: {REPO_ROOT}\n")

    # 1. 写入固定指针配置
    cfg_file = HOME / ".config" / "personal-memory" / "repo_path"
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    cfg_file.write_text(f"{REPO_ROOT}\n", encoding="utf-8")
    print(f"[1/4] 写入路径索引: {cfg_file}")

    # 2. 注册全局 Skill 软链接
    skill_targets = [
        HOME / ".codex-one" / "skills" / "personal-memory",
        HOME / ".claude" / "skills" / "personal-memory",
    ]
    if (HOME / ".comate" / "skills").exists():
        skill_targets.append(HOME / ".comate" / "skills" / "personal-memory")

    print("[2/4] 安装全局 Agent Skills:")
    for target in skill_targets:
        if target.parent.parent.exists():
            status = ensure_symlink(SKILL_SRC, target)
            print(f"  - {target}: {status}")

    # 3. 更新全局 Agent 引导说明（自动识别高价值节点沉淀 + 免密同步 GitHub）
    agent_block = f"""## Personal Memory Wiki（跨目录沉淀与决策联动）

- 用户的个人记忆库位于：`{REPO_ROOT}`（也可读取 `~/.config/personal-memory/repo_path` 或 `$PERSONAL_MEMORY_DIR`）。它按 LLM Wiki 组织：`reviews/daily/`、`inbox/` 是 raw 层（只追加）；`profile/`、`learning/topics/`、`decisions/` 是 wiki 层（一个东西一页，原地改写）；`index.md` 是唯一入口；`log.md` 记每次操作。完整规则见 `{REPO_ROOT}/AGENTS.md`。
- **跨目录沉淀协议（任务结束时自动执行，不必等用户提醒）**：
  在**任意项目目录**协助开发、排查或讨论方案后，若产出了以下高价值信息：非显而易见的根因排查、可复用的架构 / 设计模式理解、与用户敲定的重要选型、一个完整模块或里程碑，则按顺序：
  1. **先落 raw**：在 `{REPO_ROOT}/reviews/daily/YYYY-MM-DD.md` 追加 1~5 行脱敏事实，链接相关 wiki 页；
  2. **查 index，更新优先**：读 `{REPO_ROOT}/index.md`，涉及的概念 / 机制 / 决策若已有页，原地更新该页（补机制、改结论、记新坑），不要按日期在页尾追加流水；
  3. **新建 wiki 页要过门**：它是一个“东西”而非事件、能写出“与用户目标的关联 / 下一步怎么用”、三个月后大概率会搜。三条凑齐才新建，并在回复里先用一句话说明建什么页；凑不齐留在 raw；
  4. **收尾**：`index.md` 加行或改状态，`log.md` 追加一行。
- **防噪音与脱敏红线**：
  - 拼写修正、样式调整、无新认知的常规小改动不记；
  - **严禁**将公司内部密钥、Token、账号密码、私有内网地址或敏感业务数据写入记忆库（仅提炼通用技术原理、架构设计与个人经验）。
- **不确定时的决策支持**：
  用户犹豫、纠结或询问选型 / 规划建议时，**必须先读取** `{REPO_ROOT}/profile/`（`context.md`, `goals.md`, `principles.md`）和 `{REPO_ROOT}/index.md` 的决策表，按主线对齐度、单向门 / 双向门、原则校验、机会成本四个维度给出有倾向的建议，并落为 `decisions/` 页。
- **同步到 GitHub**（独立于当前工作仓库，不污染当前工程 Git 状态）：
  每次更新记忆库后执行 `python3 "{REPO_ROOT}/scripts/sync_memory.py" "<type>: <简明中文说明>"`，并在回复末尾用一句话告知沉淀了什么。"""

    agent_instruction_files = []
    if (HOME / ".codex-one").exists():
        agent_instruction_files.append(HOME / ".codex-one" / "AGENTS.md")
    if (HOME / ".claude").exists():
        agent_instruction_files.append(HOME / ".claude" / "CLAUDE.md")

    print("[3/4] 更新全局 Agent 指令文件:")
    for md_file in agent_instruction_files:
        act = upsert_marked_block(md_file, agent_block, MARKER_START, MARKER_END)
        print(f"  - {md_file}: {act}")

    # 4. 配置 ~/.zshrc 环境变量与快捷巡检命令 pmem
    zshrc = HOME / ".zshrc"
    zsh_block = f'''export PERSONAL_MEMORY_DIR="{REPO_ROOT}"
alias pmem='python3 "{REPO_ROOT}/scripts/memory_status.py"'
alias pmem-sync='python3 "{REPO_ROOT}/scripts/sync_memory.py"'
alias pmem-cd='cd "{REPO_ROOT}"' '''
    zsh_act = upsert_marked_block(zshrc, zsh_block, ZSH_MARKER_START, ZSH_MARKER_END)
    print(f"[4/4] 配置终端环境变量与快捷命令 (~/.zshrc): {zsh_act}")
    print("  - 任意终端输入 `pmem` 即可查看记忆库状态与到期决策")
    print("  - 任意终端输入 `pmem-sync` 即可一键提交并推送到 GitHub")
    print("  - 任意终端输入 `pmem-cd` 即可一键跳转到记忆库目录")
    print("\n全部完成！现在你在任意目录启动本地 Agent 都能直接联动维护个人记忆库了。")


if __name__ == "__main__":
    main()
