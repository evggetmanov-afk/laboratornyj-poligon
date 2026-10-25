#!/usr/bin/env python3
"""
projects/strategy_engine/src/planner.py
Контур А: Генератор детерминированных карточек стратегий.
Использование:
  python3 projects/strategy_engine/src/planner.py --goal "Цель стратегии" --title "Краткое имя"
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

TASKS_DIR = Path("projects/strategy_engine/tasks")

def get_next_strat_id(today_str: str) -> str:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(TASKS_DIR.glob(f"STRAT-{today_str}-*.md"))
    max_idx = 0
    for p in existing:
        parts = p.stem.split("-")
        if len(parts) == 3 and parts[2].isdigit():
            max_idx = max(max_idx, int(parts[2]))
    next_idx = max_idx + 1
    return f"STRAT-{today_str}-{next_idx:02d}"

def create_strategy_card(goal: str, title: str) -> Path:
    today_str = datetime.now().strftime("%Y%m%d")
    strat_id = get_next_strat_id(today_str)
    
    file_path = TASKS_DIR / f"{strat_id}.md"

    template = f"""# Карточка стратегии: {title}

- ID: {strat_id}
- ЦЕЛЬ: {goal}
- ДАТА: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Инварианты и запреты (Negative Constraints)
1. Запрещено модифицировать файлы вне скоупа задачи.
2. Все команды должны возвращать код 0.
3. Остановка конвейера при первой ошибке.

## Шаги исполнения

### Шаг 1: Pre-flight проверка среды
CMD: test -d projects/strategy_engine && echo "Среда готова"

### Шаг 2: Выполнение целевого действия
CMD: echo "Выполнение шага по цели: {goal}"

### Шаг 3: Верификация результата
CMD: echo "OK"
"""

    file_path.write_text(template, encoding="utf-8")
    return file_path

def main():
    parser = argparse.ArgumentParser(description="Генератор карточек стратегий (Контур А)")
    parser.add_argument("--goal", required=True, help="Формулировка цели стратегии")
    parser.add_argument("--title", default="Новая стратегия", help="Заголовок карточки")
    
    args = parser.parse_args()

    out_file = create_strategy_card(args.goal, args.title)
    print(f"✅ Карточка стратегии сформирована: {out_file}")
    print(f"Для запуска выполните: python3 projects/strategy_engine/src/runner.py {out_file}")

if __name__ == "__main__":
    main()