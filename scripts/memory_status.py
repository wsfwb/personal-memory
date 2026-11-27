#!/usr/bin/env python3
"""
Personal Memory Wiki lint / 状态巡检脚本（终端快捷命令 pmem）

检查项：
1. 决策：待拍板（proposed）与到期需回看（review_date <= 今天 且 decided）
2. raw：inbox 条目超过 7 天未消化
3. index 一致性：wiki 页未入 index.md；index.md 指向不存在的文件
4. 链接：wiki 页内相对链接指向不存在的文件
5. 孤儿页：除 index.md 外没有任何页面链向它的 wiki 页
6. 过期页：status 为 learning / to-practice 且超过 90 天未更新
7. 核心页：principles.md 条目数超过上限

退出码始终为 0；结果供人或 Agent 阅读。
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INBOX_STALE_DAYS = 7
TOPIC_STALE_DAYS = 90
PRINCIPLES_MAX = 30

WIKI_DIRS = [
    ROOT / "profile",
    ROOT / "learning" / "topics",
    ROOT / "decisions",
    ROOT / "reviews" / "weekly",
    ROOT / "reviews" / "postmortems",
]
RAW_DIRS = [ROOT / "reviews" / "daily", ROOT / "inbox"]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


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


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def md_files(folder: Path, exclude: set[str] | None = None) -> list[Path]:
    if not folder.exists():
        return []
    exclude = exclude or set()
    return sorted(p for p in folder.rglob("*.md") if p.name not in exclude)


def wiki_pages() -> list[Path]:
    pages: list[Path] = []
    for d in WIKI_DIRS:
        pages.extend(md_files(d))
    return pages


def resolve_links(page: Path) -> list[tuple[str, Path | None]]:
    """返回页面内的相对链接及其解析结果（None 表示指向不存在的文件）。外链与锚点忽略。"""
    out: list[tuple[str, Path | None]] = []
    for raw in LINK_RE.findall(read(page)):
        if raw.startswith(("http://", "https://", "mailto:", "#", "codex://")):
            continue
        target = raw.split("#", 1)[0]
        if not target:
            continue
        candidate = (page.parent / target).resolve()
        out.append((raw, candidate if candidate.exists() else None))
    return out


def page_date(page: Path, meta: dict[str, str]) -> dt.date | None:
    """取页面的更新日期：frontmatter updated > date > 文件 mtime。"""
    for key in ("updated", "date", "created"):
        v = meta.get(key)
        if v:
            try:
                return dt.date.fromisoformat(v[:10])
            except ValueError:
                pass
    # 老页面可能把日期写在正文里（- **日期**：2026-11-25）
    m = re.search(r"日期\*{0,2}[：:]\s*(\d{4}-\d{2}-\d{2})", read(page))
    if m:
        return dt.date.fromisoformat(m.group(1))
    return dt.date.fromtimestamp(page.stat().st_mtime)


def page_status(page: Path, meta: dict[str, str]) -> str:
    if meta.get("status"):
        return meta["status"]
    m = re.search(r"状态\*{0,2}[：:]\s*`?([a-z-]+)`?", read(page))
    return m.group(1) if m else ""


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def section(title: str, items: list[str], ok_text: str = "无") -> None:
    print(f"[{title}] {len(items) if items else ok_text}" if items else f"[{title}] {ok_text}")
    for it in items:
        print(f"  {it}")
    print()


def main() -> None:
    today = dt.date.today()
    print(f"=== Personal Memory Wiki lint ({today.isoformat()}) ===\n")

    pages = wiki_pages()
    index_path = ROOT / "index.md"
    index_text = read(index_path)

    # 1. 决策
    due: list[str] = []
    proposed: list[str] = []
    for df in md_files(ROOT / "decisions", exclude={"index.md"}):
        meta = parse_frontmatter(df)
        status = meta.get("status", "")
        title = meta.get("title", df.stem)
        if status == "proposed":
            proposed.append(f"* [待拍板] {title} ({rel(df)})")
        elif status == "decided" and meta.get("review_date"):
            try:
                if dt.date.fromisoformat(meta["review_date"]) <= today:
                    due.append(f"! [到期回看 {meta['review_date']}] {title} ({rel(df)})")
            except ValueError:
                due.append(f"? review_date 格式错误: {rel(df)}")
    section("决策：待拍板 / 到期回看", proposed + due)

    # 2. inbox 超期
    stale_inbox: list[str] = []
    for p in md_files(ROOT / "inbox", exclude={"README.md"}):
        age = (today - dt.date.fromtimestamp(p.stat().st_mtime)).days
        mark = "!" if age > INBOX_STALE_DAYS else "-"
        stale_inbox.append(f"{mark} {rel(p)} ({age} 天)")
    section(f"Inbox 待消化（超过 {INBOX_STALE_DAYS} 天标 !）", stale_inbox)

    # 3. index 一致性
    index_targets: set[Path] = set()
    missing_in_fs: list[str] = []
    for raw, resolved in resolve_links(index_path):
        if resolved is None:
            missing_in_fs.append(f"! index 指向不存在的文件: {raw}")
        else:
            index_targets.add(resolved)
    not_in_index = [
        f"! 未入 index: {rel(p)}" for p in pages if p.resolve() not in index_targets
    ]
    section("index 一致性", missing_in_fs + not_in_index)

    # 4. 坏链接 + 5. 孤儿页（入链统计不含 index.md，含 raw 层）
    broken: list[str] = []
    inbound: dict[Path, int] = {p.resolve(): 0 for p in pages}
    link_sources = pages + [p for d in RAW_DIRS for p in md_files(d)] + [ROOT / "log.md"]
    for src in link_sources:
        for raw, resolved in resolve_links(src):
            if resolved is None:
                broken.append(f"! {rel(src)} -> {raw}")
            elif resolved in inbound and resolved != src.resolve():
                inbound[resolved] += 1
    section("坏链接", broken)

    core = {(ROOT / "profile" / n).resolve() for n in ("context.md", "goals.md", "principles.md")}
    orphans = [
        f"- {rel(p)}" for p in pages
        if inbound[p.resolve()] == 0 and p.resolve() not in core
    ]
    section("孤儿页（只有 index 链到它，考虑从相关页加引用或归档）", orphans)

    # 6. 过期页
    stale_pages: list[str] = []
    for p in md_files(ROOT / "learning" / "topics"):
        meta = parse_frontmatter(p)
        status = page_status(p, meta)
        if status not in ("learning", "to-practice"):
            continue
        d = page_date(p, meta)
        if d and (today - d).days > TOPIC_STALE_DAYS:
            stale_pages.append(f"! {rel(p)} [{status}] 最后更新 {d}，要么用掉要么归档")
    section(f"过期页（learning/to-practice 超过 {TOPIC_STALE_DAYS} 天未动）", stale_pages)

    # 7. principles 条数
    principles_text = read(ROOT / "profile" / "principles.md")
    n_items = sum(
        1 for line in principles_text.splitlines()
        if re.match(r"^\s*(\d+\.|-)\s+\S", line) and not line.strip().startswith("- *(")
    )
    over = [f"! principles.md 共 {n_items} 条，超过上限 {PRINCIPLES_MAX}，新增前先合并或淘汰"] if n_items > PRINCIPLES_MAX else []
    section(f"核心页：principles 条数 {n_items}/{PRINCIPLES_MAX}", over, ok_text="正常")

    # 概览
    daily = sorted((ROOT / "reviews" / "daily").glob("*.md"), reverse=True)
    weekly = sorted((ROOT / "reviews" / "weekly").glob("*.md"), reverse=True)
    print("[概览]")
    print(f"  - wiki 页: {len(pages)}（topics {len(md_files(ROOT / 'learning' / 'topics'))}, decisions {len(md_files(ROOT / 'decisions', exclude={'index.md'}))}）")
    print(f"  - 最近日常记录: {daily[0].stem if daily else '暂无'}")
    print(f"  - 最近周复盘:   {weekly[0].stem if weekly else '暂无'}")


if __name__ == "__main__":
    main()
