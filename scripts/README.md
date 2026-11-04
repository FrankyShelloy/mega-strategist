# scripts/ — проверки и отчёты

Семь скриптов: пять ядра и два автоматизации. `check.py` и `resume.py` берут проект из `projects/ACTIVE`; тренировочный прогон до G3 пройден 4.11, демо — после брифа.

| Скрипт | Назначение | Контракт |
|---|---|---|
| `check.py` | валидатор | без флагов — активный проект из `projects/ACTIVE`; `--all` — все проекты; `--hook` — JSON из stdin, проверяет `claims.md`/`sources.csv`/`state.md` изменённого проекта; `--staged` — все проекты перед коммитом; `--secrets` — только скан; `--root <path>` — проверка фикстуры; exit 0/2 |
| `resume.py` | брифинг для нового чата | `--project` переопределяет `projects/ACTIVE`; печатает `state.md`, последние 10 строк `run-log.csv`, вывод `check.py` |
| `report.py` | отчёт и смета | `--project projects/<slug>`; собирает `report.md` из артефактов; токены и рубли берёт только из `manual-costs.csv`, иначе пишет «нет замеров» |
| `review.py` | пересмотр | `--project`, `--today YYYY-MM-DD`, `--strict`; показывает решения с наступившим пересмотром, источники старше 365 дней и источники без даты; exit 2 при находках в `--strict` |
| `new_project.py` | новый кейс | `<slug> --question "..."`; копирует скелет `projects/demo/` без `report.md` и журналов, заполняет `state.md` и шапку `run-log.csv`; существующий проект не перезаписывает |
| `verify_urls.py` | проверка ссылок | читает `sources.csv`, GET с User-Agent и таймаутом 10 с, ищет ключевые слова цитаты в HTML, пишет таблицу в `corrections.md`; нужен `requests` |
| `baseline_run.py` | baseline-сравнение | один прямой вызов DeepSeek API по `brief.md`, сохраняет `baseline-raw.md` и `baseline-comparison.md`; ключ — только из `DEEPSEEK_API_KEY`, usage пишется в `manual-costs.csv` при успехе |

Зависимость: `requests` нужен только двум скриптам автоматизации (`verify_urls.py`, `baseline_run.py`). Остальные — stdlib. Без `DEEPSEEK_API_KEY` baseline не выдумывает ответ, а фиксирует блокировку и собирает сравнение по метрикам пайплайна.

Общие правила: Python 3.11+, только stdlib, относительные пути от корня репозитория, никаких записей вне проекта. `check.py` намеренно не ходит в сеть и не проверяет доступность URL.
