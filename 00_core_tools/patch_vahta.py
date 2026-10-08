import re

vahta_file = "00_core_tools/vahta.py"
try:
    with open(vahta_file, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Добавляем вызов валидатора перед формированием пакета передачи смены
    verify_call = """
    # Проверка физических артефактов перед передачей смены
    verify_script = os.path.join(CORE_DIR, "verify_task.py") if 'CORE_DIR' in locals() else "00_core_tools/verify_task.py"
    if os.path.exists(verify_script):
        ret = os.system(f"python3 {verify_script}")
        if ret != 0:
            print("\\n❌ Передача смены остановлена: устраните фантомные задачи в TASK.md!")
            sys.exit(1)
"""
    
    # 2. Обеспечиваем гарантированное прикрепление системного промпта к контексту
    prompt_inject = """
    prompt_file = "00_core_tools/prompts/Системный_промпт_взаимодействия.md"
    prompt_content = ""
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as pf:
            prompt_content = pf.read().strip() + "\\n\\n---\\n\\n"
"""

    print("✅ Логика патча сформирована. Применяем к 00_core_tools/vahta.py")
except Exception as e:
    print(f"Ошибка чтения: {e}")
