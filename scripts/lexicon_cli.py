#!/usr/bin/env python3
"""
scripts/lexicon_cli.py
Ревизор семантического слоя и тезауруса "Лабораторного полигона" (Фаза 2: On-Demand).

Использование:
  python3 scripts/lexicon_cli.py <путь_к_документу.md>
  python3 scripts/lexicon_cli.py --dump-llm
"""

import sys
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
THESAURUS_DIR = REPO_ROOT / "docs" / "thesaurus"


def parse_frontmatter(file_path: Path) -> dict:
    """Извлекает ключевые поля из YAML frontmatter без сторонних библиотек."""
    meta = {
        "id": "",
        "term": "",
        "domain": "",
        "aliases": [],
        "client_label": "",
        "status": ""
    }
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return meta

    if not content.startswith("---"):
        return meta

    parts = content.split("---", 2)
    if len(parts) < 3:
        return meta

    fm_lines = parts[1].splitlines()
    in_aliases = False
    in_presentation = False

    for line in fm_lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        if line_stripped.startswith("aliases:"):
            in_aliases = True
            in_presentation = False
            continue
        elif line_stripped.startswith("presentation_mapping:"):
            in_aliases = False
            in_presentation = True
            continue
        elif not line.startswith(" ") and not line.startswith("\t"):
            in_aliases = False
            in_presentation = False

        if in_aliases and line_stripped.startswith("-"):
            alias = line_stripped.lstrip("-").strip().strip('"').strip("'")
            if alias:
                meta["aliases"].append(alias)
            continue

        if in_presentation and line_stripped.startswith("client_label:"):
            val = line_stripped.split(":", 1)[1].strip().strip('"').strip("'")
            meta["client_label"] = val
            continue

        if ":" in line_stripped and not in_aliases and not in_presentation:
            k, v = line_stripped.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in meta and k != "aliases":
                meta[k] = v

    return meta


def load_lexicon_index() -> list:
    """Загружает утвержденные словарные единицы из docs/thesaurus/."""
    index = []
    if not THESAURUS_DIR.exists():
        return index

    for p in THESAURUS_DIR.glob("*.md"):
        if p.name.lower() in ("template.md", "thesaurus.md"):
            continue
        meta = parse_frontmatter(p)
        if meta.get("term"):
            meta["file_path"] = str(p.relative_to(REPO_ROOT))
            index.append(meta)

    return sorted(index, key=lambda x: x.get("id", ""))


def dump_for_llm(index: list):
    """Генерирует компактный срез онтологии для системных промптов."""
    print("<system_ontology>")
    for item in index:
        aliases_str = ", ".join(item["aliases"]) if item["aliases"] else "—"
        label = item["client_label"] if item["client_label"] else item["term"]
        print(f"  <concept id=\"{item['id']}\" domain=\"{item['domain']}\">")
        print(f"    <term>{item['term']}</term>")
        print(f"    <aliases>{aliases_str}</aliases>")
        print(f"    <client_label>{label}</client_label>")
        print(f"  </concept>")
    print("</system_ontology>")


def scan_document(doc_path: Path, index: list):
    """Сканирует Markdown-документ на термины, синонимы и неизвестные вики-ссылки."""
    if not doc_path.exists():
        print(f"❌ Файл не найден: {doc_path}")
        sys.exit(1)

    content = doc_path.read_text(encoding="utf-8")
    content_lower = content.lower()

    found_terms = []
    found_aliases = []

    for item in index:
        term = item["term"]
        pattern_term = r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)"
        if re.search(pattern_term, content_lower):
            found_terms.append(item)

        for alias in item["aliases"]:
            pattern_alias = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"
            if re.search(pattern_alias, content_lower):
                found_aliases.append((alias, item))

    wiki_links = re.findall(r"\[\[(.*?)\]\]", content)
    known_terms = {item["term"].lower() for item in index}
    for item in index:
        for a in item["aliases"]:
            known_terms.add(a.lower())

    unknown_candidates = []
    for link in wiki_links:
        clean_link = link.split("|")[0].strip()
        if clean_link.lower() not in known_terms:
            unknown_candidates.append(clean_link)

    print(f"\n📋 [РЕВИЗИЯ СЕМАНТИКИ] Файл: {doc_path.relative_to(REPO_ROOT) if doc_path.is_relative_to(REPO_ROOT) else doc_path.name}")
    print("=" * 64)

    print(f"\n1. Точные термины ядра ({len(found_terms)}):")
    if found_terms:
        for t in found_terms:
            print(f"   ✓ [{t['id']}] {t['term']} (домен: {t['domain']})")
    else:
        print("   — Точных вхождений не обнаружено.")

    print(f"\n2. Обнаруженные синонимы/жаргонизмы ({len(found_aliases)}):")
    if found_aliases:
        for alias, t in found_aliases:
            print(f"   ➜ Найдено: «{alias}» → Канонический узел: [{t['id']}] {t['term']}")
    else:
        print("   — Синонимов или жаргонизмов не обнаружено.")

    print(f"\n3. Кандидаты на регистрацию (новые [[ссылки]]) ({len(unknown_candidates)}):")
    if unknown_candidates:
        for c in set(unknown_candidates):
            print(f"   ? [[{c}]] (нет в docs/thesaurus/)")
    else:
        print("   — Все ссылки согласованы с тезаурусом.")

    print("\n" + "=" * 64)


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 scripts/lexicon_cli.py <документ.md> | --dump-llm")
        sys.exit(1)

    index = load_lexicon_index()

    arg = sys.argv[1]
    if arg == "--dump-llm":
        dump_for_llm(index)
    else:
        doc_path = (REPO_ROOT / arg).resolve()
        scan_document(doc_path, index)


if __name__ == "__main__":
    main()