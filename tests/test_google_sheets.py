#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Google Sheets
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

def test_credentials_file():
    """Тестирование файла credentials.json"""
    print("🔑 Проверка файла credentials.json...")
    
    credentials_file = Path("credentials.json")
    if not credentials_file.exists():
        print("❌ Файл credentials.json не найден")
        return False
    
    try:
        import json
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Отсутствуют поля в credentials.json: {missing_fields}")
            return False
        
        print(f"✅ Файл credentials.json корректен")
        print(f"   Тип: {creds['type']}")
        print(f"   Проект: {creds['project_id']}")
        print(f"   Email: {creds['client_email']}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Файл credentials.json содержит неверный JSON")
        return False
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")
        return False

def test_google_sheets_auth():
    """Тестирование аутентификации Google Sheets"""
    print("\n🔐 Тестирование аутентификации Google Sheets...")
    
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        
        print("✅ Аутентификация успешна")
        return client
        
    except Exception as e:
        print(f"❌ Ошибка аутентификации: {e}")
        return None

def test_sheet_access(client, sheet_url):
    """Тестирование доступа к таблице"""
    if not client or not sheet_url:
        return False
    
    print(f"\n📊 Тестирование доступа к таблице...")
    print(f"   URL: {sheet_url}")
    
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        title = sheet.title
        rows_count = len(sheet.get_all_values())
        
        print(f"✅ Доступ к таблице успешен")
        print(f"   Название: {title}")
        print(f"   Строк: {rows_count}")
        
        # Показываем первые несколько строк
        if rows_count > 0:
            print(f"   Первые 3 строки:")
            for i, row in enumerate(sheet.get_all_values()[:3]):
                preview = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
                print(f"     {i+1}. {preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка доступа к таблице: {e}")
        return False

def test_config_urls():
    """Проверка URL в конфигурации"""
    print("\n⚙️  Проверка конфигурации...")
    
    try:
        from config.settings import config_manager
        config = config_manager.load_config()
        
        print(f"   B2B URL: {config.google_sheets.b2b_sheet_url or 'Не настроен'}")
        print(f"   B2C URL: {config.google_sheets.b2c_sheet_url or 'Не настроен'}")
        print(f"   Credentials: {config.google_sheets.credentials_file}")
        print(f"   Интервал: {config.google_sheets.update_interval // 3600} часов")
        
        return config.google_sheets.b2b_sheet_url or config.google_sheets.b2c_sheet_url
        
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def main():
    """Главная функция"""
    print("🧪 Диагностика Google Sheets")
    print("=" * 50)
    
    # Проверка файла credentials
    if not test_credentials_file():
        print("\n💡 Решение:")
        print("   1. Создайте сервисный аккаунт в Google Cloud Console")
        print("   2. Скачайте JSON ключ и сохраните как credentials.json")
        print("   3. Предоставьте доступ к таблицам сервисному аккаунту")
        return
    
    # Проверка конфигурации
    has_urls = test_config_urls()
    if not has_urls:
        print("\n💡 Решение:")
        print("   Добавьте в .env файл:")
        print("   SHEET_URL_B2B=https://docs.google.com/spreadsheets/d/YOUR_B2B_SHEET_ID/edit")
        print("   SHEET_URL_B2C=https://docs.google.com/spreadsheets/d/YOUR_B2C_SHEET_ID/edit")
        return
    
    # Тестирование аутентификации
    client = test_google_sheets_auth()
    if not client:
        print("\n💡 Решение:")
        print("   1. Проверьте правильность файла credentials.json")
        print("   2. Убедитесь, что сервисный аккаунт активен")
        print("   3. Проверьте права доступа к Google Sheets API")
        return
    
    # Тестирование доступа к таблицам
    try:
        from config.settings import config_manager
        config = config_manager.load_config()
        
        b2b_success = test_sheet_access(client, config.google_sheets.b2b_sheet_url)
        b2c_success = test_sheet_access(client, config.google_sheets.b2c_sheet_url)
        
        if b2b_success or b2c_success:
            print("\n✅ Google Sheets настроен корректно!")
            print("   Можно запускать автоматические обновления")
        else:
            print("\n❌ Нет доступа ни к одной таблице")
            print("💡 Решение:")
            print("   1. Предоставьте доступ к таблицам сервисному аккаунту")
            print("   2. Скопируйте email сервисного аккаунта из credentials.json")
            print("   3. Добавьте его как редактора в Google Sheets")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    main()
