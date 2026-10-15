#!/usr/bin/env python3
"""
apply_payload.py — детерминированный исполнитель развертывания файлов из задач LLM.
Использование:
    python3 apply_payload.py                  # читает .swap/TASK.md
    python3 apply_payload.py tasks/task1.md   # читает указанный файл задачи
"""

import os
import re
import sys
from pathlib import Path

DEFAULT_TASK_FILE = Path(".swap/TASK.md")

# Регулярное выражение для захвата пути и содержимого
BLOCK_PATTERN = re.compile(
    r"<<<FILE_PATH:\s*([^\r\n]+)\r?\n(.*?)<<<FILE_CONTENT_END>>>",
    re.DOTALL
)

def apply_task(task_file: Path) -> None:
    if not task_file.exists():
        print(f"[ERROR] Файл задачи '{task_file}' не найден.", file=sys.stderr)
        sys.exit(1)

    try:
        content = task_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Не удалось прочитать '{task_file}': {e}", file=sys.stderr)
        sys.exit(1)

    matches = BLOCK_PATTERN.findall(content)
    if not matches:
        print(f"[ERROR] В файле '{task_file}' не найдено блоков <<<FILE_PATH: ...>>>", file=sys.stderr)
        sys.exit(1)

    cwd = Path.cwd().resolve()
    processed_files = []

    print(f"[*] Обработка задачи: {task_file} (найдено файлов: {len(matches)})")

    for rel_path_raw, file_body in matches:
        rel_path_str = rel_path_raw.strip()
        target_path = Path(rel_path_str)

        # 1. Проверка безопасности (Path Traversal)
        try:
            resolved_target = (cwd / target_path).resolve()
            if not str(resolved_target).startswith(str(cwd)):
                print(f"[SECURITY BLOCKED] Попытка записи вне рабочей директории: {rel_path_str}", file=sys.stderr)
                continue
        except Exception as e:
            print(f"[ERROR] Некорректный путь '{rel_path_str}': {e}", file=sys.stderr)
            continue

        # 2. Создание родительских папок (любой глубины вложенности)
        resolved_target.parent.mkdir(parents=True, exist_ok=True)

        # 3. Атомарная запись через временный файл
        tmp_target = resolved_target.with_suffix(resolved_target.suffix + ".atomic.tmp")
        try:
            # Нормализация: убираем лишний хвостовой перевод строк, оставляем строго один \n в конце
            clean_body = file_body.rstrip("\r\n") + "\n"
            tmp_target.write_text(clean_body, encoding="utf-8")
            tmp_target.replace(resolved_target)  # Атомарный перенос
        except Exception as e:
            if tmp_target.exists():
                tmp_target.unlink()
            print(f"[ERROR] Ошибка записи '{rel_path_str}': {e}", file=sys.stderr)
            continue

        # 4. Проверка и фиксация размера
        size_bytes = resolved_target.stat().st_size
        processed_files.append((rel_path_str, size_bytes))
        print(f"  [+] Записан: {rel_path_str:<40} ({size_bytes:>6} байт)")

    print(f"[DONE] Успешно зафиксировано на диске файлов: {len(processed_files)}.")

if __name__ == "__main__":
    task_file_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TASK_FILE
    apply_task(task_file_arg)