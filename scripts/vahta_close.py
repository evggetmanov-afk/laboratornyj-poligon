#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Закрыть вахту
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🏁

import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
SWAP_TASK_PATH = ROOT_DIR / ".swap" / "TASK.md"
JOURNAL_DIR = ROOT_DIR / "watch_log"

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


def get_next_journal_path(journal_dir: Path) -> Path:
    journal_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y_%m_%d")
    existing = sorted(journal_dir.glob(f"journal_{today_str}_*.md"))
    if not existing:
        next_idx = 1
    else:
        last_name = existing[-1].stem
        try:
            last_idx = int(last_name.split("_")[-1])
            next_idx = last_idx + 1
        except ValueError:
            next_idx = len(existing) + 1
    return journal_dir / f"journal_{today_str}_{next_idx:02d}.md"


def main() -> None:
    if not SWAP_TASK_PATH.exists():
        play_sound_and_notify("Лабораторный полигон", "Ошибка: .swap/TASK.md не найден")
        sys.exit(1)

    task_content = SWAP_TASK_PATH.read_text(encoding="utf-8").strip()
    if not task_content or task_content == INITIAL_TASK_TEMPLATE.strip():
        play_sound_and_notify("Лабораторный полигон", "Предупреждение: TASK.md пуст или не заполнен")
        sys.exit(0)

    target_journal = get_next_journal_path(JOURNAL_DIR)
    close_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    journal_header = f"# ЖУРНАЛ СМЕНЫ: {target_journal.stem}\n*Закрыто:* {close_time_str}\n\n---\n\n"

    target_journal.write_text(journal_header + task_content + "\n", encoding="utf-8")
    SWAP_TASK_PATH.write_text(INITIAL_TASK_TEMPLATE, encoding="utf-8")

    msg = f"Вахта закрыта: {target_journal.name}"
    play_sound_and_notify("Лабораторный полигон", msg)


if __name__ == "__main__":
    main()
