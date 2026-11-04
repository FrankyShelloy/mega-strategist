#!/usr/bin/env python3
"""Собирает projects/<slug>/report.md. Деньги берёт только из manual-costs.csv."""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def section(text, title):
    start = text.find(f"## {title}")
    if start < 0:
        return ""
    rest = text[start + len(title) + 4:]
    end = rest.find("\n## ")
    return rest[:end if end >= 0 else None].strip()


def embed(path, drop_title=False):
    lines = read(path).splitlines()
    if drop_title and lines and lines[0].startswith("# "):
        lines = lines[1:]
    out = []
    for line in lines:
        if line.startswith("# "):
            out.append("### " + line[2:])
        elif line.startswith("## "):
            out.append("#### " + line[3:])
        else:
            out.append(line)
    return "\n".join(out).strip()


def bullets(path):
    return [line[2:] for line in read(path).splitlines() if line.startswith("- ") and line[2:].strip()]


def sources(path):
    if not path.exists():
        return "Нет sources.csv."
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    out = [f"Источников: {len(rows)}.", "", "| id | title | type | published |", "|---|---|---|---|"]
    out += [f"| {r.get('id', '')} | {r.get('title', '')} | {r.get('type', '')} | {r.get('published', '')} |" for r in rows]
    return "\n".join(out)


def options(path):
    out = []
    for file in sorted((path / "options").glob("*.md")):
        text = read(file)
        title = next((line[2:] for line in text.splitlines() if line.startswith("# ")), file.stem)
        out.append(f"### {title}\n{section(text, 'Механика') or '—'}")
    return "\n\n".join(out) or "Вариантов нет."


def costs(path):
    file = path / "manual-costs.csv"
    if not file.exists():
        return "Ручных замеров нет: `manual-costs.csv` не создан. Токены и рубли не оцениваются."
    rows = list(csv.DictReader(file.open(encoding="utf-8", newline="")))
    cols = ["stage", "tokens_in", "tokens_out", "cost_rub", "human_min"]
    table = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    table += ["| " + " | ".join(r.get(c) or "" for c in cols) + " |" for r in rows]

    def total(col):
        numbers = [float(r[col]) for r in rows if (r.get(col) or "").strip()]
        return f"{sum(numbers):g}" if numbers else "нет замеров"

    table += ["", f"Итого cost_rub: {total('cost_rub')}; human_min: {total('human_min')}."]
    return "\n".join(table)


def main():
    parser = argparse.ArgumentParser(description="Собрать report.md проекта")
    parser.add_argument("--project", default="projects/demo", help="каталог проекта")
    args = parser.parse_args()
    project = (ROOT / args.project).resolve()
    if not (project / "state.md").exists():
        print(f"нет state.md: {project}", file=sys.stderr)
        return 1
    parts = [
        f"# Отчёт: {project.name}",
        f"_Собрано {date.today().isoformat()} из артефактов проекта. Ручные замеры не выдумываются._",
        "## Запрос\n" + (embed(project / "brief.md") or "—"),
        "## Что известно и откуда\n" + ("\n".join(f"- {b}" for b in bullets(project / "claims.md")) or "Утверждений нет.") + "\n\n" + sources(project / "sources.csv"),
        "## Варианты\n" + options(project),
        "## Стратегии\n" + "\n\n".join(embed(project / "strategy" / name) or "—" for name in ("product.md", "communication.md")),
        "## План проверки\n" + (embed(project / "strategy" / "test-plan.md", drop_title=True) or "—"),
        "## Стоимость и время\n" + costs(project),
    ]
    (project / "report.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"готово: {(project / 'report.md').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
