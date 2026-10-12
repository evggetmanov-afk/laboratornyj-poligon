#!/usr/bin/env python3
import os
import re
import glob
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FILE = os.path.join(REPO_ROOT, "Система", "Промпты", "Системный_промпт_взаимодействия.md")
JOURNAL_DIR = os.path.join(REPO_ROOT, "Вахтенный_журнал")
TASK_FILE = os.path.join(REPO_ROOT, ".swap", "TASK.md")
INCIDENTS_DIR = REPO_ROOT

def get_latest_journal_entries():
    # Ищем как регулярные журналы, так и файлы закрытых вех
    files = glob.glob(os.path.join(JOURNAL_DIR, "Журнал *.md")) + glob.glob(os.path.join(JOURNAL_DIR, "ВЕХА_*.md"))
    journal_files = sorted(files)
    total_files = len(journal_files)

    if not journal_files:
        return "", total_files

    latest_file = journal_files[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Разбиваем по заголовкам записей (## или ###)
    sections = re.split(r'(?m)^(?=#{2,3}\s)', content)
    header = sections[0] if sections and not sections[0].startswith('#') else ""
    entries = [s for s in sections if s.startswith('#')]

    # Берем последние 3-4 блока
    tail_entries = entries[-4:] if len(entries) >= 4 else entries
    result_text = header.strip() + "\n\n" + "".join(tail_entries).strip()
    return result_text, total_files

def get_task_contract():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def count_incidents():
    incident_files = glob.glob(os.path.join(INCIDENTS_DIR, "Инциденты *.md"))
    total_incidents = 0
    for file_path in incident_files:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("## ") or line.startswith("### ") or "Сбой" in line or "Ошибка" in line:
                    total_incidents += 1
    return total_incidents

def main():
    prompt_text = ""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()

    journal_text, total_journals = get_latest_journal_entries()
    task_contract = get_task_contract()
    total_incidents = count_incidents()

    reminders = []
    if total_journals > 7:
        reminders.append(f"💡 В журнале накопилось {total_journals} файлов. Чтобы навести порядок, напиши: «Проводим ревизию»")
    if total_incidents > 3:
        reminders.append(f"⚠️ В логах зафиксировано {total_incidents} записей об инцидентах. Чтобы устранить причины, напиши: «Разбираем ошибки»")

    reminders_block = ""
    if reminders:
        reminders_block = "\n\n---\n### 🔔 Системные напоминания\n" + "\n".join(reminders)

    task_block = ""
    if task_contract:
        task_block = f"\n\n---\n\n# Оперативный контракт кванта (.swap/TASK.md)\n\n{task_contract}"

    cheat_sheet = """
---
### 🧭 Памятка команд:
* **«Делаем»** — применить предложенный код / команду в терминале.
* **«==»** — подтвердить успешное выполнение без ошибок.
* **«Сдать смену»** — сохранить в Git, пройти Remote Guard и обновить контекст.
"""

    final_payload = f"{prompt_text}{task_block}\n\n---\n\n# Оперативный контекст вахты\n\n{journal_text}{reminders_block}{cheat_sheet}"

    # Копирование в буфер обмена macOS
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(final_payload.encode('utf-8'))

    # Звуковой сигнал
    os.system("afplay /System/Library/Sounds/Pop.aiff")

    print("✅ Контекст вахты скопирован в буфер обмена.")
    if reminders:
        print("\n" + "\n".join(reminders))

if __name__ == "__main__":
    main()
