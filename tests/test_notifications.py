#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы уведомлений
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager
from monitoring.notifications import (
    notification_manager, alert_manager,
    TelegramNotificationChannel, NotificationLevel
)
from telethon import TelegramClient

async def test_telegram_notifications():
    """Тестирование Telegram уведомлений"""
    print("🧪 Тестирование системы уведомлений...")
    
    try:
        # Загружаем конфигурацию
        config = config_manager.load_config()
        
        print(f"📋 Конфигурация уведомлений:")
        print(f"   - Telegram уведомления: {'✅' if config.notifications.enable_telegram_notifications else '❌'}")
        print(f"   - Admin ID: {config.notifications.admin_telegram_id or 'Не настроен'}")
        print(f"   - Уровень: {config.notifications.notification_level}")
        print(f"   - Webhook уведомления: {'✅' if config.notifications.enable_webhook_notifications else '❌'}")
        print(f"   - Webhook URL: {config.notifications.webhook_url or 'Не настроен'}")
        
        # Проверяем настройки
        if not config.notifications.enable_telegram_notifications:
            print("❌ Telegram уведомления отключены в конфигурации")
            print("   Установите ENABLE_TELEGRAM_NOTIFICATIONS=true")
            return False
        
        if not config.notifications.admin_telegram_id:
            print("❌ ADMIN_TELEGRAM_ID не настроен")
            print("   Установите ADMIN_TELEGRAM_ID=ваш_telegram_id")
            return False
        
        # Создаем Telegram клиент для тестирования
        print("📱 Создание Telegram клиента...")
        
        notification_client = TelegramClient(
            "test_notification_session",
            config.telegram.api_id,
            config.telegram.api_hash
        )
        
        # Запускаем клиент
        await notification_client.start(phone=config.telegram.phone)
        print("✅ Telegram клиент запущен")
        
        # Создаем канал уведомлений
        telegram_channel = TelegramNotificationChannel(
            client=notification_client,
            admin_chat_id=config.notifications.admin_telegram_id
        )
        
        # Добавляем канал в менеджер
        notification_manager.add_channel(telegram_channel)
        print(f"✅ Канал уведомлений добавлен для admin: {config.notifications.admin_telegram_id}")
        
        # Настраиваем алерты
        alert_manager.add_default_rules()
        print("✅ Система алертов настроена")
        
        # Тестируем разные типы уведомлений
        print("\n📤 Отправка тестовых уведомлений...")
        
        # Информационное уведомление
        success = await notification_manager.send_info(
            "Тест уведомлений",
            "Это тестовое информационное уведомление для проверки системы",
            rate_limit_key="test_info",
            rate_limit_seconds=0  # Отключаем rate limit для тестов
        )
        print(f"   ℹ️  Информационное: {'✅' if success else '❌'}")
        
        # Предупреждение
        success = await notification_manager.send_warning(
            "Тест предупреждения",
            "Это тестовое предупреждение для проверки системы",
            rate_limit_key="test_warning",
            rate_limit_seconds=0
        )
        print(f"   ⚠️  Предупреждение: {'✅' if success else '❌'}")
        
        # Ошибка
        success = await notification_manager.send_error(
            "Тест ошибки",
            "Это тестовая ошибка для проверки системы",
            rate_limit_key="test_error",
            rate_limit_seconds=0
        )
        print(f"   ❌ Ошибка: {'✅' if success else '❌'}")
        
        # Критическое уведомление
        success = await notification_manager.send_critical(
            "Тест критического уведомления",
            "Это тестовое критическое уведомление для проверки системы",
            rate_limit_key="test_critical",
            rate_limit_seconds=0
        )
        print(f"   🚨 Критическое: {'✅' if success else '❌'}")
        
        # Тестируем алерты
        print("\n🚨 Тестирование алертов...")
        
        # Симулируем низкий процент успешности
        test_metrics = {
            'success_rate': 75.0,  # Низкий процент
            'total_flood_waits': 5,
            'last_activity': None
        }
        
        await alert_manager.check_alerts(test_metrics)
        print("   ✅ Алерты протестированы")
        
        # Проверяем историю уведомлений
        history = notification_manager.get_notification_history(10)
        print(f"\n📊 История уведомлений: {len(history)} записей")
        
        # Отключаем клиент
        await notification_client.disconnect()
        print("✅ Telegram клиент отключен")
        
        print("\n🎉 Тестирование завершено успешно!")
        print(f"📱 Проверьте Telegram - должны прийти 4 тестовых сообщения")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

async def test_webhook_notifications():
    """Тестирование Webhook уведомлений"""
    print("\n🌐 Тестирование Webhook уведомлений...")
    
    try:
        config = config_manager.load_config()
        
        if not config.notifications.enable_webhook_notifications:
            print("❌ Webhook уведомления отключены")
            return False
        
        if not config.notifications.webhook_url or config.notifications.webhook_url == "https://your-webhook-url.com":
            print("❌ WEBHOOK_URL не настроен")
            return False
        
        from monitoring.notifications import WebhookNotificationChannel
        
        webhook_channel = WebhookNotificationChannel(config.notifications.webhook_url)
        notification_manager.add_channel(webhook_channel)
        
        success = await notification_manager.send_info(
            "Тест Webhook",
            "Это тестовое уведомление через Webhook",
            rate_limit_key="test_webhook",
            rate_limit_seconds=0
        )
        
        print(f"   🌐 Webhook: {'✅' if success else '❌'}")
        return success
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Webhook: {e}")
        return False

def show_configuration_help():
    """Показать помощь по настройке"""
    print("\n📋 Настройка системы уведомлений:")
    print("=" * 50)
    print("Для включения Telegram уведомлений установите:")
    print("   ENABLE_TELEGRAM_NOTIFICATIONS=true")
    print("   ADMIN_TELEGRAM_ID=123456789")
    print("   NOTIFICATION_LEVEL=INFO")
    print()
    print("Для включения Webhook уведомлений установите:")
    print("   ENABLE_WEBHOOK_NOTIFICATIONS=true")
    print("   WEBHOOK_URL=https://your-webhook-url.com")
    print()
    print("Уровни уведомлений: DEBUG, INFO, WARNING, ERROR, CRITICAL")

async def main():
    """Главное меню"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ УВЕДОМЛЕНИЙ")
    print("=" * 50)
    
    print("Выберите действие:")
    print("1. Тестировать Telegram уведомления")
    print("2. Тестировать Webhook уведомления")
    print("3. Показать помощь по настройке")
    print("4. Выход")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        await test_telegram_notifications()
    elif choice == "2":
        await test_webhook_notifications()
    elif choice == "3":
        show_configuration_help()
    elif choice == "4":
        print("👋 До свидания!")
    else:
        print("❌ Неверный выбор")

if __name__ == "__main__":
    asyncio.run(main())
