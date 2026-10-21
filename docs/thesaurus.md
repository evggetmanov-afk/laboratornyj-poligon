# Тезаурус и Словарь системы

Единая витрина понятийного аппарата и онтологии «Лабораторного полигона» и проекта «Tennis Blitz».

> **Инвариант архитектуры (ADR-004):** Данный файл является представлением только для чтения (Read-Only View). Прямое редактирование файла запрещено. Все канонические сущности ведутся строго в виде атомарных карточек в каталоге `docs/thesaurus/*.md`[cite: 1].

---

## 1. Динамическая витрина (Obsidian Dataview)

```dataview
TABLE 
  id as "ID",
  domain as "Домен",
  aliases as "Синонимы (aliases)",
  presentation_mapping.client_label as "Клиентский фасад",
  status as "Статус"
FROM "docs/thesaurus"
WHERE file.name != "TEMPLATE" AND file.name != "thesaurus"
SORT id ASC