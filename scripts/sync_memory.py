#!/usr/bin/env python3
"""
Personal Memory 一键提交与 GitHub 自动同步脚本
供本地 Agent（CodexOne / Claude Code 等）在任意目录更新记忆库后直接调用：
  python3 "$PERSONAL_MEMORY_DIR/scripts/sync_memory.py" "learn: 沉淀 Agent 上下文裁剪策略"

功能：
1. 自动在记忆库目录执行安全扫描（拦截误写入的 ghp_/sk- 等敏感 Token）
2. git add -A && git commit（若有文件变更）
3. git pull --rebase origin main（兼容多端更新）
4. git push origin main（通过本机 osxkeychain 免密自动推送至 GitHub）
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 常见敏感凭证正则（防止 Agent 误把业务密钥同步到公开/远程 GitHub）
SECRET_PATTERNS = [
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"), "GitHub Token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub Fine-grained PAT"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "API Secret Key (sk-...)"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Private Key"),
]


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        text=True,
        capture_output=True,
    )


def scan_staged_diff_for_secrets() -> list[str]:
    diff_res = run_git("diff", "--cached", "-U0")
    findings: list[str] = []
    for line in diff_res.stdout.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(label)
    return sorted(set(findings))


def main() -> int:
    msg = (
        sys.argv[1].strip()
        if len(sys.argv) > 1 and sys.argv[1].strip()
        else f"log: 自动同步个人记忆库 ({dt.datetime.now().strftime('%Y-%m-%d %H:%M')})"
    )

    status_res = run_git("status", "--porcelain")
    if status_res.returncode != 0:
        print(f"[sync_memory] git status 失败: {status_res.stderr.strip()}", file=sys.stderr)
        return 1

    has_changes = bool(status_res.stdout.strip())
    if has_changes:
        add_res = run_git("add", "-A")
        if add_res.returncode != 0:
            print(f"[sync_memory] git add 失败: {add_res.stderr.strip()}", file=sys.stderr)
            return 1

        secrets = scan_staged_diff_for_secrets()
        if secrets:
            run_git("reset")
            print(
                f"[sync_memory] 安全拦截！检测到疑似敏感凭证 ({', '.join(secrets)})，已取消提交，请脱敏后重试。",
                file=sys.stderr,
            )
            return 2

        commit_res = run_git("commit", "-m", msg)
        if commit_res.returncode != 0:
            print(f"[sync_memory] git commit 失败: {commit_res.stderr.strip()}", file=sys.stderr)
            return 1
        print(f"[sync_memory] 已本地提交: {msg}")
    else:
        print("[sync_memory] 工作区无新增文件变更，检查远程同步状态...")

    # 先拉取远程可能存在的新提交，避免冲突
    pull_res = run_git("pull", "--rebase", "origin", "main")
    if pull_res.returncode != 0:
        print(
            f"[sync_memory] git pull --rebase 警告: {pull_res.stderr.strip()}",
            file=sys.stderr,
        )

    push_res = run_git("push", "origin", "main")
    if push_res.returncode != 0:
        print(
            f"[sync_memory] 本地提交已保存，但推送到 GitHub 失败（请检查网络或 Token 有效性）:\n{push_res.stderr.strip()}",
            file=sys.stderr,
        )
        return 3

    print("[sync_memory] 已成功同步推送到 GitHub (origin/main)！")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
