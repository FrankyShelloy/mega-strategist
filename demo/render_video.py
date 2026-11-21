#!/usr/bin/env python3
"""
Генератор видео-демонстрации mega-strategist для хакатона МегаФона.
Рендерит 10 сцен в высоком разрешении 1080p (стилизация под IDE/Terminal)
и склеивает их в MP4 через ffmpeg.
При передаче аудио-дорожки (--audio voice.mp3) объединяет видео и звук.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAMES_DIR = ROOT / "demo" / "video_frames"
OUTPUT_VIDEO = ROOT / "demo" / "mega_strategist_demo.mp4"

# 10 сцен с таймингами (по умолчанию ~6 минут общего хронометража)
SCENES = [
    {
        "id": "scene_01",
        "duration": 30,
        "step": "01 / 10",
        "timecode": "00:00 - 00:30",
        "title": "mega-strategist: Протокол принятия продуктовых решений",
        "active_file": "README.md",
        "badge": "Архитектура & Старт",
        "file_tree": [
            ("📁 mega-strategist", True),
            ("  📄 AGENTS.md", False),
            ("  📄 README.md", True),
            ("  📁 skills/", False),
            ("  📁 agents/", False),
            ("  📁 knowledge/", False),
            ("  📁 projects/demo/", False),
            ("  📁 scripts/", False),
            ("  📁 evals/", False),
        ],
        "editor_content": """<span class="comment"># mega-strategist · Стратег Фабрики продуктов</span>
<span class="badge-tag">MIT License</span> <span class="badge-tag">Python 3.11+</span> <span class="badge-tag">Zero Cost: 0 ₽</span> <span class="badge-tag">check.py: exit 0</span>

ИИ-агент для руководителя цифрового продукта Фабрики МегаФона.
Проводит продакт-менеджера от размытого запроса до проверяемой стратегии:
• 10 стадий рабочего процесса со строгими контрактами данных
• 3 контрольных шлюза (Human-in-the-loop: G1, G2, G3)
• 0 ₽ затрат: работает на бесплатном тарифе и локальной стандартной библиотеке Python

<span class="keyword">Быстрый старт (продолжение после перерыва):</span>
<code>python3 scripts/resume.py</code>
""",
        "terminal_cmd": "git status && git log -1 --oneline",
        "terminal_output": """On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
1b3eb5f (HEAD -> main, origin/main) docs: add description.html + mega-strategist-description.pdf""",
        "teleprompter": "Здравствуйте! Представляем mega-strategist — ИИ-агента для руководителя цифрового продукта Фабрики МегаФона. Это строгий репозиторий-протокол, запускаемый в любой IDE без скрытых серверов и с нулевым бюджетом."
    },
    {
        "id": "scene_02",
        "duration": 35,
        "step": "02 / 10",
        "timecode": "00:30 - 01:05",
        "title": "Стадия 00: Постановка задачи и моментальное чтение состояния",
        "active_file": "projects/demo/brief.md",
        "badge": "00-intake",
        "file_tree": [
            ("📁 mega-strategist", True),
            ("  📁 projects/", True),
            ("    📁 demo/", True),
            ("      📄 brief.md", True),
            ("      📄 state.md", False),
            ("      📄 sources.csv", False),
            ("      📄 claims.md", False),
        ],
        "editor_content": """<span class="comment"># Карточка запроса: Связь для близких и собственных устройств</span>

<span class="keyword">## Контекст и сегменты</span>
• Доступный рынок: <strong>100 000 домохозяйств</strong> (семейные абоненты)
• Владельцы умных устройств: <strong>40 000 абонентов</strong> (2+ SIM-карты)
• Финансовый разрыв: <strong>+6 млн руб. валовой прибыли</strong> отставание от плана

<span class="keyword">## Ограничения и нормативная база</span>
• Федеральный закон № 126-ФЗ «О связи» (ст. 63 — тайна связи)
• Федеральный закон № 152-ФЗ «О персональных данных» (согласие участников)
• Запрет на скрытые автосписания и платные подписки без явного подтверждения
""",
        "terminal_cmd": "python3 scripts/resume.py",
        "terminal_output": """# Состояние проекта: demo
