#!/usr/bin/env python3
"""
Скрипт для отображения статистики работы бота
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager
from config.targets import TEST_TARGETS, TARGETS
from config.messages import MESSAGES_B2B, MESSAGES_B2C
from utils.logger import get_logger
from core.broadcaster import EnhancedBroadcaster
from monitoring.metrics import MetricsCollector, HealthChecker

def print_system_overview():
    """Общий обзор системы"""
    print("🎯 SendMessageBot - Обзор системы")
    print("=" * 60)
    
    config = config_manager.load_config()
    
    print(f"📱 API ID: {config.telegram.api_id}")
    print(f"📁 Сессия: {config.telegram.session_name}")
    print(f"🎯 Основных чатов: {len(TARGETS)}")
    print(f"🧪 Тестовых чатов: {len(TEST_TARGETS)}")
    print(f"💬 B2B сообщений: {len(MESSAGES_B2B)}")
    print(f"💬 B2C сообщений: {len(MESSAGES_B2C)}")
    
    print(f"\n⚙️  Настройки рассылки:")
    print(f"   - Задержка между чатами: {config.broadcasting.delay_between_chats}с")
    print(f"   - Задержка между циклами: {config.broadcasting.delay_between_cycles}с")
    print(f"   - Максимальные повторы: {config.broadcasting.max_retries}")
    print(f"   - Планировщик: {'Включен' if config.broadcasting.enable_scheduling else 'Отключен'}")
    
    if config.broadcasting.enable_scheduling:
        print(f"   - Время начала: {config.broadcasting.start_time_hour}:00")
        print(f"   - Время окончания: {config.broadcasting.end_time_hour}:00")
    
    print("=" * 60)

def print_targets_info():
    """Информация о целевых чатах"""
    print("\n🎯 Целевые чаты:")
    print("-" * 30)
    
    print(f"🧪 Тестовые чаты ({len(TEST_TARGETS)}):")
    for i, chat_id in enumerate(TEST_TARGETS, 1):
        print(f"   {i}. {chat_id}")
    
    print(f"\n📱 Основные чаты (первые 10 из {len(TARGETS)}):")
    for i, chat_id in enumerate(TARGETS[:10], 1):
        print(f"   {i}. {chat_id}")
    
    if len(TARGETS) > 10:
        print(f"   ... и еще {len(TARGETS) - 10} чатов")

def print_messages_info():
    """Информация о сообщениях"""
    print("\n💬 Сообщения для рассылки:")
    print("-" * 30)
    
    print(f"📊 B2B сообщения ({len(MESSAGES_B2B)}):")
    for i, msg in enumerate(MESSAGES_B2B[:3], 1):  # Показываем первые 3
        preview = msg[:100] + "..." if len(msg) > 100 else msg
        print(f"   {i}. {preview}")
    
    if len(MESSAGES_B2B) > 3:
        print(f"   ... и еще {len(MESSAGES_B2B) - 3} сообщений")
    
    print(f"\n📊 B2C сообщения ({len(MESSAGES_B2C)}):")
    for i, msg in enumerate(MESSAGES_B2C[:2], 1):  # Показываем первые 2
        preview = msg[:100] + "..." if len(msg) > 100 else msg
        print(f"   {i}. {preview}")
    
    if len(MESSAGES_B2C) > 2:
        print(f"   ... и еще {len(MESSAGES_B2C) - 2} сообщений")

async def simulate_broadcaster_stats():
    """Симуляция статистики broadcaster'ов"""
    print("\n📊 Симуляция статистики (без реальной отправки):")
    print("-" * 50)
    
    config = config_manager.load_config()
    
    # Создаем тестовые broadcaster'ы
    b2b_broadcaster = EnhancedBroadcaster(
        config=config,
        name="B2B_Test",
        targets=TEST_TARGETS,
        messages=MESSAGES_B2B[:2]
    )
    
    b2c_broadcaster = EnhancedBroadcaster(
        config=config,
        name="B2C_Test",
        targets=TEST_TARGETS,
        messages=MESSAGES_B2C[:1]
    )
    
    # Показываем статистику
    b2b_broadcaster.print_stats()
    b2c_broadcaster.print_stats()

def print_health_check():
    """Проверка здоровья системы"""
    print("\n🏥 Проверка здоровья системы:")
    print("-" * 40)
    
    # Создаем тестовый MetricsCollector
    metrics = MetricsCollector()
    health_checker = HealthChecker(metrics)
    
    # Симулируем некоторые метрики
    from monitoring.metrics import MessageMetric
    from datetime import datetime
    
    # Добавляем тестовые метрики
    test_metric = MessageMetric(
        timestamp=datetime.now(),
        chat_id=-1002679672234,
        message_id=1,
        success=True,
        response_time=1.5
    )
    metrics.record_message(test_metric)
    
    # Проверяем здоровье
    health = health_checker.check_health()
    
    status_emoji = {
        'healthy': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    print(f"Общий статус: {status_emoji.get(health['status'], '❓')} {health['status'].upper()}")
    print(f"Время проверки: {health['timestamp']}")
    
    for check_name, check_result in health['checks'].items():
        emoji = status_emoji.get(check_result['status'], '❓')
        print(f"  {emoji} {check_name}: {check_result['message']}")

def print_usage_examples():
    """Примеры использования"""
    print("\n💡 Примеры использования:")
    print("-" * 30)
    
    print("🚀 Запуск бота:")
    print("   python main_simple.py          # Упрощенная версия")
    print("   python main_improved.py        # Полная версия")
    
    print("\n📊 Просмотр статистики:")
    print("   python show_stats.py           # Этот скрипт")
    print("   python switch_targets.py       # Переключение чатов")
    
    print("\n🔧 Управление:")
    print("   Ctrl+C                         # Остановка бота")
    print("   python migrate_project.py      # Миграция старых файлов")

async def main():
    """Главная функция"""
    print_system_overview()
    print_targets_info()
    print_messages_info()
    await simulate_broadcaster_stats()
    print_health_check()
    print_usage_examples()
    
    print(f"\n🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ Готово! Система настроена и готова к работе.")

if __name__ == "__main__":
    asyncio.run(main())
