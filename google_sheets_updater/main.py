"""
Google Sheets Updater Service
Независимый микросервис для автоматического обновления Google таблиц
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импорта shared компонентов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google_sheets_updater.config.settings import load_config
from google_sheets_updater.updater.sheet_updater import SheetUpdater
from google_sheets_updater.updater.scheduled_updater import ScheduledUpdater
from google_sheets_updater.utils.logger import get_logger


async def main():
    """Главная функция сервиса"""
    logger = None
    updater = None
    scheduled_updater = None
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Инициализация логгера
        logger = get_logger(config.logging)
        logger.info("=" * 60)
        logger.info("🚀 Google Sheets Updater Service запущен")
        logger.info("=" * 60)
        
        # Создание updater
        updater = SheetUpdater(config)
        
        # Создание планировщика для обновления из Telegram (если включен)
        if config.enable_telegram_scheduled_update:
            scheduled_updater = ScheduledUpdater(config, updater)
            # Запуск обоих сервисов параллельно
            await asyncio.gather(
                updater.start(),
                scheduled_updater.start(),
                return_exceptions=True
            )
        else:
            # Запуск только основного updater
            await updater.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал прерывания...")
        if logger:
            logger.info("Остановка сервиса...")
        
        # Корректная остановка
        if scheduled_updater:
            await scheduled_updater.stop()
        if updater:
            await updater.stop()
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        if logger:
            logger.exception("Критическая ошибка при запуске")
        
        # Корректная остановка
        if scheduled_updater:
            await scheduled_updater.stop()
        if updater:
            await updater.stop()
            
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

