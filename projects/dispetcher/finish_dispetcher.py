import os
import sys
import shutil
import subprocess

VAULT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vault'))
INBOX = os.path.join(VAULT, '01_Inbox')
L_DIR = os.path.join(INBOX, '03_Processing')
A_DIR = os.path.join(INBOX, '04_Processed')
REGISTRY = os.path.join(VAULT, '00_System', 'INBOX_REGISTRY.md')

def get_files(d):
    return [f for f in sorted(os.listdir(d)) if f.endswith('.md') and not f.startswith('.')] if os.path.exists(d) else []

l_files = get_files(L_DIR)

if not l_files:
    print('[!] Ошибка: 01_Inbox/03_Processing пуст. Нет активного такта для закрытия.')
    sys.exit(1)

raw_file = l_files[0]
src_raw = os.path.join(L_DIR, raw_file)
dst_raw = os.path.join(A_DIR, raw_file)

# 1. Перемещение отработанного сырья в архив
shutil.move(src_raw, dst_raw)
print(f'[✓] Сырьё перемещено в архив: 01_Inbox/04_Processed/{raw_file}')

# 2. Обновление реестра (если существует)
if os.path.exists(REGISTRY):
    try:
        with open(REGISTRY, 'a', encoding='utf-8') as f:
            f.write(f"\n| {raw_file} | processed | [[01_Inbox/04_Processed/{raw_file}]] |")
        print(f'[✓] Запись добавлена в {os.path.basename(REGISTRY)}')
    except Exception as e:
        print(f'[!] Не удалось обновить реестр: {e}')

# 3. Фиксация в Git
try:
    subprocess.run(['git', 'add', '.'], check=True)
    commit_msg = f"feat(dispetcher): finalize quantum {raw_file}"
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
    print(f'[✓] Git commit успешно создан: "{commit_msg}"')
except Exception as e:
    print(f'[!] Git commit пропущен или завершился с ошибкой: {e}')

print(f'\n[🏁] Такт успешно закрыт. Замок 03_Processing снят. Система готова к следующему циклу.')
