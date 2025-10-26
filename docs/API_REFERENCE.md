# 📚 API Справочник SendMessageBot

## 📋 Содержание

- [🏗️ Архитектура](#️-архитектура)
- [🔧 Основные классы](#-основные-классы)
- [📊 Конфигурация](#-конфигурация)
- [🚀 Броудкастеры](#-броудкастеры)
- [📝 Сообщения](#-сообщения)
- [🎯 Цели](#-цели)
- [📊 Мониторинг](#-мониторинг)
- [🛠️ Утилиты](#️-утилиты)
- [📈 Примеры использования](#-примеры-использования)

## 🏗️ Архитектура

### Основные компоненты

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main App      │    │  Config Manager │    │  Logger         │
│   (main.py)     │    │  (settings.py)  │    │  (logger.py)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Broadcasters   │    │  Google Sheets  │    │  Monitoring     │
│  (broadcaster.py)│    │  (google_sheets.py)│    │  (monitoring/) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Telegram API   │    │  Google API     │    │  Reports        │
│  (Telethon)     │    │  (gspread)      │    │  (reports.py)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Основные классы

### `EnhancedBroadcaster`

Основной класс для отправки сообщений в Telegram.

```python
class EnhancedBroadcaster:
    def __init__(self, config: AppConfig, name: str, targets: List[int], 
                 messages: List[str], session_name: str):
        """
        Инициализация броудкастера
        
        Args:
            config: Конфигурация приложения
            name: Имя броудкастера
            targets: Список ID целевых чатов
            messages: Список сообщений для отправки
            session_name: Путь к файлу сессии
        """
    
    async def start(self) -> None:
        """Запуск броудкастера"""
    
    async def stop(self) -> None:
        """Остановка броудкастера"""
    
    async def send_messages(self) -> None:
        """Отправка сообщений в целевые чаты"""
    
    async def _ensure_connection(self) -> None:
        """Обеспечение подключения к Telegram"""
    
    async def _send_single_message(self, chat_id: int, message: str) -> bool:
        """Отправка одного сообщения в чат"""
```

### `ConfigManager`

Управление конфигурацией приложения.

```python
class ConfigManager:
    def load_config(self) -> AppConfig:
        """
        Загрузка конфигурации из .env файла
        
        Returns:
            AppConfig: Загруженная конфигурация
        """
    
    def save_config(self, config: AppConfig) -> None:
        """
        Сохранение конфигурации
        
        Args:
            config: Конфигурация для сохранения
        """
    
    def validate_config(self, config: AppConfig) -> bool:
        """
        Валидация конфигурации
        
        Args:
            config: Конфигурация для проверки
            
        Returns:
            bool: True если конфигурация валидна
        """
```

### `GoogleSheetsFetcher`

Работа с Google Sheets.

```python
class GoogleSheetsFetcher:
    def __init__(self, credentials_path: str = "credentials.json"):
        """
        Инициализация клиента Google Sheets
        
        Args:
            credentials_path: Путь к файлу с учетными данными
        """
    
    def fetch_messages(self, sheet_url: str) -> List[str]:
        """
        Получение сообщений из Google Sheets
        
        Args:
            sheet_url: URL таблицы
            
        Returns:
            List[str]: Список сообщений
        """
    
    def test_connection(self, sheet_url: str) -> bool:
        """
        Тестирование подключения к таблице
        
        Args:
            sheet_url: URL таблицы
            
        Returns:
            bool: True если подключение успешно
        """
```

## 📊 Конфигурация

### `AppConfig`

Основная конфигурация приложения.

```python
@dataclass
class AppConfig:
    # Telegram настройки
    api_id: int
    api_hash: str
    phone: str
    
    # Цели
    targets: List[int]
    
    # Сообщения
    b2b_messages: List[str]
    b2c_messages: List[str]
    aaa_messages: List[str]
    gus_messages: List[str]
    
    # Настройки рассылки
    message_delay: int = 1
    max_retries: int = 3
    flood_wait_delay: int = 60
    
    # Логирование
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
```

### `GoogleSheetsConfig`

Конфигурация Google Sheets.

```python
@dataclass
class GoogleSheetsConfig:
    b2b_sheet_url: Optional[str] = None
    b2c_sheet_url: Optional[str] = None
    aaa_sheet_url: Optional[str] = None
    gus_sheet_url: Optional[str] = None
```

### `LoggingConfig`

Конфигурация логирования.

```python
@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/bot.log"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 🚀 Броудкастеры

### Создание броудкастера

```python
from core.broadcaster import EnhancedBroadcaster
from config.settings import config_manager

# Загрузка конфигурации
config = config_manager.load_config()

# Создание броудкастера
broadcaster = EnhancedBroadcaster(
    config=config,
    name="B2B_Broadcaster",
    targets=config.targets,
    messages=config.b2b_messages,
    session_name="sessions/acc1"
)

# Запуск
await broadcaster.start()
```

### Управление броудкастерами

```python
# Список всех броудкастеров
broadcasters = [
    EnhancedBroadcaster(config, "B2B", targets, b2b_messages, "sessions/acc1"),
    EnhancedBroadcaster(config, "B2C", targets, b2c_messages, "sessions/acc2"),
    EnhancedBroadcaster(config, "AAA", targets, aaa_messages, "sessions/acc1"),
    EnhancedBroadcaster(config, "GUS", targets, gus_messages, "sessions/acc2"),
]

# Запуск всех броудкастеров
for broadcaster in broadcasters:
    await broadcaster.start()

# Остановка всех броудкастеров
for broadcaster in broadcasters:
    await broadcaster.stop()
```

## 📝 Сообщения

### Загрузка сообщений

```python
from config.messages import MESSAGESB2B, MESSAGESB2C
from config.messages_aaa import MESSAGESAAA
from config.messages_gus import MESSAGESGUS

# Локальные сообщения
b2b_messages = MESSAGESB2B
b2c_messages = MESSAGESB2C
aaa_messages = MESSAGESAAA
gus_messages = MESSAGESGUS
```

### Обновление сообщений из Google Sheets

```python
from utils.google_sheets import GoogleSheetsFetcher

fetcher = GoogleSheetsFetcher()

# Обновление B2B сообщений
b2b_messages = fetcher.fetch_messages(config.b2b_sheet_url)

# Обновление B2C сообщений
b2c_messages = fetcher.fetch_messages(config.b2c_sheet_url)

# Обновление AAA сообщений
aaa_messages = fetcher.fetch_messages(config.aaa_sheet_url)

# Обновление GUS сообщений
gus_messages = fetcher.fetch_messages(config.gus_sheet_url)
```

### Форматирование сообщений

```python
def format_message(message: str, variables: dict = None) -> str:
    """
    Форматирование сообщения с переменными
    
    Args:
        message: Исходное сообщение
        variables: Словарь переменных
        
    Returns:
        str: Отформатированное сообщение
    """
    if variables:
        return message.format(**variables)
    return message

# Пример использования
message = "Привет, {name}! Цена: {price} руб."
formatted = format_message(message, {"name": "Иван", "price": "1000"})
```

## 🎯 Цели

### Управление целевыми чатами

```python
from config.targets import TEST_TARGETS, PRODUCTION_TARGETS

# Тестовые чаты
test_chats = TEST_TARGETS

# Основные чаты
production_chats = PRODUCTION_TARGETS

# Переключение между тестовыми и основными
use_test_chats = True
targets = TEST_TARGETS if use_test_chats else PRODUCTION_TARGETS
```

### Добавление новых целей

```python
# Добавление нового чата
new_chat_id = -1001234567890
TEST_TARGETS.append(new_chat_id)

# Удаление чата
TEST_TARGETS.remove(-1001234567890)

# Проверка существования чата
if chat_id in TEST_TARGETS:
    print("Чат найден")
```

## 📊 Мониторинг

### Сбор метрик

```python
from monitoring.metrics import MetricsCollector

collector = MetricsCollector()

# Увеличение счетчика отправленных сообщений
collector.increment_sent_messages()

# Увеличение счетчика ошибок
collector.increment_errors()

# Запись времени выполнения
collector.record_execution_time("send_message", 1.5)

# Получение статистики
stats = collector.get_stats()
print(f"Отправлено: {stats['sent_messages']}")
print(f"Ошибок: {stats['errors']}")
```

### Логирование

```python
from utils.logger import get_logger

# Создание логгера
logger = get_logger("broadcaster", config.logging)

# Различные уровни логирования
logger.debug("Отладочная информация")
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.critical("Критическая ошибка")

# Логирование с контекстом
logger.info("Отправка сообщения", extra={
    "chat_id": chat_id,
    "message_length": len(message)
})
```

### Отчеты

```python
from monitoring.reports import ReportGenerator

generator = ReportGenerator()

# Создание ежедневного отчета
daily_report = generator.generate_daily_report()

# Создание отчета по ошибкам
error_report = generator.generate_error_report()

# Отправка отчета
generator.send_report(daily_report, "admin@example.com")
```

## 🛠️ Утилиты

### Обработка ошибок

```python
from core.retry import retry_with_backoff
from core.exceptions import FloodWaitError

@retry_with_backoff(max_retries=3, base_delay=5)
async def send_message_with_retry(chat_id: int, message: str):
    """
    Отправка сообщения с повторными попытками
    
    Args:
        chat_id: ID чата
        message: Сообщение для отправки
    """
    try:
        await client.send_message(chat_id, message)
    except FloodWaitError as e:
        logger.warning(f"FloodWait: {e.seconds} секунд")
        raise
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        raise
```

### Валидация данных

```python
from utils.helpers import validate_chat_id, validate_message

def validate_broadcaster_data(targets: List[int], messages: List[str]) -> bool:
    """
    Валидация данных броудкастера
    
    Args:
        targets: Список ID чатов
        messages: Список сообщений
        
    Returns:
        bool: True если данные валидны
    """
    # Проверка целей
    for chat_id in targets:
        if not validate_chat_id(chat_id):
            return False
    
    # Проверка сообщений
    for message in messages:
        if not validate_message(message):
            return False
    
    return True
```

### Безопасность

```python
from utils.security import SecurityManager

security = SecurityManager()

# Шифрование чувствительных данных
encrypted_data = security.encrypt("sensitive_data")

# Расшифровка данных
decrypted_data = security.decrypt(encrypted_data)

# Проверка целостности файлов
is_valid = security.verify_file_integrity("sessions/acc1.session")
```

## 📈 Примеры использования

### Полный пример запуска

```python
import asyncio
from config.settings import config_manager
from core.broadcaster import EnhancedBroadcaster

async def main():
    # Загрузка конфигурации
    config = config_manager.load_config()
    
    # Создание броудкастеров
    broadcasters = [
        EnhancedBroadcaster(config, "B2B", config.targets, config.b2b_messages, "sessions/acc1"),
        EnhancedBroadcaster(config, "B2C", config.targets, config.b2c_messages, "sessions/acc2"),
        EnhancedBroadcaster(config, "AAA", config.targets, config.aaa_messages, "sessions/acc1"),
        EnhancedBroadcaster(config, "GUS", config.targets, config.gus_messages, "sessions/acc2"),
    ]
    
    try:
        # Запуск всех броудкастеров
        for broadcaster in broadcasters:
            await broadcaster.start()
        
        # Ожидание завершения
        await asyncio.gather(*[b.send_messages() for b in broadcasters])
        
    finally:
        # Остановка всех броудкастеров
        for broadcaster in broadcasters:
            await broadcaster.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Пример с обработкой ошибок

```python
import asyncio
from core.exceptions import FloodWaitError, RetryError

async def robust_broadcasting():
    try:
        await broadcaster.start()
        await broadcaster.send_messages()
    except FloodWaitError as e:
        logger.warning(f"FloodWait: {e.seconds} секунд")
        await asyncio.sleep(e.seconds)
        await robust_broadcasting()
    except RetryError as e:
        logger.error(f"Превышено количество попыток: {e}")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        raise
```

### Пример с мониторингом

```python
import asyncio
from monitoring.metrics import MetricsCollector
from monitoring.reports import ReportGenerator

async def monitored_broadcasting():
    metrics = MetricsCollector()
    reporter = ReportGenerator()
    
    try:
        start_time = time.time()
        
        await broadcaster.start()
        await broadcaster.send_messages()
        
        execution_time = time.time() - start_time
        metrics.record_execution_time("broadcasting", execution_time)
        
    except Exception as e:
        metrics.increment_errors()
        logger.error(f"Ошибка: {e}")
        
    finally:
        # Генерация отчета
        report = reporter.generate_daily_report()
        reporter.send_report(report)
```

---

**Удачного использования API! 🚀**

