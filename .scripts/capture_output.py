#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] [Вахта] Захват вывода iTerm2 в буфер чата
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 📋

import os
import sys
import subprocess
import datetime

def play_sound(sound_name="Pop"):
    sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
    if os.path.exists(sound_path):
        subprocess.run(["afplay", sound_path], stderr=subprocess.DEVNULL)

def get_iterm2_screen_text(lines_count: int = 45) -> str:
    """Программно забирает текст текущего экрана iTerm2 через AppleScript."""
    apple_script = """
    tell application "iTerm2"
        if (count of windows) > 0 then
            tell current session of current window
                get text
            end tell
        else
            return ""
        end if
    end tell
    """
    try:
        res = subprocess.run(
            ["osascript", "-e", apple_script],
            capture_output=True,
            text=True,
            check=True
        )
        full_text = res.stdout.strip()
        if not full_text:
            return ""
        lines = [line.rstrip() for line in full_text.splitlines()]
        tail_lines = lines[-lines_count:] if len(lines) > lines_count else lines
        return "\n".join(tail_lines).strip()
    except Exception as e:
        try:
            cb = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True).stdout.strip()
            if cb:
                return f"[Fallback pbpaste]\n{cb}"
        except Exception:
            pass
        return f"Ошибка чтения экрана iTerm2: {e}"

def set_clipboard(text: str):
    subprocess.run(["pbcopy"], input=text, text=True, check=True)

def main():
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    # 1. Считываем экран iTerm2
    screen_content = get_iterm2_screen_text(lines_count=45)
    if not screen_content:
        screen_content = "Пустой экран iTerm2 на момент захвата."

    # 2. Формируем чистый блок для отчета в чат (без записи на диск)
    chat_payload = (
        f"📋 **Вывод терминала iTerm2 [{timestamp}]**\n\n"
        f"```text\n"
        f"{screen_content}\n"
        f"```\n"
    )

    try:
        set_clipboard(chat_payload)
        play_sound("Pop")
    except Exception as e:
        play_sound("Basso")
        sys.stderr.write(f"Ошибка обновления буфера обмена: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
