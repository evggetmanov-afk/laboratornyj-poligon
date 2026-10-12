#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @raycast.schemaVersion 1
# @raycast.title [Лаб] [Вахта] Захват экрана iTerm2 в лог и буфер чата
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🔬

import os
import sys
import subprocess
import datetime
from pathlib import Path

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
        # Оставляем информативный хвост экрана
        tail_lines = lines[-lines_count:] if len(lines) > lines_count else lines
        return "\n".join(tail_lines).strip()
    except Exception as e:
        # Фолбэк на буфер обмена, если iTerm2 не ответил
        try:
            cb = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True).stdout.strip()
            if cb:
                return f"[Fallback pbpaste]\n{cb}"
        except Exception:
            pass
        return f"Ошибка чтения экрана iTerm2: {e}"

def get_target_journal(vault_dir: Path) -> tuple[Path, str]:
    cwd = Path.cwd().resolve()
    try:
        rel = cwd.relative_to(vault_dir)
        parts = rel.parts
        if len(parts) >= 2 and parts[0] == "01_projects":
            project_name = parts[1]
            project_dir = vault_dir / "01_projects" / project_name
            journal_dir = project_dir / "journal"
            journal_dir.mkdir(parents=True, exist_ok=True)
            return journal_dir, f"PROJECT: {project_name}"
    except ValueError:
        pass

    root_journal = vault_dir / "Вахтенный_журнал"
    root_journal.mkdir(parents=True, exist_ok=True)
    return root_journal, "CORE"

def set_clipboard(text: str):
    subprocess.run(["pbcopy"], input=text, text=True, check=True)

def main():
    vault_dir = Path("/Users/getmanov/Лабораторный_полигон").resolve()
    journal_dir, context_level = get_target_journal(vault_dir)

    today_str = datetime.date.today().isoformat()
    today_file = journal_dir / f"{today_str}.md"
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    # 1. Считываем свежий экран iTerm2
    screen_content = get_iterm2_screen_text(lines_count=45)
    if not screen_content:
        screen_content = "Пустой экран iTerm2 на момент захвата."

    # 2. Фиксируем инцидент в вахтенном журнале на диске
    journal_entry = f"\n## Инцидент [{timestamp}]\n- **Уровень:** {context_level}\n\n```text\n{screen_content}\n```\n"

    try:
        with open(today_file, "a", encoding="utf-8") as f:
            f.write(journal_entry)
    except Exception as e:
        play_sound("Basso")
        sys.stderr.write(f"Ошибка записи в журнал {today_file}: {e}\n")
        sys.exit(1)

    # 3. Подготавливаем буфер обмена для быстрой вставки (Cmd+V) в чат LLM
    chat_payload = (
        f"🚨 **Инцидент терминала [{timestamp}]**\n"
        f"- Лог: `{context_level}` → `{today_file.name}`\n\n"
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

if __name__ == "__main__":
    main()
