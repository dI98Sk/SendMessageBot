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
from google_sheets_updater.utils.logger import get_logger


async def main():
    """Главная функция сервиса"""
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
        
        # Запуск сервиса
        await updater.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал прерывания...")
        logger.info("Остановка сервиса...")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        if 'logger' in locals():
            logger.exception("Критическая ошибка при запуске")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

