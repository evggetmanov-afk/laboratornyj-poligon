# КВАНТ РАБОТЫ: Спецификация диспетчеризации инбокса (inbox_dispatch_spec)

## 1. СКОУП
- Изменять: specs/inbox_dispatch_spec.md, .swap/TASK.md
- Только чтение: specs/file_naming_convention_spec.md, PROJECT_PASSPORT.md

## 2. КОНТРАКТ
1. Спроектировать спецификацию маршрутизации заметок из 01_inbox/ в целевые каталоги (ready/, projects/<name>/, docs/).
2. Зафиксировать правила маппинга тегов [домен] и полей frontmatter на целевые каталоги.
3. Закрепить правила обновления поля stage (inbox -> ready / done) при строгом сохранении неизменности имени файла и поля id.
4. Описать протокол обработки ошибок, отсутствия тегов назначения и изоляции в _quarantine/.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Файл specs/inbox_dispatch_spec.md создан на диске через save.
- Спецификация полностью согласуется с инвариантами specs/file_naming_convention_spec.md.
- Статус в .swap/TASK.md переведен в DONE.

## 4. СТАТУС
- DONE