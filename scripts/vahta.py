#!/usr/bin/env python3
"""
Скрипт управления сменами (вахтой) Лабораторного полигона.
Управляет шлюзом .swap/, архивирует контракты в watch_log/,
собирает контекст в системный буфер (pbcopy) и фиксирует коммиты в Git.
"""

import os
import sys
import glob
import shutil
import subprocess
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROMPT_FILE = os.path.join(ROOT_DIR, "project_passport.md")
JOURNAL_DIR = os.path.join(ROOT_DIR, "watch_log")
SWAP_DIR = os.path.join(ROOT_DIR, ".swap")
TASK_FILE = os.path.join(SWAP_DIR, "task.md")
TASK_TEMPLATE = os.path.join(SWAP_DIR, "task_template.md")

REMINDER_TEXT = """---
### 🧭 Триггеры управления:
- **«Думай»** — архитектура, риски, формулирование контракта (Read-Only).
- **«Делай»** — диспетчеризация конвейера, атомарные шаги Zsh, запись .swap/task.md.
- **«Пиши код»** / **«Генерируй файл»** — санкция на генерацию монолита под утилиту save.
- **«Сдать смену»** — регламент консервации и фиксации вахты в Git.
"""

def play_sound(sound_name="Pop.aiff"):
    sound_path = f"/System/Library/Sounds/{sound_name}"
    if os.path.exists(sound_path):
        os.system(f"afplay {sound_path}")

def ensure_dirs():
    os.makedirs(SWAP_DIR, exist_ok=True)
    os.makedirs(JOURNAL_DIR, exist_ok=True)

def get_latest_watch_entries():
    files = sorted(glob.glob(os.path.join(JOURNAL_DIR, "*_task_closed.md")))
    if not files:
        return "", 0
    latest_file = files[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return content, len(files)

def get_task_contract():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def open_shift():
    ensure_dirs()
    timestamp_display = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt_text = ""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()

    task_content = get_task_contract()
    if not task_content or "СТАТУС ВАХТЫ" in task_content:
        task_content = f"""# КВАНТ РАБОТЫ: Новая задача
Дата открытия: {timestamp_display}

## 1. СКОУП
- Изменять: 
- Только чтение: 

## 2. КОНТРАКТ
- [Спецификация входов, выходов, инвариантов]

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки: 
- Ожидаемый результат: 

## 4. СТАТУС
- IN_PROGRESS

{REMINDER_TEXT}"""
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            f.write(task_content)

    latest_log, total_logs = get_latest_watch_entries()

    task_block = f"\n\n---\n\n# Оперативный контракт кванта (.swap/task.md)\n\n{task_content}"
    watch_block = f"\n\n---\n\n# Оперативный контекст вахты\n\n{latest_log if latest_log else 'История смен пуста.'}\n\n{REMINDER_TEXT}"

    final_payload = f"{prompt_text}{task_block}{watch_block}"

    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    process.communicate(final_payload.encode("utf-8"))

    play_sound("Pop.aiff")
    print("✅ [OPEN] Контекст вахты скопирован в буфер обмена.")
    print(f"Инициализирован/проверен {TASK_FILE}")

def close_shift():
    ensure_dirs()
    if not os.path.exists(TASK_FILE):
        print("Файл .swap/task.md не найден. Нечего закрывать.")
        return

    with open(TASK_FILE, "r", encoding="utf-8") as f:
        task_content = f.read().strip()

    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_display = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    archive_file = os.path.join(JOURNAL_DIR, f"{timestamp_file}_task_closed.md")
    shutil.copy2(TASK_FILE, archive_file)

    summary_status = f"""# СТАТУС ВАХТЫ
- Смена закрыта: {timestamp_display}
- Архив смены: {os.path.relpath(archive_file, ROOT_DIR)}
- Ядро и .swap/ сохранены.

{REMINDER_TEXT}"""
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        f.write(summary_status)

    subprocess.run(["git", "add", archive_file, TASK_FILE], cwd=ROOT_DIR, check=False)
    commit_msg = f"chore(watch_log): close shift {timestamp_file}"
    commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT_DIR, capture_output=True, text=True)

    play_sound("Glass.aiff")
    print("✅ [CLOSE] Смена успешно закрыта.")
    print(f"📝 Слепок сохранен: {os.path.relpath(archive_file, ROOT_DIR)}")
    if commit_res.returncode == 0:
        print(f"🔒 Зафиксирован коммит: {commit_msg}")
    else:
        print(f"ℹ️ Git status: {commit_res.stdout.strip() or commit_res.stderr.strip()}")

def main():
    if len(sys.argv) < 2:
        print("Использование: vahta.py [open|close|status]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "open":
        open_shift()
    elif cmd == "close":
        close_shift()
    elif cmd == "status":
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("Нет активной вахты (.swap/task.md отсутствует).")
    else:
        print(f"Неизвестная команда: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()