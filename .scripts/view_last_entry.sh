#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title [Лабораторный] Показать последнюю запись
# @raycast.mode fullOutput
# @raycast.packageName Лабораторный Полигон
# @raycast.icon 🔬

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

VAULT="/Users/getmanov/Лабораторный_полигон"
LAST_INBOX=$(ls -t "$VAULT/Входящие"/*.md 2>/dev/null | head -n 1)

echo "=== ПОСЛЕДНЯЯ ЗАМЕТКА ИЗ ВХОДЯЩИХ ==="
if [ -n "$LAST_INBOX" ]; then
  echo "Файл: $(basename "$LAST_INBOX")"
  echo "----------------------------------------"
  cat "$LAST_INBOX"
else
  echo "Входящие пусты."
fi

echo ""
echo "=== ПОСЛЕДНИЙ БЛОК ВАХТЕННОГО ЖУРНАЛА ==="
DATE_STR=$(date +"%Y-%m-%d")
JOURNAL="$VAULT/Вахтенный_журнал/${DATE_STR}_Журнал.md"
if [ -f "$JOURNAL" ]; then
  tail -n 15 "$JOURNAL"
else
  echo "Журнал за сегодня еще не создан."
fi