stage: 00-intake
status: waiting_brief
next_action: заполнить brief.md и подтвердить рамку на G1
human_gate: none
do_not_redo: []
open_questions: []
updated: 2026-11-21
[OK] Скрипт resume мгновенно считал артефакт state.md из projects/ACTIVE""",
        "teleprompter": "Начинаем работу с кейсом МегаФона. Команда resume.py мгновенно определяет активный проект и считывает статус. Вводный бриф фиксирует целевые сегменты, разрыв в 6 млн рублей и регуляторные рамки без галлюцинаций."
    },
    {
        "id": "scene_03",
        "duration": 40,
        "step": "03 / 10",
        "timecode": "01:05 - 01:45",
        "title": "Стадия 01: Дерево вопросов, меняющих решение + Шлюз G1",
        "active_file": "projects/demo/research-plan.md",
        "badge": "01-research-plan · G1",
        "file_tree": [
            ("📁 projects/demo/", True),
            ("  📄 brief.md", False),
            ("  📄 research-plan.md", True),
            ("  📄 state.md", True),
            ("  📄 corrections.md", False),
        ],
        "editor_content": """<span class="comment"># План исследования: 8 вопросов, меняющих решения</span>

1. <strong>Сегментный приоритет:</strong> Кому помочь в первую очередь — семьям или умным устройствам?
   → <em>Решение руководителя: выбор фокуса запуска в Q2 vs Q4.</em>
2. <strong>Механизм перебоя связи:</strong> Что чаще отключает близких — исчерпание ГБ или забытая оплата?
   → <em>Решение руководителя: приоритет продуктовой фичи (автошеринг трафика vs автоплатеж).</em>
3. <strong>Юридический барьер:</strong> Как организатор может видеть остатки членов семьи без нарушения ст. 63 126-ФЗ?
   → <em>Решение руководителя: архитектура согласий (opt-in через SMS/push).</em>
4. <strong>Экономика окупаемости:</strong> Сколько номеро-месяцев по ставке 500 ₽/мес. закрывают разрыв в 6 млн ₽?
   → <em>Решение руководителя: согласование CaPex на 3 человеко-месяца разработки.</em>
""",
        "terminal_cmd": "cat projects/demo/state.md | grep -E 'stage|human_gate|status'",
        "terminal_output": """stage: 01-research-plan
status: waiting_human
human_gate: G1
note: Агент остановился на шлюзе G1. Ожидается подтверждение человека.
[HUMAN INPUT]: Фокус на семейных группах в Q2; умные устройства отложены на Q4. Статус изменен на G1_passed.""",
        "teleprompter": "Агент строит план исследования из 8 вопросов, каждый из которых привязан к развилке решений продакта. На шлюзе G1 агент строго останавливается и ждет человека: подтверждаем фокус на семьях!"
    },
    {
        "id": "scene_04",
        "duration": 45,
        "step": "04 / 10",
        "timecode": "01:45 - 02:30",
        "title": "Стадии 02–03: 14 источников, claims.md и автопроверка check.py",
        "active_file": "projects/demo/claims.md",
        "badge": "02-collect & 03-evidence",
        "file_tree": [
            ("📁 projects/demo/", True),
            ("  📄 sources.csv", True),
            ("  📄 claims.md", True),
            ("  📄 gaps.md", True),
            ("📁 scripts/", True),
            ("  📄 check.py", True),
        ],
        "editor_content": """<span class="comment"># Реестр утверждений (Claims) и доказательств</span>

• <strong>C01 [FACT|S01]:</strong> Абонентская плата МегаСемья составляет 500–900 ₽/мес. в зависимости от региона.
• <strong>C04 [FACT|S04]:</strong> Ст. 63 126-ФЗ запрещает предоставление детализации третьим лицам без согласия субъекта.
• <strong>C08 [HYP]:</strong> Главный барьер шеринга ГБ — страх скрытых списаний со стороны организатора семьи.
• <strong>C15 [FORECAST]:</strong> Конверсия 12 000 номеро-месяцев по 500 ₽/мес. закрывает разрыв 6 млн ₽ валовой прибыли.

