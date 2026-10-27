# ТАКТИЧЕСКИЙ КОНТРАКТ ЗАДАЧИ

## 1. Метаданные
- **Дата:** 2026-10-27
- **Исполнитель:** AI / Оператор
- **Контекст:** Лабораторный_полигон (macOS, APFS, Zsh, Git)
- **Целевые артефакты:**
  - `.swap/task.md`
  - `scripts/mirror.py`
  - `~/.zshrc` (актуализация алиаса)
  - `methodology/compliance_audit_spec.md`

## 2. Скоуп и контекст изменений
- Восстановление и адаптация утилиты зеркалирования `scripts/mirror.py` под плоскую топологию (взамен расформированной `00_core_tools/`).
- Формирование монолитного снимка `SNAPSHOT.md` в целевом каталоге Google Диска:
  `~/Library/CloudStorage/GoogleDrive-evg.getmanov@gmail.com/Мой диск/AI_Mirror`.
- Фильтрация: сбор `.md`, `.py`, `.sh`, `.json`, `.yaml` из `docs/`, `specs/`, `roles/`, `methodology/`, `projects/`, `.swap/`, `scripts/`, корневых файлов `project_passport.md`, `roles_registry.md`.
- Исключение: `.git`, `__pycache__`, `.DS_Store`, бинарные/тяжелые медиафайлы (`.mp4`, `.m4a`, `.wav` и т.д.).
- Обновление системного алиаса `mirror` в `~/.zshrc`.
- Фиксация двухуровневого регламента аудита (L1 — экспресс, L2 — облачный контур) в `methodology/compliance_audit_spec.md`.

## 3. Критерии приемки (DoD)
1. Контракт зафиксирован в `.swap/task.md`.
2. Файл `scripts/mirror.py` создан, синтаксически валиден, протестирован локально через запуск `python3 scripts/mirror.py`.
3. Файл `SNAPSHOT.md` корректно сформирован в `~/Library/CloudStorage/GoogleDrive-evg.getmanov@gmail.com/Мой диск/AI_Mirror`.
4. Алиас `mirror` в `~/.zshrc` указывает на актуальный путь `python3 ~/Лабораторный_полигон/scripts/mirror.py`.
5. Спецификация двухуровневого аудита создана в `methodology/compliance_audit_spec.md`.
6. Смена успешно закрыта через `python3 scripts/vahta.py close`.