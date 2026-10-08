#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] [Вахта] Захват ошибки из буфера в дневной лог
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🔬

import os
import sys
import subprocess
import datetime
from pathlib import Path
import traceback

def play_sound(sound_name="Pop"):
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
    if os.path.exists(sound_path):
        subprocess.run(["afplay", sound_path], stderr=subprocess.DEVNULL)

def get_target_journal(vault_dir: Path) -> tuple[Path, str]:
    cwd = Path.cwd().resolve()
    
    # Проверка, находимся ли мы внутри проекта в 01_projects
    try:
        rel = cwd.relative_to(vault_dir)
        parts = rel.parts
        if len(parts) >= 2 and parts[0] == "01_projects":
            project_name = parts[1]
            project_dir = vault_dir / "01_projects" / project_name
            journal_dir = project_dir / "journal"
            journal_dir.mkdir(parents=True, exist_ok=True)
            return journal_dir, f"PROJECT: {project_name}"
    except ValueError:
        pass

    # Фолбэк на корневой системный журнал
    root_journal = vault_dir / "Вахтенный_журнал"
    root_journal.mkdir(parents=True, exist_ok=True)
    return root_journal, "CORE"

def main():
    vault_dir = Path("/Users/getmanov/Лабораторный_полигон").resolve()
    journal_dir, context_level = get_target_journal(vault_dir)
    
    today_file = journal_dir / f"{datetime.date.today()}.md"
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    clipboard_content = ""
    try:
        res = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
        clipboard_content = res.stdout.strip()
    except Exception as e:
        clipboard_content = f"Ошибка чтения буфера: {e}\n{traceback.format_exc()}"

    if not clipboard_content:
        clipboard_content = "Пустой буфер обмена на момент захвата."

    entry = f"\n## Инцидент [{timestamp}]\n- **Уровень:** {context_level}\n\n```text\n{clipboard_content}\n```\n"

    try:
        with open(today_file, "a", encoding="utf-8") as f:
            f.write(entry)
        play_sound("Pop")
    except Exception as e:
        play_sound("Basso")
        sys.stderr.write(f"Ошибка записи в журнал {today_file}: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
