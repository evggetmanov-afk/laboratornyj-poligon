#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
from pathlib import Path

def play_sound(sound_name):
    sound_path = Path(f"/System/Library/Sounds/{sound_name}.aiff")
    if sound_path.exists():
        subprocess.run(["afplay", str(sound_path)], check=False)

def main():
    repo_root = Path(__file__).resolve().parent.parent
    sys_prompt_file = repo_root / "Система" / "Промпты" / "Системный_Промпт.md"
    log_dir = repo_root / "Вахтенный_журнал"

    if not sys_prompt_file.exists():
        print(f"Ошибка: не найден системный промпт {sys_prompt_file}", file=sys.stderr)
        play_sound("Basso")
        sys.exit(1)

    if not log_dir.exists():
        print(f"Ошибка: не найден каталог журнала {log_dir}", file=sys.stderr)
        play_sound("Basso")
        sys.exit(1)

    # Поиск последней закрытой записи по времени модификации
    log_files = [f for f in log_dir.glob("*.md") if f.is_file()]
    if not log_files:
        print("Ошибка: в вахтенном журнале нет записей", file=sys.stderr)
        play_sound("Basso")
        sys.exit(1)

    latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

    sys_text = sys_prompt_file.read_text(encoding="utf-8").strip()
    log_text = latest_log.read_text(encoding="utf-8").strip()

    handover_payload = f"""# КОНТЕКСТ ЗАСТУПЛЕНИЯ НА ВАХТУ

## 1. СИСТЕМНЫЙ КОНТРАКТ
{sys_text}

---

## 2. ПОСЛЕДНЯЯ ЗАПИСЬ ВАХТЕННОГО ЖУРНАЛА ({latest_log.name})
{log_text}

---

## 3. ДИРЕКТИВА ПЕРВОГО ОТВЕТА
Войди в работу строго по утвержденному протоколу заступления на вахту.
Никаких вступительных приветствий и клише.
Ответь строго по шаблону:
> **Вахта принята.**
> * **Базовая веха:** [Название закрытой вехи из журнала]
> * **Состояние контура:** [Статус контура]
> * **Фокус текущей смены:** [Первая задача]
> 
> *Готов к работе. Жду вводных или команду.*
""".strip()

    # Копирование в буфер обмена macOS через pbcopy
    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True, encoding="utf-8")
    process.communicate(input=handover_payload)

    if process.returncode == 0:
        print(f"✓ Контекст вахты скопирован в буфер обмена (лог: {latest_log.name})")
        play_sound("Pop")
    else:
        print("Ошибка при копировании в буфер обмена", file=sys.stderr)
        play_sound("Basso")
        sys.exit(1)

if __name__ == "__main__":
    main()