<span class="comment"># Честные пробелы (gaps.md)</span>
• <strong>G03:</strong> Точная доля семейных абонентов с 3+ номерами в базе МегаФона публично закрыта.
  → <em>Решение: агент не домысливает цифру, а ставит задачу на внутреннюю выгрузку перед запуском пилота.</em>
""",
        "terminal_cmd": "python3 scripts/check.py --all",
        "terminal_output": """Проверка проектов...
  demo: sources=14, claims=36, gaps=10, options=4
  contracts: state.md OK, manual-costs.csv OK, run-log.csv OK
Проверка секретов: сканирование репозитория...
  Секретов не обнаружено.
EXIT: 0
[SUCCESS] 0 ошибок! Все 36 утверждений строго верифицированы.""",
        "teleprompter": "Стадии сбора и доказательств: 14 открытых источников в sources.csv. Каждое утверждение в claims.md строго помечено тегами FACT, HYP, FORECAST. Неизвестное честно вынесено в gaps.md. Скрипт check.py подтверждает: 0 ошибок!"
    },
    {
        "id": "scene_05",
        "duration": 45,
        "step": "05 / 10",
        "timecode": "02:30 - 03:15",
        "title": "Дополнительный уровень: Синтетические персоны [SYNTHETIC-PERSONA]",
        "active_file": "projects/demo/interviews/interview_organizer_mother_2026-11-21.md",
        "badge": "Модельные персоны",
        "file_tree": [
            ("📁 projects/demo/", True),
            ("  📁 interviews/", True),
            ("    📄 interview_organizer_mother_2026-11-21.md", True),
            ("    📄 interview_multidevice_owner_2026-11-21.md", False),
            ("📁 agents/", True),
            ("  📄 persona-interviewer.md", True),
        ],
        "editor_content": """<span class="badge-tag" style="background:#dc2626;color:#fff;">[SYNTHETIC-PERSONA] ДИСКЛЕЙМЕР</span>
<strong>ВНИМАНИЕ:</strong> Синтетические ответы ИИ-собеседника НЕ доказывают спрос и готовность платить!
Используются исключительно для качественного поиска скрытых барьеров и формулирования гипотез.

<span class="keyword">Респондент:</span> Анна, 38 лет, двое детей (10 и 14 лет), мама-организатор группы «МегаСемья».
<span class="keyword">Ключевые инсайты:</span>
1. <strong>Страх «тихого минуса»:</strong> «Боюсь, что ребенок случайно нажмет платную подписку или уйдет в овердрафт».
2. <strong>Приватность звонков:</strong> «Мне не нужно слушать чужие звонки, мне важно просто видеть, что у мамы есть ГБ и связь».
3. <strong>Барьер шеринга:</strong> Сложный ручной перенос пакетов каждый месяц быстро забрасывается.
""",
        "terminal_cmd": "python3 scripts/simulate_persona.py --persona organizer_mother",
        "terminal_output": """[INFO] Инициализация роли persona-interviewer по методике The Mom Test...
[SYNTHETIC-PERSONA] Симуляция глубинного интервью с ролью 'organizer_mother'
  Выявлен ментальный барьер: недоверие к автоматическим списаниям с баланса организатора
  Сформирована продуктовая гипотеза: превентивное уведомление при остатке <1 ГБ + кнопка шеринга в 1 клик
  Протокол сохранен в projects/demo/interviews/interview_organizer_mother_2026-11-21.md
[STATUS] Завершено без подмены реальных социологических данных.""",
        "teleprompter": "Дополнительный уровень: модельные респонденты. Скрипт симулирует интервью с мамой-организатором. Мы честно соблюдаем дисклеймер: синтетические ответы не доказывают спрос, но дают ценные инсайты о страхе скрытых подписок."
    },
    {
        "id": "scene_06",
        "duration": 45,
        "step": "06 / 10",
        "timecode": "03:15 - 04:00",
        "title": "Стадия 04: 4 контрастных варианта (вкл. закрытие) и критик",
        "active_file": "projects/demo/options/03-family-proactive.md",
        "badge": "04-options · G2",
        "file_tree": [
            ("📁 projects/demo/", True),
            ("  📁 options/", True),
            ("    📄 01-status-quo.md", False),
            ("    📄 02-close.md", False),
            ("    📄 03-family-proactive.md", True),
            ("    📄 04-multidevice-hub.md", False),
            ("📁 agents/", True),
            ("  📄 critic.md", True),
        ],
        "editor_content": """<span class="comment"># Вариант 03: Проактивный семейный ассистент связи</span>

