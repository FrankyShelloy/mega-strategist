# Фикстуры проверок

`bad_project/` содержит ровно три искусственные ошибки:
1. `projects/bad/claims.md` — утверждение без ссылки `[S#]`.
2. `projects/bad/claims.md` — ссылка `[S99]`, которой нет в `sources.csv`.
3. `secret.md` — имитация ключа.

Проверка:

```bash
python3 scripts/check.py --root evals/fixtures/bad_project
```

Ожидаемо: 3 строки ошибок, exit 2. На основном репозитории `evals/fixtures` исключён из скана секретов.
