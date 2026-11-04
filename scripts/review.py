#!/usr/bin/env python3
"""Просроченные пересмотры решений и устаревшие источники."""
import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STALE_DAYS = 365


def day(value):
    try:
        return datetime.strptime((value or "").strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def table(path):
    if not path.exists():
        return []
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    head = [cell.strip() for cell in lines[0].strip("|").split("|")]
    return [dict(zip(head, [cell.strip() for cell in line.strip("|").split("|")])) for line in lines[2:]]


def main():
    parser = argparse.ArgumentParser(description="Что пора пересмотреть")
    parser.add_argument("--project", default="projects/demo", help="каталог проекта")
    parser.add_argument("--today", help="дата проверки YYYY-MM-DD")
    parser.add_argument("--strict", action="store_true", help="exit 2 при находках")
    args = parser.parse_args()
    today = day(args.today) if args.today else date.today()
    if not today:
        print("дата: нужен YYYY-MM-DD", file=sys.stderr)
        return 1
    project = (ROOT / args.project).resolve()
    if not (project / "state.md").exists():
        print(f"нет state.md: {project}", file=sys.stderr)
        return 1
    due = []
    for row in table(project / "decision-log.md"):
        when = day(row.get("Пересмотр"))
        status = (row.get("Статус") or "").lower()
        if when and when <= today and status not in {"superseded", "closed", "закрыто", "отменено"}:
            due.append(row)
    sources = project / "sources.csv"
    rows = list(csv.DictReader(sources.open(encoding="utf-8", newline=""))) if sources.exists() else []
    stale = [row for row in rows if (when := day(row.get("accessed"))) and (today - when).days > STALE_DAYS]
    missing = [row for row in rows if not day(row.get("accessed"))]
    print(f"=== РЕШЕНИЯ К ПЕРЕСМОТРУ ({len(due)}) ===")
    for row in due:
        print(f"- {row.get('#', '?')}: {row.get('Решение', '')} (пересмотр {row.get('Пересмотр')}, статус {row.get('Статус', '')})")
    print(f"\n=== ИСТОЧНИКИ СТАРШЕ {STALE_DAYS} ДНЕЙ ({len(stale)}) ===")
    for row in stale:
        print(f"- {row.get('id', '?')}: {row.get('title', '')} (accessed {row.get('accessed')})")
    print(f"\n=== ИСТОЧНИКИ БЕЗ ДАТЫ ДОСТУПА ({len(missing)}) ===")
    for row in missing:
        print(f"- {row.get('id', '?')}: {row.get('title', '')}")
    return 2 if args.strict and (due or stale or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
