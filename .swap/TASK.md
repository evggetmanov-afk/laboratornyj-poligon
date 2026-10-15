# КВАНТ РАБОТЫ: Синхронизация scripts/raw_to_inbox.py со спецификацией именования

## 1. СКОУП
- Изменять: .swap/TASK.md, scripts/raw_to_inbox.py
- Только чтение: specs/file_naming_convention_spec.md, specs/inbox_gateway_spec.md

## 2. КОНТРАКТ
- Привести генерацию ID и имен файлов в scripts/raw_to_inbox.py к стандарту:
  1. Формат штампа времени: YYYY_MM_DD_HHmmss.
  2. Формирование имени файла: <timestamp_id>[_<collision_index>][tags] <semantic_title>.md.
  3. Если имя исходного файла уже содержит штамп YYYY_MM_DD_HHmmss, использовать его; если нет — генерировать новый штамп и подставлять семантическое имя исходного файла.
  4. При обнаружении коллизии в целевой папке инкрементировать суффикс (_001, _002) и синхронно обновлять поле id в YAML frontmatter.
  5. Обеспечить код возврата 0 при успешном переносе и сохранение режима FIFO / --all.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Синтаксическая валидность: python3 -m py_compile scripts/raw_to_inbox.py
- Проверка справки: python3 scripts/raw_to_inbox.py --help && echo "OK"
- Ожидаемый результат: OK

## 4. СТАТУС
- DONE