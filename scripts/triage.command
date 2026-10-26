#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
echo "=== САНИТАРНЫЙ ОСМОТР ОТСТОЙНИКОВ ==="
python3 scripts/inbox_triage.py --dry-run
echo ""
echo "Нажмите Enter для выхода..."
read -r