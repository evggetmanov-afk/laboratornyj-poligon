#!/usr/bin/env bash
# scripts/scan_lexicon.sh
# Фасад для быстрого запуска ревизии семантики (Zsh/Bash)
#
# Использование:
#   ./scripts/scan_lexicon.sh                     # Проверяет последний измененный .md файл
#   ./scripts/scan_lexicon.sh <файл.md>          # Проверяет конкретный документ
#   ./scripts/scan_lexicon.sh --dump-llm         # Выводит онтологию для контекста LLM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LEXICON_CLI="$REPO_ROOT/scripts/lexicon_cli.py"

if [[ ! -f "$LEXICON_CLI" ]]; then
    echo "❌ Ошибка: Не найден исполнитель $LEXICON_CLI"
    exit 1
fi

if [[ "$1" == "--dump-llm" ]]; then
    python3 "$LEXICON_CLI" --dump-llm
    exit 0
fi

TARGET_DOC="$1"

if [[ -z "$TARGET_DOC" ]]; then
    LAST_DOC="$(find "$REPO_ROOT/docs" "$REPO_ROOT/specs" -type f -name "*.md" ! -iname "thesaurus.md" ! -iname "template.md" -exec stat -f "%m %N" {} + 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)"
    if [[ -z "$LAST_DOC" ]]; then
        echo "❌ Ошибка: Не найдено Markdown-документов для анализа в docs/ и specs/"
        exit 1
    fi
    TARGET_DOC="$LAST_DOC"
    echo "⚡ Целевой документ не указан. Выбран последний измененный:"
    echo "   $TARGET_DOC"
fi

python3 "$LEXICON_CLI" "$TARGET_DOC"