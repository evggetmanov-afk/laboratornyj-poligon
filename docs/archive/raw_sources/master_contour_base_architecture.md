---
cssclasses:
  - landscape
---

# Мастер-контур: Базовая архитектура

```mermaid
flowchart LR
    %% ========================================================
    %% ВЕРХНИЙ ЭТАЖ: УПРАВЛЕНИЕ И СТАНДАРТЫ (Сверху вниз ↓)
    %% ========================================================
    subgraph GovernancePlane [ВЕРХНИЙ КОНТУР: УПРАВЛЕНИЕ И СТАНДАРТЫ]
        direction TB
        Manager[Управленец / Архитектор среды<br><i>Контроль актуальности и непротиворечивости</i>]
        
        subgraph StandardsStore [Нормативная база]
            direction LR
            StdMaster[(Стандарты мастера)]
            StdClient[(Стандарты заказчика)]
        end
        
        Manager -->|Аудит, версионирование, устранение коллизий| StdMaster
        Manager -.->|Верификация требований| StdClient
    end

    %% ========================================================
    %% СРЕДНИЙ ЭТАЖ: ПРОИЗВОДСТВЕННЫЙ КОНВЕЙЕР (Слева направо →)
    %% ========================================================
    ExtClient[Внешний заказчик] --> RawIn[Папка: raw inbox]
    ExtClient -.->|Передача требований| StdClient
    
    RawIn --> InGate[Входной шлюз переноса]
    
    subgraph MasterZone [ПРОИЗВОДСТВЕННЫЙ КОНТУР МАСТЕРА]
        direction LR
        InCard[Входная карточка задания] --> MasterCore[Мастер]
        MasterCore --> OutBox[Папка: outbox]
    end

    InGate --> InCard
    OutBox --> OutGate[Выходной шлюз преобразования]
    OutGate --> ReadyOut[Папка готовой продукции]
    
    subgraph ExtSystem [ПРИЕМКА ВНЕШНЕЙ СИСТЕМЫ]
        direction LR
        Receiver[Инструмент приёмки] --> ClientPipeline[(База / пайплайн заказчика)]
    end
    ReadyOut --> Receiver

    %% ========================================================
    %% НИЖНИЙ ЭТАЖ: ОБЕСПЕЧЕНИЕ И СРЕДА (Снизу вверх ↑)
    %% ========================================================
    subgraph SupportPlane [НИЖНИЙ КОНТУР: ОБЕСПЕЧЕНИЕ И СРЕДА]
        Sandbox[Песочница / Зона экспериментов]
    end

    %% ========================================================
    %% МЕЖУРОВНЕВЫЕ СВЯЗИ
    %% ========================================================
    %% Управление (Сверху вниз)
    StdMaster -->|Регламент входа| InGate
    StdClient -->|Регламент выхода| OutGate

    %% Обеспечение (Снизу вверх)
    Sandbox <-->|Среда отладки| MasterCore
    Manager -.->|Контроль готовности среды| Sandbox

    %% ========================================================
    %% СТИЛИЗАЦИЯ
    %% ========================================================
    classDef manager fill:#fff9c4,stroke:#f57f17,stroke-width:2px;
    classDef control fill:#f9fbe7,stroke:#827717,stroke-width:1.5px;
    classDef process fill:#ffffff,stroke:#263238,stroke-width:1.5px;
    classDef support fill:#ede7f6,stroke:#512da8,stroke-width:1.5px,stroke-dasharray: 4 4;
    classDef boundary fill:#f8f9fa,stroke:#b0bec5,stroke-width:1px;

    class Manager manager;
    class StdMaster,StdClient control;
    class ExtClient,RawIn,InGate,InCard,MasterCore,OutBox,OutGate,ReadyOut,Receiver,ClientPipeline process;
    class Sandbox support;
    class GovernancePlane,StandardsStore,MasterZone,ExtSystem,SupportPlane boundary;
```