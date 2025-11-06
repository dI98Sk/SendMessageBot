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
    delay_between_chats: int = 90  # Увеличено до 90 секунд (1.5 мин) для 4 параллельных broadcaster'ов
    cycle_delay: int = 3600  # Увеличено с 20 минут до 1 часа между циклами
    max_retries: int = 5  # Увеличено с 3 до 5 попыток
    retry_delay: int = 120  # Увеличено до 2 минут между повторами
    start_time_hour: int = 6
    enable_scheduling: bool = True
    quiet_hour_start: int = 0  # Начало тихого часа (00:00)
    quiet_hour_end: int = 7    # Конец тихого часа (07:00)
    enable_quiet_hours: bool = True  # Включить тихий час
    min_interval_per_chat: int = 900  # Увеличено до 15 минут между отправками в один чат (для 4 broadcaster'ов)
    adaptive_delay_enabled: bool = True  # Адаптивная задержка при ошибках
    adaptive_delay_multiplier: float = 2.0  # Увеличено до 2.0 для более агрессивного замедления при ошибках
    max_delay_between_chats: int = 180  # Увеличено до 3 минут максимальная задержка

@dataclass
class GoogleSheetsConfig:
    """Конфигурация Google Sheets"""
    credentials_file: str = "credentials.json"
    b2b_sheet_url: Optional[str] = None
    b2c_sheet_url: Optional[str] = None
    aaa_sheet_url: Optional[str] = None  # Прайсы AAA
    gus_sheet_url: Optional[str] = None  # Прайсы GUS
    aaa_ads_sheet_url: Optional[str] = None  # Реклама AAA
    gus_ads_sheet_url: Optional[str] = None  # Реклама GUS
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
    report_interval_hours: float = 3.0  # Отчеты каждые 3 часа (поддержка дробных значений)
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
    targets_ads: List[int] = field(default_factory=list)
    targets_prices: List[int] = field(default_factory=list)
    targets_ads_test: List[int] = field(default_factory=list)  # Тестовые чаты для рекламы
    b2b_messages: List[str] = field(default_factory=list)
    b2c_messages: List[str] = field(default_factory=list)
    aaa_messages: List[str] = field(default_factory=list)  # Прайсы AAA
    gus_messages: List[str] = field(default_factory=list)  # Прайсы GUS
    aaa_ads_messages: List[str] = field(default_factory=list)  # Реклама AAA
    gus_ads_messages: List[str] = field(default_factory=list)  # Реклама GUS

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
            delay_between_chats=int(os.getenv("DELAY_BETWEEN_CHATS", 40)),  # Обновлено: 40 секунд по умолчанию
            cycle_delay=int(os.getenv("CYCLE_DELAY", 3600)),  # Обновлено: 1 час по умолчанию
            max_retries=int(os.getenv("MAX_RETRIES", 5)),  # Обновлено: 5 попыток по умолчанию
            retry_delay=int(os.getenv("RETRY_DELAY", 60)),
            start_time_hour=int(os.getenv("START_TIME_HOUR", 6)),
            enable_scheduling=os.getenv("ENABLE_SCHEDULING", "true").lower() == "true",
            quiet_hour_start=int(os.getenv("QUIET_HOUR_START", 0)),
            quiet_hour_end=int(os.getenv("QUIET_HOUR_END", 7)),
            enable_quiet_hours=os.getenv("ENABLE_QUIET_HOURS", "true").lower() == "true",
            min_interval_per_chat=int(os.getenv("MIN_INTERVAL_PER_CHAT", 600)),  # Обновлено: 10 минут по умолчанию
            adaptive_delay_enabled=os.getenv("ADAPTIVE_DELAY_ENABLED", "true").lower() == "true",
            adaptive_delay_multiplier=float(os.getenv("ADAPTIVE_DELAY_MULTIPLIER", 1.5)),
            max_delay_between_chats=int(os.getenv("MAX_DELAY_BETWEEN_CHATS", 120))
        )

        # Создание конфигурации Google Sheets
        google_sheets_config = GoogleSheetsConfig(
            credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            b2b_sheet_url=os.getenv("SHEET_URL_B2B"),
            b2c_sheet_url=os.getenv("SHEET_URL_B2C"),
            aaa_sheet_url=os.getenv("BUY_SELL_PRICE_AAA_SHEET_URL"),
            gus_sheet_url=os.getenv("BUY_SELL_PRICE_GUS_SHEET_URL"),
            aaa_ads_sheet_url=os.getenv("ADS_AAA_SHEET_URL"),
            gus_ads_sheet_url=os.getenv("ADS_GUS_SHEET_URL"),
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
            report_interval_hours=float(os.getenv("REPORT_INTERVAL_HOURS", "3.0")),  # Отчеты каждые N часов (поддержка дробных значений)
            timezone=os.getenv("REPORTS_TIMEZONE", "Europe/Moscow")
        )

        # Импорт targets и messages
        try:
            from .targets import TARGETS, TEST_TARGETS, ADS_TARGET, PRICE_TARGET, TEST_TARGETS_ADS
            from .messages import MESSAGES_B2B, MESSAGES_B2C
            from .messages_aaa import MESSAGESAAA
            from .messages_gus import MESSAGESGUS
            from .messages_aaa_ads import MESSAGES_AAA_ADS
            from .messages_gus_ads import MESSAGES_GUS_ADS
        except ImportError:
            # Fallback если файлы не найдены
            TARGETS = []
            TEST_TARGETS = []
            ADS_TARGET = []
            PRICE_TARGET = []
            TEST_TARGETS_ADS = []
            MESSAGES_B2B = []
            MESSAGES_B2C = []
            MESSAGESAAA = []
            MESSAGESGUS = []
            MESSAGES_AAA_ADS = []
            MESSAGES_GUS_ADS = []


        self._config = AppConfig(
            telegram=telegram_config,
            broadcasting=broadcasting_config,
            google_sheets=google_sheets_config,
            logging=logging_config,
            notifications=notifications_config,
            reports=reports_config,
            # targets=TARGETS,
            targets_ads=ADS_TARGET,
            targets_prices=PRICE_TARGET,
            targets_ads_test=TEST_TARGETS_ADS,  # Тестовые чаты для рекламы
            targets=TEST_TARGETS,
            b2b_messages=MESSAGES_B2B,
            b2c_messages=MESSAGES_B2C,
            aaa_messages=MESSAGESAAA,
            gus_messages=MESSAGESGUS,
            aaa_ads_messages=MESSAGES_AAA_ADS,
            gus_ads_messages=MESSAGES_GUS_ADS,
        )
        
        return self._config
    
    def get_config(self) -> AppConfig:
        """Получение текущей конфигурации"""
        if self._config is None:
            return self.load_config()
        return self._config

# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()
