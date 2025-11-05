#!/usr/bin/env python3
"""
Скрипт для автоматического исправления config/settings.py на сервере
Запустите: python FIX_FOR_SERVER.py
"""
import os
from pathlib import Path

def fix_settings_file():
    """Исправить config/settings.py"""
    
    settings_file = Path("config/settings.py")
    
    if not settings_file.exists():
        print("❌ Файл config/settings.py не найден!")
        print(f"   Текущая директория: {os.getcwd()}")
        return False
    
    print("=" * 70)
    print("🔧 ИСПРАВЛЕНИЕ config/settings.py")
    print("=" * 70)
    print()
    
    # Читаем файл
    content = settings_file.read_text(encoding='utf-8')
    original_content = content
    
    # Исправление 1: В классе ReportsConfig
    print("1️⃣  Исправление типа report_interval_hours в классе...")
    content = content.replace(
        'report_interval_hours: int = 3  # Отчеты каждые 3 часа',
        'report_interval_hours: float = 3.0  # Отчеты каждые 3 часа (поддержка дробных значений)'
    )
    
    # Также проверяем вариант без комментария
    content = content.replace(
        'report_interval_hours: int = 3',
        'report_interval_hours: float = 3.0'
    )
    
    # Исправление 2: В методе load_config
    print("2️⃣  Исправление парсинга REPORT_INTERVAL_HOURS...")
    content = content.replace(
        'report_interval_hours=int(os.getenv("REPORT_INTERVAL_HOURS", 3))',
        'report_interval_hours=float(os.getenv("REPORT_INTERVAL_HOURS", "3.0"))'
    )
    
    # Проверяем изменения
    if content == original_content:
        print()
        print("⚠️  ВНИМАНИЕ: Ничего не изменено!")
        print("   Возможно файл уже исправлен, или строки отличаются.")
        print()
        print("   Попробуйте исправить вручную:")
        print("   1. Найдите строку: report_interval_hours: int = 3")
        print("      Замените на:    report_interval_hours: float = 3.0")
        print()
        print("   2. Найдите строку: report_interval_hours=int(os.getenv(...)")
        print("      Замените int на float и 3 на \"3.0\"")
        return False
    
    # Сохраняем
    settings_file.write_text(content, encoding='utf-8')
    
    print()
    print("=" * 70)
    print("✅ ФАЙЛ УСПЕШНО ИСПРАВЛЕН!")
    print("=" * 70)
    print()
    print("📝 Внесенные изменения:")
    print("  ✅ report_interval_hours: int → float")
    print("  ✅ Парсинг REPORT_INTERVAL_HOURS: int() → float()")
    print()
    print("🚀 Теперь можно запускать:")
    print("   python main.py")
    print()
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = fix_settings_file()
        
        if success:
            # Проверяем что файл работает
            print("🧪 Проверка исправленного файла...")
            try:
                from config.settings import config_manager
                config = config_manager.load_config()
                print("✅ Конфигурация загружается без ошибок!")
                print(f"✅ report_interval_hours = {config.reports.report_interval_hours} (тип: {type(config.reports.report_interval_hours).__name__})")
            except Exception as e:
                print(f"❌ Ошибка при загрузке конфигурации: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

