# Блок-схема процесса обработки заметок в Knowledge Pipeline

Документ визуализирует жизненный цикл входящего сырья от момента попадания в приемный шлюз до фиксации атомарной сущности в базе знаний Obsidian и коммита в репозиторий Git.

---

## 1. ДИАГРАММА ПОТОКА

```mermaid
flowchart TD
    %% Определение стилей узлов
    classDef storage fill:#2b303c,stroke:#6c7a96,stroke-width:1px,color:#fff;
    classDef accent fill:#1f425f,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef warn fill:#4a3512,stroke:#f59e0b,stroke-width:1px,color:#fff;
    classDef success fill:#163824,stroke:#10b981,stroke-width:2px,color:#fff;

    subgraph C2 ["Контур 2: Операционный цикл (Google Диск)"]
        raw_inbox["📥 kp_inbox / 00_raw_inbox<br/>(Сырые заметки, веб-клипы, расшифровки)"]:::storage
        ingest_step["⚙️ raw_to_inbox.py<br/>(Присвоение ID: YYYYMMDDHHMMSS_raw)"]:::accent
        extract_step["🧠 Экстракция сути / Ревью<br/>(Пакетный разбор контекста)"]:::accent
    end

    subgraph Filter ["Шлюз валидации и чистоты"]
        check_quality{"Качество сырья<br/>и ценность?"}:::warn
        archive_raw["🗄️ Архив сырья (Google Диск)<br/>(Политика No-Delete)"]:::storage
        quarantine_node["🪞 _quarantine / Отсев<br/>(Тяжелые файлы, дубли, брак)"]:::warn
    end

    subgraph C1 ["Контур 1: Рабочее ядро (SSD MacBook / Git)"]
        atomic_card["📝 Атомарная карточка<br/>(Формат ABC / ADR / Markdown)"]:::accent
        save_stream["📋 Clipboard Stream<br/>(### FILE: ... + save / apply_payload.py)"]:::accent
        obsidian_vault["📦 ready/ / docs/<br/>(Obsidian Vault & Git Commit)"]:::success
    end

    %% Потоки данных
    raw_inbox --> ingest_step
    ingest_step --> extract_step
    extract_step --> check_quality

    check_quality -- "Мусор / Брак" --> quarantine_node
    check_quality -- "Ценно" --> atomic_card
    atomic_card -. "Сырец перенесен" .-> archive_raw

    atomic_card --> save_stream
    save_stream --> obsidian_vault
