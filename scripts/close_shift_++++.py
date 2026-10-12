#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Закрыть вахту (++++ )
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon ⚙️

import subprocess
from pathlib import Path
import locale

try:
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
except Exception:
    pass

VAULT_DIR = Path("/Users/getmanov/Лабораторный_полигон")
JOURNAL_DIR = VAULT_DIR / "Вахтенный_журнал"

def main():
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], stderr=subprocess.DEVNULL)
    
    osa_cmd = "display notification \"Вахта успешно закрыта по триггеру ++++\" with title \"Лабораторный полигон\""
    subprocess.run(["osascript", "-e", osa_cmd])

if __name__ == "__main__":
    main()
