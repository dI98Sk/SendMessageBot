#!/usr/bin/env python3
"""
Тестовый запуск ТОЛЬКО рекламных broadcaster'ов с тестовыми чатами
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

# Отключаем scheduling и тихий час для теста
os.environ["ENABLE_SCHEDULING"] = "false"
os.environ["ENABLE_QUIET_HOURS"] = "false"

from config.settings import config_manager
from core.broadcaster import EnhancedBroadcaster
from utils.logger import get_logger

async def test_ads_broadcasters():
    """Тест рекламных broadcaster'ов"""
    print("=" * 80)
    print("🎬 ТЕСТОВЫЙ ЗАПУСК РЕКЛАМНЫХ BROADCASTER'ОВ")
    print("=" * 80)
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚙️  Настройки:")
    print("   - Scheduling: ОТКЛЮЧЕН")
    print("   - Тихий час: ОТКЛЮЧЕН")
    print("   - Чаты: ТЕСТОВЫЕ")
    print()
    
    # Загрузка конфигурации
    config = config_manager.load_config()
    logger = get_logger("test_ads", config.logging)
    
    # Проверка конфигурации
    print("📋 Конфигурация:")
    print(f"  ✓ Тестовых чатов для рекламы: {len(config.targets_ads_test)}")
    print(f"  ✓ AAA ADS сообщений: {len(config.aaa_ads_messages)}")
    print(f"  ✓ GUS ADS сообщений: {len(config.gus_ads_messages)}")
    print()
    
    if not config.targets_ads_test:
        print("❌ Ошибка: TEST_TARGETS_ADS пуст!")
        print("   Проверьте config/targets.py")
        return
    
    print("🎯 Тестовые чаты для рекламы:")
    for i, chat_id in enumerate(config.targets_ads_test, 1):
        print(f"   {i}. {chat_id}")
    print()
    
    # Создаем только рекламные broadcaster'ы
    broadcasters = []
    
    # AAA Реклама - Анна Макарова (acc2)
    print("📱 Создание AAA_ADS_Broadcaster...")
    aaa_ads = EnhancedBroadcaster(
        config=config,
        name="AAA_ADS_TEST_Broadcaster",
        targets=config.targets_ads_test,  # Используем ТЕСТОВЫЕ чаты
        messages=config.aaa_ads_messages,
        session_name="sessions/acc2"  # Анна Макарова
    )
    broadcasters.append(aaa_ads)
    print(f"   ✅ Создан (acc2): {len(config.targets_ads_test)} чатов, {len(config.aaa_ads_messages)} сообщений")
    
    # GUS Реклама - Яблочный Гусь Менеджер (acc1)
    print("📱 Создание GUS_ADS_Broadcaster...")
    gus_ads = EnhancedBroadcaster(
        config=config,
        name="GUS_ADS_TEST_Broadcaster",
        targets=config.targets_ads_test,  # Используем ТЕСТОВЫЕ чаты
        messages=config.gus_ads_messages,
        session_name="sessions/acc1"  # Яблочный Гусь Менеджер
    )
    broadcasters.append(gus_ads)
    print(f"   ✅ Создан (acc1): {len(config.targets_ads_test)} чатов, {len(config.gus_ads_messages)} сообщений")
    
    print(f"\n📊 Всего broadcaster'ов: {len(broadcasters)}")
    
    print("\n" + "=" * 80)
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ")
    print("=" * 80)
    print("📝 Broadcaster'ы будут работать 3 минуты")
    print("💡 Нажмите Ctrl+C для досрочной остановки")
    print("=" * 80)
    print()
    
    try:
        # Запускаем broadcaster'ы
        tasks = []
        for broadcaster in broadcasters:
            logger.info(f"Запуск {broadcaster.name}")
            task = asyncio.create_task(broadcaster.start())
            tasks.append(task)
        
        # Ждем 3 минуты
        await asyncio.sleep(180)
        
        print("\n⏰ 3 минуты истекли, останавливаем...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Остановка по Ctrl+C...")
    finally:
        # Останавливаем все broadcaster'ы
        print("\n🛑 Остановка broadcaster'ов...")
        for broadcaster in broadcasters:
            await broadcaster.stop()
        
        # Статистика
        print("\n" + "=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        
        for broadcaster in broadcasters:
            stats = broadcaster.get_stats()
            print(f"\n🤖 {stats['name']}:")
            print(f"   ✅ Отправлено: {stats['total_sent']}")
            print(f"   ❌ Ошибок: {stats['total_failed']}")
            print(f"   ⏳ FloodWait: {stats['flood_waits']}")
            
            if stats['total_sent'] + stats['total_failed'] > 0:
                success_rate = (stats['total_sent'] / (stats['total_sent'] + stats['total_failed'])) * 100
                print(f"   📈 Успешность: {success_rate:.1f}%")
        
        # Общая статистика
        total_sent = sum(b.stats.total_sent for b in broadcasters)
        total_failed = sum(b.stats.total_failed for b in broadcasters)
        
        print(f"\n📊 ВСЕГО:")
        print(f"   ✅ Отправлено: {total_sent}")
        print(f"   ❌ Ошибок: {total_failed}")
        
        if total_sent > 0:
            print(f"\n✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
            print(f"   Отправлено {total_sent} сообщений в тестовые чаты")
        elif total_failed > 0:
            print(f"\n⚠️  ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ")
            print(f"   Проверьте логи: tail -f bot.log")
        else:
            print(f"\n⚠️  НЕТ ДАННЫХ")
            print(f"   Возможно, broadcaster'ы еще не успели отправить сообщения")
        
        print("\n" + "=" * 80)
        print("✅ Тестирование завершено!")
        print("=" * 80)
        
        if total_sent > 0:
            print("\n💡 Следующие шаги:")
            print("   1. Проверьте сообщения в тестовых чатах Telegram")
            print("   2. Если все ОК, можно запускать на production чатах")
            print("   3. Для production: python main.py")

if __name__ == "__main__":
    asyncio.run(test_ads_broadcasters())

