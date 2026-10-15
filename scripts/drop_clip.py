#!/usr/bin/env python3
"""
scripts/drop_clip.py — быстрый сброс системного буфера обмена macOS в 00_raw_inbox.
Генерирует имя вида: 00_raw_inbox/YYYY_MM_DD_HHmmss_raw.md
Гарантирует наличие поля id в YAML-шапке, тождественного имени файла.
"""

import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def get_clipboard_text() -> str:
    """Получает текст из системного буфера обмена macOS через pbpaste."""
    try:
        proc = subprocess.run(
            ["pbpaste"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc.stdout
    except Exception as exc:
        print(f"❌ [ОШИБКА] Не удалось прочитать буфер обмена: {exc}", file=sys.stderr)
        sys.exit(1)


def get_target_path_and_id(inbox_dir: Path, now: datetime) -> tuple[Path, str]:
    """
    Формирует уникальный путь с секундной точностью YYYY_MM_DD_HHmmss.
    При коллизиях добавляет трехзначный суффикс _001, _002.
    Возвращает (target_path, file_id).
    """
    base_prefix = now.strftime("%Y_%m_%d_%H%M%S")
    candidate_file = inbox_dir / f"{base_prefix}_raw.md"
    if not candidate_file.exists():
        return candidate_file, base_prefix

    idx = 1
    while True:
        suffix = f"_{idx:03d}"
        candidate_file = inbox_dir / f"{base_prefix}_raw{suffix}.md"
        candidate_id = f"{base_prefix}{suffix}"
        if not candidate_file.exists():
            return candidate_file, candidate_id
        idx += 1


def inject_yaml_id(text: str, file_id: str, now: datetime) -> str:
    """
    Проверяет наличие YAML-шапки. Внедряет новую или обновляет поле id.
    """
    created_str = now.strftime("%Y-%m-%d %H:%M:%S")
    yaml_pattern = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
    match = yaml_pattern.match(text)

    if not match:
        header = f"---\nid: {file_id}\ncreated: {created_str}\n---\n\n"
        return header + text

    yaml_body = match.group(1)
    rest_of_text = text[match.end():]

    id_pattern = re.compile(r"^id:\s*.*$", re.MULTILINE)
    if id_pattern.search(yaml_body):
        updated_body = id_pattern.sub(f"id: {file_id}", yaml_body)
    else:
        updated_body = f"id: {file_id}\n" + yaml_body

    return f"---\n{updated_body}\n---\n" + rest_of_text


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Использование: python3 scripts/drop_clip.py")
        print("Забирает текст из буфера обмена и сохраняет в 00_raw_inbox/YYYY_MM_DD_HHmmss_raw.md")
        print("Автоматически привязывает id в YAML frontmatter к имени файла.")
        sys.exit(0)

    repo_root = Path(__file__).resolve().parent.parent
    inbox_dir = repo_root / "00_raw_inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    text = get_clipboard_text()
    if not text.strip():
        print("⚠️ [ВНИМАНИЕ] Буфер обмена пуст или содержит только пробелы. Файл не создан.")
        sys.exit(0)

    now = datetime.now()
    target_path, file_id = get_target_path_and_id(inbox_dir, now)
    final_text = inject_yaml_id(text, file_id, now)

    try:
        target_path.write_text(final_text, encoding="utf-8")
        rel_path = target_path.relative_to(repo_root)
        print(f"✅ [DROP] Сохранено в {rel_path} (id: {file_id}, {len(final_text)} симв.)")
    except Exception as exc:
        print(f"❌ [ОШИБКА] Сбой записи файла {target_path}: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()