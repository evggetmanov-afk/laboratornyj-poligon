---
id: 202609170430
дата: 2026-09-17
время: 04:30:41
тип: входящие
статус: сырое
теги:
  - входящие
---
---
id: 202609170430
дата: 2026-09-17
время: 04:30:41
тип: входящие
статус: сырое
теги:
  - входящие
---

# graph TD

```mermaid
graph TD
    subgraph Lab ["Контур 1: Исследовательская лаборатория"]
        Raw["Сырые задачи / Логи / Заметки"] --> NLM["NotebookLM <br/>(Анализ, дедупликация, дельта)"]
        NLM --> IntKROOF["Блок оценки ИнтКРООФ <br/>(Интерпретатор / Ручной контур)"]
        IntKROOF --> Golden["«Золотые стандарты» <br/>(Шаблоны заданий)"]
    end

    subgraph Prod ["Контур 2: Автоматический продакшн"]
        Shortcut["Хоткей / Raycast / Скрипты"] --> Aider["Aider CLI / псевдоним 'пом'"]
        Golden -.-> Sync["sync_prompts.py"]
        Sync --> Repo["Репозиторий AI_Pipeline / Tennis_Brain"]
        Repo --> Aider
        Aider --> Execute["Выполнение в терминале <br/>(Строгий протокол «Думаем → Делаем»)"]
    end

    Execute --> Vahta["Утилита вахты <br/>(.scripts/vahta.py)"]
    Vahta --> Journal["Вахтенный журнал <br/>( Obsidian Markdown )"]
    Journal --> Git["Git Push / Remote Guard <br/>( Синхронизация с GitHub )"]
    Git --> ShiftEnd["Команда «Сдать смену» <br/>( Очистка контекста / Context Rot Protection )"]

    style Lab fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4
    style Prod fill:#1e1e2e,stroke:#a6e3a1,stroke-width:2px,color:#cdd6f4