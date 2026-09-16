#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Собрать контекст вахты
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 📋

import os
import subprocess
from pathlib import Path

VAULT_DIR = Path("/Users/getmanov/Лабораторный_полигон")
PROMPT_PATH = VAULT_DIR / "Система" / "Промпты" / "Системный_Промпт.md"
JOURNAL_DIR = VAULT_DIR / "Вахтенный_журнал"

def play_sound(sound_name):
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
    if os.path.exists(sound_path):
        subprocess.run(["afplay", sound_path], stderr=subprocess.DEVNULL)

def notify(message, title="Лабораторный полигон"):
    osa_cmd = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", osa_cmd], stderr=subprocess.DEVNULL)

def copy_to_clipboard(text):
    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    process.communicate(text.encode("utf-8"))

def main():
    parts = []

    if PROMPT_PATH.exists():
        prompt_content = PROMPT_PATH.read_text(encoding="utf-8").strip()
        parts.append(prompt_content)
    else:
        notify("Системный промпт не найден", "Ошибка Вахты")
        play_sound("Basso")
        return

    if JOURNAL_DIR.exists():
        log_files = [f for f in JOURNAL_DIR.glob("*.md") if f.is_file()]
        if log_files:
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            log_content = latest_log.read_text(encoding="utf-8").strip()
            parts.append(f"\n\n---\n\n# Последняя запись вахты ({latest_log.name})\n\n{log_content}")

    full_context = "\n\n".join(parts)
    copy_to_clipboard(full_context)

    play_sound("Pop")
    notify("Контекст вахты скопирован в буфер", "Вахта")

if __name__ == "__main__":
    main()
