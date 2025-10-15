#!/usr/bin/env python3
"""
Утилита для управления системой отчетов
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager
from monitoring.reports import TelegramReporter
from core.broadcaster import EnhancedBroadcaster
from utils.logger import get_logger

# Получаем конфигурацию для логгера
config = config_manager.load_config()
logger = get_logger(__name__, config.logging)

async def test_telegram_reports():
    """Тестирование отправки отчета в Telegram"""
    print("🧪 Тестирование системы отчетов...")
    
    try:
        # Загружаем конфигурацию
        config = config_manager.load_config()
        
        if not config.reports.enable_reports:
            print("❌ Система отчетов отключена в конфигурации")
            return False
        
        if not config.reports.telegram_bot_token or not config.reports.telegram_channel_id:
            print("❌ Не настроены REPORTS_BOT_TOKEN или REPORTS_CHANNEL_ID")
            return False
        
        # Создаем тестовый репортер
        reporter = TelegramReporter(
            bot_token=config.reports.telegram_bot_token,
            channel_id=config.reports.telegram_channel_id,
            timezone=config.reports.timezone
        )
        
        # Создаем тестовые broadcaster'ы для демонстрации
        test_broadcasters = []
        
        # Тестовый B2B broadcaster
        b2b_broadcaster = EnhancedBroadcaster(
            api_id=config.telegram.api_id,
            api_hash=config.telegram.api_hash,
            phone=config.telegram.phone,
            session_name="test_b2b_reports",
            messages=config.b2b_messages[:2],  # Берем только 2 сообщения для теста
            targets=config.test_targets,
            delay_between_messages=30,
            delay_between_cycles=60,
            max_retries=2,
            use_proxy=config.telegram.use_proxy,
            proxy_config=config.telegram.proxy_config
        )
        test_broadcasters.append(b2b_broadcaster)
        
        # Тестовый B2C broadcaster
        b2c_broadcaster = EnhancedBroadcaster(
            api_id=config.telegram.api_id,
            api_hash=config.telegram.api_hash,
            phone=config.telegram.phone,
            session_name="test_b2c_reports",
            messages=config.b2c_messages[:1],  # Берем только 1 сообщение для теста
            targets=config.test_targets,
            delay_between_messages=30,
            delay_between_cycles=60,
            max_retries=2,
            use_proxy=config.telegram.use_proxy,
            proxy_config=config.telegram.proxy_config
        )
        test_broadcasters.append(b2c_broadcaster)
        
        print("📤 Отправка тестового отчета...")
        
        # Отправляем тестовый отчет
        success = await reporter.send_report(test_broadcasters)
        
        if success:
            print("✅ Тестовый отчет отправлен успешно!")
            print(f"📊 Канал: {config.reports.telegram_channel_id}")
            print(f"⏰ Интервал отчетов: {config.reports.report_interval_hours} часов")
            print(f"🌍 Часовой пояс: {config.reports.timezone}")
        else:
            print("❌ Ошибка отправки тестового отчета")
        
        return success
        
    except Exception as e:
        logger.error(f"Ошибка тестирования отчетов: {e}")
        print(f"❌ Ошибка: {e}")
        return False

async def send_manual_report():
    """Ручная отправка отчета"""
    print("📊 Отправка ручного отчета...")
    
    try:
        config = config_manager.load_config()
        
        if not config.reports.enable_reports:
            print("❌ Система отчетов отключена")
            return False
        
        # Создаем репортер
        reporter = TelegramReporter(
            bot_token=config.reports.telegram_bot_token,
            channel_id=config.reports.telegram_channel_id,
            timezone=config.reports.timezone
        )
        
        # Создаем пустой список broadcaster'ов для демонстрации
        # В реальном использовании здесь должны быть активные broadcaster'ы
        empty_broadcasters = []
        
        success = await reporter.send_report(empty_broadcasters)
        
        if success:
            print("✅ Ручной отчет отправлен!")
        else:
            print("❌ Ошибка отправки ручного отчета")
        
        return success
        
    except Exception as e:
        logger.error(f"Ошибка отправки ручного отчета: {e}")
        print(f"❌ Ошибка: {e}")
        return False

def show_reports_config():
    """Показать конфигурацию отчетов"""
    print("⚙️ Конфигурация системы отчетов:")
    print("=" * 50)
    
    try:
        config = config_manager.load_config()
        
        print(f"📊 Включена: {'✅' if config.reports.enable_reports else '❌'}")
        print(f"🤖 Bot Token: {'✅ Настроен' if config.reports.telegram_bot_token else '❌ Не настроен'}")
        print(f"📺 Channel ID: {'✅ Настроен' if config.reports.telegram_channel_id else '❌ Не настроен'}")
        print(f"⏰ Интервал: {config.reports.report_interval_hours} часов")
        print(f"🌍 Часовой пояс: {config.reports.timezone}")
        
        if config.reports.enable_reports and config.reports.telegram_bot_token and config.reports.telegram_channel_id:
            print("\n✅ Система отчетов готова к работе!")
        else:
            print("\n❌ Система отчетов не настроена полностью")
            print("\nНеобходимые переменные окружения:")
            print("- ENABLE_REPORTS=true")
            print("- REPORTS_BOT_TOKEN=your_bot_token")
            print("- REPORTS_CHANNEL_ID=@your_channel")
            print("- REPORT_INTERVAL_HOURS=12")
            print("- REPORTS_TIMEZONE=Europe/Moscow")
        
    except Exception as e:
        logger.error(f"Ошибка получения конфигурации: {e}")
        print(f"❌ Ошибка: {e}")

async def main():
    """Главное меню"""
    while True:
        print("\n" + "=" * 60)
        print("📈 УПРАВЛЕНИЕ СИСТЕМОЙ ОТЧЕТОВ")
        print("=" * 60)
        print("1. Показать конфигурацию отчетов")
        print("2. Тестировать отправку отчета")
        print("3. Отправить ручной отчет")
        print("4. Выход")
        print("=" * 60)
        
        try:
            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == "1":
                show_reports_config()
            elif choice == "2":
                await test_telegram_reports()
            elif choice == "3":
                await send_manual_report()
            elif choice == "4":
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n👋 Выход...")
            break
        except Exception as e:
            logger.error(f"Ошибка в меню: {e}")
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