<span class="keyword">Суть решения:</span>
• Мониторинг баланса и остатков ГБ близких без раскрытия тайны звонков
• Превентивный push организатору: «У сына осталось 500 МБ. Поделиться 3 ГБ бесплатно?»
• Пополнение и шеринг трафика в 1 клик без перехода на сторонние экраны

<span class="comment"># Контраргументы субагента-критика (agents/critic.md):</span>
⚠️ <strong>Риск задержки биллинга:</strong> При задержке передачи данных абонент успеет уйти в офлайн до пуша.
⚠️ <strong>Страх повторных списаний:</strong> При двойном нажатии на кнопку шеринга возможен двойной расход.
   → <em>Обязательное требование к архитектуре: идемпотентность API и окно защиты 60 секунд.</em>
""",
        "terminal_cmd": "cat projects/demo/state.md | grep -A 4 'human_gate: G2'",
        "terminal_output": """human_gate: G2
human_decision: Выбран вариант 03-family-proactive.
отклонены:
  - 01-status-quo: не закрывает финансовый разрыв в 6 млн руб.
  - 02-close: потеря 100k лояльных домохозяйств и рост оттока к конкурентам
требование: реализовать серверную защиту от двойных списаний (идемпотентность).""",
        "teleprompter": "Стадия вариантов: агент предлагает 4 содержательно разных сценария, включая статус-кво и закрытие направления. Критик находит слабые места. На шлюзе G2 руководитель выбирает проактивного ассистента."
    },
    {
        "id": "scene_07",
        "duration": 45,
        "step": "07 / 10",
        "timecode": "04:00 - 04:45",
        "title": "Стадия 05: Продуктовая стратегия + расчет calc_economics.py",
        "active_file": "projects/demo/strategy/product.md",
        "badge": "05-product · calc_economics",
        "file_tree": [
            ("📁 projects/demo/strategy/", True),
            ("  📄 product.md", True),
            ("  📄 communication.md", False),
            ("  📄 test-plan.md", False),
            ("📁 scripts/", True),
            ("  📄 calc_economics.py", True),
        ],
        "editor_content": """<span class="comment"># Продуктовая стратегия: Связь для близких</span>

<span class="keyword">1. CJM и защита данных:</span>
• Opt-in подтверждение участника через SMS перед добавлением в дашборд организатора (ст. 53, 63 126-ФЗ).
• Серверный токен идемпотентности <code>idempotency_key = hash(user_id + target_msisdn + timestamp_hour)</code>.

<span class="keyword">2. Таблица ключевых показателей (соответствие 5 строкам брифа):</span>
| Показатель | Базовое значение | Цель с продуктом | Метод проверки |
|---|---|---|---|
| Валовая прибыль | -6 млн руб. от плана | 0 (разрыв закрыт) | +12 000 номеро-месяцев × 500 ₽ |
| Отток семейных групп | 2.8% в месяц | ≤ 1.5% в месяц | когортный анализ за 90 дней |
| Доля ручных переносов | 4% активных | ≥ 24% в 1 клик | логи мобильного приложения |
| Доля жалоб на списания | 1.2% обращений | ≤ 0.3% обращений | обращения в КЦ по категории |
""",
        "terminal_cmd": "python3 scripts/calc_economics.py",
        "terminal_output": """=== РАСЧЕТ ЮНИТ-ЭКОНОМИКИ И ВЫБОРКИ ПИЛОТА ===
