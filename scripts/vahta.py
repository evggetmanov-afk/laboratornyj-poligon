#!/usr/bin/env python3
import os
import sys
import re
import glob
import shutil
import datetime
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FILE = os.path.join(REPO_ROOT, "PROJECT_PASSPORT.md")
JOURNAL_DIR = os.path.join(REPO_ROOT, "watch_log")
SWAP_DIR = os.path.join(REPO_ROOT, ".swap")
TASK_FILE = os.path.join(SWAP_DIR, "TASK.md")
TASK_TEMPLATE = os.path.join(SWAP_DIR, "TASK_TEMPLATE.md")
SWAP_ARCHIVE_DIR = os.path.join(SWAP_DIR, "archive")
INCIDENTS_DIR = JOURNAL_DIR


def play_sound(sound_name="Pop.aiff"):
    sound_path = f"/System/Library/Sounds/{sound_name}"
    if os.path.exists(sound_path):
        os.system(f"afplay {sound_path}")


def get_latest_journal_entries():
    files = glob.glob(os.path.join(JOURNAL_DIR, "journal_*.md")) + glob.glob(
        os.path.join(JOURNAL_DIR, "milestone_*.md")
    )
    journal_files = sorted(files)
    total_files = len(journal_files)

    if not journal_files:
        return "", total_files

    latest_file = journal_files[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"(?m)^(?=#{2,3}\s)", content)
    header = sections[0] if sections and not sections[0].startswith("#") else ""
    entries = [s for s in sections if s.startswith("#")]

    tail_entries = entries[-4:] if len(entries) >= 4 else entries
    result_text = header.strip() + "\n\n" + "".join(tail_entries).strip()
    return result_text, total_files


def get_task_contract():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def count_incidents():
    incident_files = glob.glob(os.path.join(INCIDENTS_DIR, "incident_*.md"))
    total_incidents = 0
    for file_path in incident_files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if (
                    line.startswith("## ")
                    or line.startswith("### ")
                    or "Сбой" in line
                    or "Ошибка" in line
                ):
                    total_incidents += 1
    return total_incidents


def open_shift():
    prompt_text = ""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()

    journal_text, total_journals = get_latest_journal_entries()
    task_contract = get_task_contract()
    total_incidents = count_incidents()

    reminders = []
    if total_journals > 7:
        reminders.append(
            f"💡 В журнале накопилось {total_journals} файлов. Чтобы навести порядок, напиши: «Проводим ревизию»"
        )
    if total_incidents > 3:
        reminders.append(
            f"⚠️ В логах зафиксировано {total_incidents} записей об инцидентах. Чтобы устранить причины, напиши: «Разбираем ошибки»"
        )

    reminders_block = ""
    if reminders:
        reminders_block = "\n\n---\n### 🔔 Системные напоминания\n" + "\n".join(reminders)

    task_block = ""
    if task_contract:
        task_block = f"\n\n---\n\n# Оперативный контракт кванта (.swap/TASK.md)\n\n{task_contract}"

    cheat_sheet = """
---
### 🧭 Памятка триггеров управления (Пункт 9 Паспорта):
- **«напиши код»** / **«дай скрипт»** / **«делай»** — снятие защитного барьера для выдачи кода.
- **«дай команду»** — запрос на генерацию терминальных команд.
- **«Сдать смену»** — формирование отчета закрытия вахты и фиксация в Git.
"""

    final_payload = (
        f"{prompt_text}{task_block}\n\n---\n\n"
        f"# Оперативный контекст вахты\n\n{journal_text}{reminders_block}{cheat_sheet}"
    )

    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    process.communicate(final_payload.encode("utf-8"))

    play_sound("Pop.aiff")
    print("✅ [OPEN] Контекст вахты скопирован в буфер обмена.")
    if reminders:
        print("\n" + "\n".join(reminders))


def close_shift():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y_%m_%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs(JOURNAL_DIR, exist_ok=True)
    os.makedirs(SWAP_ARCHIVE_DIR, exist_ok=True)

    today_journals = sorted(glob.glob(os.path.join(JOURNAL_DIR, f"journal_{date_str}_*.md")))
    next_num = len(today_journals) + 1
    new_journal_name = f"journal_{date_str}_{next_num:02d}.md"
    new_journal_path = os.path.join(JOURNAL_DIR, new_journal_name)

    task_content = ""
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            task_content = f.read().strip()

    journal_entry = f"""# ЖУРНАЛ СМЕНЫ: journal_{date_str}_{next_num:02d}
*Закрыто:* {timestamp_str}

---

## 1. ВЫПОЛНЕННЫЙ КОНТРАКТ
{task_content if task_content else "Контракт не был зафиксирован в .swap/TASK.md"}

---

## 2. СТАТУС ВАХТЫ
- Смена закрыта через vahta.py close.
- Ядро и .swap/ сохранены.
"""
    with open(new_journal_path, "w", encoding="utf-8") as f:
        f.write(journal_entry)

    if task_content:
        archived_task_name = f"task_{date_str}_{next_num:02d}.md"
        archived_task_path = os.path.join(SWAP_ARCHIVE_DIR, archived_task_name)
        with open(archived_task_path, "w", encoding="utf-8") as f:
            f.write(task_content)

    if os.path.exists(TASK_TEMPLATE):
        shutil.copy(TASK_TEMPLATE, TASK_FILE)
    else:
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            f.write("# ТЕКУЩИЙ КОНТРАКТ ЗАДАЧИ\n\n## 1. ЦЕЛЬ\n- \n\n## 2. ШАГИ\n- [ ] \n")

    play_sound("Glass.aiff")
    print(f"✅ [CLOSE] Смена успешно закрыта.")
    print(f"📝 Журнал сохранен: {os.path.relpath(new_journal_path, REPO_ROOT)}")
    print(f"🛡️  Каталог .swap/ сохранен, TASK.md сброшен к исходному шаблону.")
    print("\nСтатус Git:")
    subprocess.run(["git", "status", "-s"])


def main():
    command = "open"
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

    if command in ["open", "start", "b"]:
        open_shift()
    elif command in ["close", "stop", "end"]:
        close_shift()
    else:
        print(f"Неизвестная команда: {command}")
        print("Использование:")
        print("  python3 scripts/vahta.py open   # Собрать контекст вахты в буфер")
        print("  python3 scripts/vahta.py close  # Закрыть смену, архивировать контракт и обновить журнал")


if __name__ == "__main__":
    main()
