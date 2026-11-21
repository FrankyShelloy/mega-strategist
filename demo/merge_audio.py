#!/usr/bin/env python3
"""
Скрипт объединения видеоряда и голосовой дорожки в итоговое демо-видео.
Использование:
  python3 demo/merge_audio.py voice.mp3
  python3 demo/merge_audio.py /path/to/my_recording.m4a --output final_mega_strategist_demo.mp4
"""

import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VIDEO = ROOT / "demo" / "mega_strategist_demo.mp4"
DEFAULT_OUTPUT = ROOT / "demo" / "final_demo_with_voice.mp4"


def get_media_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def merge(audio_path, video_path=DEFAULT_VIDEO, output_path=DEFAULT_OUTPUT):
    audio_path = Path(audio_path).resolve()
    if not audio_path.exists():
        print(f"Ошибка: аудиофайл {audio_path} не найден!", file=sys.stderr)
        return 1

    if not video_path.exists():
        print(f"Ошибка: видеофайл {video_path} не найден! Сначала запустите: python3 demo/render_video.py", file=sys.stderr)
        return 1

    audio_dur = get_media_duration(audio_path)
    video_dur = get_media_duration(video_path)
    print(f"Длительность звука: {audio_dur:.1f} сек ({audio_dur/60:.2f} мин)")
    print(f"Длительность видео: {video_dur:.1f} сек ({video_dur/60:.2f} мин)")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]

    print(f"Создание итогового видео: {output_path}...")
    subprocess.run(cmd, check=True)
    print(f"\n[УСПЕХ] Итоговое видео со звуком создано!")
    print(f"Файл: {output_path}")
    print(f"Размер: {output_path.stat().st_size // 1024} КБ")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Объединение видеоряда и голоса")
    parser.add_argument("audio", help="Путь к аудиофайлу (mp3, wav, m4a, ogg, aac)")
    parser.add_argument("--video", default=DEFAULT_VIDEO, help="Путь к исходному видео")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Путь к итоговому файлу")
    args = parser.parse_args()

    sys.exit(merge(args.audio, args.video, args.output))


if __name__ == "__main__":
    main()
