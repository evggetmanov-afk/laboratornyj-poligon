#!/usr/bin/env bash
set -e

# Проверка наличия аргумента сообщения
if [ -z "$1" ]; then
    echo "❌ [ОШИБКА] Укажите сообщение коммита."
    echo "Использование: ./scripts/quick_commit.sh \"тип(область): описание\""
    exit 1
fi

COMMIT_MSG="$1"

# Проверка наличия изменений в рабочем дереве
STATUS_OUTPUT=$(git status -s)
if [ -z "$STATUS_OUTPUT" ]; then
    echo "ℹ️  [GIT] Рабочее дерево чисто, изменений для коммита нет."
    exit 0
fi

echo "🔍 [1/4] Исходный статус репозитория:"
echo "$STATUS_OUTPUT"
echo "----------------------------------------"

# Добавление всех отслеживаемых и новых файлов
echo "📦 [2/4] Индексация изменений (git add -A)..."
git add -A

# Выполнение коммита
echo "💾 [3/4] Фиксация коммита: \"$COMMIT_MSG\""
git commit -m "$COMMIT_MSG"

# Итоговая проверка чистоты дерева
echo "----------------------------------------"
echo "✅ [4/4] Финальный статус:"
git status -s

# Звуковой сигнал завершения в macOS
afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true
echo "🎉 Коммит успешно зафиксирован."