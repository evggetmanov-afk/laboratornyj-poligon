#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title [Лаб] Быстрая заметка во Входящие
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 📥
# @raycast.packageName Лабораторный полигон

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/clip_to_inbox.py"
