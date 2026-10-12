#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] [Вахта] Захват ошибки из буфера в дневной лог
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🔬

import subprocess
import datetime
from pathlib import Path
import traceback

VAULT_DIR = Path("/Users/getmanov/Лабораторный_полигон")
JOURNAL_DIR = VAULT_DIR / "Вахтенный_журнал"
JOURNAL_DIR.mkdir(exist_ok=True)

today_file = JOURNAL_DIR / f"{datetime.date.today()}.md"
timestamp = datetime.datetime.now().strftime("%H:%M:%S")

clipboard_content = ""
error_details = ""

try:
    result = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
    clipboard_content = result.stdout.strip()
    if not clipboard_content:
        clipboard_content = "[Буфер обмена пуст]"
except Exception as e:
    try:
        osa_result = subprocess.run(
            ["osascript", "-e", "the clipboard as text"],
            capture_output=True, text=True, check=True
        )
        clipboard_content = osa_result.stdout.strip()
        if not clipboard_content:
            clipboard_content = "[Буфер обмена пуст (через osascript)]"
    except Exception as osa_e:
        error_details = f"Ошибка чтения: {e} | osascript: {osa_e}\n{traceback.format_exc()}"
        clipboard_content = f"[Не удалось прочитать буфер обмена]\n{error_details}"

log_entry = f"\n## Инцидент [{timestamp}]\n\n```text\n{clipboard_content}\n```\n"

try:
    with today_file.open("a", encoding="utf-8") as f:
        f.write(log_entry)
    subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], stderr=subprocess.DEVNULL)
except Exception:
    pass
