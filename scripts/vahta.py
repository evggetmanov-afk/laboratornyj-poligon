#!/usr/bin/env python3
import os
import subprocess
import shutil

# Автоматически определяем корень репозитория на уровень выше папки scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, cwd=VAULT_ROOT, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR: {e.stderr.strip()}]"

def build_handoff():
    git_head = run_cmd("git log -n 1 --oneline")
    git_status = run_cmd("git status -s")
    if not git_status:
        git_status = "[Чисто - незакоммиченных изменений нет]"

    files = []
    for root, _, filenames in os.walk(VAULT_ROOT):
        if ".git" in root or "_quarantine" in root:
            continue
        for f in filenames:
            if not f.startswith("."):
                rel = os.path.relpath(os.path.join(root, f), VAULT_ROOT)
                files.append(rel)
    files.sort()
    files_tree = "\n".join(f"- {f}" for f in files)

    handoff_text = f"""# КВАНТ ПЕРЕДАЧИ ВАХТЫ (WARM HANDOFF)
**Точка фиксации Git:** {git_head}

## 1. Физическое состояние на диске (APFS)
Статус изменений:
{git_status}

Файлы в репозитории:
{files_tree}

---
**Инструкция для LLM:** Контекст инициализирован объективным срезом файловой системы. Никаких домыслов. Жди задачу оператора."""

    return handoff_text

def copy_to_clipboard(text):
    if shutil.which("pbcopy"):
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=text)
        return True
    return False

def main():
    print("=== [⚙️ УПРОЩЕННОЕ ЯДРО: ПЕРЕДАЧА ВАХТЫ] ===")
    handoff_payload = build_handoff()
    copied = copy_to_clipboard(handoff_payload)
    
    print("\n----------------------------------------")
    print(handoff_payload)
    print("----------------------------------------")
    
    if copied:
        print("\n✅ Квант контекста скопирован в буфер обмена (Cmd + V)!")
    else:
        print("\n⚠️ pbcopy недоступен.")

if __name__ == "__main__":
    main()
