#!/usr/bin/env python3
"""
Тест новых broadcaster'ов для рекламы
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from main import SendMessageBotApp

async def test_broadcasters():
    """Тест создания всех broadcaster'ов"""
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ НОВЫХ BROADCASTER'ОВ")
    print("=" * 70)
    
    app = SendMessageBotApp()
    
    try:
        # Инициализация
        print("\n📋 Инициализация...")
        await app.initialize()
        
        print("\n✅ Инициализация завершена успешно!")
        
        # Проверка конфигурации
        print("\n📊 Конфигурация:")
        print(f"  ✓ Targets (test): {len(app.config.targets)}")
        print(f"  ✓ Targets ADS: {len(app.config.targets_ads)}")
        print(f"  ✓ Targets PRICES: {len(app.config.targets_prices)}")
        print(f"\n  ✓ AAA Messages (price): {len(app.config.aaa_messages)}")
        print(f"  ✓ GUS Messages (price): {len(app.config.gus_messages)}")
        print(f"  ✓ AAA ADS Messages: {len(app.config.aaa_ads_messages)}")
        print(f"  ✓ GUS ADS Messages: {len(app.config.gus_ads_messages)}")
        
        # Проверка Google Sheets настроек
        print(f"\n📋 Google Sheets URLs:")
        print(f"  AAA Price: {'✅' if app.config.google_sheets.aaa_sheet_url else '❌'}")
        print(f"  GUS Price: {'✅' if app.config.google_sheets.gus_sheet_url else '❌'}")
        print(f"  AAA ADS: {'✅' if app.config.google_sheets.aaa_ads_sheet_url else '❌'}")
        print(f"  GUS ADS: {'✅' if app.config.google_sheets.gus_ads_sheet_url else '❌'}")
        
        # Проверка broadcaster'ов
        print(f"\n🤖 Broadcaster'ы ({len(app.broadcasters)} шт.):")
        print("=" * 70)
        
        for idx, broadcaster in enumerate(app.broadcasters, 1):
            print(f"\n{idx}. {broadcaster.name}")
            print(f"   Session: {broadcaster.session_name}")
            print(f"   Чатов: {len(broadcaster.targets)}")
            print(f"   Сообщений: {len(broadcaster.messages)}")
            print(f"   Статус: {'🟢 Готов' if broadcaster._client else '🔴 Не инициализирован'}")
        
        print("\n" + "=" * 70)
        print("📊 ИТОГОВАЯ СТАТИСТИКА:")
        print("=" * 70)
        
        # Подсчет broadcaster'ов по типу
        price_broadcasters = [b for b in app.broadcasters if 'PRICE' in b.name]
        ads_broadcasters = [b for b in app.broadcasters if 'ADS' in b.name]
        
        print(f"\n  📈 PRICE broadcaster'ы: {len(price_broadcasters)}")
        for b in price_broadcasters:
            print(f"     - {b.name}: {len(b.targets)} чатов, {len(b.messages)} сообщений")
        
        print(f"\n  📢 ADS broadcaster'ы: {len(ads_broadcasters)}")
        for b in ads_broadcasters:
            print(f"     - {b.name}: {len(b.targets)} чатов, {len(b.messages)} сообщений")
        
        print(f"\n  🎯 Всего broadcaster'ов: {len(app.broadcasters)}")
        print(f"  ✅ Ожидается: 4 (2 PRICE + 2 ADS)")
        
        if len(app.broadcasters) == 4:
            print("\n✅ ВСЕ BROADCASTER'Ы СОЗДАНЫ УСПЕШНО!")
        else:
            print(f"\n⚠️  ВНИМАНИЕ: Ожидалось 4 broadcaster'а, создано {len(app.broadcasters)}")
        
        # Проверка отчетов
        print("\n📊 Система отчетов:")
        if app.telegram_reporter:
            print(f"  ✅ Включена")
            print(f"  📤 Интервал: {app.config.reports.report_interval_hours} часов")
            print(f"  📱 Канал: {app.config.reports.telegram_channel_id}")
        else:
            print(f"  ❌ Отключена")
        
        print("\n" + "=" * 70)
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("=" * 70)
        
        print("\n💡 Следующие шаги:")
        print("   1. Обновите сообщения из Google Sheets:")
        print("      python scripts/update_ads_messages.py")
        print("   2. Запустите бот:")
        print("      python main.py")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_broadcasters())


