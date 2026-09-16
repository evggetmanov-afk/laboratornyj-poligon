#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Добавить в Ежедневник
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 🔬

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

VAULT_DIR="/Users/getmanov/Лабораторный_полигон"
JOURNAL_DIR="$VAULT_DIR/Вахтенный_журнал"
DATE_STR=$(date "+%Y-%m-%d")
TIME_STR=$(date "+%H:%M:%S")
TARGET="$JOURNAL_DIR/$DATE_STR.md"

mkdir -p "$JOURNAL_DIR"

CLIPBOARD_TEXT=$(pbpaste)

if [ -z "$CLIPBOARD_TEXT" ]; then
  afplay /System/Library/Sounds/Basso.aiff 2>/dev/null
  osascript -e 'display notification "Буфер обмена пуст" with title "Лабораторный полигон"'
  exit 1
fi

if [ ! -f "$TARGET" ]; then
  cat << HEADER > "$TARGET"
---
id: $(date "+%Y%m%d%H%M")
дата: $DATE_STR
тип: вахтенный_журнал
статус: в_работе
теги:
  - вахтенный_журнал
---

# Вахтенный журнал за $DATE_STR

HEADER
fi

cat << ENTRY >> "$TARGET"

## Запись [$TIME_STR]

\`\`\`text
$CLIPBOARD_TEXT
\`\`\`
ENTRY

afplay /System/Library/Sounds/Glass.aiff 2>/dev/null
osascript -e 'display notification "Запись успешно добавлена в журнал" with title "Лабораторный полигон"'
