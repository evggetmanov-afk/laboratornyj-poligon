#!/usr/bin/env python3
"""
container_gateway.py — Транзакционный распаковщик браузерных контейнеров (ADR-004).

Принимает поток данных из sys.stdin (pbpaste) или из переданного файла-аргумента.
Реализует трехфазную модель с истинным откатом (All-or-Nothing):
1. Валидация: regex-поиск маркеров (с защитой от NBSP), проверка схемы poly-container/v1,
   строгий Path.resolve().relative_to() и черный список путей.
2. Стейджинг: запись файлов во временную изолированную директорию .swap/tx_<timestamp>/.
3. Фиксация с откатом: создание бэкапов заменяемых файлов и атомарный перенос.
   При любом сбое выполняется полный реверсивный откат состояния на диске.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

SCHEMA_VERSION = "poly-container/v1"

# Регулярные выражения для маркеров с поддержкой неразрывных пробелов (\u00a0)
START_PATTERN = re.compile(r"===[ \t\u00a0]*START_CONTAINER[ \t\u00a0]*===")
END_PATTERN = re.compile(r"===[ \t\u00a0]*END_CONTAINER[ \t\u00a0]*===")

# Защищенные зоны репозитория
PROTECTED_CORE_DIRS = {"specs", "scripts"}
FORBIDDEN_ROOT_FILES = {"PROJECT_PASSPORT.md", "ROLES_REGISTRY.md", ".zshrc", ".bashrc", ".env"}
FORBIDDEN_SEGMENTS = {".git", ".swap", ".vscode", ".idea", ".DS_Store"}


def parse_container_text(raw_text: str) -> dict:
    """Извлекает и парсит JSON между строгими маркерами контейнера."""
    start_match = START_PATTERN.search(raw_text)
    if not start_match:
        raise ValueError("Маркер начала '=== START_CONTAINER ===' не найден во входном потоке.")

    end_match = END_PATTERN.search(raw_text, start_match.end())
    if not end_match:
        raise ValueError("Маркер окончания '=== END_CONTAINER ===' не найден во входном потоке.")

    json_payload = raw_text[start_match.end() : end_match.start()].strip()
    if not json_payload:
        raise ValueError("Тело контейнера между маркерами пустое.")

    try:
        data = json.loads(json_payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка парсинга JSON манифеста: {e}")

    if not isinstance(data, dict):
        raise ValueError("Корень манифеста должен быть JSON-объектом.")

    if data.get("schema") != SCHEMA_VERSION:
        raise ValueError(
            f"Неподдерживаемая схема: '{data.get('schema')}'. Ожидается: '{SCHEMA_VERSION}'."
        )

    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Поле 'files' должно быть непустым списком объектов.")

    return data


def validate_file_paths(files: list, allow_core: bool, repo_root: Path) -> list:
    """
    Фаза 1: Проверяет безопасность путей файлов пакета.
    Возвращает список проверенных кортежей: (относительный_путь, абсолютный_путь, content, executable).
    """
    validated = []
    repo_root_real = repo_root.resolve()

    for idx, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"Элемент files[{idx}] не является JSON-объектом.")

        rel_path = item.get("path")
        content = item.get("content")
        executable = bool(item.get("executable", False))

        if not rel_path or not isinstance(rel_path, str):
            raise ValueError(f"Элемент files[{idx}] содержит некорректный 'path'.")
        if content is None or not isinstance(content, str):
            raise ValueError(f"Элемент files[{idx}] ('{rel_path}') содержит некорректный 'content'.")

        rel_path_obj = Path(rel_path.strip())

        if rel_path_obj.is_absolute():
            raise ValueError(f"[SECURITY BLOCKED] Запрещен абсолютный путь: '{rel_path}'")

        # Строгая проверка выхода за корень репозитория через relative_to
        try:
            target_abs = (repo_root / rel_path_obj).resolve()
            normalized_rel = target_abs.relative_to(repo_root_real)
        except (ValueError, RuntimeError):
            raise ValueError(f"[SECURITY BLOCKED] Выход за границы репозитория: '{rel_path}'")

        parts = normalized_rel.parts
        if not parts:
            raise ValueError(f"[SECURITY BLOCKED] Попытка записи в корень репозитория: '{rel_path}'")

        # Защита от запрещенных сегментов в любой части пути
        for segment in parts:
            if segment in FORBIDDEN_SEGMENTS:
                raise ValueError(
                    f"[SECURITY BLOCKED] Запись в защищенную системную зону '{segment}' запрещена: '{rel_path}'"
                )

        # Защита корневых системных файлов
        if len(parts) == 1 and parts[0] in FORBIDDEN_ROOT_FILES:
            raise ValueError(f"[SECURITY BLOCKED] Изменение корневого системного файла запрещено: '{rel_path}'")

        # Защита каталогов ядра
        if parts[0] in PROTECTED_CORE_DIRS and not allow_core:
            raise ValueError(
                f"[CORE BLOCKED] Запись в ядро '{parts[0]}/' заблокирована. "
                f"Используйте флаг --allow-core для разблокировки: '{rel_path}'"
            )

        validated.append((normalized_rel, target_abs, content, executable))

    return validated


def process_container(input_stream_or_file: str, allow_core: bool) -> None:
    repo_root = Path.cwd().resolve()
    swap_dir = repo_root / ".swap"
    swap_dir.mkdir(parents=True, exist_ok=True)

    # 1. Чтение и парсинг
    manifest = parse_container_text(input_stream_or_file)
    task_name = manifest.get("task", "Без названия")
    files_list = manifest["files"]

    print(f"[*] Инициализация контейнера: '{task_name}'")
    print(f"[*] Файлов в манифесте: {len(files_list)}")

    # Фаза 1: Валидация всех путей
    validated_files = validate_file_paths(files_list, allow_core, repo_root)
    print("  [✓] Фаза 1 (Валидация путей и безопасности): УСПЕШНО")

    # Фаза 2: Стейджинг в буферную директорию
    tx_id = f"tx_{int(time.time() * 1000)}"
    staging_dir = swap_dir / tx_id
    staging_dir.mkdir(parents=True, exist_ok=False)
    backup_dir = staging_dir / "_backups"

    try:
        staging_map = []
        for rel_path, target_abs, content, executable in validated_files:
            stage_target = staging_dir / rel_path
            stage_target.parent.mkdir(parents=True, exist_ok=True)

            clean_body = content.rstrip("\r\n") + "\n"
            stage_target.write_text(clean_body, encoding="utf-8")

            if executable:
                current_mode = stage_target.stat().st_mode
                stage_target.chmod(current_mode | 0o111)

            staging_map.append((stage_target, target_abs, rel_path))

        print(f"  [✓] Фаза 2 (Стейджинг в {staging_dir.name}): УСПЕШНО")

        # Фаза 3: Фиксация с транзакционным откатом
        backups = []
        backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            for stage_target, target_abs, rel_path in staging_map:
                target_abs.parent.mkdir(parents=True, exist_ok=True)

                if target_abs.exists():
                    backup_copy = backup_dir / f"bak_{len(backups)}"
                    shutil.copy2(target_abs, backup_copy)
                    backups.append((backup_copy, target_abs))
                else:
                    backups.append((None, target_abs))

                os.replace(stage_target, target_abs)
                size = target_abs.stat().st_size
                print(f"   [+] Зафиксирован: {str(rel_path):<40} ({size:>6} байт)")

            print("  [✓] Фаза 3 (Фиксация All-or-Nothing): УСПЕШНО")
            print(f"[DONE] Контейнер успешно развернут. Обработано файлов: {len(validated_files)}")

        except Exception as commit_err:
            print(f"\n[CRITICAL ERROR] Сбой фиксации: {commit_err}. Запуск отката...", file=sys.stderr)
            for bak, original in reversed(backups):
                try:
                    if bak is not None and bak.exists():
                        os.replace(bak, original)
                    elif original.exists():
                        original.unlink(missing_ok=True)
                except Exception as rollback_err:
                    print(f"[FATAL] Ошибка отката для '{original}': {rollback_err}", file=sys.stderr)
            raise commit_err

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Транзакция отменена: {e}", file=sys.stderr)
        print("[!] Состояние репозитория сохранено без изменений.", file=sys.stderr)
        sys.exit(1)
    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Транзакционный распаковщик браузерных контейнеров CONTAINER (ADR-004)."
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Путь к файлу контейнера (если не передан — чтение из sys.stdin).",
    )
    parser.add_argument(
        "--allow-core",
        action="store_true",
        help="Разрешить запись в каталоги ядра (specs/, scripts/).",
    )

    args = parser.parse_args()

    try:
        if args.file:
            if not args.file.exists():
                print(f"[ERROR] Файл '{args.file}' не найден.", file=sys.stderr)
                sys.exit(1)
            raw_input = args.file.read_text(encoding="utf-8")
        else:
            if sys.stdin.isatty():
                print("[ERROR] sys.stdin пуст. Передайте данные через пайп (pbpaste | ...) или укажите файл.", file=sys.stderr)
                sys.exit(1)
            raw_input = sys.stdin.read()

        process_container(raw_input, allow_core=args.allow_core)

    except Exception as err:
        print(f"[ОТКАЗ] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()