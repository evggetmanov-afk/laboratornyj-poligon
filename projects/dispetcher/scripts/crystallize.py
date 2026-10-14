
def get_next_cn_id(notes_dir):
    import glob, os, re
    files = glob.glob(os.path.join(notes_dir, "*.md"))
    nums = []
    for f in files:
        m = re.search(r"CN-(\d+)", os.path.basename(f))
        if m:
            nums.append(int(m.group(1)))
    next_num = max(nums) + 1 if nums else 1
    return f"CN-{next_num:03d}"

#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from datetime import date
import subprocess

if len(sys.argv) < 4:
    print("Использование: python3 crystallize.py <REQ_ID> <CN_ID> <CN_SLUG> <TITLE> <TAGS> <CONTENT_FILE_OR_STDIN>")
    sys.exit(1)

req_id = sys.argv[1].upper()       # например: REQ-003
cn_id = get_next_cn_id("projects/dispetcher/vault/02_Notes") if sys.argv[2].upper() == "AUTO" else sys.argv[2].upper()        # например: CN-003
cn_slug = sys.argv[3]              # например: Quantum_Tacts
title = sys.argv[4]                # например: Квантованность тактов деятельности
tags_str = sys.argv[5]             # например: concept/process,status/active

root = Path("/Users/getmanov/Лабораторный_полигон/projects/dispetcher/vault")
notes_dir = root / "02_Notes"
registry_file = root / "00_System" / "INBOX_REGISTRY.md"
cn_filename = f"{cn_id}_{cn_slug}.md"
cn_path = notes_dir / cn_filename

# Читаем тело заметки из stdin
content = sys.stdin.read().strip()
today = date.today().isoformat()

# Формируем фронтматтер
tags_formatted = "\n".join([f"  - {t.strip()}" for t in tags_str.split(",")])
note_text = f"""---
type: concept
status: active
created: {today}
updated: {today}
tags:
{tags_formatted}
---

# {cn_id}: {title}

> **Статус:** Действует | **Родительское требование:** [[01_Inbox/Baseline_Requirements/{req_id}|{req_id}]] | **Контур:** 02_Notes

---

{content}

---

## 🔗 Связанные сущности
- [[01_Inbox/Baseline_Requirements/{req_id}|{req_id}: Исходное требование]]
- [[00_System/INBOX_REGISTRY|INBOX_REGISTRY.md]]
"""

# 1. Записываем концепт в 02_Notes
notes_dir.mkdir(parents=True, exist_ok=True)
cn_path.write_text(note_text, encoding="utf-8")
print(f"✅ Создана концепция: {cn_path.name}")

# 2. Обновляем INBOX_REGISTRY.md
if registry_file.exists():
    reg_text = registry_file.read_text(encoding="utf-8")
    # Ищем строчку с данным REQ и заменяем [ ] на [x] с добавлением ссылки
    pattern = rf"-\s*\[[ xX]\]\s*(\[\[[^\]]*{req_id}[^\]]*\]\][^\n]*)"
    replacement = rf"- [x] \1 — обработано в [[02_Notes/{cn_id}_{cn_slug}|{cn_id}]]"
    
    # Если уже было "обработано в", просто обновляем
    if f"{req_id}" in reg_text:
        new_reg_text = re.sub(
            rf"-\s*\[[ xX]\]\s*(\[\[01_Inbox/Baseline_Requirements/{req_id}[^\|]*\|{req_id}:?[^\]]*\]\])(?:\s*—\s*обработано[^\n]*)?",
            rf"- [x] \1 — обработано в [[02_Notes/{cn_id}_{cn_slug}|{cn_id}]]",
            reg_text
        )
        registry_file.write_text(new_reg_text, encoding="utf-8")
        print(f"✅ Обновлен реестр {registry_file.name}: {req_id} -> [x]")

# 3. Делаем git add и commit
repo_root = Path("/Users/getmanov/Лабораторный_полигон")
commit_msg = f"vault: process {req_id} into concept {cn_id} {title}"
subprocess.run(["git", "-C", str(repo_root), "add", str(cn_path), str(registry_file)], check=True)
res = subprocess.run(["git", "-C", str(repo_root), "commit", "-m", commit_msg], capture_output=True, text=True)
print(res.stdout.strip())
