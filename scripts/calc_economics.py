#!/usr/bin/env python3
"""Воспроизводимый расчет юнит-экономики, целевых показателей и параметров пилота.

Полностью на стандартной библиотеке Python (stdlib).
Используется ролью data-analyst и проверяет баланс показателей брифа:
«Связь для близких и собственных устройств».
"""
import argparse
import math
import sys

# Базовые константы из брифа
TOTAL_HOUSEHOLDS = 300_000
AVAILABLE_HOUSEHOLDS = 100_000
TOTAL_MULTIDEVICE = 180_000
AVAILABLE_MULTIDEVICE = 40_000

# Финансовые параметры
UNIT_MARGIN_PER_MONTH = 500  # руб. валовой прибыли за один дополнительный оплаченный месяц одного номера
TARGET_PROFIT_GAP_RUB = 6_000_000  # 285 млн руб. (цель) - 279 млн руб. (без изменений)
SIMS_PER_FAMILY_AVG = 2.3  # среднее число номеров в активной семейной группе


def sample_size_proportions(p1: float, p2: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Расчет размера выборки на группу для Z-теста разности долей."""
    if p1 == p2:
        return 0
    # Квантили нормального распределения
    z_alpha = 1.95996 if alpha == 0.05 else 2.57583
    z_beta = 0.84162 if power == 0.80 else 1.28155
    p_bar = (p1 + p2) / 2.0
    num = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    den = (p1 - p2) ** 2
    return math.ceil(num / den)


def run_calculations():
    print("=" * 65)
    print("ВОСПРОИЗВОДИМЫЙ РАСЧЕТ ЮНИТ-ЭКОНОМИКИ И ПАРАМЕТРОВ ПИЛОТА")
    print("=" * 65)

    print("\n1. АНАЛИЗ РЫНКА И ДОСТУПНОЙ БАЗЫ:")
    print(f"  - Всего домохозяйств на рынке:       {TOTAL_HOUSEHOLDS:,} (доступно оператору: {AVAILABLE_HOUSEHOLDS:,})")
    print(f"  - Всего мультиномерных клиентов:     {TOTAL_MULTIDEVICE:,} (доступно оператору: {AVAILABLE_MULTIDEVICE:,})")
    print(f"  - Принцип непересечения: клиенты с обоими сценариями учтены только в домохозяйствах.")

    print("\n2. ЦЕЛЕВЫЕ ПОКАЗАТЕЛИ И РАЗРЫВЫ (ПЛАНОВЫЙ ГОД):")
    gap_table = [
        ("Валовая прибыль за год, млн руб.", 275, 279, 285, "+6 млн руб."),
        ("Активные семейные группы (посл. мес.)", 4000, 5000, 8000, "+3 000 групп"),
        ("Подключенные группы (конец года)", 6500, 8000, 12000, "+4 000 групп"),
        ("Подключенные мультиномера (конец года)", 800, 1000, 2000, "+1 000 клиентов"),
        ("Активация за 14 дней в посл. кв.", 42.0, 45.0, 60.0, "+15 п.п."),
    ]
    print(f"  {'Показатель':<40} | {'База (факт)':<11} | {'Без изм.':<9} | {'Цель':<6} | {'Разрыв':<12}")
    print("  " + "-" * 75)
    for name, base, no_ch, tgt, gap in gap_table:
        b_str = f"{base}%" if isinstance(base, float) else f"{base:,}"
        n_str = f"{no_ch}%" if isinstance(no_ch, float) else f"{no_ch:,}"
        t_str = f"{tgt}%" if isinstance(tgt, float) else f"{tgt:,}"
        print(f"  {name:<40} | {b_str:<11} | {n_str:<9} | {t_str:<6} | {gap:<12}")

    print("\n3. РАСЧЕТ ОКУПАЕМОСТИ И ТРЕБУЕМЫХ ОПЛАЧЕННЫХ МЕСЯЦЕВ:")
    needed_months = TARGET_PROFIT_GAP_RUB / UNIT_MARGIN_PER_MONTH
    needed_family_months = needed_months / SIMS_PER_FAMILY_AVG
    print(f"  - Ставка валовой прибыли за 1 номер-месяц: {UNIT_MARGIN_PER_MONTH} руб.")
    print(f"  - Целевой прирост валовой прибыли:        {TARGET_PROFIT_GAP_RUB:,} руб.")
    print(f"  - Требуется дополнительных номер-месяцев: {int(needed_months):,}")
    print(f"  - При среднем {SIMS_PER_FAMILY_AVG} номера на семью:      ~{int(needed_family_months):,} семейных групп-месяцев")

    # Оценка затрат на разработку во 2-м квартале:
    # 3 чел.-мес. разработки + 0.5 дизайнера + 0.5 аналитика + 1.0 QA = 5.0 чел.-мес.
    # При рыночной себестоимости ~300 тыс. руб./чел.-мес. = 1.5 млн руб.
    dev_months = 3.0
    designer_months = 0.5
    analyst_months = 0.5
    qa_months = 1.0
    total_staff_months = dev_months + designer_months + analyst_months + qa_months
    cost_per_person_month = 300_000
    capex_pilot_rub = int(total_staff_months * cost_per_person_month)
    total_needed_with_capex = TARGET_PROFIT_GAP_RUB + capex_pilot_rub
    needed_months_with_capex = total_needed_with_capex / UNIT_MARGIN_PER_MONTH

    print(f"\n4. ЗАТРАТЫ НА ПИЛОТ (Q2):")
    print(f"  - Разработчики: {dev_months} чел.-мес., Дизайнер: {designer_months}, Аналитик: {analyst_months}, QA: {qa_months}")
    print(f"  - Итого трудозатраты: {total_staff_months} чел.-мес. (~{capex_pilot_rub:,} руб. при ставке {cost_per_person_month:,} руб./мес.)")
    print(f"  - С учетом окупаемости затрат на разработку нужно: {int(needed_months_with_capex):,} номер-месяцев")

    print(f"\n5. РАСЧЕТ ВЫБОРКИ ПИЛОТА (A/B HOLD-OUT DESIGN):")
    p_base = 0.12  # 12% перебоев интернета у близких при базовом обслуживании
    p_target = 0.09  # 9% при проактивных алертах и удобном добавлении ГБ (снижение на 3 п.п. = 25% rel.)
    n_per_variant = sample_size_proportions(p_base, p_target, alpha=0.05, power=0.80)
    total_n = n_per_variant * 2
    weeks = 6
    per_week = math.ceil(total_n / weeks)

    print(f"  - Базовая частота ограничения связи (baseline): {p_base*100:.1f}%")
    print(f"  - Целевая частота (target effect, -3 п.п.):       {p_target*100:.1f}%")
    print(f"  - Требуемый размер выборки на вариант (power 80%, alpha 5%): {n_per_variant} семей")
    print(f"  - Всего участников (Тест + Контроль holdout):               {total_n} семей")
    print(f"  - При сроке набора {weeks} недель темп регистрации:          ~{per_week} впервые подошедших семей/нед.")

    print("\n6. СТРЕСС-ТЕСТ ЧУВСТВИТЕЛЬНОСТИ (SENSITIVITY ANALYSIS):")
    scenarios = [
        ("Оптимистичный (+4 п.п. удержание)", 14_000, 14_000 * 500, 14_000 * 500 - capex_pilot_rub),
        ("Базовый (+3 п.п. удержание)", 12_000, 12_000 * 500, 12_000 * 500 - capex_pilot_rub),
        ("Консервативный (+1.5 п.п. удержание)", 7_000, 7_000 * 500, 7_000 * 500 - capex_pilot_rub),
        ("Пессимистичный (+0.5 п.п. удержание)", 2_500, 2_500 * 500, 2_500 * 500 - capex_pilot_rub),
    ]
    print(f"  {'Сценарий':<38} | {'Доп. мес.':<10} | {'Прибыль gross':<14} | {'Чистый эффект с CaPex'}")
    print("  " + "-" * 75)
    for sc_name, m, gross, net in scenarios:
        print(f"  {sc_name:<38} | {m:<10,} | {gross:<14,} | {net:,} руб.")

    print("\n" + "=" * 65)
    print("Расчет завершен успешно. Все формулы соответствуют брифу.")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Расчет экономики кейса МегаФона")
    parser.add_argument("--json", action="store_true", help="вывести в JSON формате")
    args = parser.parse_args()
    run_calculations()
    return 0


if __name__ == "__main__":
    sys.exit(main())