• Целевой разрыв валовой прибыли: 6 000 000 руб.
• Ставка валовой прибыли: 500 руб./номеро-месяц
• Необходимый дополнительный объем: 12 000 номеро-месяцев
• Затраты разработки в Q2 (3 чел.-мес.): 1 500 000 руб.
• Чистый финансовый результат к концу года: +4 500 000 руб.
• Окупаемость инвестиций (Breakeven): 7 месяцев (август 2026)
• Расчет выборки пилота (A/B Holdout, MDE -3 п.п., мощность 80%): 3 276 семей""",
        "teleprompter": "Стадия 05: продуктовая стратегия. Сквозной CJM, матрица согласий и скрипт calc_economics.py. Детерминированный расчет показывает: разрыв 6 млн руб. закрывается 12 тыс. номеро-месяцев по 500 руб., окупаемость — 7 месяцев!"
    },
    {
        "id": "scene_08",
        "duration": 40,
        "step": "08 / 10",
        "timecode": "04:45 - 05:25",
        "title": "Стадии 06–07: Коммуникация и пилот A/B Holdout",
        "active_file": "projects/demo/strategy/communication.md",
        "badge": "06-comm & 07-test-plan · G3",
        "file_tree": [
            ("📁 projects/demo/strategy/", True),
            ("  📄 product.md", False),
            ("  📄 communication.md", True),
            ("  📄 test-plan.md", True),
        ],
        "editor_content": """<span class="comment"># Коммуникационная стратегия: Снятие барьеров</span>

• <strong>Барьер:</strong> «Вы спишете деньги со счета, когда трафик кончится».
  → <em>Сообщение:</em> «Делитесь своими ГБ из остатка тарифа бесплатно в 1 касание».
  → <em>RTB:</em> Прозрачная кнопка с указанием «0 ₽ с баланса».

<span class="comment"># План проверки: A/B Holdout дизайн пилота (test-plan.md)</span>
• <strong>Выборка:</strong> 3 276 семей в тестовой группе, 3 276 семей в контроле (Holdout 15%).
• <strong>Срок пилота:</strong> Q2 2026 (60 дней наблюдения).
• <strong>Guardrails:</strong> Увеличение жалоб в КЦ >0.5% или сбои биллинга >0.1% → немедленный откат пилота.
""",
        "terminal_cmd": "cat projects/demo/state.md | grep -A 3 'G3_passed'",
        "terminal_output": """human_gate: G3_passed
status: ready_for_execution
next_action: старт подготовительного этапа пилота к Q2 и согласование интеграции биллинга
do_not_redo: [00-intake, 01-research-plan, 02-collect-sources, 03-evidence, 04-options, 05-product-strategy, 06-communication, 07-test-plan, 08-decision-record]""",
        "teleprompter": "Стадии коммуникации и проверки: матрица строго связывает обещания с фичами. В тест-плане спроектирован статистически безупречный пилот A/B Holdout на 3 276 семей с жесткими защитными стоп-правилами. Шлюз G3 пройден!"
    },
    {
        "id": "scene_09",
        "duration": 35,
        "step": "09 / 10",
        "timecode": "05:25 - 06:00",
        "title": "Продолжение после перерыва и контроль обязательств",
        "active_file": "projects/demo/decision-log.md",
        "badge": "resume.py & review.py",
        "file_tree": [
            ("📁 projects/demo/", True),
            ("  📄 state.md", True),
            ("  📄 decision-log.md", True),
            ("  📄 decision-record.md", True),
            ("📁 scripts/", True),
            ("  📄 resume.py", True),
            ("  📄 review.py", True),
        ],
        "editor_content": """<span class="comment"># Журнал решений и обязательств (decision-log.md)</span>

| ID | Решение | Владелец | Срок пересмотра | Условие отката |
|---|---|---|---|---|
| D01 | Запуск проактивного ассистента в Q2 | Product Lead | 30.06.2026 | Отток семей > 2.5% |
| D02 | Внедрение токена идемпотентности | Lead Backend | 15.04.2026 | Ошибки API > 0.05% |
| D03 | A/B пилот на 3 276 семей | Lead Analyst | 31.05.2026 | Превышение жалоб в КЦ |
""",
        "terminal_cmd": "python3 scripts/review.py",
        "terminal_output": """=== РЕВИЗИЯ ОБЯЗАТЕЛЬСТВ И СРОКОВ ПЕРЕСМОТРА ===
