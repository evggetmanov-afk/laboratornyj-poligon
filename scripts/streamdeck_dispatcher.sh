#!/usr/bin/env zsh
# Диспетчер команд для Elgato Stream Deck в репозитории Лабораторный полигон

# Определение корня репозитория относительно расположения скрипта
SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h}"

cd "$REPO_ROOT" || {
    osascript -e 'display notification "Не удалось перейти в корень репозитория" with title "Stream Deck: Ошибка"'
    exit 1
}

ACTION="$1"

notify() {
    local title="$1"
    local message="$2"
    osascript -e "display notification \"$message\" with title \"$title\""
}

case "$ACTION" in
    save)
        OUTPUT=$(python3 scripts/save_clip.py 2>&1)
        STATUS=$?
        if [ $STATUS -eq 0 ]; then
            notify "Stream Deck: SAVE" "Файл успешно сохранен на SSD"
        else
            notify "Stream Deck: SAVE Ошибка" "$OUTPUT"
        fi
        ;;
    diff)
        # Открытие diff в терминале через osascript
        osascript -e "tell application \"Terminal\" to do script \"cd '$REPO_ROOT' && git diff\""
        ;;
    status)
        STATUS_OUT=$(git status -s)
        if [ -z "$STATUS_OUT" ]; then
            notify "Stream Deck: GIT STATUS" "Рабочее дерево чистое"
        else
            notify "Stream Deck: GIT STATUS" "$STATUS_OUT"
        fi
        ;;
    payload)
        OUTPUT=$(pbpaste | python3 scripts/apply_payload.py 2>&1)
        STATUS=$?
        if [ $STATUS -eq 0 ]; then
            notify "Stream Deck: PAYLOAD" "Пакет успешно распакован"
        else
            notify "Stream Deck: PAYLOAD Ошибка" "$OUTPUT"
        fi
        ;;
    vahta_stat)
        OUTPUT=$(python3 scripts/vahta.py status 2>&1)
        notify "Stream Deck: ВАХТА" "$OUTPUT"
        ;;
    vahta_close)
        OUTPUT=$(python3 scripts/vahta.py close 2>&1)
        STATUS=$?
        if [ $STATUS -eq 0 ]; then
            notify "Stream Deck: ВАХТА ЗАКРЫТА" "Смена зафиксирована"
        else
            notify "Stream Deck: Сбой закрытия" "$OUTPUT"
        fi
        ;;
    *)
        notify "Stream Deck" "Неизвестное действие: $ACTION"
        exit 1
        ;;
esac