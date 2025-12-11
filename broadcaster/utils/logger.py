"""
Улучшенная система логирования
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from broadcaster.config.settings import LoggingConfig

class WindowsSafeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    RotatingFileHandler с обработкой ошибок на Windows
    Обрабатывает PermissionError при ротации файла, если файл заблокирован другим процессом
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rotation_failed = False  # Флаг для отслеживания неудачных попыток ротации
    
    def emit(self, record):
        """
        Переопределяем emit для обработки ошибок при записи
        """
        try:
            super().emit(record)
        except (PermissionError, OSError) as e:
            # На Windows файл может быть заблокирован
            if sys.platform == 'win32':
                # Пытаемся записать предупреждение в stderr
                try:
                    if not self._rotation_failed:
                        print(
                            f"⚠️  Ошибка записи в лог-файл {self.baseFilename}: {e}",
                            file=sys.stderr
                        )
                        print(
                            "   Файл может быть заблокирован другим процессом.",
                            file=sys.stderr
                        )
                        self._rotation_failed = True
                except:
                    pass
            else:
                # На других ОС пробрасываем ошибку дальше
                raise
    
    def doRollover(self):
        """
        Переопределяем doRollover для безопасной обработки ошибок на Windows
        """
        try:
            super().doRollover()
            self._rotation_failed = False  # Сбрасываем флаг при успешной ротации
        except (PermissionError, OSError) as e:
            # На Windows файл может быть заблокирован другим процессом
            # В этом случае просто пропускаем ротацию и продолжаем писать в текущий файл
            if sys.platform == 'win32':
                # Пытаемся записать предупреждение в stderr, так как файл может быть заблокирован
                try:
                    if not self._rotation_failed:
                        print(
                            f"⚠️  Не удалось выполнить ротацию лог-файла {self.baseFilename}: {e}",
                            file=sys.stderr
                        )
                        print(
                            "   Файл заблокирован другим процессом. Продолжаем писать в текущий файл.",
                            file=sys.stderr
                        )
                        print(
                            "   Рекомендация: закройте другие процессы, использующие этот файл, или перезапустите бота.",
                            file=sys.stderr
                        )
                        self._rotation_failed = True
                except:
                    pass  # Если даже stderr недоступен, просто игнорируем
            else:
                # На других ОС пробрасываем ошибку дальше
                raise

class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для консольного вывода"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)

class LoggerManager:
    """Менеджер логгеров"""
    
    def __init__(self):
        self._loggers: dict = {}
    
    def get_logger(self, name: str, config: LoggingConfig) -> logging.Logger:
        """Получение или создание логгера"""
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.level.upper()))
        
        # Очищаем существующие хэндлеры
        logger.handlers.clear()
        
        # Создаем ротирующий файловый хэндлер
        log_path = Path(config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Используем кастомный хэндлер для Windows, который обрабатывает ошибки ротации
        file_handler = WindowsSafeRotatingFileHandler(
            log_path,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            config.format,
            datefmt=config.date_format
        ))
        logger.addHandler(file_handler)
        
        # Создаем консольный хэндлер если включен
        if config.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(ColoredFormatter(
                config.format,
                datefmt=config.date_format
            ))
            logger.addHandler(console_handler)
        
        # Предотвращаем дублирование логов
        logger.propagate = False
        
        self._loggers[name] = logger
        return logger

# Глобальный менеджер логгеров
logger_manager = LoggerManager()

def get_logger(name: str, config: LoggingConfig) -> logging.Logger:
    """Удобная функция для получения логгера"""
    return logger_manager.get_logger(name, config)
