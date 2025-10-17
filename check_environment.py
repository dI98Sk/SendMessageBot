"""
Скрипт для диагностики окружения и проверки готовности к запуску бота
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import json

def print_header(text):
    """Печать заголовка"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_python_version():
    """Проверка версии Python"""
    print_header("🐍 Проверка Python")
    print(f"Версия Python: {sys.version}")
    print(f"Путь к Python: {sys.executable}")
    
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print("✅ Версия Python подходит (требуется 3.8+)")
        return True
    else:
        print("❌ Требуется Python 3.8 или выше")
        return False

def check_environment_variables():
    """Проверка переменных окружения"""
    print_header("🔐 Проверка переменных окружения")
    
    required_vars = ["API_ID", "API_HASH"]
    optional_vars = [
        "SESSION_NAME",
        "SHEET_URL_B2B", 
        "SHEET_URL_B2C",
        "GOOGLE_CREDENTIALS_FILE",
        "ADMIN_TELEGRAM_ID"
    ]
    
    all_ok = True
    
    print("\n📋 Обязательные переменные:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:4] + "..." if len(value) > 4 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ❌ {var}: НЕ УСТАНОВЛЕНА")
            all_ok = False
    
    print("\n📋 Опциональные переменные:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if "URL" in var:
                masked = value[:30] + "..." if len(value) > 30 else value
            else:
                masked = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ⚠️  {var}: не установлена")
    
    return all_ok

def check_sessions_directory():
    """Проверка директории с сессиями"""
    print_header("📁 Проверка директории sessions/")
    
    sessions_dir = Path("sessions")
    
    # Проверяем существование директории
    if not sessions_dir.exists():
        print(f"❌ Директория {sessions_dir} не существует")
        print(f"   Создаем директорию...")
        try:
            sessions_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Директория создана")
        except Exception as e:
            print(f"   ❌ Ошибка создания: {e}")
            return False
    else:
        print(f"✅ Директория {sessions_dir} существует")
    
    # Проверяем права на запись
    test_file = sessions_dir / ".test_write"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ Права на запись в директорию есть")
    except Exception as e:
        print(f"❌ Нет прав на запись: {e}")
        return False
    
    # Проверяем файлы сессий
    session_files = list(sessions_dir.glob("*.session"))
    if session_files:
        print(f"\n📝 Найдено файлов сессий: {len(session_files)}")
        for session_file in session_files:
            size = session_file.stat().st_size
            print(f"  - {session_file.name}: {size} байт")
    else:
        print(f"⚠️  Файлы сессий не найдены")
        print(f"   При первом запуске потребуется авторизация")
    
    return True

def check_credentials_file():
    """Проверка файла credentials.json"""
    print_header("🔑 Проверка credentials.json")
    
    creds_file = Path("credentials.json")
    
    if not creds_file.exists():
        print(f"❌ Файл {creds_file} не найден")
        print(f"   Полный путь: {creds_file.absolute()}")
        print(f"\n💡 Что делать:")
        print(f"   1. Скачайте credentials.json из Google Cloud Console")
        print(f"   2. Поместите его в корень проекта: {Path.cwd()}")
        print(f"   3. Убедитесь что файл называется 'credentials.json'")
        return False
    
    print(f"✅ Файл {creds_file} найден")
    print(f"   Путь: {creds_file.absolute()}")
    
    # Проверяем размер
    size = creds_file.stat().st_size
    print(f"   Размер: {size} байт")
    
    if size == 0:
        print(f"❌ Файл пустой!")
        return False
    
    if size < 100:
        print(f"⚠️  Файл слишком маленький, возможно поврежден")
        return False
    
    # Проверяем что это валидный JSON
    try:
        with open(creds_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем ключевые поля
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            print(f"❌ Отсутствуют обязательные поля: {missing_fields}")
            return False
        
        print(f"✅ JSON валиден")
        print(f"   Type: {data.get('type')}")
        print(f"   Project ID: {data.get('project_id')}")
        print(f"   Client Email: {data.get('client_email')}")
        
        if data.get('type') != 'service_account':
            print(f"⚠️  Тип не 'service_account', возможны проблемы")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Файл не является валидным JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return False

def check_config_files():
    """Проверка конфигурационных файлов"""
    print_header("⚙️  Проверка конфигурационных файлов")
    
    config_dir = Path("config")
    if not config_dir.exists():
        print(f"❌ Директория {config_dir} не существует")
        return False
    
    print(f"✅ Директория {config_dir} существует")
    
    required_files = [
        "messages.py",
        "targets.py",
        "settings.py"
    ]
    
    all_ok = True
    for filename in required_files:
        file_path = config_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {filename}: {size} байт")
        else:
            print(f"  ❌ {filename}: НЕ НАЙДЕН")
            all_ok = False
    
    return all_ok

def check_system_time():
    """Проверка системного времени"""
    print_header("⏰ Проверка системного времени")
    
    now = datetime.now()
    print(f"Текущее время системы: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"UTC время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем что время не слишком старое/новое
    year = now.year
    if year < 2024 or year > 2030:
        print(f"⚠️  Время системы выглядит неправильно!")
        print(f"   Это может вызвать проблемы с JWT подписью Google Sheets")
        print(f"   Синхронизируйте время на сервере")
        return False
    
    print(f"✅ Время системы выглядит корректно")
    return True

def check_dependencies():
    """Проверка зависимостей"""
    print_header("📦 Проверка установленных пакетов")
    
    required_packages = [
        "telethon",
        "gspread", 
        "oauth2client",
        "python-dotenv",
        "pytz"
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}: НЕ УСТАНОВЛЕН")
            all_ok = False
    
    if not all_ok:
        print(f"\n💡 Установите недостающие пакеты:")
        print(f"   pip install -r requirements_improved.txt")
    
    return all_ok

def main():
    """Главная функция"""
    print("\n" + "🔍 ДИАГНОСТИКА ОКРУЖЕНИЯ SENDMESSAGEBOT 🔍".center(70))
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Рабочая директория: {Path.cwd()}")
    print(f"Операционная система: {sys.platform}")
    
    checks = [
        ("Python", check_python_version),
        ("Переменные окружения", check_environment_variables),
        ("Директория sessions/", check_sessions_directory),
        ("Файл credentials.json", check_credentials_file),
        ("Конфигурационные файлы", check_config_files),
        ("Системное время", check_system_time),
        ("Зависимости", check_dependencies),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Ошибка при проверке '{name}': {e}")
            results[name] = False
    
    # Итоговая статистика
    print_header("📊 ИТОГОВАЯ СТАТИСТИКА")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nПройдено проверок: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Бот готов к запуску.")
        print("Запустите бота командой: python main_improved.py")
        return 0
    else:
        print("\n⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ. Исправьте их перед запуском бота.")
        print("\n💡 Рекомендации:")
        
        if not results.get("Переменные окружения"):
            print("   - Создайте файл .env с переменными из ENV_TEMPLATE.md")
        
        if not results.get("Директория sessions/"):
            print("   - Скопируйте файлы сессий в директорию sessions/")
        
        if not results.get("Файл credentials.json"):
            print("   - Скачайте credentials.json из Google Cloud Console")
            print("   - Или отключите интеграцию Google Sheets в .env")
        
        if not results.get("Системное время"):
            print("   - Синхронизируйте время на сервере")
            print("   - Для Windows: net start w32time && w32tm /resync")
            print("   - Для Linux: sudo ntpdate pool.ntp.org")
        
        if not results.get("Зависимости"):
            print("   - Установите зависимости: pip install -r requirements_improved.txt")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

