#!/usr/bin/env bash
# @raycast.schemaVersion 1
# @raycast.title Ревизия семантики документа
# @raycast.mode fullOutput
# @raycast.packageName Knowledge Tools
# @raycast.icon 📖

# Определение корня репозитория
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LEXICON_CLI="$REPO_ROOT/scripts/lexicon_cli.py"

TARGET_FILE="$1"

# 1. Если аргумент не передан, проверяем буфер обмена macOS
if [[ -z "$TARGET_FILE" ]]; then
    CLIP_VAL="$(pbpaste | tr -d '\n')"
    if [[ -f "$CLIP_VAL" ]]; then
        TARGET_FILE="$CLIP_VAL"
    elif [[ -f "$REPO_ROOT/$CLIP_VAL" ]]; then
        TARGET_FILE="$REPO_ROOT/$CLIP_VAL"
    fi
fi

# 2. Если в буфере нет пути к файлу, берем последний измененный Markdown-документ
if [[ -z "$TARGET_FILE" ]]; then
    LAST_DOC="$(find "$REPO_ROOT/docs" "$REPO_ROOT/specs" -type f -name "*.md" ! -name "thesaurus.md" ! -name "TEMPLATE.md" -exec stat -f "%m %N" {} + 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)"
    if [[ -n "$LAST_DOC" && -f "$LAST_DOC" ]]; then
        TARGET_FILE="$LAST_DOC"
    fi
fi

if [[ -z "$TARGET_FILE" || ! -f "$TARGET_FILE" ]]; then
    echo "❌ Ошибка: Целевой файл не найден. Передайте путь аргументом или скопируйте в буфер обмена."
    exit 1
fi

python3 "$LEXICON_CLI" "$TARGET_FILE"