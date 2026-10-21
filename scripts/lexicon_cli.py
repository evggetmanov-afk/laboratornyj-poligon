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
    except Exception as e:
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
        raw_line = line
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "aliases:":
            in_aliases = True
            in_presentation = False
            continue
        elif stripped == "presentation_mapping:":
            in_presentation = True
            in_aliases = False
            continue
        elif re.match(r"^[a-zA-Z_0-9]+:", stripped):
            in_aliases = False
            in_presentation = False

        if in_aliases:
            if stripped.startswith("- "):
                val = stripped[2:].strip().strip('"').strip("'")
                if val:
                    meta["aliases"].append(val)
            continue

        if in_presentation:
            if stripped.startswith("client_label:"):
                val = stripped.split("client_label:", 1)[1].strip().strip('"').strip("'")
                meta["client_label"] = val
            continue

        if ":" in stripped:
            k, v = stripped.split(":", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in meta:
                meta[k] = v

    return meta


def load_lexicon_index() -> list:
    """Загружает утвержденные словарные единицы из docs/thesaurus/."""
    index = []
    if not THESAURUS_DIR.exists():
        return index

    for p in THESAURUS_DIR.glob("*.md"):
        if p.name in ("TEMPLATE.md", "thesaurus.md"):
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
        t = item["term"]
        if t and t.lower() in content_lower:
            found_terms.append(item)
            continue

        matched_alias = None
        for a in item["aliases"]:
            if a.lower() in content_lower:
                matched_alias = a
                break
        if matched_alias:
            found_aliases.append((item, matched_alias))

    wiki_links = set(re.findall(r"\[\[(.*?)\]\]", content))
    unresolved_candidates = []

    known_keys = set()
    for item in index:
        if item["term"]:
            known_keys.add(item["term"].lower())
        for a in item["aliases"]:
            known_keys.add(a.lower())

    for link in wiki_links:
        clean_target = link.split("|")[0].strip()
        clean_name = clean_target.split("/")[-1].replace(".md", "").strip().lower()
        if clean_name not in known_keys and not any(item["id"].lower() == clean_name for item in index):
            unresolved_candidates.append(clean_target)

    print(f"\n📋 [РЕВИЗИЯ СЕМАНТИКИ] Файл: {doc_path.relative_to(REPO_ROOT) if doc_path.is_relative_to(REPO_ROOT) else doc_path}")
    print("=" * 64)

    print(f"\n1. Точные термины ядра ({len(found_terms)}):")
    if found_terms:
        for it in found_terms:
            print(f"   ✓ [{it['id']}] {it['term']} (домен: {it['domain']})")
    else:
        print("   — Прямых вхождений канонических терминов не обнаружено.")

    print(f"\n2. Обнаруженные синонимы/жаргонизмы ({len(found_aliases)}):")
    if found_aliases:
        for it, alias in found_aliases:
            print(f"   ➜ Найдено: «{alias}» → Канонический узел: [{it['id']}] {it['term']}")
    else:
        print("   — Альтернативных формулировок не обнаружено.")

    print(f"\n3. Кандидаты на регистрацию (новые [[ссылки]]) ({len(unresolved_candidates)}):")
    if unresolved_candidates:
        for c in sorted(unresolved_candidates):
            print(f"   ? [[{c}]] (нет в docs/thesaurus/)")
    else:
        print("   — Все ссылки согласованы с тезаурусом.")

    print("\n" + "=" * 64)


def main():
    if len(sys.argv) < 2:
        print("Использование:\n  python3 scripts/lexicon_cli.py <путь_к_документу.md>\n  python3 scripts/lexicon_cli.py --dump-llm")
        sys.exit(1)

    arg = sys.argv[1]
    index = load_lexicon_index()

    if arg == "--dump-llm":
        dump_for_llm(index)
        return

    target_file = Path(arg).resolve()
    scan_document(target_file, index)


if __name__ == "__main__":
    main()