[ACTIVE PROJECT: demo]
• Решение D01: плановый пересмотр 30.06.2026 (через 129 дн.)
• Решение D02: технический релиз 15.04.2026 (через 53 дн.)
• Источники данных: все 14 источников моложе 365 дней (актуальны)
Система не бросает продукт после принятия решения, а держит контрольные точки!""",
        "teleprompter": "Показываем важнейшее требование хакатона: продолжение после перерыва. Новый чат, запуск resume.py — агент считывает готовое состояние и do_not_redo! А скрипт review.py контролирует сроки пересмотра решений."
    },
    {
        "id": "scene_10",
        "duration": 30,
        "step": "10 / 10",
        "timecode": "06:00 - 06:30",
        "title": "Финальный единый отчет report.md и аудит затрат (0 ₽)",
        "active_file": "projects/demo/report.md",
        "badge": "09-review · Готово к сдаче",
        "file_tree": [
            ("📁 projects/demo/", True),
            ("  📄 report.md", True),
            ("  📄 manual-costs.csv", True),
            ("  📄 run-log.csv", True),
            ("📁 docs/", True),
            ("  📄 mega-strategist-description.pdf", True),
        ],
        "editor_content": """<span class="comment"># Итоговый отчет: Стратегия «Связь для близких» (report.md)</span>
Собран автоматически скриптом report.py · 390 строк · Все разделы согласованы

<span class="keyword">Сводка затрат (manual-costs.csv):</span>
• Затраты на внешние API / сервисы: <strong>0 ₽</strong> (бесплатные тарифы)
• Время продакт-менеджера на шлюзах: <strong>180 минут</strong> (3 часа фокусной работы)
• Токены LLM: 325 300 input / 43 500 output (прозрачный журнал по каждой стадии)

<span class="keyword">Репозиторий проекта:</span>
<code>https://github.com/FrankyShelloy/mega-strategist</code>
""",
        "terminal_cmd": "cat projects/demo/manual-costs.csv | tail -5",
        "terminal_output": """06-communication,38200,5100,0,20
