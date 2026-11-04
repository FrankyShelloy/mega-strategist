# Переносимость и хуки

## Статус проверок
- **Проверено 4.11:** `python3 scripts/check.py`, `--all`, `--secrets`, проверка фикстуры и ручной запуск `.githooks/pre-commit`.
- **Не подтверждено:** автозапуск IDE-хука в DeepSeek harness, нативное чтение `.claude/settings.json` в Claude Code, поддержка hooks в Cursor, поведение Antigravity.
- До подтверждения действует ручное правило: после записи в `claims.md` и `sources.csv` выполнить `python3 scripts/check.py`.

## Что переносится без изменений
`AGENTS.md`, `CLAUDE.md`, `skills/`, `knowledge/`, `projects/`, `scripts/`. Пути относительные, внешних Python-пакетов нет. Активный проект задаётся строкой в `projects/ACTIVE`.

## Хук после записи в claims.md
Конфиг `PostToolUse` лежит в `.claude/settings.json` и должен вызывать `scripts/check.py --hook`.

### DeepSeek harness
**Статус: не подтверждено.** Мост `@deepseek-ai/dsh-hooks-claude-code` читает конфиг Claude Code, но в тестовом профиле 4.11 маркер `SessionStart` не создался, а запись в `claims.md` через `edit` не вызвала `check.py`. Это заготовка, не рабочий рецепт.

Пример подключения:
```yaml
- insert:
    - id: hooks-claude-code
      name: '@deepseek-ai/dsh-hooks-claude-code'
      config:
        configPath: ./.claude/settings.json
        projectDir: .
```

**Как проверить:**
1. Создать чистый профиль и добавить мост через `insert`.
2. Перезапустить сессию и проверить маркер `SessionStart`.
3. Изменить `projects/training/claims.md` вручную.
4. Убедиться, что `check.py --hook` реально запустился: код выхода и запись в журнале.
5. Если маркера или запуска нет — оставить ручной режим и записать результат в `run-log.csv`.

### Claude Code
**Статус: не проверено в этой среде.** Утверждение «`.claude/settings.json` читается нативно» взято из документации, а не из эксперимента.

**Как проверить:** открыть клон в Claude Code, изменить `claims.md`, посмотреть, вызвался ли `check.py --hook`. Если да — зафиксировать версию и дату; если нет — ручной режим.

### Cursor
**Статус: не проверено.** Если версия Cursor поддерживает hooks, повторить тот же смысл: после сохранения файла запускать `python3 scripts/check.py --hook`. Если hooks недоступны — добавить в правила среды строку «после записи в `claims.md`, `sources.csv`, `state.md` выполнить `python3 scripts/check.py`». Это дисциплина, а не автоматика; в PDF так и писать.

### Antigravity
**Статус: не подтверждено.** Утверждение «хуков нет» не проверялось: среда не устанавливалась. Неизвестно, читает ли она `AGENTS.md` автоматически и поддерживает ли post-write команды.

**Как проверить:**
1. Установить Antigravity и открыть клон.
2. Проверить, видит ли среда `AGENTS.md` (задать вопрос о правилах проекта).
3. Найти в настройках hooks или post-save actions.
4. Если их нет — рассчитывать только на ручной `check.py` и правило в промпте.
5. Записать версию среды и результат в `docs/submission.md`.

## Git-хук
Подключение через `core.hooksPath`:
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```
`pre-commit` вызывает `scripts/check.py --staged` и проверяет все проекты. Скрипт запускался вручную 4.11 (exit 0); полный коммит с хуком ещё не прогонялся.

## Проверка переносимости (10 минут)
1. Клон в новый каталог.
2. `python3 scripts/check.py` — 0 ошибок для проекта из `projects/ACTIVE`.
3. `python3 scripts/check.py --all` — 0 ошибок для всех проектов.
4. `python3 scripts/resume.py` — печатает состояние и следующий шаг.
5. Изменить строку в `claims.md`; убедиться, что хук или ручная команда даёт тот же результат.
6. Записать среду и результат в `docs/submission.md`.
