#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
scripts/raw_to_inbox.py
Подающий скрипт конвейера: перемещает заготовки из 00_raw_inbox/ в 01_inbox/
с нормализацией монолитного ключа id (14 цифр), фиксацией родового case_id
и установкой stage: inbox.
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = VAULT_DIR / "00_raw_inbox"
INBOX_DIR = VAULT_DIR / "01_inbox"


def parse_and_enrich_content(content: str) -> tuple[str, str, str]:
    """
    Разбирает YAML frontmatter, нормализует монолитный id (14 цифр),
    фиксирует case_id, stage=inbox, type=task (если отсутствует).
    Возвращает (обновленный_контент, id, case_id).
    """
    fm_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = fm_pattern.match(content)

    fm_dict = {}
    if match:
        fm_raw = match.group(1)
        body = content[match.end():]
        for line in fm_raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm_dict[k.strip()] = v.strip().strip('"\'')
    else:
        body = content

    # Нормализация ID (оставляем только цифры)
    raw_id = fm_dict.get("id", "")
    compact_id = re.sub(r"\D", "", raw_id)
    if len(compact_id) < 14:
        now_dt = datetime.now()
        compact_id = now_dt.strftime("%Y%m%d%H%M%S")
        if "created" not in fm_dict:
            fm_dict["created"] = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Привязка полей
    fm_dict["id"] = compact_id
    if "case_id" not in fm_dict or not fm_dict["case_id"]:
        fm_dict["case_id"] = compact_id
    case_id = fm_dict["case_id"]

    fm_dict["stage"] = "inbox"
    if "type" not in fm_dict:
        fm_dict["type"] = "task"

    # Сборка чистового frontmatter
    preferred_order = ["id", "case_id", "created", "type", "stage", "title", "ref_path", "refs"]
    new_fm = ["---"]
    for k in preferred_order:
        if k in fm_dict:
            new_fm.append(f"{k}: {fm_dict[k]}")
    for k, v in fm_dict.items():
        if k not in preferred_order:
            new_fm.append(f"{k}: {v}")
    new_fm.append("---")

    enriched_content = "\n".join(new_fm) + "\n" + body
    return enriched_content, compact_id, case_id


def transfer_file(source_path: Path, target_dir: Path) -> Path:
    """Обогащает метаданными и атомарно перемещает файл."""
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    enriched_content, file_id, case_id = parse_and_enrich_content(content)

    # Имя в целевой папке: базовое имя с сохранением расширения
    dest_name = source_path.name
    dest_path = target_dir / dest_name

    # Защита от коллизий имен файлов
    counter = 1
    stem = source_path.stem
    ext = source_path.suffix
    while dest_path.exists():
        dest_path = target_dir / f"{stem}_{counter:03d}{ext}"
        counter += 1

    # Запись обогащенного содержимого во временный файл и перемещение
    temp_target = dest_path.with_suffix(".tmp")
    with open(temp_target, "w", encoding="utf-8") as f:
        f.write(enriched_content)

    temp_target.replace(dest_path)
    source_path.unlink()

    return dest_path


def main():
    parser = argparse.ArgumentParser(
        description="Подача заготовок из 00_raw_inbox/ в 01_inbox/ с обогащением ключами id и case_id."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Переместить все накопившиеся файлы разом.",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default=None,
        help="Имя конкретного файла в 00_raw_inbox/ для переноса.",
    )

    args = parser.parse_args()

    if not RAW_DIR.exists():
        print(f"[INFO] Папка {RAW_DIR.name} отсутствует. Нечего переносить.")
        sys.exit(0)

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    # Список файлов .md
    files = sorted([p for p in RAW_DIR.iterdir() if p.is_file() and p.suffix == ".md"])

    if not files:
        print("[INFO] Очередь 00_raw_inbox пуста.")
        sys.exit(0)

    to_process: list[Path] = []

    if args.filename:
        target = RAW_DIR / args.filename
        if not target.exists() or not target.is_file():
            print(f"[ERROR] Файл {args.filename} не найден в {RAW_DIR.name}.")
            sys.exit(1)
        to_process = [target]
    elif args.all:
        to_process = files
    else:
        # По умолчанию FIFO — самый старый файл
        to_process = [files[0]]

    for item in to_process:
        result_path = transfer_file(item, INBOX_DIR)
        print(f"[TRANSFERRED] {item.name} -> {INBOX_DIR.name}/{result_path.name}")

    sys.exit(0)


if __name__ == "__main__":
    main()