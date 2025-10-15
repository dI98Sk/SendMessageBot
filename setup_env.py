#!/usr/bin/env python3
"""
Интерактивный скрипт для настройки .env файла
"""
import os
import getpass
from pathlib import Path

def get_input(prompt, default=None, sensitive=False):
    """Получение ввода от пользователя с поддержкой значений по умолчанию"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if sensitive:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()
    
    return value if value else default

def setup_telegram_config():
    """Настройка конфигурации Telegram API"""
    print("\n" + "="*50)
    print("📱 НАСТРОЙКА TELEGRAM API")
    print("="*50)
    print("Получите эти данные на https://my.telegram.org")
    
    api_id = get_input("API ID (число)")
    api_hash = get_input("API Hash", sensitive=True)
    session_name = get_input("Имя сессии", "sendmessagebot_session")
    
    return {
        "API_ID": api_id,
        "API_HASH": api_hash,
        "SESSION_NAME": session_name
    }

def setup_proxy_config():
    """Настройка прокси (опционально)"""
    print("\n" + "="*50)
    print("🌐 НАСТРОЙКА ПРОКСИ (ОПЦИОНАЛЬНО)")
    print("="*50)
    
    use_proxy = get_input("Использовать прокси? (y/n)", "n").lower() == 'y'
    
    if not use_proxy:
        return {"PROXY_ENABLED": "false"}
    
    print("Настройка прокси:")
    proxy_type = get_input("Тип прокси (mtproto/socks5/http)", "mtproto")
    proxy_addr = get_input("Адрес прокси")
    proxy_port = get_input("Порт прокси", "8888")
    proxy_secret = get_input("Секрет прокси", sensitive=True) if proxy_type == "mtproto" else ""
    
    return {
        "PROXY_ENABLED": "true",
        "PROXY_PROTOCOL": proxy_type,
        "PROXY_ADDR": proxy_addr,
        "PROXY_PORT": proxy_port,
        "PROXY_SECRET": proxy_secret
    }

def setup_broadcasting_config():
    """Настройка параметров рассылки"""
    print("\n" + "="*50)
    print("📢 НАСТРОЙКА РАССЫЛКИ")
    print("="*50)
    
    delay_between_chats = get_input("Задержка между чатами (секунды)", "5")
    cycle_delay = get_input("Задержка между циклами (секунды)", "900")
    max_retries = get_input("Максимальное количество попыток", "3")
    retry_delay = get_input("Задержка между попытками (секунды)", "60")
    start_time_hour = get_input("Час начала рассылки (0-23)", "6")
    enable_scheduling = get_input("Включить планировщик? (true/false)", "true")
    
    return {
        "DELAY_BETWEEN_CHATS": delay_between_chats,
        "CYCLE_DELAY": cycle_delay,
        "MAX_RETRIES": max_retries,
        "RETRY_DELAY": retry_delay,
        "START_TIME_HOUR": start_time_hour,
        "ENABLE_SCHEDULING": enable_scheduling
    }

def setup_google_sheets_config():
    """Настройка Google Sheets"""
    print("\n" + "="*50)
    print("📊 НАСТРОЙКА GOOGLE SHEETS")
    print("="*50)
    
    use_sheets = get_input("Использовать Google Sheets? (y/n)", "n").lower() == 'y'
    
    if not use_sheets:
        return {
            "GOOGLE_CREDENTIALS_FILE": "credentials.json",
            "SHEET_URL_B2B": "",
            "SHEET_URL_B2C": "",
            "GOOGLE_UPDATE_INTERVAL": "3600"
        }
    
    credentials_file = get_input("Путь к файлу учетных данных", "credentials.json")
    sheet_url_b2b = get_input("URL таблицы B2B сообщений")
    sheet_url_b2c = get_input("URL таблицы B2C сообщений")
    update_interval = get_input("Интервал обновления (секунды)", "3600")
    
    return {
        "GOOGLE_CREDENTIALS_FILE": credentials_file,
        "SHEET_URL_B2B": sheet_url_b2b,
        "SHEET_URL_B2C": sheet_url_b2c,
        "GOOGLE_UPDATE_INTERVAL": update_interval
    }

def setup_logging_config():
    """Настройка логирования"""
    print("\n" + "="*50)
    print("📝 НАСТРОЙКА ЛОГИРОВАНИЯ")
    print("="*50)
    
    log_level = get_input("Уровень логирования (DEBUG/INFO/WARNING/ERROR/CRITICAL)", "INFO")
    log_file = get_input("Путь к файлу логов", "logs/bot.log")
    log_max_size = get_input("Максимальный размер файла лога (байты)", "10485760")
    log_backup_count = get_input("Количество резервных файлов", "5")
    log_console = get_input("Вывод в консоль? (true/false)", "false")
    
    return {
        "LOG_LEVEL": log_level,
        "LOG_FILE": log_file,
        "LOG_MAX_SIZE": log_max_size,
        "LOG_BACKUP_COUNT": log_backup_count,
        "LOG_CONSOLE": log_console
    }

def setup_security_config():
    """Настройка безопасности"""
    print("\n" + "="*50)
    print("🔒 НАСТРОЙКА БЕЗОПАСНОСТИ")
    print("="*50)
    
    master_password = get_input("Мастер-пароль для шифрования", sensitive=True)
    
    return {
        "MASTER_PASSWORD": master_password
    }

def setup_monitoring_config():
    """Настройка мониторинга"""
    print("\n" + "="*50)
    print("📊 НАСТРОЙКА МОНИТОРИНГА")
    print("="*50)
    
    enable_notifications = get_input("Включить уведомления? (y/n)", "n").lower() == 'y'
    
    if not enable_notifications:
        return {
            "ENABLE_STATUS_NOTIFICATIONS": "false",
            "ADMIN_TELEGRAM_ID": "",
            "WEBHOOK_URL": ""
        }
    
    admin_telegram_id = get_input("Telegram ID администратора для уведомлений")
    webhook_url = get_input("Webhook URL для мониторинга (опционально)", "")
    
    return {
        "ENABLE_STATUS_NOTIFICATIONS": "true",
        "ADMIN_TELEGRAM_ID": admin_telegram_id,
        "WEBHOOK_URL": webhook_url
    }

def setup_performance_config():
    """Настройка производительности"""
    print("\n" + "="*50)
    print("⚡ НАСТРОЙКА ПРОИЗВОДИТЕЛЬНОСТИ")
    print("="*50)
    
    max_connections = get_input("Максимальное количество подключений", "10")
    operation_timeout = get_input("Таймаут операций (секунды)", "30")
    thread_pool_size = get_input("Размер пула потоков", "5")
    
    return {
        "MAX_CONNECTIONS": max_connections,
        "OPERATION_TIMEOUT": operation_timeout,
        "THREAD_POOL_SIZE": thread_pool_size
    }

def create_env_file(config):
    """Создание .env файла"""
    env_content = """# ==============================================
