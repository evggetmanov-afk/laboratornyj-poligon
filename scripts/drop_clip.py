#!/usr/bin/env python3
"""
scripts/drop_clip.py
Универсальный шлюз сброса сырья в 00_raw_inbox/:
1. Перехват физических файлов из Finder (Cmd+C на файле без изменения оригинала).
2. Перехват скопированного текста с выжимкой первых слов в имя файла.
3. Инъекция монолитного 14-значного YAML id (YYYYMMDDHHmmss).
Спецификация: specs/file_naming_convention_spec.md
"""

import sys
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = BASE_DIR / "00_raw_inbox"


def get_finder_selected_files() -> list[Path]:
    """
    Проверяет, лежат ли в буфере обмена macOS физические файлы из Finder.
    Возвращает список путей к существующим файлам.
    """
    apple_script = """
    on run
        set fileList to {}
        try
            tell application "Finder" to set theSelection to the clipboard as «class furl»
            set end of fileList to (POSIX path of theSelection)
            return fileList
        on error
            try
                tell application "Finder" to set theSelection to the clipboard as list
                repeat with anItem in theSelection
                    set end of fileList to (POSIX path of (anItem as «class furl»))
                end repeat
                return fileList
            on error
                return ""
            end try
        end try
    end run
    """
    try:
        proc = subprocess.run(
            ["osascript", "-e", apple_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        raw_output = proc.stdout.strip()
        if not raw_output:
            return []
        
        paths = []
        for line in raw_output.split(", "):
            clean_path = line.strip()
            if clean_path and os.path.exists(clean_path):
                paths.append(Path(clean_path))
        return paths
    except Exception:
        return []


def get_clipboard_text() -> str:
    """Извлекает текстовое содержимое буфера обмена macOS."""
    try:
        result = subprocess.run(
            ["pbpaste"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except Exception as e:
        print(f"❌ [DROP] Ошибка чтения буфера обмена: {e}", file=sys.stderr)
        return ""


def clean_slug_title(text: str, max_words: int = 5, max_chars: int = 40) -> str:
    """
    Извлекает первые значимые слова из текста для заголовка.
    Игнорирует YAML-шапку и Markdown-решетки.
    """
    # Убираем YAML-шапку, если есть
    yaml_pattern = re.compile(r"^---\n.*?\n---\n?", re.DOTALL)
    clean_text = yaml_pattern.sub("", text).strip()

    # Берем первую непустую строку
    lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
    if not lines:
        return ""

    first_line = lines[0]
    # Убираем маркеры заголовков Markdown (#, ## и т.д.)
    first_line = re.sub(r"^#+\s*", "", first_line).strip()
    # Убираем недопустимые символы файловой системы
    first_line = re.sub(r'[/\\:*?"<>|]', " ", first_line)
    # Нормализуем пробелы
    words = [w for w in first_line.split() if w]

    if not words:
        return ""

    slug = " ".join(words[:max_words])
    if len(slug) > max_chars:
        slug = slug[:max_chars].rstrip()

    return slug.strip()


def inject_yaml_id(text: str, file_id: str, now: datetime, default_title: str = "") -> str:
    """
    Проверяет наличие YAML-шапки. Внедряет новую или обновляет поле id.
    При необходимости прописывает title.
    """
    created_str = now.strftime("%Y-%m-%d %H:%M:%S")
    yaml_pattern = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
    match = yaml_pattern.match(text)

    if not match:
        title_line = f'title: "{default_title}"\n' if default_title else ""
        header = f"---\nid: {file_id}\ncreated: {created_str}\n{title_line}---\n\n"
        return header + text

    yaml_body = match.group(1)
    rest_of_text = text[match.end():]

    if re.search(r"^id:\s*.*$", yaml_body, flags=re.MULTILINE):
        new_yaml_body = re.sub(
            r"^id:\s*.*$",
            f"id: {file_id}",
            yaml_body,
            flags=re.MULTILINE
        )
    else:
        new_yaml_body = f"id: {file_id}\n" + yaml_body

    if not re.search(r"^created:\s*.*$", new_yaml_body, flags=re.MULTILINE):
        new_yaml_body = f"created: {created_str}\n" + new_yaml_body

    if default_title and not re.search(r"^title:\s*.*$", new_yaml_body, flags=re.MULTILINE):
        new_yaml_body = f'{new_yaml_body}\ntitle: "{default_title}"'

    return f"---\n{new_yaml_body.strip()}\n---\n\n{rest_of_text.lstrip()}"


def get_unique_target(inbox_dir: Path, base_prefix: str, semantic_part: str) -> tuple[Path, str]:
    """Формирует уникальный путь и ID с учетом возможных коллизий секунды."""
    title_suffix = f" {semantic_part}" if semantic_part else ""
    candidate_name = f"{base_prefix}_raw{title_suffix}.md"
    candidate_file = inbox_dir / candidate_name

    if not candidate_file.exists():
        return candidate_file, base_prefix

    idx = 1
    while True:
        col_suffix = f"_{idx:03d}"
        candidate_name = f"{base_prefix}_raw{col_suffix}{title_suffix}.md"
        candidate_file = inbox_dir / candidate_name
        candidate_id = f"{base_prefix}{col_suffix}"
        if not candidate_file.exists():
            return candidate_file, candidate_id
        idx += 1


def process_dropped_file(src_path: Path, inbox_dir: Path, now: datetime):
    """Безопасно копирует содержимое существующего файла в inbox без изменения оригинала."""
    try:
        content = src_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"⚠️ [DROP] Пропущен бинарный файл: {src_path.name}")
        return

    base_prefix = now.strftime("%Y%m%d%H%M%S")
    stem = src_path.stem
    # Очищаем stem от старых технических префиксов дат, если они уже были
    clean_stem = re.sub(r"^\d{4}[_-]?\d{2}[_-]?\d{2}[_-]?\d{4,6}[_ -]*", "", stem).strip()
    semantic_name = clean_stem if clean_stem else stem

    target_path, file_id = get_unique_target(inbox_dir, base_prefix, semantic_name)
    final_content = inject_yaml_id(content, file_id, now, default_title=semantic_name)

    target_path.write_text(final_content, encoding="utf-8")
    print(f"✅ [DROP FILE] Скопировано в {target_path.relative_to(BASE_DIR)} (id: {file_id})")
    print(f"ℹ️ Исходный файл не изменен: {src_path}")


def process_clipboard_text(text: str, inbox_dir: Path, now: datetime):
    """Сохраняет текстовую заметку с извлечением первых слов в имя файла."""
    base_prefix = now.strftime("%Y%m%d%H%M%S")
    semantic_words = clean_slug_title(text)

    target_path, file_id = get_unique_target(inbox_dir, base_prefix, semantic_words)
    final_content = inject_yaml_id(text, file_id, now, default_title=semantic_words)

    target_path.write_text(final_content, encoding="utf-8")
    print(f"✅ [DROP TEXT] Сохранено в {target_path.relative_to(BASE_DIR)} (id: {file_id}, {len(text)} симв.)")


def main():
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()

    # 1. Сначала проверяем, скопирован ли файл в Finder
    finder_files = get_finder_selected_files()
    if finder_files:
        for f in finder_files:
            process_dropped_file(f, INBOX_DIR, now)
        return

    # 2. Если файлов нет, проверяем текстовый буфер
    content = get_clipboard_text().strip()
    if not content:
        print("⚠️ [DROP] Буфер обмена пуст. Файл не создан.")
        sys.exit(0)

    process_clipboard_text(content, INBOX_DIR, now)


if __name__ == "__main__":
    main()