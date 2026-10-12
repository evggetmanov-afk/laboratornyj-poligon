import subprocess
from pathlib import Path

# Автоматическое определение корня полигона из расположения скрипта (scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

def get_file_content(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"[Файл не найден: {path.name}]"

def build_vahta_packet():
    # 1. Тонкий мета-контракт и поведенческий протокол (анти-сикофантия)
    meta_contract = (
        "SYSTEM CONTRACT & BEHAVIORAL PROTOCOL:\n"
        "1. Работай строго по правилам, инвариантам и стандартам, описанным в папке methodology/.\n"
        "2. Локальный репозиторий лабораторного полигона — единственный источник правды (SSOT).\n"
        "3. КОММУНИКАТИВНЫЙ ФИЛЬТР:\n"
        "   - Категорически запрещено хвалить пользователя, восхищаться его решениями или говорить, какой он гениальный.\n"
        "   - Никаких попыток угождать, подстраиваться под мнение ради вежливости или сглаживать углы.\n"
        "   - Стиль общения: слегка скептичный, прямой, аналитичный и ироничный. Если в архитектуре или логике есть дыра — указывай на нее сразу и жестко.\n\n"
    )
    
    # 2. Проектный паспорт
    project_passport_path = ROOT_DIR / "PROJECT_PASSPORT.md"
    project_passport = f"--- ПРОЕКТНЫЙ ПАСПОРТ ---\n{get_file_content(project_passport_path)}\n\n"

    # 3. Реестр ролей
    roles_path = ROOT_DIR / "ROLES_REGISTRY.md"
    roles_passport = f"--- РЕЕСТР РОЛЕЙ ---\n{get_file_content(roles_path)}\n\n"

    # 4. Последняя карточка вахтенного журнала из watch_log
    journal_dir = ROOT_DIR / "watch_log"
    journals = sorted(journal_dir.glob("Журнал *.md")) if journal_dir.exists() else []
    latest_journal = journals[-1].read_text(encoding="utf-8") if journals else "Журналы в watch_log отсутствуют."
    journal_block = f"--- АКТУАЛЬНЫЙ КОНТЕКСТ СМЕНЫ ---\n{latest_journal}"

    # Сборка итогового пакета в буфер обмена
    packet = f"{meta_contract}{project_passport}{roles_passport}{journal_block}"
    
    process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(packet.encode('utf-8'))
    print("Пакет вахты лабораторного полигона успешно собран и скопирован в буфер обмена.")

if __name__ == "__main__":
    build_vahta_packet()