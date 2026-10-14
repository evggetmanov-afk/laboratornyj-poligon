#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def main():
    repo_root = Path.home() / "Лабораторный_полигон"
    vault = repo_root / "projects/dispetcher/vault"
    system_dir = vault / "00_System"

    core_files = [
        system_dir / "SESSION_BOOT.md",
        system_dir / "Specs/SPEC-CLI-001_Ephemeral_Scaffolding.md",
        system_dir / "Specs/SPEC-OPS-001_Crystallization_Protocol.md",
        system_dir / "Specs/SPEC-ABC-001_Transformation_Method.md",
        system_dir / "Templates/TPL-ABC-001_Card_Template.md",
    ]

    bundle = ["=== DISPETCHER CONTEXT BOOT: NATIVE REPOSITORY SPECS ===\n"]

    for fpath in core_files:
        if fpath.exists():
            rel = fpath.relative_to(vault)
            bundle.append(f"\n--- FILE: {rel} ---\n")
            bundle.append(fpath.read_text(encoding="utf-8").strip())
        else:
            bundle.append(f"\n--- FILE MISSING: {fpath.name} ---")

    full_text = "\n".join(bundle)

    tmp_out = Path("/tmp/dispetcher_context.txt")
    tmp_out.write_text(full_text, encoding="utf-8")

    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(full_text.encode("utf-8"))
        clipboard_status = "Скопировано в буфер обмена (Cmd+V)"
    except Exception:
        clipboard_status = "pbcopy недоступен"

    print(f"OK: Собрано документов: {len(core_files)}")
    print(f"OK: Дамп сохранен в {tmp_out}")
    print(f"OK: {clipboard_status}")

if __name__ == "__main__":
    main()
