"""
Конфигурация Google Sheets Updater Service
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any


@dataclass
class LoggingConfig:
    """Конфигурация логирования"""
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: str = "logs/updater.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True


@dataclass
class GoogleSheetsConfig:
    """Конфигурация Google Sheets"""
    credentials_file: str = "credentials.json"
    # URL таблиц для обновления
    price_aaa_sheet_url: Optional[str] = None
    price_gus_sheet_url: Optional[str] = None
    ads_aaa_sheet_url: Optional[str] = None
    ads_gus_sheet_url: Optional[str] = None


@dataclass
class DataSourceConfig:
    """Конфигурация источника данных"""
    source_type: str  # 'api', 'database', 'file', 'google_sheet'
    source_config: Dict[str, Any]  # Конкретная конфигурация источника


@dataclass
class UpdaterConfig:
    """Основная конфигурация сервиса"""
    google_sheets: GoogleSheetsConfig = field(default_factory=GoogleSheetsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    update_interval_seconds: int = 3600  # 1 час по умолчанию
    data_sources: List[DataSourceConfig] = field(default_factory=list)
    enable_auto_update: bool = True


def load_config() -> UpdaterConfig:
    """
    Загрузка конфигурации из переменных окружения
    
    Приоритет:
    1. .env.updater (если существует)
    2. Переменные окружения системы
    3. Значения по умолчанию
    """
    # Попытка загрузить .env.updater
    env_file = Path(".env.updater")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Google Sheets конфигурация
    google_sheets_config = GoogleSheetsConfig(
        credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
        price_aaa_sheet_url=os.getenv("BUY_SELL_PRICE_AAA_SHEET_URL"),
        price_gus_sheet_url=os.getenv("BUY_SELL_PRICE_GUS_SHEET_URL"),
        ads_aaa_sheet_url=os.getenv("ADS_AAA_SHEET_URL"),
        ads_gus_sheet_url=os.getenv("ADS_GUS_SHEET_URL"),
    )
    
    # Логирование
    logging_config = LoggingConfig(
        level=os.getenv("UPDATER_LOG_LEVEL", "INFO"),
        file_path=os.getenv("UPDATER_LOG_FILE", "logs/updater.log"),
        enable_console=os.getenv("UPDATER_LOG_CONSOLE", "true").lower() == "true"
    )
    
    # Основная конфигурация
    config = UpdaterConfig(
        google_sheets=google_sheets_config,
        logging=logging_config,
        update_interval_seconds=int(os.getenv("UPDATER_UPDATE_INTERVAL", "3600")),
        enable_auto_update=os.getenv("UPDATER_ENABLE_AUTO_UPDATE", "true").lower() == "true"
    )
    
    return config


if __name__ == "__main__":
    # Тест загрузки конфигурации
    config = load_config()
    print("Конфигурация загружена:")
    print(f"  Credentials: {config.google_sheets.credentials_file}")
    print(f"  Update interval: {config.update_interval_seconds} секунд")
    print(f"  Log file: {config.logging.file_path}")

