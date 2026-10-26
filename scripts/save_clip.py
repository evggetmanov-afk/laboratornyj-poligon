#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent

def play_sound(sound_name: str):
    sound_path = Path(f"/System/Library/Sounds/{sound_name}.aiff")
    if sound_path.exists():
        subprocess.run(["afplay", str(sound_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def notify(title: str, message: str):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_clipboard() -> str:
    try:
        res = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
        return res.stdout
    except Exception as e:
        play_sound("Sosumi")
        notify("Лабораторный полигон", f"Ошибка pbpaste: {e}")
        print(f"❌ Ошибка чтения буфера обмена: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    text = get_clipboard()
    if not text.strip():
        play_sound("Basso")
        notify("Лабораторный полигон", "Буфер обмена пуст")
        print("⚠️ Буфер обмена пуст.", file=sys.stderr)
        sys.exit(1)

    target_path_raw = None
    content_to_write = text

    if len(sys.argv) > 1:
        target_path_raw = sys.argv[1]
    else:
        lines = text.splitlines(keepends=True)
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            m = re.match(r'^(?:### FILE:|<<<FILE_PATH:)\s*([^\s]+)', line)
            if m:
                target_path_raw = m.group(1)
                content_to_write = "".join(lines[i+1:])
                content_to_write = re.sub(r'<<<FILE_CONTENT_END>>>\s*$', '', content_to_write)
                break

    if not target_path_raw:
        play_sound("Basso")
        notify("Лабораторный полигон", "Маркер пути не найден (### FILE: <путь>)")
        print('❌ Путь не определен. Укажи аргумент: save <путь> или добавь в начало буфера "### FILE: <путь>"', file=sys.stderr)
        sys.exit(1)

    path_obj = Path(target_path_raw)
    if not path_obj.is_absolute():
        final_path = (VAULT_DIR / path_obj).resolve()
    else:
        final_path = path_obj.resolve()

    try:
        final_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.write_text(content_to_write, encoding="utf-8")
        play_sound("Tink")
    except Exception as e:
        play_sound("Sosumi")
        notify("Лабораторный полигон", f"Ошибка диска: {e}")
        print(f"❌ Ошибка записи в {final_path}: {e}", file=sys.stderr)
        sys.exit(1)

    rel_path_str = str(final_path)
    try:
        rel_path_str = str(final_path.relative_to(VAULT_DIR))
    except ValueError:
        pass

    report = f"✅ [SAVE] Записано на диск: {rel_path_str} ({len(content_to_write)} симв.)"
    print(report)
    play_sound("Glass")
    notify("Лабораторный полигон", f"Записано: {rel_path_str}")

if __name__ == "__main__":
    main()