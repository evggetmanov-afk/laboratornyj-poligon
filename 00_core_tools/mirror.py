#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Базовая папка — текущий Лабораторный_полигон
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.expanduser(
    '~/Library/CloudStorage/GoogleDrive-evg.getmanov@gmail.com/Мой диск/AI_Mirror'
)
SNAPSHOT_FILE = os.path.join(TARGET_DIR, 'SNAPSHOT.md')
AUDIT_PROMPT_FILE = os.path.join(TARGET_DIR, 'PROMPT_AUDIT.md')

SOURCE_DIRS = [
    os.path.join(BASE_DIR, '00_core_tools'),
    os.path.join(BASE_DIR, '_draft'),
    os.path.join(BASE_DIR, '01_projects'),
]

IGNORE_DIRS = {'.git', '__pycache__', '.pytest_cache', 'env', 'venv'}

AUDIT_INSTRUCTION = """# Протокол ревизии «Зазеркалья»

Действуй строго по протоколу аудита на основе текущего SNAPSHOT.md:

1. 🔍 **Картина (Рентген)**: Сведи текущее состояние полигона в короткую матрицу: что стабильно, что в работе, что зависло.
2. 🧹 **Лишний огород**: Укажи 2–3 элемента (скрипты, правила, шаги регламента), которые усложняют процесс, но не приносят реальной ценности.
3. ⏳ **Зависшие дела**: Какие задачи переходят из смены в смену без прогресса и почему?
4. 🎯 **Критика и следующий шаг**: Раскритикуй текущий вектор и сформулируй ровно один чёткий контракт задачи (TASK) для следующего кванта на Маке.
"""

def ensure_target_dir():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR, exist_ok=True)
        print(f"📁 Создана папка зеркала: {TARGET_DIR}")

def write_audit_prompt():
    with open(AUDIT_PROMPT_FILE, 'w', encoding='utf-8') as f:
        f.write(AUDIT_INSTRUCTION.strip())

def collect_markdown_files():
    collected = []
    for s_dir in SOURCE_DIRS:
        if not os.path.exists(s_dir):
            continue
        for root, dirs, files in os.walk(s_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
            for file in sorted(files):
                if file.endswith('.md'):
                    collected.append(os.path.join(root, file))
    return collected

def build_snapshot():
    ensure_target_dir()
    write_audit_prompt()
    
    md_files = collect_markdown_files()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as out:
        out.write(f"# СИСТЕМНЫЙ СЛЕПОК ПОЛИГОНА (SNAPSHOT)\n")
        out.write(f"*Сгенерировано*: {now_str}\n")
        out.write(f"*Всего файлов в слепке*: {len(md_files)}\n\n")
        out.write("=" * 60 + "\n\n")

        for fpath in md_files:
            rel_path = os.path.relpath(fpath, BASE_DIR)
            out.write(f"## ФАЙЛ: {rel_path}\n\n")
            out.write("```markdown\n")
            try:
                with open(fpath, 'r', encoding='utf-8') as src:
                    out.write(src.read().strip())
            except Exception as e:
                out.write(f"Ошибка чтения: {e}")
            out.write("\n```\n\n")
            out.write("-" * 40 + "\n\n")

    print(f"✅ Слепок обновлён: {SNAPSHOT_FILE}")
    print(f"📄 Файлов упаковано: {len(md_files)}")
    print(f"📋 Шаблон аудита: {AUDIT_PROMPT_FILE}")

if __name__ == '__main__':
    build_snapshot()
