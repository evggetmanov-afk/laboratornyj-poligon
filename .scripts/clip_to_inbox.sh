#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Быстрая заметка во Входящие
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 📥

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

VAULT_DIR="/Users/getmanov/Лабораторный_полигон"
INBOX_DIR="$VAULT_DIR/Входящие"
TIMESTAMP=$(date "+%Y-%m-%d_%H-%M-%S")
TARGET="$INBOX_DIR/Заметка_$TIMESTAMP.md"

mkdir -p "$INBOX_DIR"

CLIPBOARD_TEXT=$(pbpaste)

if [ -z "$CLIPBOARD_TEXT" ]; then
  afplay /System/Library/Sounds/Basso.aiff 2>/dev/null
  osascript -e 'display notification "Буфер обмена пуст" with title "Лабораторный полигон"'
  exit 1
fi

cat << NOTE > "$TARGET"
---
id: $(date "+%Y%m%d%H%M")
дата: $(date "+%Y-%m-%d")
время: $(date "+%H:%M:%S")
тип: входящие
статус: сырое
теги:
  - входящие
---

# Входящая заметка от $(date "+%Y-%m-%d %H:%M:%S")

$CLIPBOARD_TEXT
NOTE

afplay /System/Library/Sounds/Glass.aiff 2>/dev/null
osascript -e 'display notification "Заметка сохранена во Входящие" with title "Лабораторный полигон"'
