"""
Тестовый скрипт для проверки системы отчетов
"""
import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования для теста
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from monitoring.reports import TelegramReporter
from config.settings import config_manager

async def test_reports():
    """Тест системы отчетов"""
    print("=" * 60)
    print("🧪 Тестирование системы отчетов")
    print("=" * 60)
    
    # Загружаем конфигурацию
    config = config_manager.load_config()
    
    # Проверяем настройки
    print("\n📋 Проверка конфигурации:")
    print(f"✓ ENABLE_REPORTS: {config.reports.enable_reports}")
    print(f"✓ BOT_TOKEN установлен: {'Да' if config.reports.telegram_bot_token else 'Нет'}")
    print(f"✓ CHANNEL_ID: {config.reports.telegram_channel_id or 'Не установлен'}")
    print(f"✓ Интервал отчетов: {config.reports.report_interval_hours} часов")
    
    if not config.reports.enable_reports:
        print("\n❌ Система отчетов ОТКЛЮЧЕНА в конфигурации!")
        print("   Установите переменную окружения ENABLE_REPORTS=true")
        return
    
    if not config.reports.telegram_bot_token:
        print("\n❌ Не установлен REPORTS_BOT_TOKEN!")
        print("   Получите токен у @BotFather в Telegram")
        return
    
    if not config.reports.telegram_channel_id:
        print("\n❌ Не установлен REPORTS_CHANNEL_ID!")
        print("   Укажите ID канала или чата для отчетов")
        return
    
    print("\n✅ Конфигурация корректна!")
    
    # Создаем репортер
    reporter = TelegramReporter(
        bot_token=config.reports.telegram_bot_token,
        channel_id=config.reports.telegram_channel_id,
        timezone=config.reports.timezone
    )
    reporter.report_interval_hours = config.reports.report_interval_hours
    
    print("\n📤 Отправка тестового отчета...")
    
    # Создаем мок broadcaster'ы с тестовыми данными
    class MockStats:
        def __init__(self):
            self.total_sent = 10
            self.total_failed = 2
            self.flood_waits = 1
            self.last_sent_time = datetime.now()
    
    class MockMetrics:
        def __init__(self):
            self.message_metrics = []
            self.stats = {'total_cycles_completed': 3}
            self.chat_stats = {}
        
        def _get_top_chats(self, n):
            return []
    
    class MockBroadcaster:
        def __init__(self, name):
            self.name = name
            self.stats = MockStats()
            self.metrics = MockMetrics()
            self._running = True
    
    # Создаем тестовые broadcaster'ы
    test_broadcasters = [
        MockBroadcaster("AAA_Broadcaster"),
        MockBroadcaster("GUS_Broadcaster")
    ]
    
    # Отправляем тестовый отчет
    success = await reporter.send_report(test_broadcasters)
    
    if success:
        print("\n✅ Тестовый отчет успешно отправлен!")
        print(f"   Проверьте канал/чат: {config.reports.telegram_channel_id}")
        print(f"   Всего отправлено отчетов: {reporter.reports_sent}")
    else:
        print("\n❌ Не удалось отправить тестовый отчет!")
        print("   Проверьте:")
        print("   1. Правильность токена бота")
        print("   2. ID канала/чата")
        print("   3. Добавлен ли бот в канал/чат")
        print("   4. Есть ли у бота права на отправку сообщений")
    
    print("\n" + "=" * 60)

async def test_empty_report():
    """Тест отправки пустого отчета (должен быть пропущен)"""
    print("\n🧪 Тест пустого отчета:")
    
    config = config_manager.load_config()
    
    if not config.reports.enable_reports or not config.reports.telegram_bot_token:
        print("⏭️  Пропускаем тест (отчеты не настроены)")
        return
    
    reporter = TelegramReporter(
        bot_token=config.reports.telegram_bot_token,
        channel_id=config.reports.telegram_channel_id,
        timezone=config.reports.timezone
    )
    
    class MockEmptyStats:
        def __init__(self):
            self.total_sent = 0
            self.total_failed = 0
            self.flood_waits = 0
            self.last_sent_time = None
    
    class MockEmptyMetrics:
        def __init__(self):
            self.message_metrics = []
            self.stats = {'total_cycles_completed': 0}
            self.chat_stats = {}
        
        def _get_top_chats(self, n):
            return []
    
    class MockEmptyBroadcaster:
        def __init__(self, name):
            self.name = name
            self.stats = MockEmptyStats()
            self.metrics = MockEmptyMetrics()
            self._running = False
    
    empty_broadcasters = [MockEmptyBroadcaster("Test")]
    
    success = await reporter.send_report(empty_broadcasters)
    
    if not success:
        print("✅ Пустой отчет корректно пропущен (это правильно!)")
    else:
        print("⚠️  Пустой отчет был отправлен (возможно, это не ожидается)")

if __name__ == "__main__":
    asyncio.run(test_reports())
    asyncio.run(test_empty_report())

