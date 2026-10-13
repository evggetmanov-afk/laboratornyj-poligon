#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Открыть вахту
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🚀

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
SWAP_DIR = ROOT_DIR / ".swap"
SWAP_TASK_PATH = SWAP_DIR / "TASK.md"

INITIAL_TASK_TEMPLATE = """# ТЕКУЩИЙ КОНТРАКТ ЗАДАЧИ

## 1. ЦЕЛЬ И КОНТЕКСТ
- 

## 2. ШАГИ ВЫПОЛНЕНИЯ
- [ ] 

## 3. ФИКСАЦИЯ ИТОГОВ
- 
"""


def play_sound_and_notify(title: str, message: str) -> None:
    subprocess.run(["afplay", "/System/Library/Sounds/Pop.aiff"], stderr=subprocess.DEVNULL)
    osa_cmd = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", osa_cmd], stderr=subprocess.DEVNULL)


def is_meaningful_content(content: str) -> bool:
    stripped = content.strip()
    return bool(stripped) and stripped != INITIAL_TASK_TEMPLATE.strip()


def main() -> None:
    SWAP_DIR.mkdir(parents=True, exist_ok=True)

    if SWAP_TASK_PATH.exists():
        current_content = SWAP_TASK_PATH.read_text(encoding="utf-8")
        if is_meaningful_content(current_content):
            msg = "Внимание: в TASK.md есть незакрытая задача. Сначала закройте прошлую смену."
            play_sound_and_notify("Лабораторный полигон", msg)
            sys.exit(1)

    SWAP_TASK_PATH.write_text(INITIAL_TASK_TEMPLATE, encoding="utf-8")
    msg = "Вахта открыта: TASK.md готов к заполнению"
    play_sound_and_notify("Лабораторный полигон", msg)


if __name__ == "__main__":
    main()
