#!/usr/bin/env python3
"""
Генератор динамической видеодемонстрации mega-strategist (Live Screencast).
Создает эффект живой записи экрана IDE:
- Движение курсора мыши (наведение, клики по табам, переходы в терминал)
- Посимвольный ввод команд в терминале с мигающим курсором
- Потоковый построчный вывод результатов CLI
- Подсветка ключевых блоков в редакторе кода
- Плавный прогресс-бар и индикатор стадии
- Объединение с обработанной и очищенной аудиодорожкой автора
"""

import sys
import time
import math
import subprocess
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FRAMES_DIR = ROOT / "demo" / "video_frames"
OUTPUT_VIDEO = ROOT / "demo" / "mega_strategist_live_demo.mp4"
AUDIO_TRACK = Path("/tmp/master_voice_processed.wav")

FPS = 25
WIDTH = 1920
HEIGHT = 1080

# Цвета терминала (RGB)
TERM_BG = (9, 10, 16)
PROMPT_COLOR = (34, 197, 94)       # зеленый
CMD_COLOR = (248, 250, 252)        # белый
TEXT_SLATE = (148, 163, 184)       # серый
TEXT_CYAN = (56, 189, 248)         # голубой
TEXT_GREEN = (74, 222, 128)        # светло-зеленый
TEXT_YELLOW = (250, 204, 21)       # желтый
TEXT_MAGENTA = (232, 121, 249)     # пурпурный

# Шрифты
FONT_MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
FONT_MONO_BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14)
FONT_UI = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 13)


def make_cursor():
    """Создает RGBA изображение указателя мыши с черной обводкой."""
    cur = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(cur)
    pts = [(0, 0), (0, 24), (6, 18), (11, 28), (15, 26), (10, 16), (18, 16)]
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    return np.array(cur)


CURSOR_RGBA = make_cursor()


def blit_cursor(frame_bgr, x, y):
    """Накладывает курсор мыши на BGR кадр."""
    x, y = int(x), int(y)
    h, w = CURSOR_RGBA.shape[:2]
    if x < 0 or y < 0 or x + w >= WIDTH or y + h >= HEIGHT:
        return
    roi = frame_bgr[y:y+h, x:x+w]
    alpha = CURSOR_RGBA[:, :, 3] / 255.0
    for c in range(3):
        # CURSOR_RGBA в RGB, roi в BGR
        color_val = CURSOR_RGBA[:, :, 2 - c]
        roi[:, :, c] = (1 - alpha) * roi[:, :, c] + alpha * color_val
    frame_bgr[y:y+h, x:x+w] = roi


def lerp_mouse(path, t):
    """Интерполяция координат мыши по контрольным точкам [(t_i, (x_i, y_i))]."""
    if t <= path[0][0]:
        return path[0][1]
    if t >= path[-1][0]:
        return path[-1][1]
    for i in range(len(path) - 1):
        t0, p0 = path[i]
        t1, p1 = path[i + 1]
        if t0 <= t <= t1:
            ratio = (t - t0) / (t1 - t0)
            # Плавная сигмоида (smoothstep)
            ratio = ratio * ratio * (3 - 2 * ratio)
            x = p0[0] + ratio * (p1[0] - p0[0])
            y = p0[1] + ratio * (p1[1] - p0[1])
            return x, y
    return path[-1][1]


