#/usr/bin/env python3 -m trace --trace /Users/getmanov/Лабораторный_полигон/.scripts/vahta.py python3
import sys
import os
import subprocess
import re

def get_clipboard():
    try:
        res = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
        return res.stdout
    except Exception as e:
        print(f'❌ Ошибка чтения буфера обмена через pbpaste: {e}', file=sys.stderr)
        sys.exit(1)

def main():
    text = get_clipboard()
    if not text.strip():
        print('⚠️  Буфер обмена пуст.', file=sys.stderr)
        sys.exit(1)

    target_path = None
    content_to_write = text

    # Если путь передан аргументом: save path/to/file
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        # Ищем маркер в первых строках: ### FILE: <path> или <<<FILE_PATH: <path>
        lines = text.splitlines(keepends=True)
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            m = re.match(r'^(?:### FILE:|<<<FILE_PATH:)\s*([^\s]+)', line)
            if m:
                target_path = m.group(1)
                content_to_write = ''.join(lines[i+1:])
                # Отрезаем закрывающий маркер, если есть
                content_to_write = re.sub(r'<<<FILE_CONTENT_END>>>\s*$', '', content_to_write)
                break

    if not target_path:
        print('❌ Путь не определен. Укажи аргумент: save <путь> или добавь в начало буфера "### FILE: <путь>"', file=sys.stderr)
        sys.exit(1)

    # Нормализуем путь и создаем директории
    target_path = os.path.normpath(target_path)
    parent_dir = os.path.dirname(target_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content_to_write)
        print(f'✅ [SAVE] Записано на диск: {target_path} ({len(content_to_write)} симв.)')
    except Exception as e:
        print(f'❌ Ошибка записи в {target_path}: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
