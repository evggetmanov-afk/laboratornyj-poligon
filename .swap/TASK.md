# КВАНТ РАБОТЫ: Ввод в строй браузерного шлюза (CONTAINER) и утилиты container_gateway.py

## 1. СКОУП
- Изменять: docs/decisions/ADR-004_Browser_Gateway_Payload.md, docs/manuals/browser_gateway_manual.md, scripts/container_gateway.py
- Только чтение: PROJECT_PASSPORT.md, scripts/apply_payload.py

## 2. КОНТРАКТ
1. Сформировать архитектурное решение ADR-004 по формату ABC с протоколом CONTAINER.
2. Сформировать пошаговую инструкцию оператора в docs/manuals/browser_gateway_manual.md.
3. Разработать независимый распаковщик scripts/container_gateway.py с трехфазной транзакционностью (All-or-Nothing).
4. Провести верификацию блока через позитивный и негативный тесты в _draft/.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки:
  test -f docs/decisions/ADR-004_Browser_Gateway_Payload.md && test -f docs/manuals/browser_gateway_manual.md && test -f scripts/container_gateway.py && echo "OK"
- Ожидаемый результат: OK

## 4. СТАТУС
- DONE