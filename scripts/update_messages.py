#!/usr/bin/env python3
"""
Скрипт для обновления сообщений из всех Google Sheets таблиц
"""
import sys
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from utils.google_sheets import GoogleSheetsFetcher

# Загружаем переменные окружения
load_dotenv()

def update_messages_from_sheet(sheet_url: str, config_file: str, messages_var: str):
    """Обновление сообщений из Google Sheet"""
    try:
        fetcher = GoogleSheetsFetcher()
        messages = fetcher.fetch_messages(sheet_url)
        
        # Создаем содержимое файла
        config_content = f"# Обновлено: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        config_content += f"{messages_var} = [\n"
        for msg in messages:
            config_content += f"    {repr(msg)},\n"
        config_content += "]\n"
        
        # Записываем в файл
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        return True, len(messages)
    except Exception as e:
        return False, str(e)

def update_all_messages():
    """Обновление всех сообщений из Google Sheets"""
    print("🔄 ОБНОВЛЕНИЕ ВСЕХ СООБЩЕНИЙ ИЗ GOOGLE SHEETS")
    print("=" * 60)
    
    # Конфигурация для обновления
    updates = [
        {
            "name": "B2B",
            "sheet_url": os.getenv("BUY_SELL_PRICE_B2B_SHEET_URL"),
            "config_file": "config/messages_b2b.py",
            "messages_var": "MESSAGESB2B"
        },
        {
            "name": "B2C", 
            "sheet_url": os.getenv("BUY_SELL_PRICE_B2C_SHEET_URL"),
            "config_file": "config/messages_b2c.py",
            "messages_var": "MESSAGESB2C"
        },
        {
            "name": "AAA",
            "sheet_url": os.getenv("BUY_SELL_PRICE_AAA_SHEET_URL"),
            "config_file": "config/messages_aaa.py",
            "messages_var": "MESSAGESAAA"
        },
        {
            "name": "GUS",
            "sheet_url": os.getenv("BUY_SELL_PRICE_GUS_SHEET_URL"),
            "config_file": "config/messages_gus.py",
            "messages_var": "MESSAGESGUS"
        }
    ]
    
    results = {}
    
    for i, update in enumerate(updates, 1):
        print(f"\n{i}️⃣ Обновление {update['name']} сообщений...")
        
        if not update['sheet_url']:
            results[update['name']] = "❌ URL не настроен"
            print(f"❌ URL для {update['name']} не настроен в .env")
            continue
        
        try:
            success, result = update_messages_from_sheet(
                update['sheet_url'],
                update['config_file'],
                update['messages_var']
            )
            
            if success:
                results[update['name']] = f"✅ Успешно ({result} сообщений)"
                print(f"✅ {update['name']} сообщения обновлены ({result} сообщений)")
            else:
                results[update['name']] = f"❌ Ошибка: {result}"
                print(f"❌ Ошибка обновления {update['name']}: {result}")
                
        except Exception as e:
            results[update['name']] = f"❌ Ошибка: {e}"
            print(f"❌ Ошибка обновления {update['name']}: {e}")
    
    # Выводим итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    for broadcaster, status in results.items():
        print(f"{broadcaster:>10}: {status}")
    
    successful = sum(1 for status in results.values() if "✅" in status)
    total = len(results)
    
    print(f"\n📈 Успешно обновлено: {successful}/{total}")
    
    if successful == total:
        print("🎉 Все сообщения обновлены успешно!")
    else:
        print("⚠️  Некоторые обновления завершились с ошибками")
    
    return successful == total

def main():
    """Главная функция"""
    print("🔄 ОБНОВЛЕНИЕ СООБЩЕНИЙ ИЗ GOOGLE SHEETS")
    print("=" * 60)
    print("Этот скрипт обновляет сообщения из всех настроенных таблиц:")
    print("• B2B (оптовые сообщения)")
    print("• B2C (розничные сообщения)")
    print("• AAA (сообщения AAA Store)")
    print("• GUS (сообщения Яблочный Гусь)")
    print("=" * 60)
    
    try:
        success = update_all_messages()
        
        if success:
            print("\n✅ Все сообщения обновлены успешно!")
            print("🚀 Теперь можно запускать main.py")
        else:
            print("\n⚠️  Некоторые обновления завершились с ошибками")
            print("🔍 Проверьте настройки Google Sheets и credentials.json")
        
    except KeyboardInterrupt:
        print("\n👋 Прерывание пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
