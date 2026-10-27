#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
scripts/vahta.py
Утилита управления рабочими сменами (вахтами), состоянием задачи
и автоматической фиксацией контекста в буфер обмена и Git.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SWAP_DIR = BASE_DIR / ".swap"
TASK_FILE = SWAP_DIR / "task.md"


def play_sound(sound_name: str):
    sound_path = Path(f"/System/Library/Sounds/{sound_name}.aiff")
    if sound_path.exists():
        subprocess.run(
            ["afplay", str(sound_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def set_clipboard(text: str):
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(text.encode("utf-8"))
    except Exception as e:
        print(f"⚠️ Ошибка копирования в буфер: {e}", file=sys.stderr)


def get_git_status() -> str:
    try:
        res = subprocess.run(
            ["git", "status", "--short"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "git status недоступен"


def open_shift():
    SWAP_DIR.mkdir(parents=True, exist_ok=True)
    if not TASK_FILE.exists():
        TASK_FILE.write_text(
            "# ТАКТИЧЕСКИЙ КОНТРАКТ ЗАДАЧИ\n\n## Цель:\n\n## DoD:\n",
            encoding="utf-8",
        )

    context_payload = f"""# КОНТЕКСТ ВАХТЫ: ЛАБОРАТОРНЫЙ ПОЛИГОН
- Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Ветка Git: main
- Активный стандарт: Правило 6 Паспорта (snake_case, без кириллицы/пробелов в путях кода).

ЖЕСТКИЙ ИНВАРИАНТ ГЕНЕРАЦИИ АРТЕФАКТОВ:
1. Модель отдает сохраняемые файлы монолитным блоком.
2. Первая строка блока СТРОГО: ### FILE: <относительный_путь>
3. Запрещено указывать имя файла в команде терминала.
4. Вызов оператора в терминале ВСЕГДА только: save
5. Команды выдавать строго по отдельности, без && и без heredoc.
"""
    set_clipboard(context_payload)
    play_sound("Glass")
    print("✅ [OPEN] Контекст вахты скопирован в буфер обмена.")
    print(f"Инициализирован/проверен {TASK_FILE}")


def status_shift():
    print(f"📍 Репозиторий: {BASE_DIR}")
    if TASK_FILE.exists():
        print(f"📄 Контракт задачи ({TASK_FILE}):")
        content = TASK_FILE.read_text(encoding="utf-8").strip()
        print(content if content else "[Контракт пуст]")
    else:
        print("⚠️ Контракт .swap/task.md отсутствует.")

    print("\n📦 Состояние Git:")
    git_st = get_git_status()
    if git_st:
        print(git_st)
    else:
        print("Рабочее дерево чистое.")


def close_shift():
    git_st = get_git_status()
    if not git_st:
        print("ℹ️ Нет изменений для фиксации в Git.")
        play_sound("Tink")
        return

    commit_msg = f"vahta: auto-close shift {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=True)
        play_sound("Glass")
        print(f"✅ [CLOSE] Смена зафиксирована коммитом: {commit_msg}")
    except subprocess.CalledProcessError as e:
        play_sound("Sosumi")
        print(f"❌ Ошибка коммита: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 scripts/vahta.py [open|status|close]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "open":
        open_shift()
    elif cmd == "status":
        status_shift()
    elif cmd == "close":
        close_shift()
    else:
        print(f"Неизвестная команда: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()