SCENE_SPECS = [
    {
        "id": "scene_01",
        "duration": 15.0,
        "base_img": FRAMES_DIR / "scene_01.png",
        "cmd": "git status && git log -1 --oneline",
        "t_type_start": 4.5,
        "t_exec": 7.5,
        "outputs": [
            ("On branch main", TEXT_SLATE, 0.2),
            ("Your branch is up to date with 'origin/main'.", TEXT_SLATE, 0.4),
            ("nothing to commit, working tree clean", TEXT_GREEN, 0.7),
            ("c4161ad feat: add 1080p demo video & merger", TEXT_CYAN, 1.0),
        ],
        "highlight": None,
        "mouse_path": [(0.0, (180, 120)), (1.8, (420, 65)), (4.0, (650, 240)), (5.5, (1380, 110)), (8.5, (1480, 180)), (15.0, (1550, 220))]
    },
    {
        "id": "scene_02",
        "duration": 17.5,
        "base_img": FRAMES_DIR / "scene_02.png",
        "cmd": "python3 scripts/resume.py",
        "t_type_start": 5.5,
        "t_exec": 8.5,
        "outputs": [
            ("# Состояние проекта: demo", CMD_COLOR, 0.1),
            ("stage: 00-intake", TEXT_CYAN, 0.3),
            ("status: waiting_brief", TEXT_YELLOW, 0.5),
            ("next_action: заполнить brief.md и подтвердить рамку на G1", TEXT_SLATE, 0.8),
            ("human_gate: none", TEXT_SLATE, 1.0),
            ("do_not_redo: []", TEXT_SLATE, 1.2),
            ("[OK] Скрипт resume считал артефакт state.md", TEXT_GREEN, 1.5),
        ],
        "highlight": (2.5, 6.0, (350, 160, 1260, 280)),
        "mouse_path": [(0.0, (180, 210)), (1.5, (450, 65)), (3.5, (600, 230)), (6.5, (1380, 110)), (10.0, (1480, 240)), (17.5, (1520, 310))]
    },
    {
        "id": "scene_03",
        "duration": 18.0,
        "base_img": FRAMES_DIR / "scene_03.png",
        "cmd": "cat projects/demo/state.md | grep -E 'stage|gate|status'",
        "t_type_start": 7.0,
        "t_exec": 10.5,
        "outputs": [
            ("stage: 01-research-plan", TEXT_CYAN, 0.2),
            ("status: waiting_human", TEXT_YELLOW, 0.5),
            ("human_gate: G1", TEXT_MAGENTA, 0.8),
            ("[HUMAN INPUT]: Фокус на семейных группах в Q2.", CMD_COLOR, 1.2),
            ("[STATUS]: Решение продакта зафиксировано -> G1_passed", TEXT_GREEN, 1.6),
        ],
        "highlight": (2.5, 7.5, (350, 150, 1260, 340)),
        "mouse_path": [(0.0, (180, 240)), (1.5, (470, 65)), (3.5, (680, 200)), (5.5, (680, 320)), (8.0, (1380, 110)), (12.0, (1500, 180)), (18.0, (1550, 260))]
    },
    {
        "id": "scene_04",
        "duration": 15.5,
        "base_img": FRAMES_DIR / "scene_04.png",
        "cmd": "python3 scripts/check.py --all",
        "t_type_start": 5.0,
        "t_exec": 7.5,
        "outputs": [
            ("Проверка проектов...", TEXT_SLATE, 0.1),
            ("  demo: sources=14, claims=36, gaps=10, options=4", TEXT_CYAN, 0.3),
            ("  contracts: state.md OK, manual-costs.csv OK", TEXT_SLATE, 0.6),
            ("Проверка секретов: сканирование репозитория... чисто.", TEXT_SLATE, 0.9),
            ("EXIT: 0", TEXT_GREEN, 1.2),
            ("[SUCCESS] 0 ошибок! Все 36 утверждений верифицированы.", TEXT_GREEN, 1.5),
        ],
        "highlight": (2.0, 5.5, (350, 150, 1260, 300)),
        "mouse_path": [(0.0, (180, 280)), (1.5, (440, 65)), (3.5, (600, 210)), (6.0, (1380, 110)), (9.5, (1500, 240)), (15.5, (1550, 280))]
    },
    {
        "id": "scene_05",
        "duration": 16.0,
        "base_img": FRAMES_DIR / "scene_05.png",
        "cmd": "python3 scripts/simulate_persona.py --persona organizer_mother",
        "t_type_start": 5.5,
        "t_exec": 8.5,
        "outputs": [
            ("[INFO] Роль persona-interviewer по методике The Mom Test...", TEXT_SLATE, 0.2),
            ("[SYNTHETIC-PERSONA] Беседа с ролью 'organizer_mother'", TEXT_YELLOW, 0.5),
            ("  Ментальный барьер: страх скрытых автосписаний с баланса", TEXT_CYAN, 0.9),
            ("  Гипотеза: push при остатке <1 ГБ + шеринг в 1 клик", CMD_COLOR, 1.3),
            ("  Протокол сохранен в projects/demo/interviews/", TEXT_SLATE, 1.6),
            ("[STATUS] Завершено без подмены реальных данных.", TEXT_GREEN, 1.9),
        ],
        "highlight": (2.0, 6.0, (350, 130, 1260, 220)),
        "mouse_path": [(0.0, (180, 300)), (1.5, (510, 65)), (3.5, (620, 150)), (6.5, (1380, 110)), (10.5, (1500, 200)), (16.0, (1540, 270))]
    },
    {
        "id": "scene_06",
        "duration": 14.5,
        "base_img": FRAMES_DIR / "scene_06.png",
        "cmd": "cat projects/demo/state.md | grep -A 4 'human_gate: G2'",
        "t_type_start": 4.5,
        "t_exec": 7.0,
        "outputs": [
            ("human_gate: G2", TEXT_MAGENTA, 0.2),
            ("human_decision: Выбран вариант 03-family-proactive.", TEXT_GREEN, 0.5),
            ("отклонены: 01-status-quo, 02-close (с фиксацией причин)", TEXT_SLATE, 0.9),
            ("требование: реализовать защиту от двойных списаний (API).", TEXT_CYAN, 1.3),
        ],
        "highlight": (1.8, 5.0, (350, 260, 1260, 360)),
        "mouse_path": [(0.0, (180, 320)), (1.5, (490, 65)), (3.0, (620, 280)), (5.5, (1380, 110)), (9.0, (1500, 180)), (14.5, (1540, 250))]
    },
    {
        "id": "scene_07",
        "duration": 17.0,
        "base_img": FRAMES_DIR / "scene_07.png",
        "cmd": "python3 scripts/calc_economics.py",
        "t_type_start": 5.5,
        "t_exec": 8.0,
        "outputs": [
            ("=== РАСЧЕТ ЮНИТ-ЭКОНОМИКИ И ВЫБОРКИ ПИЛОТА ===", CMD_COLOR, 0.2),
            ("• Целевой разрыв валовой прибыли: 6 000 000 руб.", TEXT_YELLOW, 0.5),
            ("• Ставка валовой прибыли: 500 руб./номеро-месяц", TEXT_CYAN, 0.8),
            ("• Необходимый объем: 12 000 номеро-месяцев", TEXT_GREEN, 1.1),
            ("• Затраты разработки в Q2 (3 чел.-мес.): 1 500 000 руб.", TEXT_SLATE, 1.4),
            ("• Окупаемость инвестиций: 7 месяцев (август 2026)", TEXT_GREEN, 1.7),
            ("• Выборка A/B Holdout (MDE -3 п.п., 80%): 3 276 семей", TEXT_CYAN, 2.0),
        ],
        "highlight": (2.0, 6.0, (350, 240, 1260, 380)),
        "mouse_path": [(0.0, (180, 350)), (1.5, (470, 65)), (3.5, (680, 320)), (6.5, (1380, 110)), (10.0, (1500, 180)), (17.0, (1530, 280))]
    },
    {
        "id": "scene_08",
        "duration": 18.0,
        "base_img": FRAMES_DIR / "scene_08.png",
        "cmd": "cat projects/demo/state.md | grep -A 3 'G3_passed'",
        "t_type_start": 6.5,
        "t_exec": 9.5,
        "outputs": [
            ("human_gate: G3_passed", TEXT_MAGENTA, 0.2),
            ("status: ready_for_execution", TEXT_GREEN, 0.5),
            ("next_action: старт подготовительного этапа пилота к Q2", TEXT_CYAN, 0.9),
            ("do_not_redo: [00-intake, 01-research-plan, 02-collect,", TEXT_SLATE, 1.3),
            ("             03-evidence, 04-options, 05-product, 06-comm]", TEXT_SLATE, 1.6),
        ],
        "highlight": (2.0, 7.0, (350, 140, 1260, 340)),
        "mouse_path": [(0.0, (180, 380)), (1.5, (490, 65)), (4.0, (650, 220)), (7.5, (1380, 110)), (12.0, (1500, 180)), (18.0, (1540, 250))]
    },
    {
        "id": "scene_09",
        "duration": 15.0,
        "base_img": FRAMES_DIR / "scene_09.png",
        "cmd": "python3 scripts/review.py",
        "t_type_start": 5.0,
        "t_exec": 7.5,
        "outputs": [
            ("=== РЕВИЗИЯ ОБЯЗАТЕЛЬСТВ И СРОКОВ ПЕРЕСМОТРА ===", CMD_COLOR, 0.2),
            ("[ACTIVE PROJECT: demo]", TEXT_CYAN, 0.5),
            ("• Решение D01: плановый пересмотр 30.06.2026 (129 дн.)", TEXT_YELLOW, 0.8),
            ("• Решение D02: технический релиз 15.04.2026 (53 дн.)", TEXT_SLATE, 1.1),
            ("• Источники данных: все 14 источников моложе 365 дней", TEXT_GREEN, 1.4),
            ("Система держит контрольные точки после решения!", TEXT_GREEN, 1.8),
        ],
        "highlight": (2.0, 5.5, (350, 160, 1260, 280)),
        "mouse_path": [(0.0, (180, 400)), (1.5, (490, 65)), (3.5, (650, 210)), (6.0, (1380, 110)), (9.5, (1500, 180)), (15.0, (1530, 260))]
    },
    {
        "id": "scene_10",
        "duration": 20.5,
        "base_img": FRAMES_DIR / "scene_10.png",
        "cmd": "cat projects/demo/manual-costs.csv | tail -5",
        "t_type_start": 6.5,
        "t_exec": 9.5,
        "outputs": [
            ("06-communication,38200,5100,0,20", TEXT_SLATE, 0.2),
            ("07-test-plan,32800,4600,0,20", TEXT_SLATE, 0.5),
            ("08-decision-record,16400,2200,0,10", TEXT_SLATE, 0.8),
            ("09-review,14200,1900,0,10", TEXT_SLATE, 1.1),
            ("Итого: 325 300 tokens in, 0 руб. расходов, 180 мин.", TEXT_GREEN, 1.5),
            ("Репозиторий: https://github.com/FrankyShelloy/mega-strategist", TEXT_CYAN, 1.9),
            ("[COMPLETED] Проект mega-strategist готов к оценке жюри!", CMD_COLOR, 2.3),
        ],
        "highlight": (2.0, 7.0, (350, 180, 1260, 310)),
        "mouse_path": [(0.0, (180, 420)), (1.5, (470, 65)), (4.0, (650, 240)), (7.0, (1380, 110)), (12.0, (1500, 210)), (20.5, (1540, 270))]
    }
]


