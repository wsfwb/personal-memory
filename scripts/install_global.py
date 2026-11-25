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

    # 3. 更新全局 Agent 引导说明（轻量指针，不干扰无关任务）
    agent_block = f"""## Personal Memory & Decision OS（跨目录联动）

- 用户的个人学习、复盘与决策支持仓库位于：`{REPO_ROOT}`（也可读取 `~/.config/personal-memory/repo_path` 或 `$PERSONAL_MEMORY_DIR`）。
- 当你在**任意工作目录**收到用户的以下意图时，请调用 `personal-memory` 技能或直接读取 `{REPO_ROOT}/AGENTS.md` 跨目录维护该仓库（使用 `git -C "{REPO_ROOT}"` 独立提交，不要污染当前工作项目的 Git 状态）：
  1. 记录日常进展、实战踩坑、读书/技术学习笔记或临时灵感（`inbox`）；
  2. 进行日复盘、周复盘、专项复盘或提炼个人原则（`profile/principles.md`）；
  3. 在不确定、纠结犹豫时请求结合个人阶段目标（`profile/goals.md`）、原则与历史决策（`decisions/`）辅助做决定。"""

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
alias pmem-cd='cd "{REPO_ROOT}"' '''
    zsh_act = upsert_marked_block(zshrc, zsh_block, ZSH_MARKER_START, ZSH_MARKER_END)
    print(f"[4/4] 配置终端环境变量与快捷命令 (~/.zshrc): {zsh_act}")
    print("  - 任意终端输入 `pmem` 即可查看记忆库状态与到期决策")
    print("  - 任意终端输入 `pmem-cd` 即可一键跳转到记忆库目录")
    print("\n全部完成！现在你在任意目录启动本地 Agent 都能直接联动维护个人记忆库了。")


if __name__ == "__main__":
    main()
