"""
Логирование для Google Sheets Updater Service
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from google_sheets_updater.config.settings import LoggingConfig


def get_logger(config: LoggingConfig) -> logging.Logger:
    """
    Создание и настройка логгера
    
    Args:
        config: Конфигурация логирования
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger("updater")
    logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))
    
    # Очистка существующих обработчиков
    logger.handlers.clear()
    
    # Форматтер
    formatter = logging.Formatter(
        config.format,
        datefmt=config.date_format
    )
    
    # Файловый обработчик
    log_file = Path(config.file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.max_file_size,
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Консольный обработчик (если включен)
    if config.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

