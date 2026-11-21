#!/usr/bin/env python3
"""Новый кейс из скелета projects/demo."""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COSTS_HEADER = "stage,tokens_in,tokens_out,cost_rub,human_min\n"
STAGES = ["00-intake","01-research-plan","02-collect-sources","03-evidence",
          "04-options","05-product-strategy","06-communication","07-test-plan",
          "08-decision-record","09-review"]
LOG = "ts,stage,actor,action,tool,artifact,status,note,tokens_in,tokens_out,cost_rub,human_min,cost_source\n"


def main():
    parser = argparse.ArgumentParser(description="Создать проект из скелета")
    parser.add_argument("slug", help="латиница, цифры, дефис")
    parser.add_argument("--question", default="", help="вопрос для brief.md")
    args = parser.parse_args()
    slug = args.slug.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,30}", slug):
        print("слаг: 2–31 символ, латиница, цифры, дефис", file=sys.stderr)
        return 1
    target = ROOT / "projects" / slug
    if target.exists():
        print(f"уже существует: {target}", file=sys.stderr)
        return 1
    shutil.copytree(ROOT / "projects" / "demo", target,
                    ignore=shutil.ignore_patterns("report.md", "run-log.csv", "manual-costs.csv"))
    state = (f"# Состояние проекта: {slug}\n\nstage: 00-intake\nstatus: waiting_brief\n"
             f"next_action: заполнить brief.md и подтвердить рамку на G1\nhuman_gate: none\n"
             f"do_not_redo: []\nopen_questions: []\nupdated: {date.today().isoformat()}\n")
    (target / "state.md").write_text(state, encoding="utf-8")
    (target / "run-log.csv").write_text(LOG, encoding="utf-8")
    # Создаём пустую таблицу ручных затрат (заполняется человеком по факту)
    costs_rows = COSTS_HEADER + "".join(f"{s},,,, \n" for s in STAGES)
    (target / "manual-costs.csv").write_text(costs_rows, encoding="utf-8")
    brief = target / "brief.md"
    if args.question and brief.exists():
        text = brief.read_text(encoding="utf-8")
        brief.write_text(text.replace("## Вопрос\n- \n", f"## Вопрос\n- {args.question.strip()}\n", 1), encoding="utf-8")
    print(f"создан: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
