#!/usr/bin/env python3
"""
Personal Memory & Decision OS 状态巡检脚本
供用户或本地 Agent 快速查看：
1. Inbox 待归档条目
2. 决策库中待拍板（proposed）或已到回看期（review_date <= 今天 且 status == decided）的决策
3. 最近一次学习、日常记录与复盘情况
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_frontmatter(md_path: Path) -> dict[str, str]:
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = re.sub(r"#.*$", "", v).strip().strip("'\"")
            meta[k.strip()] = v
    return meta


def list_md_files(folder: Path, exclude: set[str] | None = None) -> list[Path]:
    if not folder.exists():
        return []
    exclude = exclude or set()
    return sorted(
        [p for p in folder.rglob("*.md") if p.name not in exclude],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def main() -> None:
    today = dt.date.today()
    print(f"=== Personal Memory & Decision OS 状态巡检 ({today.isoformat()}) ===\n")

    # 1. Inbox 检查
    inbox_items = list_md_files(ROOT / "inbox", exclude={"README.md"})
    print(f"[Inbox 待归档] 共 {len(inbox_items)} 条")
    for item in inbox_items[:5]:
        print(f"  - {item.relative_to(ROOT)}")
    print()

    # 2. 决策回看检查
    decision_files = list_md_files(ROOT / "decisions", exclude={"index.md"})
    due_decisions: list[tuple[Path, dict[str, str]]] = []
    proposed_decisions: list[tuple[Path, dict[str, str]]] = []

    for df in decision_files:
        meta = parse_frontmatter(df)
        status = meta.get("status", "")
        review_date_str = meta.get("review_date", "")
        if status == "proposed":
            proposed_decisions.append((df, meta))
        elif status == "decided" and review_date_str:
            try:
                r_date = dt.date.fromisoformat(review_date_str)
                if r_date <= today:
                    due_decisions.append((df, meta))
            except ValueError:
                pass

    print(f"[决策追踪] 总记录 {len(decision_files)} 条 | 待拍板 {len(proposed_decisions)} 条 | 到期需回看 {len(due_decisions)} 条")
    for df, meta in proposed_decisions:
        print(f"  * [待拍板] {meta.get('title', df.stem)} ({df.relative_to(ROOT)})")
    for df, meta in due_decisions:
        print(f"  ! [到期回看: {meta.get('review_date')}] {meta.get('title', df.stem)} ({df.relative_to(ROOT)})")
    print()

    # 3. 学习与复盘概览
    learning_notes = list_md_files(ROOT / "learning" / "topics")
    daily_logs = sorted((ROOT / "reviews" / "daily").glob("*.md"), reverse=True) if (ROOT / "reviews" / "daily").exists() else []
    weekly_reviews = sorted((ROOT / "reviews" / "weekly").glob("*.md"), reverse=True) if (ROOT / "reviews" / "weekly").exists() else []

    latest_daily = daily_logs[0].stem if daily_logs else "暂无"
    latest_weekly = weekly_reviews[0].stem if weekly_reviews else "暂无"

    print("[学习与复盘概览]")
    print(f"  - 专题学习笔记数: {len(learning_notes)}")
    print(f"  - 最近日常记录:   {latest_daily}")
    print(f"  - 最近周复盘:     {latest_weekly}")


if __name__ == "__main__":
    main()
