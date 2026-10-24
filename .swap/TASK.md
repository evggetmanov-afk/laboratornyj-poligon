# КВАНТ РАБОТЫ: Фиксация ADR-005 и регламента двухконтурного мастера

## 1. СКОУП
- Изменять: docs/decisions/ADR-005_Two_Contour_Dialog_Master.md, docs/manuals/two_contour_master_manual.md, .swap/TASK.md
- Только чтение: PROJECT_PASSPORT.md

## 2. КОНТРАКТ
1. Зафиксировать архитектурное решение ADR-005 по формату ABC.
2. Подготовить регламент оператора двухконтурного мастера.

## 3. КРИТЕРИЙ ПРИЕМКИ (Definition of Done)
- Команда проверки:
  test -f docs/decisions/ADR-005_Two_Contour_Dialog_Master.md && test -f docs/manuals/two_contour_master_manual.md && echo "OK"
- Ожидаемый результат: OK

## 4. СТАТУС
- DONE