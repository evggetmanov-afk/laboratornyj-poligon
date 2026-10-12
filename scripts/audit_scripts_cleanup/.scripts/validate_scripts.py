#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Валидировать скрипты
# @raycast.mode fullOutput
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🔍

import os
from pathlib import Path

SCRIPTS_DIR = Path("/Users/getmanov/Лабораторный_полигон/.scripts")
REQUIRED_FIELDS = ["@raycast.schemaVersion", "@raycast.title", "@raycast.mode", "@raycast.packageName", "@raycast.icon"]

def validate():
    if not SCRIPTS_DIR.exists():
        print(f"[-] Каталог {SCRIPTS_DIR} не найден.")
        return

    files = sorted([f for f in SCRIPTS_DIR.iterdir() if f.is_file() and f.suffix in [".sh", ".py"]])
    print(f"=== Проверка скриптов в {SCRIPTS_DIR.name} (всего: {len(files)}) ===\n")

    has_errors = False

    for script in files:
        issues = []
        if not os.access(script, os.X_OK):
            issues.append("нет прав на исполнение (+x)")

        try:
            lines = script.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            print(f"[FAIL] {script.name}: ошибка чтения ({e})")
            has_errors = True
            continue

        if not lines:
            issues.append("файл пуст")
        else:
            first_line = lines[0].strip()
            if script.suffix == ".sh" and first_line != "#!/bin/bash":
                issues.append(f"неверный шебанг ({first_line})")
            elif script.suffix == ".py" and not (first_line.startswith("#!/") and "python" in first_line):
                issues.append(f"неверный шебанг ({first_line})")

        content = "\n".join(lines)
        for field in REQUIRED_FIELDS:
            if field not in content:
                issues.append(f"отсутствует поле {field}")

        if issues:
            print(f"[FAIL] {script.name}: {', '.join(issues)}")
            has_errors = True
        else:
            print(f"[OK]   {script.name}")

    print("\n" + ("❌ Обнаружены дефекты." if has_errors else "✅ Все скрипты соответствуют стандарту."))

if __name__ == "__main__":
    validate()
