# КВАНТ РАБОТЫ: Мастер графических блок-схем (Mermaid Master)

## 1. СКОУП
- Изменять:
  - `.swap/TASK.md`
  - `specs/mermaid_master_spec.md`
  - `ROLES_REGISTRY.md`
- Только чтение:
  - `00_raw_inbox/Архитектор производственных схем (Mermaid Architect).md`
  - `00_raw_inbox/Мастер-контур Базовая архитектура.md`
  - `00_raw_inbox/Мастер-контур Полная расширенная архитектура.md`
  - `00_raw_inbox/print-landscape.css`
  - `PROJECT_PASSPORT.md`

## 2. КОНТРАКТ
1. Проанализировать исходные требования к схемам из `00_raw_inbox/`.
2. Спроектировать спецификацию `specs/mermaid_master_spec.md`:
   - Поддерживаемые типы схем (flowchart, sequence, state, class).
   - Правила стилизации и темы печати (интеграция `print-landscape.css`).
   - Синтаксические инварианты (направление потоков, экранирование узлов, запрет циклических дедлоков).
3. Зарегистрировать интерфейсную роль `/схема` в `ROLES_REGISTRY.md`.
4. Предусмотреть формат выгрузки схем через стандарт Clipboard Stream.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки:
  `test -f specs/mermaid_master_spec.md && grep -q "/схема" ROLES_REGISTRY.md && echo "OK"`
- Ожидаемый результат: `OK`

## 4. СТАТУС
- DONE
