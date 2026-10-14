---
id: {{TIMESTAMP_UID}}
title: "{{TITLE}}"
date: {{DATE}}
source_raw: "[[01_Inbox/04_Processed/{{SOURCE_FILE}}]]"
онтология: гипотеза | факт | правило | закон
status: crystallized
tags:
  - knowledge
  - crystal
---

# {{TITLE}}

## 1. Сущность и контекст
{{CONTENT}}

## 2. Физическое обоснование
- Источник: `{{SOURCE_FILE}}`
- Слой знания: `онтология`

## 3. Вектор влияния на систему
- Если факт: накапливается в базе `02_Notes/`.
- Если правило: обновляет регламенты `00_System/Operations/` или промпты станков.
- Если закон: вносит изменения в инварианты ядра `00_System/Specs/` или ADR.
