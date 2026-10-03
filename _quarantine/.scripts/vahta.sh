#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Вахта (Передача контекста)
# @raycast.mode silent
# @raycast.packageName Лабораторный полигон
# @raycast.icon 📋

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

VAULT_DIR="/Users/getmanov/Лабораторный_полигон"
SCRIPT_PATH="$VAULT_DIR/.scripts/vahta.py"

if [ -f "$SCRIPT_PATH" ]; then
  /usr/bin/env python3 "$SCRIPT_PATH"
else
  afplay /System/Library/Sounds/Basso.aiff 2>/dev/null
  osascript -e 'display notification "Скрипт vahta.py не найден" with title "Лабораторный полигон"'
  exit 1
fi
