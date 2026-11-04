#!/usr/bin/env python3
"""Проверки каркаса: теги, ссылки, поля, секреты, next_action."""
import argparse, csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r"\[(FACT|HYP|FORECAST)\]")
SREF = re.compile(r"\[S(\d+)\]")
SECRET = re.compile(r"(sk-[A-Za-z0-9]{10,}|AIza[0-9A-Za-z_-]{10,}|ghp_[A-Za-z0-9]{10,}|-----BEGIN (?:RSA|OPENSSH) PRIVATE KEY-----)")
STATE = ("stage", "status", "next_action", "human_gate", "do_not_redo", "open_questions", "updated")
SOURCE = ("id", "url", "title", "type", "license", "quote")
SKIP = {".git", "__pycache__", ".venv", "node_modules"}

def err(errors, path, message):
    errors.append(f"{path}: {message}")
def parse_state(path, errors):
    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    for key in STATE:
        if not data.get(key):
            err(errors, path, f"пустое поле {key}")
def parse_sources(path, errors):
    ids = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for number, row in enumerate(csv.DictReader(handle), 2):
            for key in SOURCE:
                if not (row.get(key) or "").strip():
                    err(errors, path, f"строка {number}: пустое поле {key}")
            source_id = (row.get("id") or "").strip()
            if source_id:
                ids.add(source_id)
    return ids
def check_claims(path, ids, errors):
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        text = line.strip()
        if not text.startswith("- ") or len(text) <= 2:
            continue
        if not TAG.search(text):
            err(errors, path, f"строка {number}: нет тега [FACT]/[HYP]/[FORECAST]")
        refs = SREF.findall(text)
        if not refs:
            err(errors, path, f"строка {number}: нет ссылки [S#]")
        for ref in refs:
            if f"S{int(ref):02d}" not in ids:
                err(errors, path, f"строка {number}: источник S{int(ref):02d} отсутствует")

def check_project(project, errors):
    state, sources, claims = project / "state.md", project / "sources.csv", project / "claims.md"
    if state.exists():
        parse_state(state, errors)
    else:
        err(errors, state, "нет state.md")
    ids = parse_sources(sources, errors) if sources.exists() else set()
    if not sources.exists():
        err(errors, sources, "нет sources.csv")
    if claims.exists():
        check_claims(claims, ids, errors)
    else:
        err(errors, claims, "нет claims.md")

def scan_file(path, errors):
    if path.suffix.lower() not in {".md", ".csv", ".py", ".json", ".yml", ".yaml", ".sh", ".txt"}:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    match = SECRET.search(text)
    if match:
        err(errors, path, f"похоже на секрет: {match.group(0)[:12]}...")

def scan_all(root, errors):
    for path in root.rglob("*"):
        if path.is_file() and not set(path.parts) & SKIP:
            if root != ROOT or "evals/fixtures" not in path.as_posix():
                scan_file(path, errors)

def hook_project(root):
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    tool = payload.get("tool_input") or {}
    raw = tool.get("file_path") or tool.get("path")
    if not raw:
        return None
    path = Path(raw).resolve()
    if root not in path.parents or path.name not in {"claims.md", "sources.csv", "state.md"}:
        return None
    return path.parent

def main():
    parser = argparse.ArgumentParser(description="Проверка каркаса mega-strategist")
    parser.add_argument("--hook", action="store_true", help="проверить файл из JSON stdin")
    parser.add_argument("--staged", action="store_true", help="полная проверка перед коммитом")
    parser.add_argument("--secrets", action="store_true", help="только скан секретов")
    parser.add_argument("--root", default=str(ROOT), help="корень проверки")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = []
    if args.hook:
        project = hook_project(root)
        if project is not None:
            check_project(project, errors)
    elif args.secrets:
        scan_all(root, errors)
    else:
        for project in sorted((root / "projects").glob("*/")):
            if project.is_dir() and not project.name.startswith("_"):
                check_project(project, errors)
        scan_all(root, errors)
    for error in errors:
        print(error, file=sys.stderr)
    return 2 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
