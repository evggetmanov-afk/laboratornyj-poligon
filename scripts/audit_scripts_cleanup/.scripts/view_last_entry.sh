#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title [Лаб] Показать последнюю запись журнала
# @raycast.mode fullOutput
# @raycast.packageName Лабораторный полигон
# @raycast.icon 👁️

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

VAULT_DIR="/Users/getmanov/Лабораторный_полигон"
JOURNAL_DIR="$VAULT_DIR/Вахтенный_журнал"

if [ ! -d "$JOURNAL_DIR" ]; then
  echo "Каталог Вахтенный_журнал не найден."
  exit 1
fi

LATEST_FILE=$(ls -t "$JOURNAL_DIR"/*.md 2>/dev/null | head -n 1)

if [ -z "$LATEST_FILE" ]; then
  echo "В вахтенном журнале пока нет записей."
  exit 0
fi

echo "=== Файл: $(basename "$LATEST_FILE") ==="
echo ""
cat "$LATEST_FILE"
