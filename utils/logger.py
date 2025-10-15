"""
Улучшенная система логирования
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from config.settings import LoggingConfig

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
        
        file_handler = logging.handlers.RotatingFileHandler(
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
