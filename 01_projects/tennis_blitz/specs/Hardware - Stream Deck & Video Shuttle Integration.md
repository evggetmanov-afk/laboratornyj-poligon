---
id: 202610081315
дата: 2026-10-08
время: 13:15
тип: аппаратная_спецификация
статус: стабильно
теги:
  - hardware
  - stream_deck
  - shuttle_jog
  - mpv_ipc
  - интеграция
---

# Спецификация интеграции: Stream Deck & Video Shuttle

## 1. Слой A: Эксплуатационный сценарий
* Физическая задача оператора: Просмотр матча в темпе без касания клавиатуры и мыши.
* Левая рука: Лежит на Jog/Shuttle (плавная перемотка, покадровый поиск точки удара).
* Правая рука: Лежит на Stream Deck (мгновенная фиксация маркеров входа/выхода, выбор исхода розыгрыша, включение микрофона).

## 2. Слой B: Протокол IPC mpv и аппаратные каналы

### 2.1. Конфигурация запуска плеера
Команда запуска:
mpv --input-ipc-server=/tmp/mpvsocket --keep-open=yes --idle=yes

### 2.2. Матрица команд IPC-сокета (/tmp/mpvsocket)
* Jog Вперед (+1 кадр): {"command": ["frame-step"]}
* Jog Назад (-1 кадр): {"command": ["frame-back-step"]}
* Shuttle Влево (откат): {"command": ["seek", -2, "relative"]}
* Shuttle Вправо (прогон): {"command": ["seek", 2, "relative"]}
* Пауза / Плей: {"command": ["cycle", "pause"]}
* Запрос позиции: {"command": ["get_property", "time-pos"]}

## 3. Слой C: Маппинг клавиш Stream Deck (Сетка профиля)

### 3.1. Структура клавиш (Профиль Теннисный Блиц)
* Клавиша 1: MARK IN (Фиксация T_in)
* Клавиша 2: MARK OUT (Фиксация T_out)
* Клавиша 3: REC VOICE (Старт/стоп аудиокомментария)
* Клавиша 4: SLICE & GO (Запуск нарезки клипа)
* Клавиши 5-8: SERVE ACE, SERVE + 1, WINNER, CANCEL/CLR
* Клавиши 9-12: ERR UNFORCED, ERR FORCED, NET ERROR, OUT DEEP

### 3.2. Логика скриптового моста
* MARK IN: сохраняет текущий time-pos в /tmp/capture_state.json под ключом t_in.
* MARK OUT: сохраняет текущий time-pos в /tmp/capture_state.json под ключом t_out.
* REC VOICE: управляет записью звука в /tmp/coach_voice.wav.
* SLICE & GO: валидирует метки и передает параметры в clip_slicer.py.

## 4. Отрицательные ограничения (Negative Constraints)
* Запрет эмуляции GUI хоткеев через AppleScript во избежание сбоев при потере фокуса окна.
* Запрет блокирующих вызовов в интерфейсе пульта.
