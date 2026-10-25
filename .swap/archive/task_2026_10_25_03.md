# КВАНТ РАБОТЫ: Восстановление спецификации и контура роли /схема

## 1. СКОУП
- Изменять:
  - `specs/mermaid_master_spec.md`
  - `ROLES_REGISTRY.md`
  - `docs/manuals/knowledge_pipeline_user_guide.md`
- Только чтение:
  - `PROJECT_PASSPORT.md`
  - `docs/manuals/knowledge_pipeline_flowchart.md`

## 2. КОНТРАКТ
1. Сформировать полную спецификацию `specs/mermaid_master_spec.md`:
   - Назначение роли `/схема` и интеграция с Mermaid/Obsidian.
   - Физические инварианты направлений:
     - Производственный цикл — строго слева направо (`LR`).
     - Контур управления — сверху вниз (`TD` / вход сверху).
     - Контуры снабжения и сырья — снизу вверх (`BT` / вход снизу).
   - Инварианты синтаксиса: snake_case для ID узлов, строгая изоляция текста в кавычках, экранирование спецсимволов.
   - Базовые типовые шаблоны (производственный конвейер, алгоритм развилок, sequence передачи сообщений).
   - Стилизация под печать (`print-landscape.css`) и Obsidian (`cssclass: landscape`).
2. Актуализировать запись роли `/схема` в `ROLES_REGISTRY.md` с точной привязкой к спецификации.
3. Дописать оборванный раздел 3 в `docs/manuals/knowledge_pipeline_user_guide.md`.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки: `python3 -c "open('specs/mermaid_master_spec.md'); open('ROLES_REGISTRY.md'); open('docs/manuals/knowledge_pipeline_user_guide.md')"`
- Ожидаемый результат: все файлы открываются без ошибок, отсутствуют оборванные блоки кода, синтаксис Mermaid-блоков замкнут.

## 4. СТАТУС
- DONE