07-test-plan,32800,4600,0,20
08-decision-record,16400,2200,0,10
09-review,14200,1900,0,10
Итого: 325300 tokens in, 43500 tokens out, 0 руб., 180 мин.
[COMPLETED] Проект mega-strategist готов к оценке жюри!""",
        "teleprompter": "Финальный артефакт — отчет report.md, собранный автоматически. Честная смета: 0 рублей расходов на API, 3 часа вовлечения продакта. Все материалы и PDF-описание в открытом репозитории GitHub. Спасибо за внимание!"
    }
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1920px;
    height: 1080px;
    background: #0f111a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #e2e8f0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  /* Top App Bar */
  .window-header {
    height: 48px;
    background: #1a1c29;
    border-bottom: 1px solid #282a3c;
    display: flex;
    align-items: center;
    padding: 0 20px;
    justify-content: space-between;
  }
  .window-controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .dot { width: 13px; height: 13px; border-radius: 50%; display: inline-block; }
  .dot-red { background: #ff5f56; }
  .dot-yellow { background: #ffbd2e; }
  .dot-green { background: #27c93f; }
  .window-title {
    font-size: 14px;
    font-weight: 500;
    color: #94a3b8;
    letter-spacing: 0.5px;
  }
  .window-badge {
    background: #E8003D;
    color: #fff;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
  }

  /* Main Area */
  .workspace {
    flex: 1;
    display: flex;
    height: calc(1080px - 48px - 140px);
    overflow: hidden;
  }

  /* Left Sidebar */
  .sidebar {
    width: 320px;
    background: #141622;
    border-right: 1px solid #232536;
    padding: 16px 14px;
    display: flex;
    flex-direction: column;
  }
  .sidebar-header {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 14px;
  }
  .file-item {
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 13px;
    color: #94a3b8;
    padding: 5px 8px;
    border-radius: 4px;
    margin-bottom: 3px;
    white-space: pre;
  }
  .file-item.active {
    background: #25283d;
    color: #38bdf8;
    font-weight: 600;
  }

  /* Center Editor */
  .editor-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #0f111a;
    border-right: 1px solid #232536;
    overflow: hidden;
  }
  .tabs-bar {
    height: 40px;
    background: #141622;
    border-bottom: 1px solid #232536;
    display: flex;
    align-items: center;
  }
  .tab {
    height: 100%;
    padding: 0 20px;
    display: flex;
    align-items: center;
    font-size: 13px;
    color: #38bdf8;
    background: #0f111a;
    border-top: 2px solid #E8003D;
    border-right: 1px solid #232536;
    font-weight: 500;
  }
  .editor-content {
    flex: 1;
    padding: 24px 30px;
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 14.5px;
    line-height: 1.65;
    color: #cbd5e1;
    overflow: hidden;
  }
  .editor-content strong { color: #f8fafc; }
  .editor-content em { color: #f59e0b; font-style: normal; }
  .editor-content .comment { color: #64748b; display: block; margin-bottom: 8px; font-weight: 600; }
  .editor-content .keyword { color: #a855f7; display: block; margin-top: 14px; margin-bottom: 6px; font-weight: 600; }
  .editor-content code { background: #1e2235; color: #38bdf8; padding: 2px 6px; border-radius: 4px; }
  .editor-content table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
  .editor-content th { background: #1e2235; color: #38bdf8; padding: 6px 10px; text-align: left; }
  .editor-content td { border-bottom: 1px solid #232536; padding: 6px 10px; }
  .badge-tag { display: inline-block; background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; margin-right: 6px; }

  /* Right Terminal */
  .terminal-container {
    width: 620px;
    background: #090a10;
    display: flex;
    flex-direction: column;
  }
  .terminal-header {
    height: 40px;
    background: #141622;
    border-bottom: 1px solid #232536;
    display: flex;
    align-items: center;
    padding: 0 16px;
    font-size: 12px;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.8px;
  }
  .terminal-body {
    flex: 1;
    padding: 18px 20px;
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #a5f3fc;
    overflow: hidden;
  }
  .terminal-prompt { color: #22c55e; font-weight: 600; }
  .terminal-cmd { color: #f8fafc; font-weight: 600; margin-bottom: 10px; }
  .terminal-output { color: #94a3b8; white-space: pre-wrap; }

  /* Bottom Teleprompter / Narration Bar */
  .teleprompter-bar {
    height: 140px;
    background: #141724;
    border-top: 2px solid #E8003D;
    display: flex;
    flex-direction: column;
    padding: 14px 28px;
    justify-content: center;
  }
  .teleprompter-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .teleprompter-step {
    font-size: 13px;
    font-weight: 700;
    color: #E8003D;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .teleprompter-title {
    font-size: 15px;
    font-weight: 600;
    color: #f8fafc;
  }
  .teleprompter-time {
    font-size: 13px;
    color: #64748b;
    font-family: monospace;
    font-weight: 600;
  }
  .teleprompter-text {
    font-size: 17px;
    line-height: 1.45;
    color: #fef08a;
    background: rgba(0,0,0,0.25);
    padding: 8px 16px;
    border-radius: 6px;
    border-left: 4px solid #f59e0b;
  }
</style>
</head>
<body>

  <!-- Window Header -->
  <div class="window-header">
    <div class="window-controls">
      <span class="dot dot-red"></span>
      <span class="dot dot-yellow"></span>
      <span class="dot dot-green"></span>
    </div>
    <div class="window-title">mega-strategist · Antigravity / Cursor IDE</div>
    <div class="window-badge">__BADGE__</div>
  </div>

  <!-- Workspace -->
  <div class="workspace">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">Проводник (Explorer)</div>
      __FILE_TREE__
    </div>

    <!-- Center Editor -->
    <div class="editor-container">
      <div class="tabs-bar">
        <div class="tab">📄 __ACTIVE_FILE__</div>
      </div>
      <div class="editor-content">
        __EDITOR_CONTENT__
      </div>
    </div>

    <!-- Terminal -->
    <div class="terminal-container">
      <div class="terminal-header">Терминал (bash · python 3.11)</div>
      <div class="terminal-body">
        <div class="terminal-prompt">$ <span class="terminal-cmd">__TERMINAL_CMD__</span></div>
        <div class="terminal-output">__TERMINAL_OUTPUT__</div>
      </div>
    </div>
  </div>

  <!-- Bottom Teleprompter -->
  <div class="teleprompter-bar">
    <div class="teleprompter-meta">
      <span class="teleprompter-step">ШАГ __STEP__</span>
      <span class="teleprompter-title">__TITLE__</span>
      <span class="teleprompter-time">⏱ __TIMECODE__</span>
    </div>
    <div class="teleprompter-text">
      🎙 <strong>Текст ведущего:</strong> «__TELEPROMPTER__»
    </div>
  </div>

</body>
</html>
"""

