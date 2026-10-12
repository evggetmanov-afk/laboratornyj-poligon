from pathlib import Path

path = Path("PROJECT_PASSPORT.md")
if not path.exists():
    print("Ошибка: PROJECT_PASSPORT.md не найден в текущей директории!")
    raise SystemExit(1)

content = path.read_text(encoding="utf-8")

rule_9 = """
9. Контроль деградации контекста и обязательный счетчик тактов:
   - Каждый ответ модели строго обязан начинаться с первой строки в формате:
     [Такт N/10 | Проект: <имя_проекта>]
   - N — порядковый номер текущего вопроса/запроса оператора в сессии.
   - При достижении Такта 8/10 модель выдает обязательный алерт на скорое закрытие вахты.
   - При достижении Такта 10/10 срабатывает жесткая стоп-линия: генерация кода и новых обсуждений блокируется, оформляется только отчет передачи смены и вызов vahta.py для перехода в чистый чат.
"""

if "Контроль деградации контекста и обязательный счетчик тактов" in content:
    print("Пункт 9 уже присутствует в PROJECT_PASSPORT.md")
else:
    target = "8. Стандарт передачи смены"
    if target in content:
        parts = content.split(target, 1)
        rest = parts[1]
        lines = rest.splitlines(keepends=True)
        idx = len(lines)
        for i, line in enumerate(lines[1:], start=1):
            if line.startswith("## ") or line.startswith("---"):
                idx = i
                break
        new_content = parts[0] + target + "".join(lines[:idx]) + "\n" + rule_9.strip() + "\n\n" + "".join(lines[idx:])
        path.write_text(new_content, encoding="utf-8")
        print("Успешно: пункт 9 добавлен в раздел инвариантов PROJECT_PASSPORT.md")
    else:
        path.write_text(content.strip() + "\**Факт:** `zsh: parse error near ')'`[span_5](start_span)[span_5](end_span).  
**Причина:** вложенные круглые скобки и кавычки внутри однострочника `python3 -c "..."` сломали парсер zsh[span_6](start_span)[span_6](end_span). Сработало защитное предупреждение: однострочники через `-c` ненадежны[span_7](start_span)[span_7](end_span).  
**Решение:** канонический безопасный транспорт через экранированный `cat << 'EOF'` во временный скрипт[span_8](start_span)[span_8](end_span).

Выполните в корне репозитория (вы уже в каталоге `Лабораторный_полигон`):

```zsh
cat << 'EOF' > update_passport.py
from pathlib import Path

passport_path = Path("PROJECT_PASSPORT.md")
if not passport_path.exists():
    print("Ошибка: PROJECT_PASSPORT.md не найден")
    exit(1)

content = passport_path.read_text(encoding="utf-8")

rule_9 = """
9. Контроль деградации контекста и обязательный счетчик тактов:
   - Каждый ответ модели строго обязан начинаться с первой строки в формате:
     [Такт N/10 | Проект: <имя_проекта>]
   - N — порядковый номер текущего вопроса/запроса оператора в сессии.
   - При достижении Такта 8/10 модель выдает обязательный алерт на скорое закрытие вахты.
   - При достижении Такта 10/10 срабатывает жесткая стоп-линия: генерация кода и новых обсуждений блокируется, оформляется только отчет передачи смены и вызов vahta.py для перехода в чистый чат.
"""

if "Контроль деградации контекста и обязательный счетчик тактов" in content:
    print("Правило уже в файле.")
else:
    passport_path.write_text(content.rstrip() + "\n" + rule_9, encoding="utf-8")
    print("Успешно: пункт 9 добавлен в PROJECT_PASSPORT.md")
