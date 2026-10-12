#!/usr/bin/env python3
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path("/Users/getmanov/Лабораторный_полигон/00_core_tools")

REQUIRED_RAYCAST_FIELDS = [
    "@raycast.schemaVersion",
    "@raycast.title",
    "@raycast.mode",
    "@raycast.packageName",
    "@raycast.icon",
]

VALID_EXTENSIONS = {".py", ".sh"}


def check_script(file_path: Path) -> list[str]:
    errors = []

    # 1. Проверка прав на исполнение
    if not os.access(file_path, os.X_OK):
        errors.append("нет прав на исполнение (+x)")

    # 2. Проверка содержимого
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"ошибка чтения файла: {e}"]

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return ["файл пуст"]

    # 3. Проверка шебанга
    first_line = lines[0]
    if not first_line.startswith("#!"):
        errors.append(f"неверный шебанг ({first_line[:30]})")

    # 4. Проверка Raycast-метаданных (только если файл позиционируется как команда Raycast)
    is_raycast_command = any("@raycast." in line for line in lines)
    if is_raycast_command:
        for field in REQUIRED_RAYCAST_FIELDS:
            if not any(field in line for line in lines):
                errors.append(f"отсутствует поле {field}")

    return errors


def main():
    if not SCRIPTS_DIR.exists():
        print(f"❌ Директория не найдена: {SCRIPTS_DIR}")
        sys.exit(1)

    files = sorted(
        [
            f
            for f in SCRIPTS_DIR.iterdir()
            if f.is_file() and f.suffix in VALID_EXTENSIONS
        ]
    )

    print(f"=== Проверка скриптов в {SCRIPTS_DIR.name} (всего: {len(files)}) ===\n")

    has_errors = False
    for script in files:
        if script.name == "validate_scripts.py":
            print(f"[OK]   {script.name}")
            continue

        errors = check_script(script)
        if errors:
            has_errors = True
            print(f"[FAIL] {script.name}: {', '.join(errors)}")
        else:
            print(f"[OK]   {script.name}")

    print()
    if has_errors:
        print("❌ Обнаружены дефекты.")
        sys.exit(1)
    else:
        print("✅ Все скрипты соответствуют регламенту.")
        sys.exit(0)


if __name__ == "__main__":
    main()
