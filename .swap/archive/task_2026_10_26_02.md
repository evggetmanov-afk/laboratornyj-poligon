# КВАНТ РАБОТЫ: Нормализация каталога specs/ и калибровка топологии

## 1. СКОУП
- Изменять:
  - `specs/` (структура каталога, регистрация имен файлов)
  - `roles/role_secretary.md` (завершение формулировки утилиты save)
  - `.swap/TASK.md` (фиксация контракта и закрытие задач)
- Только чтение:
  - `PROJECT_PASSPORT.md`
  - `specs/knowledge_pipeline_spec.md`

## 2. КОНТРАКТ
1. Верифицировать 7 файлов инвариантов от 29.09 и переименовать по стандарту `snake_case` латиницей (ВЫПОЛНЕНО).
2. Завершить формулировку в `roles/role_secretary.md` (ВЫПОЛНЕНО).
3. Проверить критерий приемки на отсутствие кириллицы и пробелов в `specs/*.md` (ВЫПОЛНЕНО).
4. Очистить `specs/` и `docs/` от мусора `.DS_Store` (ВЫПОЛНЕНО).
5. Верифицировать `specs/knowledge_pipeline_spec.md` и откалибровать монолитный индекс `YYYYMMDDHHMM` вместе с `docs/concept_inbox_task_stream.md` (ВЫПОЛНЕНО).
6. Зафиксировать изменения в Git (ВЫПОЛНЕНО).

## 3. ВЫПОЛНЕННЫЙ БЭКЛОГ (Калибровка путей и шаблонов)
- `specs/logic_anomaly_protocol_spec.md`: заменен путь `Вахтенный_журнал/` -> `watch_log/`.
- `specs/pipeline_architecture_showcase_spec.md`: обновлены фильтры выборки Dataview (`Карточки/` -> `docs/`, `Входящие/` -> `00_raw_inbox/`, `01_inbox/`).
- `specs/skill_boundaries_and_domains_spec.md`: устранен `cat << 'EOF'`, прописан `save`, каталоги приведены к `docs/` и `scripts/`.
- `specs/code_jurisdiction_and_atomic_write_spec.md`: актуализированы пути (`raw/` -> `00_raw_inbox/`, `.state/` -> `.swap/`, `docs/`, `watch_log/`).
- `specs/self_describing_code_passport_spec.md`: путь `.scripts/` исправлен на `scripts/`.
- `specs/knowledge_pipeline_spec.md`: закреплен запрет кириллицы, монолитный таймстемп `YYYYMMDDHHMM`.
- `docs/concept_inbox_task_stream.md`: устранен устаревший формат `YYYY_MM_DD_HHMM`, синхронизирован монолитный таймстемп `YYYYMMDDHHMM`.

## 4. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки: `git status -s`
- Ожидаемый результат: все изменения зафиксированы в Git, рабочее дерево чисто, контракт закрыт.

## 5. СТАТУС
- DONE