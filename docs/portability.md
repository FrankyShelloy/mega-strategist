# Переносимость и хуки

## Что переносится без изменений
`AGENTS.md`, `skills/`, `knowledge/`, `projects/`, `scripts/`. Пути относительные, внешних Python-пакетов нет.

## Хук после записи в claims.md
В репозитории один IDE-хук: `PostToolUse` на `Write|Edit` вызывает `scripts/check.py --hook`. Скрипт сам проверяет, относится ли изменённый файл к `claims.md`, `sources.csv` или `state.md`, и возвращает exit 2 с текстом ошибки.

### DeepSeek harness
Мост `@deepseek-ai/dsh-hooks-claude-code` читает конфиг Claude Code. Пример подключения:

```yaml
- name: '@deepseek-ai/dsh-hooks-claude-code'
  config:
    configPath: ./.claude/settings.json
    projectDir: .
```

Если мост не включён в профиле, хук не срабатывает. Тогда проверка запускается вручную после стадии: `python3 scripts/check.py --hook`.

### Claude Code
`.claude/settings.json` читается нативно. Ничего дополнительно подключать не нужно.

### Cursor
Если версия Cursor поддерживает hooks, повторить тот же смысл: после сохранения файла запускать `python3 scripts/check.py --hook`. Если hooks недоступны — добавить в правила среды одну строку «после записи в `claims.md`, `sources.csv`, `state.md` выполнить `python3 scripts/check.py`». Это дисциплина, а не автоматика; в PDF так и написать.

### Antigravity
Хуков нет. Gemini используется как проверяющий по уже собранным материалам, без поиска. Проверки запускаются вручную в конце стадии.

## Git-хук
Подключение через `core.hooksPath`:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

Сейчас pre-commit — заглушка; с 5.11 вызывает `scripts/check.py --staged`.

## Проверка переносимости (10 минут)
1. Клон в новый каталог.
2. `python3 scripts/check.py` — 0 ошибок.
3. `python3 scripts/resume.py` — печатает состояние и следующий шаг.
4. Изменить строку в `claims.md`; убедиться, что хук или ручная команда даёт тот же результат.
5. Записать среду и результат в `docs/submission.md`.
