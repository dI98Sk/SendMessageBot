#!/usr/bin/env python3
"""
Упрощенная версия для тестирования новой архитектуры
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager, AppConfig
from config.targets import TEST_TARGETS
from config.messages import MESSAGES_B2B, MESSAGES_B2C
from utils.logger import get_logger
from core.broadcaster import EnhancedBroadcaster

async def test_new_broadcaster():
    """Тестирование нового broadcaster"""
    print("🚀 Тестирование новой архитектуры SendMessageBot")
    print("=" * 50)
    
    try:
        # Загрузка конфигурации
        config = config_manager.load_config()
        print(f"✅ Конфигурация загружена: API_ID={config.telegram.api_id}")
        
        # Настройка логгера
        logger = get_logger("test", config.logging)
        logger.info("Начинаем тестирование новой архитектуры")
        
        # Создание broadcaster для B2B
        print("\n📱 Создание B2B Broadcaster...")
        b2b_broadcaster = EnhancedBroadcaster(
            config=config,
            name="B2B_Test",
            targets=TEST_TARGETS,  # Используем тестовые чаты
            messages=MESSAGES_B2B[:2]  # Только первые 2 сообщения для теста
        )
        
        print(f"✅ B2B Broadcaster создан")
        print(f"   - Целевых чатов: {len(TEST_TARGETS)}")
        print(f"   - Сообщений: {len(MESSAGES_B2B[:2])}")
        
        # Тестирование подключения
        print("\n🔌 Тестирование подключения к Telegram...")
        await b2b_broadcaster._ensure_connection()
        print("✅ Подключение к Telegram успешно")
        
        # Получение статистики
        stats = b2b_broadcaster.get_stats()
        print(f"\n📊 Статистика:")
        print(f"   - Имя: {stats['name']}")
        print(f"   - Целевых чатов: {stats['targets_count']}")
        print(f"   - Сообщений: {stats['messages_count']}")
        print(f"   - Статус: {'Запущен' if stats['running'] else 'Остановлен'}")
        
        print("\n🎉 Тестирование завершено успешно!")
        print("\nДля запуска полной версии используйте:")
        print("python main_improved.py")
        
        # Остановка broadcaster
        await b2b_broadcaster.stop()
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_broadcaster())
