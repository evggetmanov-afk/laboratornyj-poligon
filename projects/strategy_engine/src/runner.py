#!/usr/bin/env python3
"""
projects/strategy_engine/src/runner.py
Контур С: Детерминированный раннер шагов стратегии.
Формат шагов в карточке:
### Шаг N: <Название>
CMD: <команда терминала>

Если путь к файлу не передан, раннер автоматически берет
последнюю созданную стратегию из projects/strategy_engine/tasks/.
"""

import sys
import os
import subprocess
import re
from pathlib import Path

TASKS_DIR = Path("projects/strategy_engine/tasks")

def get_latest_strategy_file() -> Path:
    if not TASKS_DIR.is_dir():
        raise FileNotFoundError(f"Каталог задач не найден: {TASKS_DIR}")
    files = list(TASKS_DIR.glob("STRAT-*.md"))
    if not files:
        raise FileNotFoundError(f"В {TASKS_DIR} нет файлов стратегий STRAT-*.md")
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]

def parse_strategy_file(file_path: Path):
    if not file_path.is_file():
        raise FileNotFoundError(f"Файл стратегии не найден: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    
    strat_id_match = re.search(r"^\s*-\s*ID:\s*(.+)$", content, re.MULTILINE)
    strat_id = strat_id_match.group(1).strip() if strat_id_match else file_path.stem

    step_pattern = re.compile(
        r"###\s*Шаг\s*(\d+)[:\.]?\s*(.*?)\n\s*CMD:\s*(.+?)(?=\n###|\n---|\Z)",
        re.DOTALL
    )

    steps = []
    for match in step_pattern.finditer(content):
        step_num = int(match.group(1))
        title = match.group(2).strip()
        cmd = match.group(3).strip()
        steps.append({
            "number": step_num,
            "title": title,
            "command": cmd
        })

    steps.sort(key=lambda s: s["number"])
    return strat_id, steps

def execute_strategy(file_path: Path) -> int:
    try:
        strat_id, steps = parse_strategy_file(file_path)
    except Exception as e:
        print(f"[RUNNER ERROR] Ошибка разбора стратегии: {e}", file=sys.stderr)
        return 1

    if not steps:
        print(f"[RUNNER WARN] В стратегии {strat_id} не найдено шагов (ожидается формат CMD: <команда>).")
        return 0

    print(f"=== СТАРТ СТРАТЕГИИ: {strat_id} ({file_path.name}) ===")
    print(f"Всего шагов к исполнению: {len(steps)}\n")

    for step in steps:
        num = step["number"]
        title = step["title"]
        cmd = step["command"]

        print(f"--- [Шаг {num}] {title} ---")
        print(f"$ {cmd}")

        res = subprocess.run(cmd, shell=True, text=True, capture_output=True)

        if res.stdout:
            print(res.stdout.rstrip())
        if res.stderr:
            print(res.stderr.rstrip(), file=sys.stderr)

        if res.returncode != 0:
            print(f"\n[FAIL] Шаг {num} завершился с ошибкой (код возврата {res.returncode})", file=sys.stderr)
            print(f"Остановка выполнения стратегии {strat_id}.", file=sys.stderr)
            return res.returncode

        print(f"[OK] Шаг {num} выполнен успешно.\n")

    print(f"=== СТРАТЕГИЯ {strat_id} ВЫПОЛНЕНА УСПЕШНО (STATUS: DONE) ===")
    return 0

def main():
    if len(sys.argv) >= 2:
        target_path = Path(sys.argv[1])
    else:
        try:
            target_path = get_latest_strategy_file()
            print(f"[RUNNER AUTO] Выбрана последняя стратегия: {target_path}")
        except Exception as e:
            print(f"[RUNNER ERROR] {e}", file=sys.stderr)
            sys.exit(1)

    exit_code = execute_strategy(target_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()