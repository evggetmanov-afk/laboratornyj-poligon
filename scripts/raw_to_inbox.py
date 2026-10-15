#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# scripts/raw_to_inbox.py
# Подающий скрипт конвейера: перемещает заготовки из 00_raw_inbox/ в 01_inbox/
# с нормализацией штампа времени YYYY_MM_DD_HHmmss, фиксацией родового case_id,
# установкой stage: inbox и разрешением коллизий согласно specs/file_naming_convention_spec.md.

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = VAULT_DIR / "00_raw_inbox"
INBOX_DIR = VAULT_DIR / "01_inbox"

# Извлечение базового штампа YYYY_MM_DD_HHmmss и опционального суффикса коллизии _XXX
TS_PATTERN = re.compile(r"^(\d{4}_\d{2}_\d{2}_\d{6})(?:_(\d{3}))?")
# Устаревший слитный формат 14 цифр (YYYYMMDDHHmmss)
LEGACY_TS_PATTERN = re.compile(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})")


def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y_%m_%d_%H%M%S")


def normalize_existing_id(raw_id: str) -> tuple[str, str]:
    raw_id = raw_id.strip()
    match = TS_PATTERN.match(raw_id)
    if match:
        base = match.group(1)
        suffix = match.group(2) or ""
        return base, suffix

    digits = re.sub(r"\D", "", raw_id)
    if len(digits) >= 14:
        d_match = LEGACY_TS_PATTERN.match(digits[:14])
        if d_match:
            base = f"{d_match.group(1)}_{d_match.group(2)}_{d_match.group(3)}_{d_match.group(4)}{d_match.group(5)}{d_match.group(6)}"
            return base, ""

    return "", ""


def parse_filename(filename: str) -> tuple[str, str, str]:
    stem = Path(filename).stem
    match = TS_PATTERN.match(stem)
    if match:
        ts_id = match.group(1)
        col_idx = match.group(2) or ""
        consumed_len = len(match.group(0))
        rest = stem[consumed_len:].lstrip(" _-")
        return ts_id, col_idx, rest

    return "", "", stem


def parse_frontmatter(content: str) -> tuple[dict, str]:
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

    return fm_dict, body


def build_frontmatter(fm_dict: dict) -> str:
    preferred_order = ["id", "case_id", "created", "type", "stage", "title", "ref_path", "refs"]
    lines = ["---"]
    for k in preferred_order:
        if k in fm_dict and fm_dict[k] is not None:
            lines.append(f"{k}: {fm_dict[k]}")
    for k, v in fm_dict.items():
        if k not in preferred_order and v is not None:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def resolve_collision_and_save(
    source_path: Path,
    target_dir: Path,
    base_ts: str,
    semantic_title: str,
    fm_dict: dict,
    body: str,
) -> Path:
    ext = source_path.suffix or ".md"
    clean_title = f" {semantic_title}" if semantic_title else ""

    candidate_id = base_ts
    candidate_name = f"{candidate_id}{clean_title}{ext}"
    candidate_path = target_dir / candidate_name

    col_num = 1
    while candidate_path.exists():
        candidate_id = f"{base_ts}_{col_num:03d}"
        candidate_name = f"{candidate_id}{clean_title}{ext}"
        candidate_path = target_dir / candidate_name
        col_num += 1

    fm_dict["id"] = candidate_id
    if "case_id" not in fm_dict or not fm_dict["case_id"]:
        fm_dict["case_id"] = base_ts

    fm_dict["stage"] = "inbox"
    if "type" not in fm_dict:
        fm_dict["type"] = "task"

    if semantic_title and "title" not in fm_dict:
        fm_dict["title"] = semantic_title

    enriched_content = build_frontmatter(fm_dict) + body

    temp_target = target_dir / f".{candidate_name}.tmp"
    with open(temp_target, "w", encoding="utf-8") as f:
        f.write(enriched_content)

    temp_target.replace(candidate_path)
    source_path.unlink()

    return candidate_path


def transfer_file(source_path: Path, target_dir: Path) -> Path:
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    fm_dict, body = parse_frontmatter(content)

    file_ts, _, file_rest = parse_filename(source_path.name)
    fm_base_ts, _ = normalize_existing_id(fm_dict.get("id", ""))

    now_dt = datetime.now()
    if file_ts:
        base_ts = file_ts
    elif fm_base_ts:
        base_ts = fm_base_ts
    else:
        base_ts = format_timestamp(now_dt)

    if "created" not in fm_dict:
        fm_dict["created"] = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    semantic_title = file_rest.strip() or fm_dict.get("title", "").strip()

    return resolve_collision_and_save(
        source_path=source_path,
        target_dir=target_dir,
        base_ts=base_ts,
        semantic_title=semantic_title,
        fm_dict=fm_dict,
        body=body,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Подача заготовок из 00_raw_inbox/ в 01_inbox/ по specs/file_naming_convention_spec.md."
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
        to_process = [files[0]]

    for item in to_process:
        result_path = transfer_file(item, INBOX_DIR)
        print(f"[TRANSFERRED] {item.name} -> {INBOX_DIR.name}/{result_path.name}")

    sys.exit(0)


if __name__ == "__main__":
    main()