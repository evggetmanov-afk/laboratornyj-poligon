#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent
TARGET_DIR = VAULT_DIR / "Входящие"

def play_sound(sound_name: str):
    sound_path = Path(f"/System/Library/Sounds/{sound_name}.aiff")
    if sound_path.exists():
        subprocess.run(["afplay", str(sound_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def notify(title: str, message: str):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    try:
        res = subprocess.run(["pbpaste"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        clipboard_text = res.stdout.decode("utf-8", errors="replace").strip()
    except Exception as e:
        play_sound("Basso")
        notify("Лабораторный полигон", f"Ошибка буфера: {e}")
        sys.exit(1)

    if not clipboard_text:
        play_sound("Basso")
        notify("Лабораторный полигон", "Буфер обмена пуст")
        sys.exit(1)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    daily_file = TARGET_DIR / f"Дневник {date_str}.md"

    if not daily_file.exists():
        header = f"""---
id: {now.strftime("%Y%m%d0000")}
дата: {date_str}
тип: дневник
статус: сырое
теги:
  - входящие
  - дневник
---

# Дневник {date_str}

"""
        daily_file.write_text(header, encoding="utf-8")

    entry = f"\n## {time_str}\n\n{clipboard_text}\n"

    try:
        with open(daily_file, "a", encoding="utf-8") as f:
            f.write(entry)
        play_sound("Pop")
        notify("Лабораторный полигон", f"Добавлено в Дневник ({date_str})")
    except Exception as e:
        play_sound("Basso")
        notify("Лабораторный полигон", f"Ошибка записи: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
