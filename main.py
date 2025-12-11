"""
Точка входа для обратной совместимости
Перенаправляет на broadcaster/main.py
"""
import sys
import asyncio
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Импортируем и запускаем broadcaster
    from broadcaster.main import main as broadcaster_main
    
    # Настройка обработки исключений
    def exception_handler(loop, context):
        print(f"Необработанное исключение: {context}")
    
    try:
        asyncio.run(broadcaster_main())
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал прерывания...")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
