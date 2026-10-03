#!/usr/bin/env python3
import os
import sys
import subprocess
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CORE_DIR = os.path.join(BASE_DIR, "00_core_tools")
PROJECTS_DIR = os.path.join(BASE_DIR, "01_projects")
DRAFT_DIR = os.path.join(BASE_DIR, "_draft")
DRAFT_TASK = os.path.join(DRAFT_DIR, "TASK.md")

PROMPT_FILE = os.path.join(CORE_DIR, "SYSTEM_PROMPT.md")
CORE_TASK = os.path.join(CORE_DIR, "TASK_CORE.md")
CORE_JOURNAL = os.path.join(CORE_DIR, "JOURNAL_CORE.md")

SOUND_EFFECT = "/System/Library/Sounds/Pop.aiff"

def play_sound():
    if os.path.exists(SOUND_EFFECT):
        subprocess.run(["afplay", SOUND_EFFECT], stderr=subprocess.DEVNULL)

def copy_to_clipboard(text):
    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    process.communicate(text.encode("utf-8"))
    play_sound()

def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def extract_last_entry(content):
    if not content:
        return ""
    # Ищем разделы заголовков уровня ##
    parts = re.split(r'(?m)(?=^##\s+)', content)
    valid_parts = [p.strip() for p in parts if p.strip()]
    if not valid_parts:
        return content
    # Если первый кусок - вводный заголовок # Журнал..., берем следующий
    if len(valid_parts) > 1 and not valid_parts[0].startswith("##"):
        return valid_parts[1]
    return valid_parts[0]

def detect_current_context():
    if not os.path.exists(DRAFT_TASK):
        return ("core", "00_core_tools", CORE_TASK, CORE_JOURNAL)
    
    content = read_file(DRAFT_TASK)
    if "00_core_tools" in content or "Ядро" in content or "TASK_CORE" in content:
        return ("core", "00_core_tools", CORE_TASK, CORE_JOURNAL)
    
    # Поиск имени проекта в заголовке
    match = re.search(r'#\s+Контракт.*?:\s*([a-zA-Z0-9_\-]+)', content)
    if match:
        proj_name = match.group(1).strip()
        proj_path = os.path.join(PROJECTS_DIR, proj_name)
        if os.path.exists(proj_path):
            t_path = os.path.join(proj_path, "TASK.md")
            j_path = os.path.join(proj_path, "JOURNAL.md")
            return ("project", proj_name, t_path, j_path)
            
    # По умолчанию ядро
    return ("core", "00_core_tools", CORE_TASK, CORE_JOURNAL)

def assemble_warm_handoff():
    ctx_type, name, task_file, journal_file = detect_current_context()
    sys_prompt = read_file(PROMPT_FILE)
    active_task = read_file(DRAFT_TASK) or read_file(task_file)
    journal_content = read_file(journal_file)
    last_briefing = extract_last_entry(journal_content)
    
    package = []
    if sys_prompt:
        package.append(sys_prompt)
        package.append("\n---\n")
    
    package.append(f"# Оперативный контекст передачи смены: {name}\n")
    if active_task:
        package.append("## Актуальный контракт задачи\n")
        package.append(active_task)
        package.append("\n---\n")
        
    if last_briefing:
        package.append("## Последний зафиксированный брифинг из журнала\n")
        package.append(last_briefing)
        package.append("\n")
        
    final_text = "\n".join(package)
    copy_to_clipboard(final_text)
    print(f"\n[✓] Контекст '{name}' успешно собран (Warm Handoff) и скопирован в буфер!")

def assemble_cold_context(ctx_type, name, task_file, journal_file):
    sys_prompt = read_file(PROMPT_FILE)
    task_text = read_file(task_file)
    journal_text = read_file(journal_file)
    
    # Обновляем _draft/TASK.md
    os.makedirs(DRAFT_DIR, exist_ok=True)
    with open(DRAFT_TASK, "w", encoding="utf-8") as f:
        f.write(task_text)
        
    package = []
    if sys_prompt:
        package.append(sys_prompt)
        package.append("\n---\n")
    package.append(f"# Контекст [{name}]\n")
    if task_text:
        package.append(task_text)
        package.append("\n---\n")
    if journal_text:
        package.append(journal_text)
        
    final_text = "\n".join(package)
    copy_to_clipboard(final_text)
    print(f"\n[✓] Проект '{name}' активирован в _draft/TASK.md и скопирован в буфер!")

def main():
    # Проверка аргумента командной строки (например, 'вахта next')
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["next", "--next", "-n"]:
        assemble_warm_handoff()
        return

    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(DRAFT_DIR, exist_ok=True)
    
    _, current_name, _, _ = detect_current_context()
    
    projects = [d for d in sorted(os.listdir(PROJECTS_DIR)) 
                if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith(".")]
    
    print("\n" + "="*58)
    print("           🧭 ДИСПЕТЧЕР ВАХТЫ И ПЕРЕДАЧИ СМЕН")
    print("="*58)
    print(f" [Enter] 🔁 ПРОДОЛЖИТЬ ТЕКУЩИЙ: [{current_name}] (Warm Handoff)")
    print("-" * 58)
    print("  0) [ ⚙️ ЯДРО СИСТЕМЫ: 00_core_tools ]")
    
    for idx, p in enumerate(projects, start=1):
        print(f"  {idx}) {p}")
        
    print("  +) [ ➕ Создать новый проект ]")
    print("="*58)
    
    choice = input("\nВыберите действие [по умолчанию Enter]: ").strip()
    
    if choice == "":
        assemble_warm_handoff()
    elif choice == "0":
        assemble_cold_context("core", "00_core_tools", CORE_TASK, CORE_JOURNAL)
    elif choice == "+":
        new_name = input("Введите имя нового проекта: ").strip()
        if new_name:
            p_path = os.path.join(PROJECTS_DIR, new_name)
            os.makedirs(p_path, exist_ok=True)
            t_file = os.path.join(p_path, "TASK.md")
            j_file = os.path.join(p_path, "JOURNAL.md")
            if not os.path.exists(t_file):
                with open(t_file, "w", encoding="utf-8") as f:
                    f.write(f"# Контракт проекта: {new_name}\n\n## Текущий квант\n- [ ] Инициализация проекта\n")
            if not os.path.exists(j_file):
                with open(j_file, "w", encoding="utf-8") as f:
                    f.write(f"# Журнал проекта: {new_name}\n\n## [{new_name}] Старт проекта\n- Проект создан.\n")
            assemble_cold_context("project", new_name, t_file, j_file)
    else:
        try:
            val = int(choice)
            if 1 <= val <= len(projects):
                target = projects[val - 1]
                p_path = os.path.join(PROJECTS_DIR, target)
                assemble_cold_context("project", target, os.path.join(p_path, "TASK.md"), os.path.join(p_path, "JOURNAL.md"))
            else:
                print("[!] Неверный номер проекта.")
        except ValueError:
            print("[!] Некорректный ввод.")

if __name__ == "__main__":
    main()
