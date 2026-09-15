#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Отправить во Входящие
# @raycast.mode silent
# @raycast.packageName Лабораторный Полигон

VAULT="/Users/getmanov/Лабораторный_полигон"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
TARGET="$VAULT/Входящие/Заметка_$TIMESTAMP.md"
CONTENT=$(pbpaste)

if [ -z "$CONTENT" ]; then
  osascript -e 'display notification "Буфер обмена пуст" with title "Полигон: Входящие"'
  exit 1
fi

cat << INBOX_EOF > "$TARGET"
---
дата: $(date +"%Y-%m-%d")
тип: входящее
статус: сырое
агент: человек
теги:
  - inbox
---

# Заметка $TIMESTAMP

$CONTENT
INBOX_EOF

osascript -e "display notification \"Сохранено во Входящие: Заметка_$TIMESTAMP.md\" with title \"Полигон\""
