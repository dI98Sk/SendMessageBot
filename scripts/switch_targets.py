#!/usr/bin/env python3
"""
Скрипт для переключения между тестовыми и основными чатами
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager

def show_current_targets():
    """Показать текущие цели"""
    config = config_manager.load_config()
    
    print("🎯 Текущие настройки целей:")
    print("=" * 40)
    print(f"📱 Основные цели (TARGETS): {len(config.targets)} чатов")
    print(f"🧪 Тестовые цели (TEST_TARGETS): {len(config.targets)} чатов")
    
    if config.targets:
        print(f"\n🧪 Тестовые чаты:")
        for i, chat_id in enumerate(config.targets, 1):
            print(f"   {i}. {chat_id}")
    
    print(f"\n📱 Основные чаты (первые 5):")
    for i, chat_id in enumerate(config.targets[:5], 1):
        print(f"   {i}. {chat_id}")
    if len(config.targets) > 5:
        print(f"   ... и еще {len(config.targets) - 5} чатов")

def check_main_improved_usage():
    """Проверить какая конфигурация используется в main_improved.py"""
    main_file = Path("main_improved.py")
    if not main_file.exists():
        print("❌ Файл main_improved.py не найден")
        return
    
    content = main_file.read_text()
    
    if "test_targets" in content:
        print("⚠️  main_improved.py использует ТЕСТОВЫЕ чаты")
        print("   Для переключения на основные чаты нужно изменить:")
        print("   targets=self.config.test_targets  →  targets=self.config.targets")
    else:
        print("✅ main_improved.py использует ОСНОВНЫЕ чаты")

def create_switched_version():
    """Создать версию main_improved.py с основными чатами"""
    main_file = Path("main_improved.py")
    if not main_file.exists():
        print("❌ Файл main_improved.py не найден")
        return
    
    content = main_file.read_text()
    
    # Заменяем test_targets на targets
    switched_content = content.replace(
        "targets=self.config.test_targets",
        "targets=self.config.targets"
    )
    
    # Создаем резервную копию
    backup_file = Path("main_improved_test_backup.py")
    backup_file.write_text(content)
    print(f"📁 Создана резервная копия: {backup_file}")
    
    # Создаем версию с основными чатами
    main_file.write_text(switched_content)
    print("✅ main_improved.py обновлен для использования основных чатов")
    print("⚠️  ВНИМАНИЕ: Теперь рассылка будет идти по ВСЕМ чатам!")

def restore_test_version():
    """Восстановить версию с тестовыми чатами"""
    backup_file = Path("main_improved_test_backup.py")
    main_file = Path("main_improved.py")
    
    if not backup_file.exists():
        print("❌ Резервная копия не найдена")
        return
    
    backup_content = backup_file.read_text()
    main_file.write_text(backup_content)
    print("✅ main_improved.py восстановлен для использования тестовых чатов")

def main():
    print("🎯 Переключатель целей для SendMessageBot")
    print("=" * 50)
    
    show_current_targets()
    print()
    check_main_improved_usage()
    print()
    
    print("Выберите действие:")
    print("1. Переключить на основные чаты (ОПАСНО!)")
    print("2. Восстановить тестовые чаты")
    print("3. Показать текущие настройки")
    print("4. Выход")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        confirm = input("⚠️  Вы уверены? Рассылка пойдет по ВСЕМ чатам! (yes/no): ")
        if confirm.lower() == "yes":
            create_switched_version()
        else:
            print("❌ Отменено")
    elif choice == "2":
        restore_test_version()
    elif choice == "3":
        show_current_targets()
    elif choice == "4":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
