#!/usr/bin/env python3
"""
Скрипт для исправления проблем с зависимостями
"""
import subprocess
import sys
import os

def check_python_environment():
    """Проверка окружения Python"""
    print("🐍 ПРОВЕРКА ОКРУЖЕНИЯ PYTHON")
    print("=" * 40)
    
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[0]}")
    
    # Проверяем виртуальное окружение
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Виртуальное окружение активно")
    else:
        print("⚠️  Виртуальное окружение НЕ активно")
    
    print()

def install_dependencies():
    """Установка зависимостей"""
    print("📦 УСТАНОВКА ЗАВИСИМОСТЕЙ")
    print("=" * 40)
    
    try:
        # Устанавливаем зависимости
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Зависимости установлены успешно")
        else:
            print(f"❌ Ошибка установки зависимостей: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("🔍 ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    print("=" * 40)
    
    required_packages = [
        "telethon",
        "gspread", 
        "oauth2client",
        "python-dotenv",
        "cryptography",
        "aiohttp",
        "structlog",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - НЕ УСТАНОВЛЕН")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Отсутствуют пакеты: {', '.join(missing_packages)}")
        return False
    else:
        print("\n✅ Все зависимости установлены")
        return True

def main():
    """Главная функция"""
    print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ С ЗАВИСИМОСТЯМИ")
    print("=" * 50)
    
    # Проверяем окружение
    check_python_environment()
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n📦 Устанавливаем отсутствующие зависимости...")
        install_dependencies()
        
        # Проверяем снова
        print("\n🔍 Повторная проверка...")
        check_dependencies()
    
    print("\n🎉 Проверка завершена!")

if __name__ == "__main__":
    main()