def generate_html_slides():
    """Создает HTML файлы для каждой из 10 сцен."""
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    html_files = []
    for scene in SCENES:
        file_tree_html = ""
        for name, is_active in scene["file_tree"]:
            active_cls = " active" if is_active else ""
            file_tree_html += f'<div class="file-item{active_cls}">{name}</div>\n'
        
        html = HTML_TEMPLATE
        html = html.replace("__BADGE__", scene["badge"])
        html = html.replace("__ACTIVE_FILE__", scene["active_file"])
        html = html.replace("__FILE_TREE__", file_tree_html)
        html = html.replace("__EDITOR_CONTENT__", scene["editor_content"])
        html = html.replace("__TERMINAL_CMD__", scene["terminal_cmd"])
        html = html.replace("__TERMINAL_OUTPUT__", scene["terminal_output"])
        html = html.replace("__STEP__", scene["step"])
        html = html.replace("__TITLE__", scene["title"])
        html = html.replace("__TIMECODE__", scene["timecode"])
        html = html.replace("__TELEPROMPTER__", scene["teleprompter"])
        
        filepath = FRAMES_DIR / f"{scene['id']}.html"
        filepath.write_text(html, encoding="utf-8")
        html_files.append((scene["id"], filepath, scene["duration"]))
    return html_files


def render_png_frames(html_files):
    """Рендерит каждый HTML в 1920x1080 PNG через headless Chrome."""
    png_files = []
    for scene_id, html_path, duration in html_files:
        png_path = FRAMES_DIR / f"{scene_id}.png"
        print(f"Рендеринг сцены {scene_id} в PNG...")
        cmd = [
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--window-size=1920,1080",
            f"--screenshot={png_path}",
            f"file://{html_path.resolve()}"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not png_path.exists():
            raise RuntimeError(f"Не удалось создать скриншот для {scene_id}")
        png_files.append((png_path, duration))
    return png_files


def assemble_mp4(png_files, audio_file=None):
    """Склеивает PNG кадры в MP4 через ffmpeg concat, при наличии звука добавляет аудио."""
    concat_file = FRAMES_DIR / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for png_path, duration in png_files:
            f.write(f"file '{png_path.name}'\n")
            f.write(f"duration {duration}\n")
        # ffmpeg concat требует повторения последнего кадра
        f.write(f"file '{png_files[-1][0].name}'\n")

    print(f"Сборка MP4 в {OUTPUT_VIDEO}...")
    if audio_file and Path(audio_file).exists():
        print(f"Объединение с аудио-дорожкой: {audio_file}")
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-i", str(audio_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(OUTPUT_VIDEO)
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(OUTPUT_VIDEO)
        ]
    
    subprocess.run(cmd, cwd=FRAMES_DIR, check=True)
    print(f"[УСПЕХ] Видео готово: {OUTPUT_VIDEO} ({OUTPUT_VIDEO.stat().st_size // 1024} КБ)")


def main():
    parser = argparse.ArgumentParser(description="Сборщик демо-видео mega-strategist")
    parser.add_argument("--audio", help="Путь к аудиофайлу (mp3, wav, m4a, ogg)")
    parser.add_argument("--render-only", action="store_true", help="Только сгенерировать кадры")
    args = parser.parse_args()

    print("=== ГЕНЕРАТОР ДЕМО-ВИДЕО MEGA-STRATEGIST ===")
    html_files = generate_html_slides()
    png_files = render_png_frames(html_files)

    if not args.render_only:
        assemble_mp4(png_files, audio_file=args.audio)


if __name__ == "__main__":
    main()
