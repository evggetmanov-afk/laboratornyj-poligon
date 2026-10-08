#!/usr/bin/env python3
import os
import sys
import re
import subprocess

def play_sound(sound_name):
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
    if os.path.exists(sound_path):
        subprocess.run(["afplay", sound_path], stderr=subprocess.DEVNULL)

def find_task_file():
    candidates = [
        "_draft/TASK.md",
        "00_core_tools/TASK_CORE.md",
        ".swap/TASK.md"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def verify_tasks(task_file):
    print(f"🔍 [РЕВИЗИЯ] Проверка физического наличия артефактов в: {task_file}")
    
    with open(task_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Ищем строки вида: - [x] ... `путь/к/файлу` или просто путь
    pattern_completed = re.compile(r"^\s*-\s*\[x\]\s*(.*)$")
    # Паттерн поиска файлов/путей (с обратными кавычками или без)
    pattern_file = re.compile(r"`([^`]+\.[a-zA-Z0-9_]+)`|([a-zA-Z0-9_\-\./А-Яа-я]+\.[a-zA-Z0-9_]+)")

    phantoms = []
    checked_count = 0

    for line_num, line in enumerate(lines, 1):
        match_done = pattern_completed.match(line)
        if match_done:
            content = match_done.group(1)
            # Ищем пути к файлам
            found_paths = []
            for m in pattern_file.finditer(content):
                path = m.group(1) or m.group(2)
                # Исключаем явный шум или расширения, не похожие на файлы
                if path and not path.startswith("http") and ("/" in path or path.endswith((".md", ".py", ".sh", ".json", ".yaml", ".yml"))):
                    found_paths.append(path)

            for raw_path in found_paths:
                checked_count += 1
                clean_path = raw_path.strip().strip("'\"")
                if not os.path.exists(clean_path):
                    phantoms.append((line_num, clean_path, content.strip()))

    if phantoms:
        print("\n❌ [АВАРИЯ: ОБНАРУЖЕНЫ СЛОВЕСНЫЕ ФАНТОМЫ!]")
        print("Галочка [x] стоит, но файл физически отсутствует на накопителе:\n")
        for num, path, desc in phantoms:
            print(f"  • Строка {num}: Файл '{path}' НЕ НАЙДЕН!")
            print(f"    Контекст: {desc}")
        print("\n🚫 Смена заблокирована. Запрещено передавать вахту с неподтвержденными артефактами.")
        play_sound("Basso")
        sys.exit(1)

    print(f"✅ [УСПЕХ] Проверено артефактов: {checked_count}. Все закрытые задачи физически подтверждены на SSD.")
    sys.exit(0)

if __name__ == "__main__":
    task_path = sys.argv[1] if len(sys.argv) > 1 else find_task_file()
    if not task_path:
        print("⚠️ Файл контракта задач (TASK.md) не найден.")
        sys.exit(0)
    verify_tasks(task_path)
