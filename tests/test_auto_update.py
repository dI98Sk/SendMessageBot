#!/usr/bin/env python3
"""
Тест автоматического обновления сообщений из Google Sheets
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager
from utils.auto_updater import AutoMessageUpdater

async def test_auto_update():
    """Тест автообновления"""
    print("=" * 70)
    print("🧪 ТЕСТ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ СООБЩЕНИЙ")
    print("=" * 70)
    print()
    
    # Загрузка конфигурации
    config = config_manager.load_config()
    
    print("📋 Проверка настроек Google Sheets:")
    print()
    
    sheets = {
        'AAA Price': config.google_sheets.aaa_sheet_url,
        'GUS Price': config.google_sheets.gus_sheet_url,
        'AAA ADS': config.google_sheets.aaa_ads_sheet_url,
        'GUS ADS': config.google_sheets.gus_ads_sheet_url,
    }
    
    for name, url in sheets.items():
        status = "✅" if url else "❌"
        print(f"  {status} {name}: {url[:50] + '...' if url and len(url) > 50 else url or 'НЕ НАСТРОЕН'}")
    
    print()
    print(f"📁 Credentials: {config.google_sheets.credentials_file}")
    
    # Проверка credentials файла
    creds_path = Path(config.google_sheets.credentials_file)
    if creds_path.exists():
        print(f"  ✅ Файл существует: {creds_path.absolute()}")
    else:
        print(f"  ❌ Файл НЕ НАЙДЕН: {creds_path.absolute()}")
        print()
        print("  Без credentials.json невозможно загрузить из Google Sheets!")
        return
    
    print()
    print("=" * 70)
    print("🔄 ЗАПУСК ТЕСТОВОГО ОБНОВЛЕНИЯ")
    print("=" * 70)
    print()
    
    try:
        # Создаем автообновлятель
        updater = AutoMessageUpdater(
            credentials_file=config.google_sheets.credentials_file,
            config=config
        )
        
        print("📥 Загружаем сообщения из Google Sheets...")
        print()
        
        # Выполняем обновление
        results = await updater.update_all_messages()
        
        print()
        print("=" * 70)
        print("📊 РЕЗУЛЬТАТЫ ОБНОВЛЕНИЯ")
        print("=" * 70)
        print()
        
        # Показываем результаты
        for msg_type, result in results.items():
            if result['success']:
                print(f"  ✅ {msg_type}: {result['count']} сообщений")
            else:
                print(f"  ❌ {msg_type}: ОШИБКА")
                if result['error']:
                    print(f"     Ошибка: {result['error']}")
        
        # Подсчет успехов
        success_count = sum(1 for r in results.values() if r['success'])
        total_messages = sum(r['count'] for r in results.values() if r['success'])
        
        print()
        print(f"📊 Итого: {success_count}/4 типов обновлено")
        print(f"📝 Всего сообщений загружено: {total_messages}")
        print()
        
        # Проверка файлов
        print("=" * 70)
        print("📁 ПРОВЕРКА ОБНОВЛЕННЫХ ФАЙЛОВ")
        print("=" * 70)
        print()
        
        files_to_check = {
            'config/messages_aaa.py': 'Прайсы AAA',
            'config/messages_gus.py': 'Прайсы GUS',
            'config/messages_aaa_ads.py': 'Реклама AAA',
            'config/messages_gus_ads.py': 'Реклама GUS',
        }
        
        for file_path, description in files_to_check.items():
            full_path = Path(file_path)
            if full_path.exists():
                # Читаем количество сообщений
                content = full_path.read_text(encoding='utf-8')
                # Подсчитываем строки с сообщениями (начинаются с пробелами и кавычкой)
                msg_count = content.count('    "')
                
                print(f"  ✅ {description}:")
                print(f"     Файл: {file_path}")
                print(f"     Сообщений: ~{msg_count}")
                
                # Показываем дату обновления если есть
                if 'Дата обновления:' in content:
                    for line in content.split('\n'):
                        if 'Дата обновления:' in line:
                            print(f"     {line.strip()}")
                            break
            else:
                print(f"  ❌ {description}: ФАЙЛ НЕ НАЙДЕН")
        
        print()
        
        if success_count == 4:
            print("=" * 70)
            print("✅ ВСЕ СООБЩЕНИЯ УСПЕШНО ОБНОВЛЕНЫ!")
            print("=" * 70)
            print()
            print("💡 Теперь можно запускать бот:")
            print("   python main.py")
            print()
        else:
            print("=" * 70)
            print("⚠️ НЕКОТОРЫЕ ТИПЫ НЕ ОБНОВЛЕНЫ")
            print("=" * 70)
            print()
            print("Проверьте:")
            print("  1. URL Google Sheets в .env")
            print("  2. Права доступа к таблицам")
            print("  3. credentials.json")
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ОШИБКА ПРИ ОБНОВЛЕНИИ")
        print("=" * 70)
        print()
        print(f"Ошибка: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("Проверьте:")
        print("  1. credentials.json существует и валиден")
        print("  2. URL Google Sheets правильные")
        print("  3. Есть доступ к таблицам")

if __name__ == "__main__":
    asyncio.run(test_auto_update())

