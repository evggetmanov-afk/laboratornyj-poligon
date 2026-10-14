import os, sys, shutil, subprocess

VAULT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vault'))
INBOX = os.path.join(VAULT, '01_Inbox')
Q_DIR = os.path.join(INBOX, '01_Queue')
P_DIR = os.path.join(INBOX, '02_Priority')
L_DIR = os.path.join(INBOX, '03_Processing')
A_DIR = os.path.join(INBOX, '04_Processed')

def get_files(d):
    return [f for f in sorted(os.listdir(d)) if f.endswith('.md') and not f.startswith('.')] if os.path.exists(d) else []

l_files = get_files(L_DIR)
p_files = get_files(P_DIR)
q_files = get_files(Q_DIR)

if l_files:
    target = os.path.join(L_DIR, l_files[0])
    status = 'RECOVERY'
elif p_files:
    target = os.path.join(L_DIR, p_files[0])
    shutil.move(os.path.join(P_DIR, p_files[0]), target)
    status = 'PRIORITY'
elif q_files:
    target = os.path.join(L_DIR, q_files[0])
    shutil.move(os.path.join(Q_DIR, q_files[0]), target)
    status = 'FIFO_QUEUE'
else:
    print('[i] Очередь пуста. 01_Inbox в режиме IDLE.')
    sys.exit(0)

fname = os.path.basename(target)
with open(target, 'r', encoding='utf-8') as f:
    body = f.read()

msg = f"""# СТАРТ: КОНТУР 2 (ИСПОЛНИТЕЛЬ)
Статус: {status}
Файл: 01_Inbox/03_Processing/{fname}

## ИНВАРИАНТЫ (ADR-003):
- Создать CN-заметку в 02_Notes/ (или спецификацию в 00_System/Specs/)
- Обязательное поле онтология: гипотеза | факт | правило | закон
- Ссылка на raw: [[01_Inbox/04_Processed/{fname}]]
- Переместить сырье по завершении:
  mv 01_Inbox/03_Processing/{fname} 01_Inbox/04_Processed/{fname}
- Обновить INBOX_REGISTRY.md и сделать Git commit

---
{body}"""

try:
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(msg.encode('utf-8'))
    print(f'[✓] Захвачен: {fname} [{status}]. Контекст в буфере (Cmd+V).')
except Exception as e:
    print(msg)