# КОНФИГУРАЦИЯ TELEGRAM API
# ==============================================
API_ID={API_ID}
API_HASH={API_HASH}
SESSION_NAME={SESSION_NAME}

# ==============================================
# КОНФИГУРАЦИЯ ПРОКСИ (ОПЦИОНАЛЬНО)
# ==============================================
PROXY_ENABLED={PROXY_ENABLED}
PROXY_PROTOCOL={PROXY_PROTOCOL}
PROXY_ADDR={PROXY_ADDR}
PROXY_PORT={PROXY_PORT}
PROXY_SECRET={PROXY_SECRET}

# ==============================================
# НАСТРОЙКИ РАССЫЛКИ
# ==============================================
DELAY_BETWEEN_CHATS={DELAY_BETWEEN_CHATS}
CYCLE_DELAY={CYCLE_DELAY}
MAX_RETRIES={MAX_RETRIES}
RETRY_DELAY={RETRY_DELAY}
START_TIME_HOUR={START_TIME_HOUR}
ENABLE_SCHEDULING={ENABLE_SCHEDULING}

# ==============================================
# GOOGLE SHEETS ИНТЕГРАЦИЯ
# ==============================================
GOOGLE_CREDENTIALS_FILE={GOOGLE_CREDENTIALS_FILE}
SHEET_URL_B2B={SHEET_URL_B2B}
SHEET_URL_B2C={SHEET_URL_B2C}
GOOGLE_UPDATE_INTERVAL={GOOGLE_UPDATE_INTERVAL}

# ==============================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ==============================================
LOG_LEVEL={LOG_LEVEL}
LOG_FILE={LOG_FILE}
LOG_MAX_SIZE={LOG_MAX_SIZE}
LOG_BACKUP_COUNT={LOG_BACKUP_COUNT}
LOG_CONSOLE={LOG_CONSOLE}

# ==============================================
# БЕЗОПАСНОСТЬ
# ==============================================
MASTER_PASSWORD={MASTER_PASSWORD}

# ==============================================
# МОНИТОРИНГ И УВЕДОМЛЕНИЯ
# ==============================================
ENABLE_STATUS_NOTIFICATIONS={ENABLE_STATUS_NOTIFICATIONS}
ADMIN_TELEGRAM_ID={ADMIN_TELEGRAM_ID}
WEBHOOK_URL={WEBHOOK_URL}

# ==============================================
# ПРОИЗВОДИТЕЛЬНОСТЬ
# ==============================================
MAX_CONNECTIONS={MAX_CONNECTIONS}
OPERATION_TIMEOUT={OPERATION_TIMEOUT}
THREAD_POOL_SIZE={THREAD_POOL_SIZE}
""".format(**config)
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ .env файл создан успешно!")

def main():
    """Основная функция"""
    print("🚀 Настройка SendMessageBot - новая архитектура")
    print("="*60)
    print("Этот скрипт поможет настроить .env файл для запуска")
    print("улучшенной версии SendMessageBot")
    print("="*60)
    
    # Проверяем, есть ли уже .env файл
    if Path('.env').exists():
        overwrite = get_input("\n.env файл уже существует. Перезаписать? (y/n)", "n")
        if overwrite.lower() != 'y':
            print("Настройка отменена.")
            return
    
    try:
        # Собираем все настройки
        config = {}
        
        # Telegram API (обязательно)
        config.update(setup_telegram_config())
        
        # Прокси (опционально)
        config.update(setup_proxy_config())
        
        # Рассылка
        config.update(setup_broadcasting_config())
        
        # Google Sheets (опционально)
        config.update(setup_google_sheets_config())
        
        # Логирование
        config.update(setup_logging_config())
        
        # Безопасность
        config.update(setup_security_config())
        
        # Мониторинг (опционально)
        config.update(setup_monitoring_config())
        
        # Производительность
        config.update(setup_performance_config())
        
        # Создаем .env файл
        create_env_file(config)
        
        print("\n" + "="*60)
        print("🎉 Настройка завершена!")
        print("\nСледующие шаги:")
        print("1. Проверьте .env файл")
        print("2. Установите зависимости: pip install -r requirements_improved.txt")
        print("3. Запустите: python main_improved.py")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nНастройка отменена пользователем.")
    except Exception as e:
        print(f"\n❌ Ошибка при настройке: {e}")

if __name__ == "__main__":
    main()
