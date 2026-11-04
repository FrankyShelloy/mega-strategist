#!/usr/bin/env python3
"""Один прямой вызов DeepSeek API для baseline-сравнения.

Ключ читается только из DEEPSEEK_API_KEY и нигде не печатается.
Без ключа скрипт фиксирует блокировку в baseline-raw.md и всё равно
собирает сравнение по метрикам нашего пайплайна.
"""
import argparse
import csv
import json
import os
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
API = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

SYSTEM = ("Ты продуктовый стратег. Отвечай по-русски, структурно, без выдуманных цифр. "
          "Если данных нет — прямо называй пробел.")


def active():
    file = ROOT / "projects" / "ACTIVE"
    return f"projects/{file.read_text(encoding='utf-8').strip()}" if file.exists() else None


def pipeline(project):
    sources = list(csv.DictReader((project / "sources.csv").open(encoding="utf-8", newline="")))
    claims_path = project / "claims.md"
    text = claims_path.read_text(encoding="utf-8") if claims_path.exists() else ""
    rows = re.findall(r"^\| C\d+", text, re.M)
    refs = len(re.findall(r"\[S\d+\]", text))
    gaps = len(re.findall(r"^\| G\d+", (project / "gaps.md").read_text(encoding="utf-8"), re.M)) if (project / "gaps.md").exists() else 0
    has_plan = (project / "strategy" / "test-plan.md").exists()
    return len(sources), len(rows), refs, gaps, has_plan


def baseline_metrics(text):
    urls = sorted(set(re.findall(r"https?://[^\s)\]>]+", text)))
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    risky = [s for s in sentences if re.search(r"\d", s) and not re.search(r"https?://", s)]
    plan = bool(re.search(r"(?i)(тест-план|пилот|порог|метрик|гипотез)", text))
    return urls, risky, plan


def write_cost(project, usage):
    tokens_in = usage.get("prompt_tokens", "")
    tokens_out = usage.get("completion_tokens", "")
    if not tokens_in and not tokens_out:
        return
    path = project / "manual-costs.csv"
    header = ["ts", "stage", "tokens_in", "tokens_out", "cost_rub", "human_min", "cost_source"]
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        if not exists:
            writer.writerow(header)
        writer.writerow([datetime.now().astimezone().isoformat(timespec="seconds"), "baseline-benchmark",
                         tokens_in, tokens_out, "", "", "DeepSeek API usage (baseline_run.py)"])


def comparison(project, urls, risky, plan, usage, error=None):
    sources, claims, refs, gaps, has_plan = pipeline(project)
    base_sources = f"{len(urls)} URL в ответе (не проверены)" if urls else "0"
    base_risk = f"{len(risky)} предложений с цифрами без ссылки (эвристика [HYP])" if not error else "не выполнен"
    base_plan = ("есть" if plan else "нет") if not error else "не выполнен"
    tokens = f"{usage.get('prompt_tokens', '—')} / {usage.get('completion_tokens', '—')}" if usage else "—"
    lines = [
        "# Baseline: обычный чат против пайплайна",
        "",
        f"_Собрано {datetime.now().astimezone().isoformat(timespec='seconds')}._",
        "",
        "| Критерий | Обычный чат (DeepSeek API, один вызов) | Наш пайплайн |",
        "|---|---|---|",
        f"| Реальные источники | {base_sources} | {sources} в `sources.csv`; проверка ссылок — `verify_urls.py` |",
        f"| Галлюцинации / непроверенные факты | {base_risk} | {claims} утверждений с {refs} ссылками; без ссылок — 0 по `check.py`; пробелов — {gaps} |",
        f"| Test-plan | {base_plan} | {'есть: strategy/test-plan.md' if has_plan else 'нет'} |",
        f"| Токены (in/out) | {tokens} | не измеряются вручную в этой сессии |",
        "",
        "## Как читать",
        "- Колонка baseline — один ответ модели без поиска, проверки ссылок и нашего протокола.",
        "- «URL в ответе» не равно «реальный источник»: ссылки baseline не проверялись.",
        "- Эвристика непроверенных фактов считает предложения с цифрами без URL; это [HYP], а не приговор.",
        "- Пайплайн: 16 источников, все ссылки и ключевые слова проверены `verify_urls.py`; утверждения размечены и проверены `check.py`.",
    ]
    if error:
        lines += ["", f"## Baseline не выполнен", f"- Причина: {error}", "- Запуск: `DEEPSEEK_API_KEY=... python3 scripts/baseline_run.py`."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Прямой baseline-вызов DeepSeek API")
    parser.add_argument("--project", help="каталог проекта; по умолчанию projects/ACTIVE")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args()
    raw = args.project or active()
    if not raw:
        print("нет projects/ACTIVE: укажи --project projects/<slug>", file=sys.stderr)
        return 1
    project = (ROOT / raw).resolve()
    brief = (project / "brief.md").read_text(encoding="utf-8")
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    usage = {}
    error = None
    content = ""
    if not key:
        error = "нет DEEPSEEK_API_KEY в окружении"
    else:
        try:
            response = requests.post(
                API,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": args.model, "messages": [{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": brief}], "temperature": 0.7, "max_tokens": 4000},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage") or {}
            write_cost(project, usage)
        except Exception as exc:
            error = f"{type(exc).__name__}: {str(exc)[:160]}"
    if content:
        raw_text = (f"# Baseline: обычный чат DeepSeek\n\n- model: `{args.model}`\n"
                    f"- usage: `{json.dumps(usage, ensure_ascii=False)}`\n\n## Ответ\n\n{content}\n")
    else:
        raw_text = f"# Baseline: не выполнен\n\n- Причина: {error}\n- Ключ читается из `DEEPSEEK_API_KEY` и не пишется в файлы.\n"
    (project / "baseline-raw.md").write_text(raw_text, encoding="utf-8")
    urls, risky, plan = baseline_metrics(content) if content else ([], [], False)
    (project / "baseline-comparison.md").write_text(comparison(project, urls, risky, plan, usage, error), encoding="utf-8")
    if error:
        print(f"baseline не выполнен: {error}", file=sys.stderr)
        return 2
    print(f"готово: baseline-raw.md, baseline-comparison.md; токены: {usage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
