#!/usr/bin/env bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Заступить на вахту
# @raycast.mode silent

# Optional parameters:
# @raycast.icon ⚓️
# @raycast.packageName Вахта

# Documentation:
# @raycast.description Сборка актуального контекста вахты в буфер обмена
# @raycast.author Вахтенный помощник

export LANG="ru_RU.UTF-8"
export LC_ALL="ru_RU.UTF-8"

REPO_DIR="/Users/getmanov/Лабораторный_полигон"
python3 "$REPO_DIR/.scripts/vahta.py"
