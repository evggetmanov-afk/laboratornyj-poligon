#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

VAULT_ROOT = os.path.expanduser("~/Лабораторный_полигон")
STATE_FILE = os.path.join(VAULT_ROOT, "00_core_tools", ".current_project")

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, cwd=VAULT_ROOT, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR: {e.stderr.strip()}]"

def get_last_project():
    if os.path.isfile(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                name = f.read().strip()
                if os.path.isdir(os.path.join(VAULT_ROOT, "01_projects", name)):
                    return name
        except Exception:
            return None
    return None

def save_current_project(name):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(name.strip())
    except Exception as e:
        print(f"[WARN] Не удалось сохранить текущий проект: {e}")

def select_project():
    projects_dir = os.path.join(VAULT_ROOT, "01_projects")
    if not os.path.isdir(projects_dir):
        print(f"[ERR] Каталог проектов не найден: {projects_dir}")
        sys.exit(1)

    projects = [d for d in sorted(os.listdir(projects_dir)) if os.path.isdir(os.path.join(projects_dir, d)) and not d.startswith(".")]
    if not projects:
        print("[ERR] В 01_projects нет активных проектов.")
        sys.exit(1)

    last_proj = get_last_project()

    print("\nДоступные варианты:")
    if last_proj:
        print(f"  [0] Продолжить текущий: {last_proj} (по умолчанию)")
    
    for idx, p in enumerate(projects, 1):
        print(f"  [{idx}] {p}")

    default_prompt = " [0]" if last_proj else f" [1-{len(projects)}]"
    
    while True:
        raw = input(f"\nВыберите проект{default_prompt}: ").strip()
        
        # Нажатие Enter при наличии последнего проекта
        if raw == "" and last_proj:
            return last_proj
        
        if raw == "0" and last_proj:
            return last_proj
            
        if raw.isdigit() and 1 <= int(raw) <= len(projects):
            selected = projects[int(raw) - 1]
            save_current_project(selected)
            return selected
            
        print("Некорректный ввод, повторите.")

def build_handoff(project_name):
    proj_path = os.path.join(VAULT_ROOT, "01_projects", project_name)
    
    git_head = run_cmd("git log -n 1 --oneline")
    git_status = run_cmd(f"git status -s 01_projects/{project_name}")
    if not git_status:
        git_status = "[Чисто - незакоммиченных изменений нет]"

    proj_files = []
    for root, _, files in os.walk(proj_path):
        for f in files:
            if not f.startswith("."):
                rel = os.path.relpath(os.path.join(root, f), VAULT_ROOT)
                proj_files.append(rel)
    proj_files.sort()
    files_tree = "\n".join(f"- {f}" for f in proj_files)

    invariant_file = os.path.join(proj_path, "specs", "Invariant_ABC_Operational_Loop.md")
    invariant_excerpt = ""
    if os.path.isfile(invariant_file):
        with open(invariant_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            invariant_excerpt = "".join(lines[:18]).strip()

    handoff_text = f"""# КВАНТ ПЕРЕДАЧИ ВАХТЫ (WARM HANDOFF)
**Проект:** {project_name}
**Точка фиксации Git:** {git_head}

## 1. Физическое состояние на диске (APFS)
Статус изменений:
{git_status}

Файлы в контуре проекта:
{files_tree}

## 2. Действующий инвариант контура (Срез specs)
{invariant_excerpt}

---
**Инструкция для LLM:** Контекст инициализирован объективным срезом файловой системы. Никаких домыслов. Жди задачу оператора по текущему проекту."""

    return handoff_text

def copy_to_clipboard(text):
    if shutil.which("pbcopy"):
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=text)
        return True
    return False

def main():
    print("=== [⚙️ ЯДРО СИСТЕМЫ: ПЕРЕДАЧА ВАХТЫ] ===")
    project = select_project()
    handoff_payload = build_handoff(project)

    copied = copy_to_clipboard(handoff_payload)
    
    print("\n----------------------------------------")
    print(handoff_payload)
    print("----------------------------------------")
    
    if copied:
        print(f"\n✅ Проект '{project}' зафиксирован.")
        print("✅ Квант контекста скопирован в буфер обмена (Cmd + V)!")
        print("Откройте новый чат и вставьте снимок.")
    else:
        print("\n⚠️ pbcopy недоступен. Скопируйте текст выше вручную.")

if __name__ == "__main__":
    main()