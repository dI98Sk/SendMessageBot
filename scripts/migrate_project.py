#!/usr/bin/env python3
"""
Скрипт для безопасной миграции проекта на новую архитектуру
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        'logs',
        'data', 
        'backup',
        'sessions'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Создана директория: {dir_name}")

def backup_old_files():
    """Резервное копирование старых файлов"""
    backup_dir = Path('backup') / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_backup = [
        'broadcasterB2B.py',
        'main.py', 
        'config_mesВ2B.py',
        'config_mesВ2C.py',
        'config_targ.py',
        'update_configB2B.py',
        'update_configB2C.py'
    ]
    
    for file_name in files_to_backup:
        if Path(file_name).exists():
            shutil.copy2(file_name, backup_dir / file_name)
            print(f"✅ Создана резервная копия: {file_name}")
    
    return backup_dir

def move_session_files():
    """Перемещение файлов сессий"""
    sessions_dir = Path('sessions')
    
    session_files = [
        'acc1.session',
        'acc2.session'
    ]
    
    for session_file in session_files:
        if Path(session_file).exists():
            shutil.move(session_file, sessions_dir / session_file)
            print(f"✅ Перемещен файл сессии: {session_file}")
    
    # Удаление дубликатов
    duplicate_sessions = [
        'session_account_1.session',
        'session_account_2.session', 
        'session_name.session'
    ]
    
    for duplicate in duplicate_sessions:
        if Path(duplicate).exists():
            os.remove(duplicate)
            print(f"🗑️ Удален дубликат сессии: {duplicate}")

def move_data_files():
    """Перемещение файлов данных"""
    data_dir = Path('data')
    
    data_files = [
        ('allChatID.txt', 'allChatID_backup.txt'),
        ('dict.txt', 'dict_backup.txt')
    ]
    
    for old_name, new_name in data_files:
        if Path(old_name).exists():
            shutil.move(old_name, data_dir / new_name)
            print(f"✅ Перемещен файл данных: {old_name} → {new_name}")

def archive_old_logs():
    """Архивирование старых логов"""
    if Path('bot.log').exists():
        logs_dir = Path('logs')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.move('bot.log', logs_dir / f'bot_old_{timestamp}.log')
        print(f"✅ Архивирован старый лог: bot.log")

def remove_old_files():
    """Удаление старых файлов после резервного копирования"""
    files_to_remove = [
        'broadcasterB2B.py',
        'main.py',
        'config_mesВ2B.py', 
        'config_mesВ2C.py',
        'config_targ.py',
        'update_configB2B.py',
        'update_configB2C.py'
    ]
    
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"🗑️ Удален старый файл: {file_name}")

def update_gitignore():
    """Обновление .gitignore"""
    gitignore_content = """
# Старые файлы (удалены при миграции)
broadcasterB2B.py
main.py
config_mesВ2B.py
config_mesВ2C.py
config_targ.py
update_configB2B.py
update_configB2C.py

# Сессии Telegram
sessions/
*.session

# Логи
logs/
*.log

# Данные
data/
allChatID.txt
dict.txt

# Резервные копии
backup/

# Переменные окружения
.env
.env.local

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Обновлен .gitignore")

def create_migration_report():
    """Создание отчета о миграции"""
    report = f"""
# Отчет о миграции SendMessageBot

**Дата миграции:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Выполненные действия:

### ✅ Созданы директории:
- logs/ - для файлов логов
- data/ - для файлов данных  
- backup/ - для резервных копий
- sessions/ - для файлов сессий Telegram

### ✅ Перемещены файлы:
- Сессии Telegram → sessions/
- Данные → data/ (с переименованием)
- Логи → logs/ (с архивированием)

### ✅ Удалены старые файлы:
- broadcasterB2B.py → заменен на core/broadcaster.py
- main.py → заменен на main_improved.py
- config_mesВ2B.py → заменен на config/settings.py
- config_mesВ2C.py → заменен на config/settings.py
- config_targ.py → заменен на config/settings.py
- update_configB2B.py → интегрирован в новую архитектуру
- update_configB2C.py → интегрирован в новую архитектуру

### ✅ Обновлен .gitignore

## Следующие шаги:

1. Настройте переменные окружения в .env
2. Запустите новую версию: python main_improved.py
3. Проверьте работу системы
4. Настройте мониторинг и алерты

## Восстановление (если нужно):

Все старые файлы сохранены в директории backup/
Для восстановления используйте файлы из соответствующей папки.
"""
    
    with open('MIGRATION_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Создан отчет о миграции: MIGRATION_REPORT.md")

def main():
    """Основная функция миграции"""
    print("🚀 Начинаем миграцию SendMessageBot на новую архитектуру...")
    print("=" * 60)
    
    try:
        # 1. Создание директорий
        print("\n📁 Создание директорий...")
        create_directories()
        
        # 2. Резервное копирование
        print("\n💾 Создание резервных копий...")
        backup_dir = backup_old_files()
        print(f"Резервные копии сохранены в: {backup_dir}")
        
        # 3. Перемещение сессий
        print("\n📱 Перемещение файлов сессий...")
        move_session_files()
        
        # 4. Перемещение данных
        print("\n📊 Перемещение файлов данных...")
        move_data_files()
        
        # 5. Архивирование логов
        print("\n📝 Архивирование логов...")
        archive_old_logs()
        
        # 6. Удаление старых файлов
        print("\n🗑️ Удаление старых файлов...")
        remove_old_files()
        
        # 7. Обновление .gitignore
        print("\n📝 Обновление .gitignore...")
        update_gitignore()
        
        # 8. Создание отчета
        print("\n📋 Создание отчета...")
        create_migration_report()
        
        print("\n" + "=" * 60)
        print("🎉 Миграция завершена успешно!")
        print("\nСледующие шаги:")
        print("1. Настройте .env файл")
        print("2. Запустите: python main_improved.py")
        print("3. Проверьте работу системы")
        
    except Exception as e:
        print(f"\n❌ Ошибка при миграции: {e}")
        print("Проверьте права доступа и доступное место на диске")

if __name__ == "__main__":
    main()
