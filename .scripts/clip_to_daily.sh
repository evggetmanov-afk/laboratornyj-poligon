#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title [Лабораторный] Добавить в Дневной журнал
# @raycast.mode silent
# @raycast.packageName Лабораторный Полигон
# @raycast.icon 🔬

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

VAULT="/Users/getmanov/Лабораторный_полигон"
DATE_STR=$(date +"%Y-%m-%d")
TIME_STR=$(date +"%H:%M")
TARGET="$VAULT/Вахтенный_журнал/${DATE_STR}_Журнал.md"
CONTENT=$(pbpaste)

if [ -z "$CONTENT" ]; then
  osascript -e 'display notification "Буфер обмена пуст" with title "Лабораторный: Журнал"'
  exit 1
fi

if [ ! -f "$TARGET" ]; then
  cat << DAILY_INIT_EOF > "$TARGET"
---
дата: $DATE_STR
тип: журнал
статус: активный
теги:
  - вахтенный_журнал
---

# Вахтенный журнал за $DATE_STR

DAILY_INIT_EOF
fi

cat << DAILY_APPEND_EOF >> "$TARGET"

### [$TIME_STR] — Оперативная фиксация
$CONTENT
DAILY_APPEND_EOF

osascript -e "display notification \"Добавлено в журнал за $DATE_STR\" with title \"Лабораторный\""
