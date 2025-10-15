"""
Централизованная конфигурация приложения
"""
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

@dataclass
class ProxyConfig:
    """Конфигурация прокси"""
    enabled: bool = False
    addr: Optional[str] = None
    port: Optional[int] = None
    secret: Optional[str] = None
    protocol: str = "mtproto"  # mtproto, socks5, http
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProxyConfig':
        """Создание конфигурации прокси из словаря"""
        if not data or not data.get("enabled", False):
            return cls(enabled=False)
        
        return cls(
            enabled=True,
            addr=data.get("addr"),
            port=data.get("port"),
            secret=data.get("secret"),
            protocol=data.get("protocol", "mtproto")
        )

@dataclass
class TelegramConfig:
    """Конфигурация Telegram клиента"""
    api_id: int
    api_hash: str
    session_name: str
    proxy: Optional[ProxyConfig] = None

@dataclass
class BroadcastingConfig:
    """Конфигурация рассылки"""
    delay_between_chats: int = 5
    cycle_delay: int = 900  # 15 минут
    max_retries: int = 3
    retry_delay: int = 60
    start_time_hour: int = 6
    enable_scheduling: bool = True

@dataclass
class GoogleSheetsConfig:
    """Конфигурация Google Sheets"""
    credentials_file: str = "credentials.json"
    b2b_sheet_url: Optional[str] = None
    b2c_sheet_url: Optional[str] = None
    update_interval: int = 3600  # 1 час

@dataclass
class NotificationsConfig:
    """Конфигурация уведомлений"""
    webhook_url: Optional[str] = None
    admin_telegram_id: Optional[int] = None
    enable_telegram_notifications: bool = False
    enable_webhook_notifications: bool = False
    notification_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

@dataclass
class ReportsConfig:
    """Конфигурация отчетов"""
    telegram_bot_token: Optional[str] = None
    telegram_channel_id: Optional[str] = None
    enable_reports: bool = False
    report_interval_hours: int = 12
    timezone: str = "Europe/Moscow"

@dataclass
class NotificationsConfig:
    """Конфигурация уведомлений"""
    webhook_url: Optional[str] = None
    admin_telegram_id: Optional[int] = None
    enable_telegram_notifications: bool = False
    enable_webhook_notifications: bool = False
    notification_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

@dataclass
class LoggingConfig:
    """Конфигурация логирования"""
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: str = "bot.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = False

@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    telegram: TelegramConfig
    broadcasting: BroadcastingConfig = field(default_factory=BroadcastingConfig)
    google_sheets: GoogleSheetsConfig = field(default_factory=GoogleSheetsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)
    reports: ReportsConfig = field(default_factory=ReportsConfig)

    # Списки целей и сообщений
    targets: List[int] = field(default_factory=list)
    test_targets: List[int] = field(default_factory=list)
    b2b_messages: List[str] = field(default_factory=list)
    b2c_messages: List[str] = field(default_factory=list)

class ConfigManager:
    """Менеджер конфигурации"""

    def __init__(self):
        self._config: Optional[AppConfig] = None

    def load_config(self) -> AppConfig:
        """Загрузка конфигурации из переменных окружения"""
        if self._config is not None:
            return self._config

        # Валидация обязательных переменных
        required_vars = ["API_ID", "API_HASH"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {missing_vars}")

        # Создание конфигурации Telegram
        proxy_data = None
        if os.getenv("PROXY_ENABLED", "").lower() == "true":
            proxy_data = {
                "enabled": True,
                "addr": os.getenv("PROXY_ADDR"),
                "port": int(os.getenv("PROXY_PORT", 0)),
                "secret": os.getenv("PROXY_SECRET"),
                "protocol": os.getenv("PROXY_PROTOCOL", "mtproto")
            }

        telegram_config = TelegramConfig(
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            session_name=os.getenv("SESSION_NAME", "session"),
            proxy=ProxyConfig.from_dict(proxy_data) if proxy_data else None
        )

        # Создание конфигурации рассылки
        broadcasting_config = BroadcastingConfig(
            delay_between_chats=int(os.getenv("DELAY_BETWEEN_CHATS", 5)),
            cycle_delay=int(os.getenv("CYCLE_DELAY", 900)),
            max_retries=int(os.getenv("MAX_RETRIES", 3)),
            retry_delay=int(os.getenv("RETRY_DELAY", 60)),
            start_time_hour=int(os.getenv("START_TIME_HOUR", 6)),
            enable_scheduling=os.getenv("ENABLE_SCHEDULING", "true").lower() == "true"
        )

        # Создание конфигурации Google Sheets
        google_sheets_config = GoogleSheetsConfig(
            credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            b2b_sheet_url=os.getenv("SHEET_URL_B2B"),
            b2c_sheet_url=os.getenv("SHEET_URL_B2C"),
            update_interval=int(os.getenv("GOOGLE_UPDATE_INTERVAL", 3600))
        )

        # Создание конфигурации логирования
        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE", "bot.log"),
            max_file_size=int(os.getenv("LOG_MAX_SIZE", 10485760)),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", 5)),
            enable_console=os.getenv("LOG_CONSOLE", "false").lower() == "true"
        )

        # Создание конфигурации уведомлений
        notifications_config = NotificationsConfig(
            webhook_url=os.getenv("WEBHOOK_URL"),
            admin_telegram_id=int(os.getenv("ADMIN_TELEGRAM_ID", 0)) if os.getenv("ADMIN_TELEGRAM_ID") else None,
            enable_telegram_notifications=os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "false").lower() == "true",
            enable_webhook_notifications=os.getenv("ENABLE_WEBHOOK_NOTIFICATIONS", "false").lower() == "true",
            notification_level=os.getenv("NOTIFICATION_LEVEL", "INFO")
        )

        # Создание конфигурации отчетов
        reports_config = ReportsConfig(
            telegram_bot_token=os.getenv("REPORTS_BOT_TOKEN"),
            telegram_channel_id=os.getenv("REPORTS_CHANNEL_ID"),
            enable_reports=os.getenv("ENABLE_REPORTS", "false").lower() == "true",
            report_interval_hours=int(os.getenv("REPORT_INTERVAL_HOURS", 12)),
            timezone=os.getenv("REPORTS_TIMEZONE", "Europe/Moscow")
        )

        # Импорт targets и messages
        try:
            from .targets import TARGETS, TEST_TARGETS
            from .messages import MESSAGES_B2B, MESSAGES_B2C
        except ImportError:
            # Fallback если файлы не найдены
            TARGETS = []
            TEST_TARGETS = []
            MESSAGES_B2B = []
            MESSAGES_B2C = []

        self._config = AppConfig(
            telegram=telegram_config,
            broadcasting=broadcasting_config,
            google_sheets=google_sheets_config,
            logging=logging_config,
            notifications=notifications_config,
            reports=reports_config,
            targets=TARGETS,
            test_targets=TEST_TARGETS,
            b2b_messages=MESSAGES_B2B,
            b2c_messages=MESSAGES_B2C
        )
        
        return self._config
    
    def get_config(self) -> AppConfig:
        """Получение текущей конфигурации"""
        if self._config is None:
            return self.load_config()
        return self._config

# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
