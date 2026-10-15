#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Drop Clipboard to Inbox
# @raycast.mode compact

# Optional parameters:
# @raycast.icon 📥
# @raycast.packageName Knowledge Pipeline

# Documentation:
# @raycast.description Забирает текст из буфера обмена и сохраняет в 00_raw_inbox с секундным штампом времени
# @raycast.author getmanov

# Разрешение абсолютного пути к корню репозитория
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Запуск рабочего скрипта через системный Python 3
cd "$REPO_ROOT" || exit 1
/usr/bin/python3 "$SCRIPT_DIR/drop_clip.py"