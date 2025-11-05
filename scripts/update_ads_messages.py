#!/usr/bin/env python3
"""
Скрипт для обновления рекламных сообщений из Google Sheets
Обновляет файлы:
- config/messages_aaa_ads.py
- config/messages_gus_ads.py
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import config_manager
from utils.google_sheets import GoogleSheetsFetcher
from utils.logger import get_logger

async def update_ads_messages():
    """Обновление рекламных сообщений из Google Sheets"""
    print("=" * 70)
    print("📊 ОБНОВЛЕНИЕ РЕКЛАМНЫХ СООБЩЕНИЙ ИЗ GOOGLE SHEETS")
    print("=" * 70)
    
    try:
        # Загрузка конфигурации
        config = config_manager.load_config()
        logger = get_logger("update_ads", config.logging)
        
        # Проверка настроек
        aaa_url = config.google_sheets.aaa_ads_sheet_url
        gus_url = config.google_sheets.gus_ads_sheet_url
        
        print(f"\n📋 Конфигурация:")
        print(f"  AAA ADS Sheet URL: {aaa_url or '❌ Не настроен'}")
        print(f"  GUS ADS Sheet URL: {gus_url or '❌ Не настроен'}")
        print(f"  Credentials: {config.google_sheets.credentials_file}")
        
        if not aaa_url and not gus_url:
            print("\n❌ Ошибка: URL Google Sheets не настроены")
            print("   Добавьте в .env файл:")
            print("   ADS_AAA_SHEET_URL=<URL_таблицы_AAA>")
            print("   ADS_GUS_SHEET_URL=<URL_таблицы_GUS>")
            return
        
        # Инициализация Google Sheets Fetcher
        fetcher = GoogleSheetsFetcher(config.google_sheets.credentials_file)
        
        # Обновление AAA ADS
        if aaa_url:
            print(f"\n📥 Загрузка рекламных сообщений AAA...")
            try:
                aaa_ads_messages = await fetcher.fetch_messages(aaa_url)
                print(f"✅ Загружено {len(aaa_ads_messages)} сообщений AAA ADS")
                
                # Сохранение в файл
                aaa_file = Path(__file__).parent.parent / "config" / "messages_aaa_ads.py"
                content = '"""\nРекламные сообщения AAA\n'
                content += 'Автоматически обновлено из Google Sheets\n'
                content += f'Дата обновления: {Path(__file__).parent.parent}\n'
                content += '"""\n\n'
                content += 'MESSAGES_AAA_ADS = [\n'
                
                for i, msg in enumerate(aaa_ads_messages, 1):
                    # Экранируем кавычки и переводы строк
                    escaped_msg = msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                    content += f'    # Сообщение {i}\n'
                    content += f'    "{escaped_msg}",\n\n'
                
                content += ']\n'
                
                aaa_file.write_text(content, encoding='utf-8')
                print(f"💾 Сохранено в {aaa_file}")
                
            except Exception as e:
                logger.error(f"Ошибка обновления AAA ADS: {e}")
                print(f"❌ Ошибка обновления AAA ADS: {e}")
        
        # Обновление GUS ADS
        if gus_url:
            print(f"\n📥 Загрузка рекламных сообщений GUS...")
            try:
                gus_ads_messages = await fetcher.fetch_messages(gus_url)
                print(f"✅ Загружено {len(gus_ads_messages)} сообщений GUS ADS")
                
                # Сохранение в файл
                gus_file = Path(__file__).parent.parent / "config" / "messages_gus_ads.py"
                content = '"""\nРекламные сообщения GUS\n'
                content += 'Автоматически обновлено из Google Sheets\n'
                content += f'Дата обновления: {Path(__file__).parent.parent}\n'
                content += '"""\n\n'
                content += 'MESSAGES_GUS_ADS = [\n'
                
                for i, msg in enumerate(gus_ads_messages, 1):
                    # Экранируем кавычки и переводы строк
                    escaped_msg = msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                    content += f'    # Сообщение {i}\n'
                    content += f'    "{escaped_msg}",\n\n'
                
                content += ']\n'
                
                gus_file.write_text(content, encoding='utf-8')
                print(f"💾 Сохранено в {gus_file}")
                
            except Exception as e:
                logger.error(f"Ошибка обновления GUS ADS: {e}")
                print(f"❌ Ошибка обновления GUS ADS: {e}")
        
        print("\n" + "=" * 70)
        print("✅ Обновление рекламных сообщений завершено!")
        print("=" * 70)
        print("\n💡 Перезапустите бот для применения изменений:")
        print("   python main.py")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(update_ads_messages())


