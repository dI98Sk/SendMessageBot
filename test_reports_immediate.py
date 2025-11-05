"""
Тест отчетов с немедленным запуском broadcaster'ов (без ожидания времени)
"""
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Временно отключаем scheduling и тихий час для теста
os.environ["ENABLE_SCHEDULING"] = "false"
os.environ["ENABLE_QUIET_HOURS"] = "false"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from main import SendMessageBotApp

async def test_immediate():
    """Тест с немедленным запуском"""
    print("=" * 80)
    print("⚡ ТЕСТ ОТЧЕТОВ С НЕМЕДЛЕННЫМ ЗАПУСКОМ")
    print("=" * 80)
    print("⚙️  Scheduling отключен")
    print("⚙️  Тихий час отключен")
    print()
    
    app = SendMessageBotApp()
    
    try:
        await app.initialize()
        
        # Проверяем конфигурацию
        print(f"✅ Scheduling включен: {app.config.broadcasting.enable_scheduling}")
        print(f"✅ Тихий час включен: {app.config.broadcasting.enable_quiet_hours}")
        print(f"📊 Интервал отчетов: {app.config.reports.report_interval_hours} часов")
        print(f"📡 Broadcaster'ов: {len(app.broadcasters)}")
        print()
        
        # Запускаем бот в фоновом режиме
        print("🚀 Запуск бота на 3 минуты...")
        print("   Broadcaster'ы начнут работу немедленно")
        print()
        
        bot_task = asyncio.create_task(app.start())
        
        # Ждем 180 секунд (3 минуты)
        await asyncio.sleep(180)
        
        # Статистика
        print("\n" + "=" * 80)
        print("📊 СТАТИСТИКА ПОСЛЕ 3 МИНУТ РАБОТЫ")
        print("=" * 80)
        
        total_sent = 0
        total_failed = 0
        
        for broadcaster in app.broadcasters:
            stats = broadcaster.get_stats()
            print(f"\n{stats['name']}:")
            print(f"  ✅ Отправлено: {stats['total_sent']}")
            print(f"  ❌ Ошибок: {stats['total_failed']}")
            print(f"  ⏳ FloodWait: {stats['flood_waits']}")
            total_sent += stats['total_sent']
            total_failed += stats['total_failed']
        
        print(f"\n📊 ВСЕГО:")
        print(f"  ✅ Отправлено: {total_sent}")
        print(f"  ❌ Ошибок: {total_failed}")
        
        # Проверяем отчеты
        if app.telegram_reporter:
            status = app.telegram_reporter.get_status()
            print(f"\n📈 Система отчетов:")
            print(f"  📤 Отправлено отчетов: {status['reports_sent']}")
            print(f"  ⏰ Последний отчет: {status['last_report_time'] or 'Не отправлялись'}")
            
            # Пытаемся отправить отчет вручную
            if total_sent > 0 or total_failed > 0:
                print(f"\n📤 Отправка итогового отчета...")
                success = await app.telegram_reporter.send_report(app.broadcasters)
                if success:
                    print("✅ Итоговый отчет отправлен!")
                else:
                    print("❌ Не удалось отправить итоговый отчет")
        
        print("\n🛑 Остановка бота...")
        
    except KeyboardInterrupt:
        print("\n⚠️  Прервано")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        logging.exception("Traceback:")
    finally:
        await app.shutdown()
        
        print("\n" + "=" * 80)
        print("✅ Тест завершен!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_immediate())


