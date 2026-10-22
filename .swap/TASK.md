# КВАНТ РАБОТЫ: Браузерный шлюз и спецификация контракта TASK_PAYLOAD

## 1. СКОУП
- Изменять:
  - `.swap/TASK.md`
  - `specs/browser_gateway_payload_spec.md`
- Только чтение:
  - `00_raw_inbox/Спецификация контракта TASK_PAYLOAD.md`
  - `00_raw_inbox/Реализация браузерного шлюза через Tampe.md`
  - `00_raw_inbox/Двухконтурная архитектура Архитектор Исп.md`
  - `00_raw_inbox/==UserScript==.md`
  - `00_raw_inbox/Критические нюансы эксплуатации браузерн.md`
  - `PROJECT_PASSPORT.md`

## 2. КОНТРАКТ
1. Проанализировать массив заметок по Tampermonkey и двухконтурному взаимодействию в `00_raw_inbox/`.
2. Сформировать нормативную инженерную спецификацию `specs/browser_gateway_payload_spec.md`:
   - Формат и структура конверта `TASK_PAYLOAD` (метаданные, манифест файлов, инструкции сборки).
   - Протокол передачи из веб-интерфейса чата в локальный буфер/файл.
   - Защитные барьеры и правила валидации перед исполнением.
3. Подготовить список отработанных сырых файлов для архивации в `docs/archive/raw_sources/`.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки:
  `test -f specs/browser_gateway_payload_spec.md && grep -q "TASK_PAYLOAD" specs/browser_gateway_payload_spec.md && echo "OK"`
- Ожидаемый результат: `OK`

## 4. СТАТУС
- DONE
