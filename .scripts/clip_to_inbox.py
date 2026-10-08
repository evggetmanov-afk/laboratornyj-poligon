#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = VAULT_DIR / "Входящие"

def play_sound(sound_name: str):
    sound_path = Path(f"/System/Library/Sounds/{sound_name}.aiff")
    if sound_path.exists():
        subprocess.run(["afplay", str(sound_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def notify(title: str, message: str):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def clean_slug(text: str) -> str:
    cleaned = re.sub(r'[\/\\:\*\?"<>\|#`\$\t\n\r]', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("---") or line.startswith("```"):
            continue
        cleaned = clean_slug(line)
        words = cleaned.split()
        if words:
            selected = words[:4]
            title = " ".join(selected)
            if len(title) > 40:
                title = title[:40].rsplit(' ', 1)[0]
            if len(title.split()) >= 2:
                return title
            elif len(words) == 1:
                return f"{words[0]} мысль"
    return "Входящая новая заметка"

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

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    note_id = now.strftime("%Y%m%d%H%M")
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    title_slug = generate_title(clipboard_text)
    file_path = INBOX_DIR / f"{title_slug}.md"

    counter = 1
    while file_path.exists():
        file_path = INBOX_DIR / f"{title_slug} {counter}.md"
        counter += 1

    content = f"""---
id: {note_id}
дата: {date_str}
время: {time_str}
тип: входящие
статус: сырое
теги:
  - входящие
---

# {title_slug}

{clipboard_text}
"""

    try:
        file_path.write_text(content, encoding="utf-8")
        play_sound("Pop")
        notify("Лабораторный полигон", f"Сохранено: {file_path.name}")
    except Exception as e:
        play_sound("Basso")
        notify("Лабораторный полигон", f"Ошибка записи: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
