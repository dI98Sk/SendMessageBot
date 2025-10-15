#!/usr/bin/env python3
"""
Быстрый запуск SendMessageBot с выбором режима
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

def show_menu():
    """Показать меню выбора"""
    print("🚀 SendMessageBot - Выбор режима запуска")
    print("=" * 50)
    print("1. 🧪 Тестирование (упрощенная версия)")
    print("2. 🚀 Полная версия с мониторингом")
    print("3. 🔧 Версия без Google Sheets")
    print("4. 📊 Просмотр статистики системы")
    print("5. 👀 Интерактивный просмотр статистики")
    print("6. 🔧 Переключение между чатами")
    print("7. 📁 Миграция старых файлов")
    print("8. 🧪 Тест Google Sheets")
    print("9. 📝 Обновление сообщений")
    print("10. 📈 Управление отчетами")
    print("0. ❌ Выход")
    print("=" * 50)

def run_simple():
    """Запуск упрощенной версии"""
    print("🧪 Запуск тестовой версии...")
    import subprocess
    subprocess.run([sys.executable, "main_simple.py"])

def run_full():
    """Запуск полной версии"""
    print("🚀 Запуск полной версии...")
    import subprocess
    subprocess.run([sys.executable, "main_improved.py"])

def run_no_google():
    """Запуск версии без Google Sheets"""
    print("🔧 Запуск версии без Google Sheets...")
    import subprocess
    subprocess.run([sys.executable, "main_no_google.py"])

def show_stats():
    """Показать статистику системы"""
    print("📊 Загрузка статистики системы...")
    import subprocess
    subprocess.run([sys.executable, "show_stats.py"])

def watch_stats():
    """Интерактивный просмотр статистики"""
    print("👀 Запуск интерактивного просмотра статистики...")
    import subprocess
    subprocess.run([sys.executable, "watch_stats.py"])

def switch_targets():
    """Переключение между чатами"""
    print("🔧 Запуск переключателя чатов...")
    import subprocess
    subprocess.run([sys.executable, "switch_targets.py"])

def migrate_files():
    """Миграция старых файлов"""
    print("📁 Запуск миграции файлов...")
    import subprocess
    subprocess.run([sys.executable, "migrate_project.py"])

def test_google_sheets():
    """Тестирование Google Sheets"""
    print("🧪 Запуск теста Google Sheets...")
    import subprocess
    subprocess.run([sys.executable, "test_google_sheets.py"])

def update_messages():
    """Обновление сообщений"""
    print("📝 Запуск обновления сообщений...")
    import subprocess
    subprocess.run([sys.executable, "update_messages.py"])

def manage_reports():
    """Управление отчетами"""
    print("📈 Запуск управления отчетами...")
    import subprocess
    subprocess.run([sys.executable, "manage_reports.py"])

def main():
    """Главная функция"""
    while True:
        try:
            show_menu()
            choice = input("\nВыберите режим (0-10): ").strip()
            
            if choice == "0":
                print("👋 До свидания!")
                break
            elif choice == "1":
                run_simple()
            elif choice == "2":
                run_full()
            elif choice == "3":
                run_no_google()
            elif choice == "4":
                show_stats()
            elif choice == "5":
                watch_stats()
            elif choice == "6":
                switch_targets()
            elif choice == "7":
                migrate_files()
            elif choice == "8":
                test_google_sheets()
            elif choice == "9":
                update_messages()
            elif choice == "10":
                manage_reports()
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\nНажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n👋 Прерывание пользователем")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
