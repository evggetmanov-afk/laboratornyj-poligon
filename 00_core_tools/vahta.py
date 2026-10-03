#!/usr/bin/env python3
import os
import re
import glob
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FILE = os.path.join(REPO_ROOT, "00_core_tools", "prompts", "Системный_промпт_взаимодействия.md")
PROJECTS_DIR = os.path.join(REPO_ROOT, "01_projects")
DRAFT_DIR = os.path.join(REPO_ROOT, "_draft")
DRAFT_TASK_FILE = os.path.join(DRAFT_DIR, "TASK.md")


def get_available_projects():
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        return []
    items = sorted(os.listdir(PROJECTS_DIR))
    projects = [item for item in items if os.path.isdir(os.path.join(PROJECTS_DIR, item)) and not item.startswith(".")]
    return projects


def select_or_create_project(projects):
    print("\n================ ВАХТА: ВЫБОР КОНТЕКСТА ================")
    for idx, project in enumerate(projects, 1):
        print(f"{idx}) {project}")
    new_idx = len(projects) + 1
    print(f"{new_idx}) [ + Создать новый проект ]")
    print("--------------------------------------------------------")

    choice = input(f"Выберите проект [1-{new_idx}] (по умолчанию 1): ").strip()
    if not choice:
        choice = "1"

    try:
        choice_idx = int(choice)
        if 1 <= choice_idx <= len(projects):
            return projects[choice_idx - 1]
        elif choice_idx == new_idx:
            new_name = input("Введите имя нового проекта (например, tennis_blitz): ").strip()
            new_name = re.sub(r'[^a-zA-Z0-9_\-а-яА-Я]', '_', new_name)
            if not new_name:
                print("Имя не может быть пустым. Отмена.")
                sys.exit(1)
            project_path = os.path.join(PROJECTS_DIR, new_name)
            os.makedirs(os.path.join(project_path, "journal"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "tasks"), exist_ok=True)
            
            init_task = f"# Контракт задачи проекта: {new_name}\n\n## Цель\n- Сформировать базовую постановку.\n"
            with open(os.path.join(project_path, "tasks", "TASK.md"), "w", encoding="utf-8") as f:
                f.write(init_task)
            print(f"✅ Проект '{new_name}' успешно инициализирован.")
            return new_name
    except ValueError:
        pass

    print("Некорректный ввод. Выбран проект по умолчанию.")
    return projects[0] if projects else None


def get_latest_journal_entries(project_dir):
    journal_dir = os.path.join(project_dir, "journal")
    search_dirs = [journal_dir, project_dir]

    files = []
    for d in search_dirs:
        if os.path.exists(d):
            files.extend(glob.glob(os.path.join(d, "Журнал *.md")))
            files.extend(glob.glob(os.path.join(d, "ВЕХА_*.md")))

    journal_files = sorted(list(set(files)))
    total_files = len(journal_files)

    if not journal_files:
        return "", total_files

    latest_file = journal_files[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r'(?m)^(?=#{2,3}\s)', content)
    header = sections[0] if sections and not sections[0].startswith('#') else ""
    entries = [s for s in sections if s.startswith('#')]

    tail_entries = entries[-4:] if len(entries) >= 4 else entries
    result_text = header.strip() + "\n\n" + "".join(tail_entries).strip()
    return result_text, total_files


def sync_and_get_task_contract(project_name, project_dir):
    os.makedirs(DRAFT_DIR, exist_ok=True)
    project_task_file = os.path.join(project_dir, "tasks", "TASK.md")
    if not os.path.exists(project_task_file):
        root_task = os.path.join(project_dir, "TASK.md")
        if os.path.exists(root_task):
            project_task_file = root_task

    task_content = ""
    if os.path.exists(project_task_file):
        with open(project_task_file, "r", encoding="utf-8") as f:
            task_content = f.read().strip()

    # Синхронизируем текущий фокус в _draft/TASK.md
    with open(DRAFT_TASK_FILE, "w", encoding="utf-8") as f:
        header = f"# [АКТИВНЫЙ ПРОЕКТ: {project_name}]\n\n"
        f.write(header + task_content)

    return task_content


def main():
    projects = get_available_projects()
    if not projects:
        selected_project = select_or_create_project([])
    else:
        selected_project = select_or_create_project(projects)

    project_dir = os.path.join(PROJECTS_DIR, selected_project)

    prompt_text = ""
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_text = f.read().strip()

    journal_text, total_journals = get_latest_journal_entries(project_dir)
    task_contract = sync_and_get_task_contract(selected_project, project_dir)

    reminders = []
    if total_journals > 7:
        reminders.append(f"💡 В журнале проекта накопилось {total_journals} файлов. Рекомендуется ревизия.")

    reminders_block = ""
    if reminders:
        reminders_block = "\n\n---\n### 🔔 Напоминания проекта\n" + "\n".join(reminders)

    task_block = ""
    if task_contract:
        task_block = f"\n\n---\n\n# Оперативный контракт кванта ({selected_project})\n\n{task_contract}"

    cheat_sheet = """
---
### 🧭 Памятка команд:
* **«Делаем»** — применить предложенный код / команду в терминале.
* **«==»** — подтвердить успешное выполнение без ошибок.
* **«Сдать смену»** — сохранить в Git и зафиксировать прогресс вехи.
"""

    final_payload = f"{prompt_text}{task_block}\n\n---\n\n# Контекст проекта [{selected_project}]\n\n{journal_text}{reminders_block}{cheat_sheet}"

    # Копирование в буфер обмена macOS
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(final_payload.encode('utf-8'))

    # Звуковой сигнал
    os.system("afplay /System/Library/Sounds/Pop.aiff")

    print(f"\n✅ Контекст вахты для проекта '{selected_project}' собран в буфер обмена.")
    if reminders:
        print("\n" + "\n".join(reminders))


if __name__ == "__main__":
    main()
