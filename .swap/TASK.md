# КВАНТ РАБОТЫ: Разработка диспетчера входящих (scripts/inbox_dispatcher.py)

## 1. СКОУП
- Изменять: scripts/inbox_dispatcher.py, .swap/TASK.md
- Только чтение: specs/inbox_dispatch_spec.md, 01_inbox/, ready/, _quarantine/

## 2. КОНТРАКТ
1. Написать утилиту scripts/inbox_dispatcher.py согласно утвержденной specs/inbox_dispatch_spec.md:
   - Парсинг тегов в имени файла [ценность][тип][домен] и полей frontmatter.
   - Маршрутизация: в projects/<project_name>/, в docs/ или по умолчанию в ready/.
   - Защита инварианта: сохранение неизменности имени файла и поля id (YYYYMMDDHHmmss).
   - Обновление поля stage во frontmatter (inbox -> ready / project).
   - Изоляция поврежденных файлов в _quarantine/.
2. Провести тестовый прогон на файлах из 01_inbox/.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- python3 -m py_compile scripts/inbox_dispatcher.py выполняется без ошибок.
- Тестовая заметка из 01_inbox/ перемещена в целевой каталог с сохранением имени и id, поле stage обновлено на ready/project.
- Код возврата 0.

## 4. СТАТУС
- DONE