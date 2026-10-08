#!/usr/bin/env python3
"""Захват последнего штатного вывода терминала iTerm2 в буфер обмена."""

import subprocess
import sys


def get_iterm_screen_contents() -> str:
    """Считывает текстовое полотно активной сессии iTerm2 через AppleScript."""
    apple_script = """
    tell application "iTerm2"
        if (count of windows) = 0 then
            return ""
        end if
        tell current session of current window
            return contents
        end tell
    end tell
    """
    result = subprocess.run(
        ["osascript", "-e", apple_script],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def copy_to_clipboard(text: str) -> None:
    """Помещает сырой текст в системный буфер обмена macOS."""
    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
    process.communicate(input=text)


def extract_last_output(raw_contents: str) -> str:
    """Очищает экранный буфер от пустот и строки промпта, возвращая последний блок."""
    lines = raw_contents.splitlines()

    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return ""

    lines.pop()

    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return ""

    collected_lines = []
    for line in reversed(lines):
        collected_lines.append(line)
        if len(collected_lines) >= 100:
            break

    collected_lines.reverse()
    return "\n".join(collected_lines).strip()


def main():
    raw_text = get_iterm_screen_contents()
    if not raw_text.strip():
        sys.exit(0)

    clean_output = extract_last_output(raw_text)
    if clean_output:
        copy_to_clipboard(clean_output)


if __name__ == "__main__":
    main()
