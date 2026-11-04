#!/usr/bin/env python3
"""Проверка sources.csv: доступность URL и наличие ключевых слов цитаты.

Требует requests (единственное исключение из правила stdlib, по прямому указанию).
Результат добавляется в projects/<slug>/corrections.md.
"""
import argparse
import csv
import html
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("нужен requests: python3 -m pip install requests", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def active():
    file = ROOT / "projects" / "ACTIVE"
    return f"projects/{file.read_text(encoding='utf-8').strip()}" if file.exists() else None


def keywords(quote):
    words = re.findall(r"[А-Яа-яЁёA-Za-z0-9]{4,}", quote.lower().replace("ё", "е"))
    stop = {"который", "которая", "которые", "этого", "этому", "также", "более", "менее", "через", "после", "перед", "только", "нужно", "можно", "будет", "были", "было", "есть", "как", "что", "для", "при", "или"}
    return [word for word in dict.fromkeys(words) if word not in stop]


def page_text(markup):
    markup = re.sub(r"(?is)<(script|style).*?</\1>", " ", markup)
    markup = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(markup)).lower().replace("ё", "е")


def check(row):
    try:
        response = requests.get(row["url"], headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        words = keywords(row["quote"])
        text = page_text(response.text)
        found = [word for word in words if word in text]
        if not words:
            verdict = "нет ключевых слов"
        elif len(found) == len(words):
            verdict = "текст найден"
        else:
            verdict = f"найдено {len(found)}/{len(words)}"
        return str(response.status_code), "да" if response.ok else "нет", verdict, response.url
    except Exception as exc:
        return "—", "нет", f"ошибка: {type(exc).__name__}: {str(exc)[:80]}", row["url"]


def main():
    parser = argparse.ArgumentParser(description="Проверить ссылки и цитаты sources.csv")
    parser.add_argument("--project", help="каталог проекта; по умолчанию projects/ACTIVE")
    args = parser.parse_args()
    raw = args.project or active()
    if not raw:
        print("нет projects/ACTIVE: укажи --project projects/<slug>", file=sys.stderr)
        return 1
    project = (ROOT / raw).resolve()
    sources = project / "sources.csv"
    if not sources.exists():
        print(f"нет sources.csv: {sources}", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(sources.open(encoding="utf-8", newline="")))
    results = [(row["id"], *check(row)) for row in rows]
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    out = [
        f"\n## Автоматическая проверка ссылок — {stamp}",
        "",
        "| id | HTTP | страница | ключевые слова | итоговый URL |",
        "|---|---|---|---|---|",
    ]
    out += [f"| {sid} | {code} | {ok} | {verdict} | {url} |" for sid, code, ok, verdict, url in results]
    available = sum(1 for _, _, ok, _, _ in results if ok == "да")
    found = sum(1 for _, _, _, verdict, _ in results if verdict == "текст найден")
    out += ["", f"Итог: страниц доступно {available}/{len(results)}; текст найден {found}/{len(results)}."]
    target = project / "corrections.md"
    if not target.exists():
        target.write_text("# Corrections: training\n\nАвтоматические и человеческие правки.\n", encoding="utf-8")
    with target.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")
    print(f"готово: {target.relative_to(ROOT)}; доступно {available}/{len(results)}; текст найден {found}/{len(results)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