def render_dynamic_video():
    print("=== ГЕНЕРАЦИЯ ДИНАМИЧЕСКОГО ВИДЕО (LIVE SCREENCAST) ===")
    total_duration = sum(s["duration"] for s in SCENE_SPECS)
    total_frames = int(total_duration * FPS)
    print(f"Общая длительность: {total_duration:.1f} сек ({total_duration/60:.2f} мин)")
    print(f"Всего кадров: {total_frames} при {FPS} FPS")

    raw_video = Path("/tmp/dynamic_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(raw_video), fourcc, float(FPS), (WIDTH, HEIGHT))

    global_frame = 0
    t0 = time.time()

    for idx, spec in enumerate(SCENE_SPECS, 1):
        scene_dur = spec["duration"]
        n_scene_frames = int(scene_dur * FPS)
        print(f"Рендеринг сцены {idx:02d}/10: {spec['id']} ({scene_dur:.1f} сек, {n_scene_frames} кадров)...")

        # Базовое изображение
        base_pil = Image.open(spec["base_img"]).convert("RGB")
        base_np = np.array(base_pil)  # RGB
        base_bgr = cv2.cvtColor(base_np, cv2.COLOR_RGB2BGR)

        cmd_text = spec["cmd"]
        t_type_start = spec["t_type_start"]
        t_exec = spec["t_exec"]
        outputs = spec["outputs"]
        highlight_box = spec["highlight"]
        mouse_path = spec["mouse_path"]

        for f in range(n_scene_frames):
            t = f / float(FPS)
            frame_bgr = base_bgr.copy()

            # 1. Очищаем область терминала (черный фон терминала)
            cv2.rectangle(frame_bgr, (1300, 88), (1920, 940), (16, 10, 9), -1)

            # 2. Подсветка в редакторе (если активна)
            if highlight_box and highlight_box[0] <= t <= highlight_box[1]:
                x1, y1, x2, y2 = highlight_box[2]
                sub_img = frame_bgr[y1:y2, x1:x2]
                # Полупрозрачная подсветка
                glow_overlay = np.full_like(sub_img, (60, 40, 20), dtype=np.uint8)
                cv2.addWeighted(glow_overlay, 0.4, sub_img, 0.6, 0, sub_img)
                cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (248, 189, 56), 2)

            # 3. Рисуем терминал через PIL
            term_crop = frame_bgr[88:940, 1300:1920]
            term_crop_rgb = cv2.cvtColor(term_crop, cv2.COLOR_BGR2RGB)
            term_pil = Image.fromarray(term_crop_rgb)
            d_term = ImageDraw.Draw(term_pil)

            y_cursor = 22
            # Отрисовка строки команды
            if t < t_type_start:
                # До ввода команды: мигает пустой курсор
                d_term.text((20, y_cursor), "$ ", font=FONT_MONO_BOLD, fill=PROMPT_COLOR)
                if (int(t * 2) % 2) == 0:
                    d_term.text((38, y_cursor), "█", font=FONT_MONO, fill=PROMPT_COLOR)
            elif t < t_exec:
                # Ввод команды по буквам
                type_progress = (t - t_type_start) / (t_exec - t_type_start)
                n_chars = int(len(cmd_text) * min(1.0, type_progress))
                typed_str = cmd_text[:n_chars]
                d_term.text((20, y_cursor), "$ ", font=FONT_MONO_BOLD, fill=PROMPT_COLOR)
                d_term.text((38, y_cursor), typed_str, font=FONT_MONO_BOLD, fill=CMD_COLOR)
                # Блок-курсор после текста
                text_len = int(d_term.textlength(typed_str, font=FONT_MONO_BOLD))
                d_term.text((38 + text_len + 2, y_cursor), "█", font=FONT_MONO, fill=TEXT_CYAN)
            else:
                # Команда выполнена, выводим полную команду
                d_term.text((20, y_cursor), "$ ", font=FONT_MONO_BOLD, fill=PROMPT_COLOR)
                d_term.text((38, y_cursor), cmd_text, font=FONT_MONO_BOLD, fill=CMD_COLOR)

                # Потоковый вывод строк
                y_cursor += 28
                dt_after_exec = t - t_exec
                for line_text, color, delay in outputs:
                    if dt_after_exec >= delay:
                        d_term.text((20, y_cursor), line_text, font=FONT_MONO, fill=color)
                        y_cursor += 22

            # Возвращаем терминал обратно в BGR
            term_result_bgr = cv2.cvtColor(np.array(term_pil), cv2.COLOR_RGB2BGR)
            frame_bgr[88:940, 1300:1920] = term_result_bgr

            # 4. Движение мыши
            mx, my = lerp_mouse(mouse_path, t)
            blit_cursor(frame_bgr, mx, my)

            # 5. Глобальный прогресс-бар в самом низу экрана (y: 1075..1080)
            progress = (global_frame + f) / float(total_frames)
            bar_w = int(WIDTH * progress)
            cv2.rectangle(frame_bgr, (0, 1074), (WIDTH, 1080), (30, 30, 40), -1)
            cv2.rectangle(frame_bgr, (0, 1074), (bar_w, 1080), (61, 0, 232), -1) # #E8003D в BGR

            out.write(frame_bgr)

        global_frame += n_scene_frames

    out.release()
    render_time = time.time() - t0
    print(f"\n[УСПЕХ] Все кадры отрендерены за {render_time:.1f} сек! ({total_frames / render_time:.1f} FPS)")

    # Объединение со звуком
    print(f"Склейка с аудиодорожкой {AUDIO_TRACK}...")
    cmd_merge = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(AUDIO_TRACK),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        str(OUTPUT_VIDEO)
    ]
    subprocess.run(cmd_merge, check=True)
    size_mb = OUTPUT_VIDEO.stat().st_size / (1024 * 1024)
    print(f"\n🎉 ИТОГОВОЕ ВИДЕО СОЗДАНО: {OUTPUT_VIDEO}")
    print(f"Размер: {size_mb:.2f} МБ")
    print(f"Длительность: {total_duration:.1f} сек (~{total_duration/60:.2f} мин)")


if __name__ == "__main__":
    render_dynamic_video()
