#!/usr/bin/env python3
"""
scripts/mirror.py
Генератор монолитного снимка ядра Лабораторного полигона (SNAPSHOT.md)
для синхронизации со вторым контуром (Google Диск / AI_Mirror).
"""

import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Целевой путь ко второму контуру на Google Диске
MIRROR_DIR = Path.home() / (
    "Library/CloudStorage/GoogleDrive-evg.getmanov@gmail.com/Мой диск/AI_Mirror"
)

# Разрешенные расширения текстовых исходников
ALLOWED_EXTENSIONS = {".md", ".py", ".sh", ".json", ".yaml", ".yml"}

# Корневые файлы ядра
ROOT_FILES = [
    "project_passport.md",
    "roles_registry.md",
]

# Целевые директории для сбора
INCLUDE_DIRS = [
    "docs",
    "specs",
    "roles",
    "methodology",
    "projects",
    ".swap",
    "scripts",
]

# Исключаемые каталоги и паттерны
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "node_modules",
}

EXCLUDE_FILES = {
    ".DS_Store",
}


def should_include_file(file_path: Path) -> bool:
    if file_path.name in EXCLUDE_FILES:
        return False
    if file_path.name.startswith("._"):
        return False
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False
    # Отсечение скрытых служебных файлов внутри директорий кроме .swap
    parts = file_path.parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return False
    return True


def collect_target_files(base_dir: Path) -> list[Path]:
    collected: list[Path] = []

    # 1. Корневые файлы
    for root_file_name in ROOT_FILES:
        rf = base_dir / root_file_name
        if rf.is_file():
            collected.append(rf)

    # 2. Файлы из целевых директорий
    for d_name in INCLUDE_DIRS:
        dir_path = base_dir / d_name
        if not dir_path.is_dir():
            continue
        for root, dirs, files in os.walk(dir_path):
            # Модифицируем dirs in-place для предотвращения захода в черные списки
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in sorted(files):
                full_path = Path(root) / f
                if should_include_file(full_path):
                    collected.append(full_path)

    # Убираем дубликаты с сохранением порядка сортировки
    seen = set()
    deduped = []
    for item in sorted(collected):
        if item not in seen:
            seen.add(item)
            deduped.append(item)

    return deduped


def build_snapshot(base_dir: Path, files: list[Path], timestamp: str) -> str:
    lines = [
        "# SNAPSHOT СИСТЕМЫ: ЛАБОРАТОРНЫЙ ПОЛИГОН",
        f"- **Метка времени:** {timestamp}",
        f"- **Базовый путь:** `{base_dir}`",
        f"- **Всего файлов в ядре:** {len(files)}",
        "",
        "## ОГЛАВЛЕНИЕ СНИМКА",
    ]

    for f in files:
        rel_path = f.relative_to(base_dir)
        lines.append(f"- `{rel_path}`")

    lines.append("\n---\n")

    for f in files:
        rel_path = f.relative_to(base_dir)
        lines.append(f"## ФАЙЛ: `{rel_path}`")
        lines.append(f"```text")
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            lines.append(content)
        except Exception as e:
            lines.append(f"[ОШИБКА ЧТЕНИЯ ФАЙЛА: {e}]")
        lines.append("```\n")

    return "\n".join(lines)


def build_prompt_audit(timestamp: str, files_count: int) -> str:
    return f"""# ПРОТОКОЛ ВНЕШНЕГО АУДИТА (L2 CONTOUR)
- **Дата фиксации:** {timestamp}
- **Объем снимка:** {files_count} артефактов
- **Файл слепка:** `SNAPSHOT.md`

## ЗАДАЧА ДЛЯ ВНЕШНЕГО АУДИТОРА
Провести комплексную ревизию монолитного снимка ядра `SNAPSHOT.md` на предмет:
1. **Топологического комплаенса:** соблюдение Правила 6 (тотальный snake_case в именах файлов и путях, отсутствие пробелов и кириллицы в директориях исходников).
2. **Целостности онтологии:** согласованность тезауруса `docs/thesaurus/` с реестрами и кодом `scripts/lexicon_cli.py`.
3. **Согласованности ролей:** актуальность `roles_registry.md` и директории `roles/`.
4. **Архитектурного дрейфа:** выявление мертвых ссылок, устаревших путей или расхождений с `project_passport.md`.
"""


def main() -> int:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"🔍 Сканирование репозитория: {BASE_DIR}")
    files = collect_target_files(BASE_DIR)

    if not files:
        print("❌ Ошибка: не найдено файлов для формирования снимка.")
        return 1

    print(f"📦 Отобрано файлов для снимка: {len(files)}")

    # Проверка доступности Google Диска
    if not MIRROR_DIR.exists():
        try:
            MIRROR_DIR.mkdir(parents=True, exist_ok=True)
            print(f"📁 Создан целевой каталог зеркала: {MIRROR_DIR}")
        except Exception as e:
            print(f"❌ Ошибка доступа к Google Диску ({MIRROR_DIR}): {e}")
            return 1

    snapshot_path = MIRROR_DIR / "SNAPSHOT.md"
    audit_path = MIRROR_DIR / "PROMPT_AUDIT.md"

    print("📝 Сборка монолитного SNAPSHOT.md...")
    snapshot_content = build_snapshot(BASE_DIR, files, timestamp)

    try:
        snapshot_path.write_text(snapshot_content, encoding="utf-8")
        print(f"✅ Записан: {snapshot_path} ({len(snapshot_content)} симв.)")
    except Exception as e:
        print(f"❌ Не удалось записать {snapshot_path}: {e}")
        return 1

    print("📝 Запись протокола PROMPT_AUDIT.md...")
    audit_content = build_prompt_audit(timestamp, len(files))
    try:
        audit_path.write_text(audit_content, encoding="utf-8")
        print(f"✅ Записан: {audit_path}")
    except Exception as e:
        print(f"❌ Не удалось записать {audit_path}: {e}")
        return 1

    print("🎉 Зеркалирование успешно завершено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())