# КВАНТ РАБОТЫ: Нормализация каталога specs/ и калибровка топологии

## 1. СКОУП
- Изменять:
  - `specs/` (структура каталога, регистрация имен файлов)
  - `roles/role_secretary.md` (завершение формулировки утилиты save)
  - `.swap/TASK.md` (фиксация контракта и запаркованных задач)
- Только чтение:
  - `PROJECT_PASSPORT.md`
  - `specs/knowledge_pipeline_spec.md`

## 2. КОНТРАКТ
1. Верифицировать 7 файлов инвариантов от 29.09 и переименовать по стандарту `snake_case` латиницей (ВЫПОЛНЕНО).
2. Завершить формулировку в `roles/role_secretary.md` (ВЫПОЛНЕНО).
3. Проверить критерий приемки на отсутствие кириллицы и пробелов в `specs/*.md` (ВЫПОЛНЕНО).
4. Очистить `specs/` и `docs/` от мусора `.DS_Store` (ВЫПОЛНЕНО).
5. Верифицировать `specs/knowledge_pipeline_spec.md` (синхронизация временного индекса и запрет кириллицы).
6. Зафиксировать изменения в Git.

## 3. ЗАПАРКОВАННЫЙ БЭКЛОГ (Калибровка путей в specs/)
- `specs/logic_anomaly_protocol_spec.md`: заменить устаревший путь `Вахтенный_журнал/` на `watch_log/`[cite: 1].
- `specs/pipeline_architecture_showcase_spec.md`: обновить фильтры выборки Dataview с `Карточки/` и `Входящие/` на актуальные каталоги `docs/` и `00_raw_inbox/`[cite: 2].
- `specs/skill_boundaries_and_domains_spec.md`: устранить конфликт с Паспортом (убрать упоминание `cat << 'EOF'`), заменить `Карточки/` на `docs/` и `.scripts/` на `scripts/`[cite: 3].
- `specs/code_jurisdiction_and_atomic_write_spec.md`: актуализировать пути (`raw/` -> `00_raw_inbox/`, `.state/` -> `.swap/`, `Вахтенный_журнал/` -> `watch_log/`)[cite: 4].
- `specs/self_describing_code_passport_spec.md`: поправить путь `.scripts/` -> `scripts/`[cite: 6].

## 4. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки: `git status -s`
- Ожидаемый результат: Все переименования зафиксированы в индексе, файлы очищены, контракт актуализирован.

## 5. СТАТУС
- IN_PROGRESS