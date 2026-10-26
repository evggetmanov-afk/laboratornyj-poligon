#!/usr/bin/env python3
"""
Диспетчер входящих сущностей (01_inbox -> ready / projects / docs / _quarantine).
Реализация спецификации specs/inbox_dispatch_spec.md.
"""

import os
import re
import shutil
import sys
from pathlib import Path

# Корень репозитория
ROOT_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = ROOT_DIR / "01_inbox"
READY_DIR = ROOT_DIR / "ready"
PROJECTS_DIR = ROOT_DIR / "projects"
DOCS_DIR = ROOT_DIR / "docs"
QUARANTINE_DIR = ROOT_DIR / "_quarantine"


def extract_frontmatter(content: str):
    """
    Извлекает YAML frontmatter и тело документа.
    Возвращает (raw_yaml, body, parsed_dict) или (None, content, None).
    """
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
    match = pattern.match(content)
    if not match:
        return None, content, None

    raw_yaml = match.group(1)
    body = match.group(2)
    meta = {}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip("'\"")

    return raw_yaml, body, meta


def normalize_id(raw_id: str) -> str:
    """Очищает ID от префиксов и знаков подчеркивания для сравнения таймстемпов."""
    cleaned = re.sub(r"^inbox_", "", raw_id)
    digits = re.sub(r"\D", "", cleaned)
    return digits


def get_filename_id(filename: str) -> str:
    """Извлекает цифровой таймстемп из начала имени файла."""
    match = re.match(r"^(\d{4}[_\-]?\d{2}[_\-]?\d{2}[_\-]?\d{2,6})", filename)
    if match:
        return re.sub(r"\D", "", match.group(1))
    return ""


def determine_target(filename: str, meta: dict) -> tuple:
    """
    Определяет целевую директорию и значение stage.
    Возвращает (target_dir, stage).
    """
    # 1. Поиск тегов в имени файла [tag]
    tags = [t.lower() for t in re.findall(r"\[(.*?)\]", filename)]

    # 2. Проверка маршрута в проекты
    project_target = meta.get("project")
    if not project_target:
        for t in tags:
            candidate = PROJECTS_DIR / t
            if candidate.is_dir():
                project_target = t
                break

    if project_target:
        target_dir = PROJECTS_DIR / project_target
        target_inbox = target_dir / "inbox"
        if target_inbox.is_dir():
            target_dir = target_inbox
        return target_dir, "project"

    # 3. Маршрут в документацию
    if any(t in ["docs", "spec", "adr", "manual"] for t in tags) or meta.get("type") in ["adr", "spec"]:
        if "adr" in tags or meta.get("type") == "adr":
            return DOCS_DIR / "decisions", "ready"
        return DOCS_DIR, "ready"

    # 4. По умолчанию - шлюз готовой базы знаний
    return READY_DIR, "ready"


def update_frontmatter_stage(raw_yaml: str, new_stage: str) -> str:
    """Обновляет или добавляет поле stage в сырой блок YAML."""
    lines = raw_yaml.splitlines()
    stage_found = False
    new_lines = []
    for line in lines:
        if re.match(r"^stage\s*:", line):
            new_lines.append(f"stage: {new_stage}")
            stage_found = True
        else:
            new_lines.append(line)

    if not stage_found:
        new_lines.append(f"stage: {new_stage}")

    return "\n".join(new_lines)


def dispatch_file(filepath: Path) -> bool:
    """Выполняет разбор, валидацию и перемещение одного файла."""
    filename = filepath.name

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Не удалось прочитать {filename}: {e}", file=sys.stderr)
        isolate_to_quarantine(filepath, "read_error")
        return False

    raw_yaml, body, meta = extract_frontmatter(content)

    # Валидация структуры frontmatter
    if raw_yaml is None or not meta or "id" not in meta:
        print(f"[INVALID] Отсутствует валидный frontmatter или id в {filename}. Отправка в _quarantine.")
        isolate_to_quarantine(filepath, "missing_frontmatter")
        return False

    # Валидация тождественности id и префикса имени файла
    file_id_digits = get_filename_id(filename)
    meta_id_digits = normalize_id(meta["id"])

    # Сравнение по минимальной длине префикса (например, YYYYMMDDHHmm)
    min_len = min(len(file_id_digits), len(meta_id_digits))
    if min_len < 8 or file_id_digits[:min_len] != meta_id_digits[:min_len]:
        print(
            f"[INVALID] Несовпадение ID ({meta['id']}) и имени файла ({filename}). Отправка в _quarantine."
        )
        isolate_to_quarantine(filepath, "id_mismatch")
        return False

    # Маршрутизация
    target_dir, new_stage = determine_target(filename, meta)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    # Обновление stage и сборка документа
    updated_yaml = update_frontmatter_stage(raw_yaml, new_stage)
    new_content = f"---\n{updated_yaml}\n---\n{body}"

    # Атомарная запись через .tmp
    tmp_path = target_dir / f"{filename}.tmp"
    try:
        tmp_path.write_text(new_content, encoding="utf-8")
        shutil.move(str(tmp_path), str(target_path))
        filepath.unlink()
        print(f"[DISPATCHED] {filename} -> {target_dir.relative_to(ROOT_DIR)}/ (stage: {new_stage})")
        return True
    except Exception as e:
        print(f"[ERROR] Сбой записи целевого файла {target_path}: {e}", file=sys.stderr)
        if tmp_path.exists():
            tmp_path.unlink()
        return False


def isolate_to_quarantine(filepath: Path, reason: str):
    """Изолирует невалидный файл в _quarantine с обновлением stage."""
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    target_path = QUARANTINE_DIR / filepath.name

    try:
        content = filepath.read_text(encoding="utf-8")
        raw_yaml, body, meta = extract_frontmatter(content)
        if raw_yaml is not None:
            updated_yaml = update_frontmatter_stage(raw_yaml, "quarantine")
            target_path.write_text(f"---\n{updated_yaml}\n---\n{body}", encoding="utf-8")
            filepath.unlink()
        else:
            shutil.move(str(filepath), str(target_path))
        print(f"[QUARANTINE] {filepath.name} изолирован в _quarantine/ ({reason})")
    except Exception as e:
        print(f"[CRITICAL] Не удалось изолировать {filepath.name}: {e}", file=sys.stderr)


def main():
    if not INBOX_DIR.exists():
        print(f"[EXIT] Каталог {INBOX_DIR} не найден.")
        return 0

    files = [
        f for f in INBOX_DIR.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix == ".md"
    ]

    if not files:
        print("[INFO] В 01_inbox нет файлов для обработки.")
        return 0

    print(f"[START] Найдено файлов для диспетчеризации: {len(files)}")
    success_count = 0
    for file in sorted(files):
        if dispatch_file(file):
            success_count += 1

    print(f"[DONE] Успешно обработано: {success_count}/{len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())