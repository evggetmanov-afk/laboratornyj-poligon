#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Закрыть карточку вахты
# @raycast.mode fullOutput
# @raycast.packageName Лабораторный полигон
# @raycast.icon 📝

import os
import subprocess
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path("/Users/getmanov/Лабораторный_полигон")
JOURNAL_DIR = VAULT_DIR / "Вахтенный_журнал"

def play_sound(sound_name):
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
    if os.path.exists(sound_path):
        subprocess.run(["afplay", sound_path], stderr=subprocess.DEVNULL)

def main():
    now = datetime.now()
    id_str = now.strftime("%Y%m%d%H%M")
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    title_part = "Сдача_вахты_и_итоги_этапа"
    file_name = f"{date_str}_{now.strftime('%H-%M')}_{title_part}.md"
    target_path = JOURNAL_DIR / file_name

    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

    content = f"""---
id: {id_str}
дата: {date_str}
время: {time_str}
тип: вахтенный_журнал
статус: завершено
теги:
  - вахта
  - фиксация_этапа
---

# Итоги вахты от {date_str} {time_str}

## 1. Завершенные задачи
* 

## 2. Статус контура
* 

## 3. Фокус следующей смены
* 
"""
    target_path.write_text(content, encoding="utf-8")
    play_sound("Glass")
    print(f"Карточка смены успешно создана: {target_path.name}")

if __name__ == "__main__":
    main()
