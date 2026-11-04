# Переносимость и хуки

## Что переносится без изменений
`AGENTS.md`, `skills/`, `knowledge/`, `projects/`, `scripts/`. Пути относительные, внешних Python-пакетов нет.

## Хук после записи в claims.md
**Статус 4.11: не подтверждено.** Конфиг `PostToolUse` лежит в `.claude/settings.json` и должен вызывать `scripts/check.py --hook`, но автоматический запуск в DeepSeek harness не сработал: в тестовом профиле `hooktest` не создался маркер `SessionStart`, а запись в `claims.md` через `edit` не вызвала `check.py`. Автоматический хук не заявляем работающим.

Ручной режим до подтверждения: после каждой записи в `claims.md` и `sources.csv` выполнить `python3 scripts/check.py`. Скрипт проверяет изменённый файл, если передан `--hook`, или весь проект без флага.

### DeepSeek harness
Мост `@deepseek-ai/dsh-hooks-claude-code` читает конфиг Claude Code. Пример подключения:

```yaml
- insert:
    - id: hooks-claude-code
      name: '@deepseek-ai/dsh-hooks-claude-code'
      config:
        configPath: ./.claude/settings.json
        projectDir: .
```

В тесте 4.11 строка собиралась через `insert`, но хук всё равно не сработал. Это не рабочий рецепт, а заготовка для следующей проверки.

Если мост не включён в профиле, хук не срабатывает. Тогда проверка запускается вручную после стадии: `python3 scripts/check.py`.

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
