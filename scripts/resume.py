#!/usr/bin/env python3
"""Брифинг для нового чата: state, последние 10 событий, предупреждения check.py."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Продолжить проект с сохранённого места")
    parser.add_argument("--project", default="projects/demo", help="каталог проекта")
    args = parser.parse_args()
    project = (ROOT / args.project).resolve()
    state = project / "state.md"
    if not state.exists():
        print(f"нет state.md: {state}", file=sys.stderr)
        return 1

    print(f"=== STATE {project.relative_to(ROOT)} ===")
    print(state.read_text(encoding="utf-8").strip())

    log = project / "run-log.csv"
    print("\n=== LAST 10 RUN-LOG ===")
    if log.exists():
        lines = log.read_text(encoding="utf-8").splitlines()
        print("\n".join(lines[:1] + lines[1:][-10:]))
    else:
        print("журнала пока нет")

    print("\n=== CHECK ===")
    check = ROOT / "scripts" / "check.py"
    if check.exists():
        result = subprocess.run([sys.executable, str(check)], capture_output=True, text=True)
        report = (result.stderr or result.stdout).strip()
        print(report if report else "0 ошибок")
    else:
        print("check.py ещё не создан")
    return 0


if __name__ == "__main__":
    sys.exit(main())
