#!/usr/bin/env python3
"""
scripts/raw_to_inbox.py
Шлюз нормализации и перемещения заметок из 00_raw_inbox/ в 01_inbox/.
Стандарт штампа: YYYYMMDDHHmmss (14 цифр без подчеркиваний).
Контроль коллизий по ID префиксу.
"""

import sys
import os
import re
import shutil
import argparse
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "00_raw_inbox"
INBOX_DIR = ROOT_DIR / "01_inbox"

# 14 цифр подряд: YYYYMMDDHHmmss
TS_PATTERN = re.compile(r"^(\d{14})(?:_(\d{3}))?")

def generate_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def parse_filename(filename):
    stem = Path(filename).stem
    match = TS_PATTERN.match(stem)
    if match:
        ts = match.group(1)
        collision = match.group(2)
        base_id = f"{ts}_{collision}" if collision else ts
        remainder = stem[match.end():].strip()
        return base_id, remainder
    return None, stem.strip()

def extract_frontmatter(content):
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return None, content

def build_frontmatter(doc_id, title, stage="inbox", doc_type="task", extra_yaml=None):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "---",
        f"id: {doc_id}",
        f"case_id: {doc_id}",
        f"created: {now_str}",
        f"type: {doc_type}",
        f"stage: {stage}",
        f"title: {title}"
    ]
    if extra_yaml:
        for line in extra_yaml.strip().splitlines():
            key = line.split(":", 1)[0].strip()
            if key not in {"id", "case_id", "created", "type", "stage", "title"}:
                lines.append(line)
    lines.append("---")
    return "\n".join(lines) + "\n"

def id_exists_in_dir(target_id, target_dir):
    """Проверяет, занят ли ID любым файлом в каталоге."""
    for f in target_dir.iterdir():
        if f.is_file() and not f.name.startswith("."):
            stem = f.stem
            match = TS_PATTERN.match(stem)
            if match:
                f_ts = match.group(1)
                f_col = match.group(2)
                f_id = f"{f_ts}_{f_col}" if f_col else f_ts
                if f_id == target_id:
                    return True
    return False

def resolve_target_name(base_id, remainder, target_dir):
    clean_base = base_id.split("_")[0]
    suffix = 0
    while True:
        current_id = f"{clean_base}_{suffix:03d}" if suffix > 0 else clean_base
        if not id_exists_in_dir(current_id, target_dir):
            if remainder:
                candidate_name = f"{current_id} {remainder}.md"
            else:
                candidate_name = f"{current_id}.md"
            target_path = target_dir / candidate_name
            return current_id, candidate_name, target_path
        suffix += 1

def process_file(source_path):
    if not source_path.is_file() or source_path.name.startswith("."):
        return False

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    existing_id, remainder = parse_filename(source_path.name)
    base_id = existing_id if existing_id else generate_timestamp()

    final_id, final_name, target_path = resolve_target_name(base_id, remainder, INBOX_DIR)

    content = source_path.read_text(encoding="utf-8")
    fm_raw, body = extract_frontmatter(content)
    title = remainder if remainder else final_id

    new_content = build_frontmatter(
        doc_id=final_id,
        title=title,
        stage="inbox",
        doc_type="task",
        extra_yaml=fm_raw
    ) + body

    temp_path = target_path.with_suffix(".tmp")
    temp_path.write_text(new_content, encoding="utf-8")
    shutil.move(str(temp_path), str(target_path))
    source_path.unlink()

    print(f"[TRANSFERRED] {source_path.name} -> 01_inbox/{final_name}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Шлюз нормализации сырья в 01_inbox")
    parser.add_argument("--all", action="store_true", help="Обработать все файлы в 00_raw_inbox")
    parser.add_argument("--file", type=str, help="Обработать конкретный файл")
    args = parser.parse_args()

    if not RAW_DIR.exists():
        print(f"[ERROR] Директория {RAW_DIR} не существует.", file=sys.stderr)
        sys.exit(1)

    if args.file:
        target = RAW_DIR / args.file
        if not target.exists():
            print(f"[ERROR] Файл {target} не найден.", file=sys.stderr)
            sys.exit(1)
        success = process_file(target)
        sys.exit(0 if success else 1)

    raw_files = sorted(
        [f for f in RAW_DIR.iterdir() if f.is_file() and not f.name.startswith(".")],
        key=lambda p: p.stat().st_mtime
    )

    if not raw_files:
        print("[INFO] 00_raw_inbox пуст. Нечего обрабатывать.")
        sys.exit(0)

    if args.all:
        for f in raw_files:
            process_file(f)
    else:
        process_file(raw_files[0])

    sys.exit(0)

if __name__ == "__main__":
    main()