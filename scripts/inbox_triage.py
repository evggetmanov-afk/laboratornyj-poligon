#!/usr/bin/env python3
"""
scripts/inbox_triage.py
Инструмент детерминированного разбора 00_raw_inbox/ и _quarantine/ по правилу No-Delete.
Использование:
  python3 scripts/inbox_triage.py --dry-run    # только отчет без перемещения
  python3 scripts/inbox_triage.py --apply      # физическое перемещение
"""

import sys
import os
import shutil
import argparse
from pathlib import Path

ROOT = Path(".")
RAW_INBOX = ROOT / "00_raw_inbox"
QUARANTINE = ROOT / "_quarantine"
ARCHIVE_INBOX = ROOT / "docs" / "archive" / "raw_inbox"

def scan_files():
    items = []
    if RAW_INBOX.is_dir():
        for p in RAW_INBOX.iterdir():
            if p.name.startswith("."):
                continue
            items.append(("raw_inbox", p))
    if QUARANTINE.is_dir():
        for p in QUARANTINE.iterdir():
            if p.name.startswith("."):
                continue
            items.append(("quarantine", p))
    return items

def categorize_item(source_zone: str, path: Path):
    name = path.name.lower()
    suffix = path.suffix.lower()

    if path.is_dir():
        if "takeout" in name:
            return "HEAVY_CLOUD_TRANSFER", "Вынос в Контур 2 (Google Диск)"
        return "DIR_REVIEW", "Каталог на ручной разбор"

    if suffix in [".zip", ".tar", ".gz", ".pdf", ".mp4", ".mov"]:
        return "HEAVY_CLOUD_TRANSFER", "Вынос в Контур 2 (Google Диск / тяжелые)"

    if "adr" in name or "архитектур" in name:
        return "DOCS_CANDIDATE", "Кандидат в docs/decisions/"

    if "спецификац" in name or "контракт" in name:
        return "SPECS_CANDIDATE", "Кандидат в specs/"

    return "ARCHIVE_RAW", "Архивация в docs/archive/raw_inbox/"

def main():
    parser = argparse.ArgumentParser(description="Триаж входящего буфера Лабораторного полигона")
    parser.add_argument("--apply", action="store_true", help="Применить физические действия")
    parser.add_argument("--dry-run", action="store_true", help="Показать план без изменений")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        args.dry_run = True

    items = scan_files()
    if not items:
        print("Входные буферы пусты.")
        return 0

    print(f"=== СКАНЕР ВХОДЯЩЕГО БУФЕРА: НАЙДЕНО ОБЪЕКТОВ: {len(items)} ===")
    
    categories = {}
    for zone, p in items:
        cat, desc = categorize_item(zone, p)
        categories.setdefault(cat, []).append((p, desc))

    for cat, file_list in categories.items():
        desc = file_list[0][1]
        print(f"\n[{cat}] ({desc}) — {len(file_list)} шт.:")
        for p, _ in file_list:
            size_kb = (p.stat().st_size // 1024) if p.is_file() else 0
            size_str = f"{size_kb} KB" if p.is_file() else "DIR"
            print(f"  - {p.name} [{size_str}]")

    if args.dry_run:
        print("\n[РЕЖИМ DRY-RUN]: Изменения на диске не производились.")
        print("Для перемещения легких файлов в архив запустите: python3 scripts/inbox_triage.py --apply")
        return 0

    if args.apply:
        ARCHIVE_INBOX.mkdir(parents=True, exist_ok=True)
        print("\n=== ПРИМЕНЕНИЕ ДЕЙСТВИЙ: АРХИВАЦИЯ ЛЕГКИХ ЗАМЕТОК ===")
        archived_count = 0
        for p, _ in categories.get("ARCHIVE_RAW", []):
            dest = ARCHIVE_INBOX / p.name
            shutil.move(str(p), str(dest))
            archived_count += 1
        print(f"✅ Перемещено в {ARCHIVE_INBOX}: {archived_count} файлов.")
        print("ℹ️ Тяжелые файлы (HEAVY_CLOUD_TRANSFER) и архитектурные кандидаты оставлены для точечной обработки.")
        return 0

if __name__ == "__main__":
    sys.exit(main())