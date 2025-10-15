#!/usr/bin/env python3
"""
Скрипт для ручного обновления сообщений из Google Sheets
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager
from utils.google_sheets import GoogleSheetsManager, MessageUpdater
from config.message_updater import MessageConfigUpdater

async def update_messages():
    """Обновление сообщений из Google Sheets"""
    print("📊 Обновление сообщений из Google Sheets")
    print("=" * 50)
    
    try:
        # Загрузка конфигурации
        config = config_manager.load_config()
        
        if not config.google_sheets.b2b_sheet_url and not config.google_sheets.b2c_sheet_url:
            print("❌ URL Google Sheets не настроены в конфигурации")
            print("Добавьте SHEET_URL_B2B и/или SHEET_URL_B2C в .env файл")
            return
        
        print(f"📱 B2B Sheet URL: {config.google_sheets.b2b_sheet_url or 'Не настроен'}")
        print(f"📱 B2C Sheet URL: {config.google_sheets.b2c_sheet_url or 'Не настроен'}")
        print(f"🔑 Credentials: {config.google_sheets.credentials_file}")
        
        # Инициализация менеджеров
        gs_manager = GoogleSheetsManager(config.google_sheets.credentials_file)
        config_updater = MessageConfigUpdater()
        message_updater = MessageUpdater(gs_manager)
        
        # Добавляем callback для обновления файла
        async def update_callback(new_messages):
            print(f"\n📝 Обновляем файл конфигурации...")
            success = config_updater.update_messages_file(
                new_messages['b2b'],
                new_messages['b2c']
            )
            if success:
                print("✅ Файл конфигурации обновлен")
                config_updater.reload_messages_module()
                print("✅ Модуль сообщений перезагружен")
            else:
                print("❌ Ошибка обновления файла конфигурации")
        
        message_updater.add_update_callback(update_callback)
        
        # Выполняем обновление
        print(f"\n🔄 Загружаем сообщения из Google Sheets...")
        success = await message_updater.update_messages_from_sheets(
            config.google_sheets.b2b_sheet_url,
            config.google_sheets.b2c_sheet_url
        )
        
        if success:
            print("\n✅ Обновление завершено успешно!")
            
            # Показываем информацию о последнем обновлении
            update_info = gs_manager.get_last_update_info()
            print(f"\n📊 Информация об обновлении:")
            print(f"   Время: {update_info['last_update']}")
            print(f"   B2B сообщений: {update_info['cached_b2b_count']}")
            print(f"   B2C сообщений: {update_info['cached_b2c_count']}")
            
            # Показываем статус файлов
            status = config_updater.get_update_status()
            print(f"\n📁 Статус файлов:")
            print(f"   Файл сообщений: {'✅' if status['messages_file_exists'] else '❌'}")
            print(f"   Резервных копий: {status['backup_count']}")
            if status['latest_backup']:
                print(f"   Последняя копия: {status['latest_backup']}")
        else:
            print("\n❌ Обновление не удалось")
            print("Проверьте:")
            print("  - Правильность URL Google Sheets")
            print("  - Наличие файла credentials.json")
            print("  - Права доступа к таблицам")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def show_update_status():
    """Показать статус обновлений"""
    print("📊 Статус обновлений сообщений")
    print("=" * 40)
    
    try:
        config = config_manager.load_config()
        gs_manager = GoogleSheetsManager(config.google_sheets.credentials_file)
        config_updater = MessageConfigUpdater()
        
        # Информация о Google Sheets
        update_info = gs_manager.get_last_update_info()
        print(f"📅 Последнее обновление: {update_info['last_update'] or 'Никогда'}")
        print(f"📱 B2B сообщений в кэше: {update_info['cached_b2b_count']}")
        print(f"📱 B2C сообщений в кэше: {update_info['cached_b2c_count']}")
        print(f"🔄 Обновление необходимо: {'Да' if update_info['update_needed'] else 'Нет'}")
        
        # Информация о файлах
        status = config_updater.get_update_status()
        print(f"\n📁 Файлы:")
        print(f"   Файл сообщений: {'✅' if status['messages_file_exists'] else '❌'}")
        print(f"   Резервных копий: {status['backup_count']}")
        if status['latest_backup_time']:
            print(f"   Последняя копия: {status['latest_backup_time']}")
        
        # Конфигурация
        print(f"\n⚙️  Конфигурация:")
        print(f"   B2B URL: {config.google_sheets.b2b_sheet_url or 'Не настроен'}")
        print(f"   B2C URL: {config.google_sheets.b2c_sheet_url or 'Не настроен'}")
        print(f"   Интервал обновления: {config.google_sheets.update_interval // 3600} часов")
        
    except Exception as e:
        print(f"❌ Ошибка получения статуса: {e}")

def main():
    """Главная функция"""
    print("🔧 Управление сообщениями Google Sheets")
    print("=" * 50)
    print("1. 🔄 Обновить сообщения")
    print("2. 📊 Показать статус")
    print("3. ❌ Выход")
    
    choice = input("\nВыберите действие (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(update_messages())
    elif choice == "2":
        asyncio.run(show_update_status())
    elif choice == "3":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
