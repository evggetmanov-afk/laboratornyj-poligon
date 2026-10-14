---
type: dashboard
status: active
created: 2026-10-14
updated: 2026-10-14
tags:
  - system/dashboard
  - status/active
---

# 🎛️ ДИСПЕТЧЕР: Оперативная витрина

> **Контур:** Инкубация (Фаза 0) | **Архитектура:** ADR-001, ADR-002 | **Режим:** Квантованные такты

---

## 📌 Текущий фокус и статус
- **Активный такт:** Такт 006 (Развертывание витрины оператора)
- **Следующий шаг:** Такт 007 (Процессинг первого требования из Inbox)
- **Контур постоянных заметок:** [[02_Notes]]
- **Состояние ядра:** [[00_System/STATE|STATE.md]]
- **Манифест системы:** [[00_System/MANIFEST|MANIFEST.md]]
- **Реестр входящих:** [[00_System/INBOX_REGISTRY|INBOX_REGISTRY.md]]
- **Словарь тегов:** [[00_System/Specs/Taxonomy/tags_dictionary|tags_dictionary.md]]

---

## 📥 Входящие требования (Inbox Pipeline)
Полный перечень из 26 базовых требований доступен в реестре:
👉 **[[00_System/INBOX_REGISTRY|Открыть реестр входящих требований (REQ-001 ... REQ-026)]]**

---

## 🏛️ Принятые архитектурные решения (ADR)
- [[00_System/Decisions/ADR-001_Git_Isolation|ADR-001: Изоляция Git-контура]]
- [[00_System/Decisions/ADR-002_Incubation_Mode|ADR-002: Режим инкубации]]

---

## 📐 Канонические шаблоны
- [[00_System/Templates/tpl_requirement|tpl_requirement]] — Шаблон требования
- [[00_System/Templates/tpl_adr|tpl_adr]] — Шаблон архитектурного решения
- [[00_System/Templates/tpl_concept|tpl_concept]] — Шаблон концепции
- [[00_System/Templates/tpl_session|tpl_session]] — Шаблон сессии

---

## ⚠️ Правила работы на станке (Negative Constraints)
1. **Запрет сырого многострочного шелла:** Никаких `cat << EOF` и `python3 -c` в терминале Zsh.
2. **Детерминизм такта:** 1 такт = 1 физический артефакт + верификация + Git-коммит с префиксом `vault(tact-xxx): ...`.
3. **Реакция на сбой:** Факт -> Причина -> Дельта -> Новое правило.