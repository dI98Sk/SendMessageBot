#!/usr/bin/env python3
"""
Скрипт для тестирования новых броудкастеров AAA и GUS
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import config_manager
from core.broadcaster import EnhancedBroadcaster
from utils.logger import get_logger

async def test_aaa_broadcaster():
    """Тестирование AAA броудкастера"""
    print("🔥 Тестирование AAA Broadcaster")
    print("=" * 50)
    
    try:
        # Загружаем конфигурацию
        config = config_manager.load_config()
        logger = get_logger("test_aaa", config.logging)
        
        # Создаем AAA броудкастер
        aaa_broadcaster = EnhancedBroadcaster(
            config=config,
            name="AAA_Test_Broadcaster",
            targets=config.targets,  # Тестовые чаты
            messages=config.aaa_messages,
            session_name="sessions/acc1"  # Оптовый аккаунт
        )
        
        print(f"✅ AAA Broadcaster создан")
        print(f"🎯 Целевых чатов: {len(config.targets)}")
        print(f"💬 Сообщений: {len(config.aaa_messages)}")
        print(f"📱 Сессия: sessions/acc1")
        
        # Подключаемся
        await aaa_broadcaster._ensure_connection()
        
        print("✅ AAA Broadcaster готов к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования AAA: {e}")
        logger.exception(f"Ошибка тестирования AAA: {e}")

async def test_gus_broadcaster():
    """Тестирование GUS броудкастера"""
    print("\n🪿 Тестирование GUS Broadcaster")
    print("=" * 50)
    
    try:
        # Загружаем конфигурацию
        config = config_manager.load_config()
        logger = get_logger("test_gus", config.logging)
        
        # Создаем GUS броудкастер
        gus_broadcaster = EnhancedBroadcaster(
            config=config,
            name="GUS_Test_Broadcaster",
            targets=config.targets,  # Тестовые чаты
            messages=config.gus_messages,
            session_name="sessions/acc2"  # Розничный аккаунт
        )
        
        print(f"✅ GUS Broadcaster создан")
        print(f"🎯 Целевых чатов: {len(config.targets)}")
        print(f"💬 Сообщений: {len(config.gus_messages)}")
        print(f"📱 Сессия: sessions/acc2")
        
        # Подключаемся
        await gus_broadcaster._ensure_connection()
        
        print("✅ GUS Broadcaster готов к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования GUS: {e}")
        logger.exception(f"Ошибка тестирования GUS: {e}")

async def test_all_broadcasters():
    """Тестирование всех броудкастеров"""
    print("🚀 Тестирование всех новых броудкастеров")
    print("=" * 60)
    
    try:
        # Загружаем конфигурацию
        config = config_manager.load_config()
        logger = get_logger("test_all", config.logging)
        
        print(f"📊 Конфигурация:")
        print(f"   🎯 Тестовых чатов: {len(config.targets)}")
        print(f"   💬 B2B сообщений: {len(config.b2b_messages)}")
        print(f"   💬 B2C сообщений: {len(config.b2c_messages)}")
        print(f"   💬 AAA сообщений: {len(config.aaa_messages)}")
        print(f"   💬 GUS сообщений: {len(config.gus_messages)}")
        
        # Создаем все броудкастеры
        broadcasters = [
            EnhancedBroadcaster(
                config=config,
                name="B2B_Test",
                targets=config.targets,
                messages=config.b2b_messages,
                session_name="sessions/acc1"
            ),
            EnhancedBroadcaster(
                config=config,
                name="B2C_Test",
                targets=config.targets,
                messages=config.b2c_messages,
                session_name="sessions/acc2"
            ),
            EnhancedBroadcaster(
                config=config,
                name="AAA_Test",
                targets=config.targets,
                messages=config.aaa_messages,
                session_name="sessions/acc1"
            ),
            EnhancedBroadcaster(
                config=config,
                name="GUS_Test",
                targets=config.targets,
                messages=config.gus_messages,
                session_name="sessions/acc2"
            )
        ]
        
        print(f"\n🔐 Подключение к аккаунтам...")
        
        # Тестируем подключение каждого броудкастера
        for broadcaster in broadcasters:
            try:
                await broadcaster._ensure_connection()
                print(f"✅ {broadcaster.name} - подключен успешно")
            except Exception as e:
                print(f"❌ {broadcaster.name} - ошибка подключения: {e}")
        
        print(f"\n🎉 Тестирование завершено!")
        print(f"📊 Всего броудкастеров: {len(broadcasters)}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        logger.exception(f"Ошибка тестирования: {e}")

async def main():
    """Главная функция"""
    print("🧪 ТЕСТИРОВАНИЕ НОВЫХ БРОУДКАСТЕРОВ")
    print("=" * 60)
    print("Этот скрипт тестирует новые броудкастеры AAA и GUS")
    print("=" * 60)
    
    while True:
        print("\nВыберите тест:")
        print("1. Тест AAA Broadcaster (acc1 - ОПТОВЫЙ)")
        print("2. Тест GUS Broadcaster (acc2 - РОЗНИЧНЫЙ)")
        print("3. Тест всех броудкастеров")
        print("4. Выход")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            await test_aaa_broadcaster()
        elif choice == "2":
            await test_gus_broadcaster()
        elif choice == "3":
            await test_all_broadcasters()
        elif choice == "4":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Прерывание пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
