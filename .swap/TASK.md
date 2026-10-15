# КВАНТ РАБОТЫ: Боевой тест scripts/raw_to_inbox.py и проверка коллизий

## 1. СКОУП
- Изменять: 00_raw_inbox/, 01_inbox/, .swap/TASK.md
- Только чтение: scripts/raw_to_inbox.py, specs/file_naming_convention_spec.md

## 2. КОНТРАКТ
1. Поместить тестовый файл в 00_raw_inbox/ без YAML frontmatter.
2. Прогнать `python3 scripts/raw_to_inbox.py`.
3. Убедиться, что файл перемещен в 01_inbox/, имя соответствует `YYYYMMDDHHmmss[tags] <title>.md`, а поле `id` в YAML строго совпадает со штампом.
4. Провести тест коллизии: создать файл с тем же базовым штампом, запустить шлюз, проверить появление суффикса `_001` в имени и синхронно в поле `id`.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Файлы обработаны и перемещены в 01_inbox/.
- `id` во frontmatter == штамп в имени файла (включая индекс коллизии).
- Код возврата `python3 scripts/raw_to_inbox.py` равен 0.

## 4. СТАТУС
- DONE