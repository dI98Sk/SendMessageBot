# 🚀 SendMessageBot - Полная система массовой рассылки сообщений в Telegram

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-Latest-green.svg)](https://github.com/LonamiWebs/Telethon)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

Мощная, масштабируемая система для автоматической рассылки сообщений в Telegram чаты с поддержкой множественных аккаунтов, Google Sheets интеграции, продвинутого мониторинга и гибкой конфигурации.

## 📋 Содержание

- [🚀 Быстрый старт](#-быстрый-старт)
- [📁 Структура проекта](#-структура-проекта)
- [⚙️ Полная настройка](#️-полная-настройка)
- [🔧 Управление и команды](#-управление-и-команды)
- [📊 Мониторинг и отчеты](#-мониторинг-и-отчеты)
- [🛠️ Разработка и расширение](#️-разработка-и-расширение)
- [🔍 Устранение неполадок](#-устранение-неполадок)
- [📈 Масштабирование](#-масштабирование)
- [📚 API Справочник](#-api-справочник)
- [🎯 Roadmap и развитие](#-roadmap-и-развитие)
- [❓ FAQ и поддержка](#-faq-и-поддержка)

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
# Клонирование репозитория
git clone <repository_url>
cd SendMessageBot

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка окружения
```bash
# Копирование шаблона конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env  # или любой другой редактор
```

### 3. Настройка аккаунтов Telegram
```bash
# Интерактивная настройка аккаунтов
python scripts/setup_accounts.py

# Или через главное меню
python run.py
# Выберите опцию "🔐 Настройка аккаунтов"
```

### 4. Настройка Google Sheets (опционально)
```bash
# Скачайте credentials.json из Google Cloud Console
# Поместите файл в корень проекта

# Тестирование подключения
python tests/test_google_sheets.py
```

### 5. Запуск системы
```bash
# Запуск с интерактивным меню
python run.py

# Или прямой запуск
python main.py
```

### 6. Проверка работы
```bash
# Просмотр статистики
python scripts/show_stats.py

# Или в реальном времени
python scripts/watch_stats.py
```

## 📁 Структура проекта

```
SendMessageBot/
├── 📁 core/                    # Основная логика системы
│   ├── broadcaster.py          # Класс EnhancedBroadcaster
│   ├── exceptions.py           # Кастомные исключения
│   ├── queue.py               # Система очередей сообщений
│   └── retry.py               # Логика повторных попыток
│
├── 📁 config/                  # Конфигурация и настройки
│   ├── settings.py            # Централизованная конфигурация
│   ├── targets.py             # Целевые чаты для рассылки
│   ├── messages.py            # Сообщения B2B/B2C
│   ├── messages_aaa.py        # Сообщения AAA Store
│   ├── messages_gus.py        # Сообщения Яблочный Гусь
│   └── message_updater.py     # Обновление сообщений из Google Sheets
│
├── 📁 utils/                   # Утилиты и вспомогательные функции
│   ├── logger.py              # Система логирования
│   ├── google_sheets.py       # Интеграция с Google Sheets
│   ├── security.py            # Безопасность и шифрование
│   └── helpers.py             # Вспомогательные функции
│
├── 📁 monitoring/              # Мониторинг и аналитика
│   ├── metrics.py             # Сбор метрик производительности
│   ├── notifications.py       # Система уведомлений
│   └── reports.py             # Генерация отчетов
│
├── 📁 scripts/                 # Скрипты управления и администрирования
│   ├── setup_accounts.py      # Настройка Telegram аккаунтов
│   ├── update_messages.py     # Обновление сообщений
│   ├── test_broadcasters.py   # Тестирование броудкастеров
│   ├── night_test.py          # Ночное тестирование
│   ├── manage_reports.py      # Управление отчетами
│   ├── switch_targets.py      # Переключение целевых чатов
│   ├── check_environment.py   # Проверка окружения
│   ├── show_stats.py          # Просмотр статистики
│   └── watch_stats.py         # Мониторинг в реальном времени
│
├── 📁 sessions/                # Файлы сессий Telegram
│   ├── acc1.session           # Оптовый аккаунт (B2B/AAA)
│   └── acc2.session           # Розничный аккаунт (B2C/GUS)
│
├── 📁 logs/                    # Логи системы
│   ├── bot.log                # Основной лог
│   └── bot_old_*.log          # Архивные логи
│
├── 📁 tests/                   # Тесты системы
│   ├── test_broadcasters.py   # Тесты броудкастеров
│   ├── test_google_sheets.py  # Тесты Google Sheets
│   └── test_notifications.py  # Тесты уведомлений
│
├── 📁 docs/                    # Документация
│   ├── SETUP_GUIDE.md         # Подробное руководство по настройке
│   ├── TROUBLESHOOTING.md     # Решение проблем
│   ├── NIGHT_TESTING_GUIDE.md # Руководство по ночному тестированию
│   ├── API_REFERENCE.md       # Справочник API
│   ├── PRODUCTION_CHECKLIST.md # Чеклист для продакшена
│   └── IMPROVEMENT_ROADMAP.md # План развития
│
├── 📁 data/                    # Данные и бэкапы
│   ├── chat_ids.txt           # ID чатов
│   ├── allChatID_backup.txt   # Бэкап чатов
│   └── dict_backup.txt        # Бэкап словарей
│
├── 📁 backup/                  # Резервные копии
│   └── messages/              # Бэкапы сообщений
│
├── 📄 main.py                  # Главный файл запуска
├── 📄 run.py                   # Интерактивный скрипт запуска
├── 📄 requirements.txt        # Python зависимости
├── 📄 .env                     # Переменные окружения
├── 📄 credentials.json         # Google Sheets credentials
├── 📄 PROJECT_STATUS_REPORT.md # Отчет о статусе проекта
└── 📄 REORGANIZATION_COMPLETE.md # Отчет о реорганизации
```

## ⚙️ Полная настройка

### Переменные окружения (.env)

#### Основные настройки Telegram
```bash
# Telegram API (обязательно)
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=your_phone_number
SESSION_NAME=session

# Прокси (опционально)
PROXY_ENABLED=false
PROXY_ADDR=
PROXY_PORT=
PROXY_SECRET=
PROXY_PROTOCOL=mtproto
```

#### Настройки рассылки
```bash
# Задержки
DELAY_BETWEEN_CHATS=15          # Задержка между чатами (сек)
CYCLE_DELAY=1200               # Задержка между циклами (сек) - 20 мин
MAX_RETRIES=3                  # Максимум повторных попыток
RETRY_DELAY=60                 # Задержка при повторе (сек)

# Планирование
START_TIME_HOUR=6              # Час начала работы
ENABLE_SCHEDULING=true         # Включить планирование
QUIET_HOUR_START=0             # Начало тихого часа
QUIET_HOUR_END=7               # Конец тихого часа
ENABLE_QUIET_HOURS=true        # Включить тихий час
```

#### Google Sheets интеграция
```bash
# URLs таблиц
BUY_SELL_PRICE_B2B_SHEET_URL=https://docs.google.com/spreadsheets/d/...
BUY_SELL_PRICE_B2C_SHEET_URL=https://docs.google.com/spreadsheets/d/...
BUY_SELL_PRICE_AAA_SHEET_URL=https://docs.google.com/spreadsheets/d/...
BUY_SELL_PRICE_GUS_SHEET_URL=https://docs.google.com/spreadsheets/d/...

# Настройки обновления
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_UPDATE_INTERVAL=3600    # Интервал обновления (сек)
```

#### Система уведомлений
```bash
# Telegram уведомления
ENABLE_TELEGRAM_NOTIFICATIONS=true
ADMIN_TELEGRAM_ID=your_admin_id

# Webhook уведомления
ENABLE_WEBHOOK_NOTIFICATIONS=false
WEBHOOK_URL=https://your-webhook-url.com
NOTIFICATION_LEVEL=INFO
```

#### Система отчетов
```bash
# Telegram отчеты
ENABLE_REPORTS=true
REPORTS_BOT_TOKEN=your_bot_token
REPORTS_CHANNEL_ID=your_channel_id
REPORT_INTERVAL_HOURS=12       # Интервал отчетов (часы)
REPORTS_TIMEZONE=Europe/Moscow
```

#### Логирование
```bash
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
LOG_MAX_SIZE=10485760          # Максимальный размер лога (байт)
LOG_BACKUP_COUNT=5
LOG_CONSOLE=false
```

### Настройка Google Sheets

#### 1. Создание проекта в Google Cloud Console
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API
4. Создайте сервисный аккаунт
5. Скачайте JSON файл с ключами
6. Переименуйте файл в `credentials.json`

#### 2. Настройка таблиц
1. Создайте Google Sheets таблицы для каждого типа сообщений
2. Поделитесь таблицами с email сервисного аккаунта
3. Добавьте URLs таблиц в `.env` файл
4. Протестируйте подключение: `python tests/test_google_sheets.py`

#### 3. Структура таблиц
Таблицы должны содержать колонки:
- **A**: Сообщения (текст для рассылки)
- **B**: Статус (активно/неактивно)
- **C**: Приоритет (1-10)
- **D**: Дата создания
- **E**: Дата обновления

### Настройка аккаунтов Telegram

#### Автоматическая настройка
```bash
python scripts/setup_accounts.py
```

#### Ручная настройка
1. Получите API_ID и API_HASH на [my.telegram.org](https://my.telegram.org/)
2. Добавьте их в `.env` файл
3. Запустите настройку аккаунтов
4. Введите номера телефонов для каждого аккаунта
5. Введите коды подтверждения

#### Структура аккаунтов
- **acc1**: Оптовый аккаунт (B2B, AAA Store)
- **acc2**: Розничный аккаунт (B2C, Яблочный Гусь)

## 🔧 Управление и команды

### Основные команды

#### Запуск системы
```bash
# Интерактивный запуск с меню
python run.py

# Прямой запуск
python main.py

# Запуск в фоновом режиме
nohup python main.py > output.log 2>&1 &
```

#### Управление сообщениями
```bash
# Обновление сообщений из Google Sheets
python scripts/update_messages.py

# Обновление конкретного типа сообщений
python scripts/update_messages.py --type b2b
python scripts/update_messages.py --type b2c
python scripts/update_messages.py --type aaa
python scripts/update_messages.py --type gus
```

#### Тестирование
```bash
# Тестирование всех броудкастеров
python scripts/test_broadcasters.py

# Ночное тестирование (игнорирует тихий час)
python scripts/night_test.py

# Тестирование Google Sheets
python tests/test_google_sheets.py
```

#### Мониторинг
```bash
# Просмотр статистики
python scripts/show_stats.py

# Мониторинг в реальном времени
python scripts/watch_stats.py

# Проверка окружения
python scripts/check_environment.py
```

#### Управление отчетами
```bash
# Настройка отчетов
python scripts/manage_reports.py

# Переключение целевых чатов
python scripts/switch_targets.py
```

### Интерактивное меню (run.py)

При запуске `python run.py` доступны следующие опции:

1. **🚀 Запуск полной системы** - Запуск всех броудкастеров
2. **🧪 Запуск тестовой версии** - Запуск с тестовыми чатами
3. **📊 Просмотр статистики** - Текущая статистика рассылки
4. **⏹️ Остановка системы** - Остановка всех процессов
5. **🔄 Перезапуск системы** - Перезапуск с обновлением
6. **🔧 Переключение между чатами** - Смена целевых чатов
7. **📁 Миграция старых файлов** - Миграция данных
8. **🧪 Тест Google Sheets** - Проверка подключения к таблицам
9. **📝 Обновление сообщений** - Загрузка сообщений из таблиц
10. **📈 Управление отчетами** - Настройка отчетности
11. **🔥 Тест новых броудкастеров** - Тестирование AAA/GUS
12. **🔄 Обновление всех сообщений** - Обновление всех источников
13. **🔐 Настройка аккаунтов** - Управление Telegram аккаунтами
14. **🌙 Ночное тестирование** - Тестирование с игнорированием тихого часа

### Управление через переменные окружения

#### Временное изменение настроек
```bash
# Изменение задержки между чатами
DELAY_BETWEEN_CHATS=30 python main.py

# Отключение тихого часа
ENABLE_QUIET_HOURS=false python main.py

# Изменение уровня логирования
LOG_LEVEL=DEBUG python main.py
```

#### Переключение между режимами
```bash
# Тестовый режим (использует TEST_TARGETS)
python -c "import os; os.environ['TEST_MODE']='true'; exec(open('main.py').read())"

# Продакшн режим (использует TARGETS)
python -c "import os; os.environ['TEST_MODE']='false'; exec(open('main.py').read())"
```

## 📊 Мониторинг и отчеты

### Система логирования

#### Уровни логирования
- **DEBUG**: Подробная отладочная информация
- **INFO**: Общая информация о работе
- **WARNING**: Предупреждения
- **ERROR**: Ошибки
- **CRITICAL**: Критические ошибки

#### Файлы логов
- **Основной лог**: `logs/bot.log`
- **Архивные логи**: `logs/bot_old_*.log`
- **Ротация логов**: Автоматическая по размеру

#### Настройка логирования
```python
# В коде
import logging
logger = logging.getLogger(__name__)
logger.info("Информационное сообщение")
logger.error("Сообщение об ошибке")
```

### Метрики производительности

#### Собираемые метрики
- Количество отправленных сообщений
- Количество ошибок
- Время выполнения операций
- Статистика по аккаунтам
- Статистика по типам сообщений
- FloodWait события

#### Просмотр метрик
```bash
# Текущая статистика
python scripts/show_stats.py

# Статистика в реальном времени
python scripts/watch_stats.py

# Экспорт статистики
python -c "
from monitoring.metrics import MetricsCollector
collector = MetricsCollector()
stats = collector.get_summary_stats()
print(stats)
"
```

### Система отчетов

#### Автоматические отчеты
- **Ежедневные отчеты**: Общая статистика за день
- **Отчеты по ошибкам**: Анализ проблем
- **Отчеты производительности**: Метрики эффективности
- **Отчеты по аккаунтам**: Статистика по каждому аккаунту

#### Настройка отчетов
```bash
# Включение отчетов
ENABLE_REPORTS=true
REPORTS_BOT_TOKEN=your_bot_token
REPORTS_CHANNEL_ID=your_channel_id
REPORT_INTERVAL_HOURS=12
```

#### Управление отчетами
```bash
# Настройка через скрипт
python scripts/manage_reports.py

# Ручная отправка отчета
python -c "
from monitoring.reports import TelegramReporter
reporter = TelegramReporter('bot_token', 'channel_id')
reporter.send_report()
"
```

### Система уведомлений

#### Типы уведомлений
- **INFO**: Информационные сообщения
- **WARNING**: Предупреждения
- **ERROR**: Ошибки
- **CRITICAL**: Критические ошибки

#### Каналы уведомлений
- **Telegram**: Уведомления в Telegram
- **Webhook**: HTTP запросы на внешние сервисы
- **Email**: Email уведомления (планируется)

#### Настройка уведомлений
```bash
# Telegram уведомления
ENABLE_TELEGRAM_NOTIFICATIONS=true
ADMIN_TELEGRAM_ID=your_admin_id

# Webhook уведомления
ENABLE_WEBHOOK_NOTIFICATIONS=true
WEBHOOK_URL=https://your-webhook-url.com
```

## 🛠️ Разработка и расширение

### Добавление нового броудкастера

#### 1. Создание файла сообщений
Создайте файл `config/messages_new.py`:
```python
# Обновлено: 2025-01-XX XX:XX:XX
MESSAGESNEW = [
    "Сообщение 1 для нового броудкастера",
    "Сообщение 2 с прайсом товаров",
    "Сообщение 3 с акциями",
    # Добавьте больше сообщений...
]
```

#### 2. Добавление URL таблицы
Добавьте в `.env`:
```bash
NEW_SHEET_URL=https://docs.google.com/spreadsheets/d/...
```

#### 3. Обновление конфигурации
Обновите `config/settings.py`:
```python
@dataclass
class GoogleSheetsConfig:
    # Существующие поля...
    new_sheet_url: Optional[str] = None

@dataclass
class AppConfig:
    # Существующие поля...
    new_messages: List[str] = field(default_factory=list)

# В методе load_config добавьте:
from .messages_new import MESSAGESNEW

# В создании конфигурации:
new_messages=MESSAGESNEW,
```

#### 4. Создание броудкастера
Обновите `main.py`:
```python
# В методе _create_broadcasters добавьте:
new_broadcaster = EnhancedBroadcaster(
    config=self.config,
    name="NEW_Broadcaster",
    targets=self.config.targets,
    messages=self.config.new_messages,
    session_name="sessions/acc1"  # или acc2
)
self.broadcasters.append(new_broadcaster)
```

### Добавление новых целевых чатов

#### 1. Обновление targets.py
```python
# Добавьте новые чаты в config/targets.py
NEW_TARGETS = [
    -1001234567890,  # Новый чат 1
    -1001234567891,  # Новый чат 2
    -1001234567892,  # Новый чат 3
]

# Или добавьте к существующим
TARGETS.extend([
    -1001234567890,
    -1001234567891,
])
```

#### 2. Обновление конфигурации
```python
# В config/settings.py
@dataclass
class AppConfig:
    # Существующие поля...
    new_targets: List[int] = field(default_factory=list)

# В методе load_config:
from .targets import NEW_TARGETS

# В создании конфигурации:
new_targets=NEW_TARGETS,
```

### Добавление нового аккаунта

#### 1. Настройка аккаунта
```bash
python scripts/setup_accounts.py
# Следуйте инструкциям для создания нового аккаунта
```

#### 2. Создание файла сессии
Новый файл сессии будет создан в `sessions/acc3.session`

#### 3. Обновление конфигурации
```python
# В main.py добавьте новый броудкастер с новым аккаунтом:
new_broadcaster = EnhancedBroadcaster(
    config=self.config,
    name="NEW_Broadcaster",
    targets=self.config.targets,
    messages=self.config.new_messages,
    session_name="sessions/acc3"  # Новый аккаунт
)
```

### Создание кастомных скриптов

#### Пример скрипта для массовой отправки
```python
#!/usr/bin/env python3
"""
Скрипт для массовой отправки сообщений
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager
from core.broadcaster import EnhancedBroadcaster

async def mass_send():
    """Массовая отправка сообщений"""
    config = config_manager.load_config()
    
    # Создаем броудкастер
    broadcaster = EnhancedBroadcaster(
        config=config,
        name="Mass_Sender",
        targets=config.targets,
        messages=config.b2b_messages,
        session_name="sessions/acc1"
    )
    
    try:
        # Запускаем броудкастер
        await broadcaster.start()
        
        # Ждем завершения
        await asyncio.sleep(3600)  # 1 час
        
    except KeyboardInterrupt:
        print("Остановка по запросу пользователя...")
    finally:
        await broadcaster.stop()

if __name__ == "__main__":
    asyncio.run(mass_send())
```

### Интеграция с внешними сервисами

#### Webhook интеграция
```python
import requests
import json

def send_webhook_notification(message, level="INFO"):
    """Отправка уведомления через webhook"""
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        return
    
    payload = {
        "message": message,
        "level": level,
        "timestamp": datetime.now().isoformat(),
        "source": "SendMessageBot"
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка отправки webhook: {e}")
```

#### API интеграция
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API для получения статистики"""
    from monitoring.metrics import MetricsCollector
    collector = MetricsCollector()
    stats = collector.get_summary_stats()
    return jsonify(stats)

@app.route('/api/send', methods=['POST'])
def send_message():
    """API для отправки сообщений"""
    data = request.json
    # Логика отправки сообщения
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

## 🔍 Устранение неполадок

### Критические ошибки

#### 1. Ошибка авторизации
```
❌ Ошибка: attempt to write a readonly database
```

**Причина**: Неправильные права доступа к файлам сессий

**Решение**:
```bash
# Исправление прав доступа
chmod 644 sessions/*.session

# Или удаление и пересоздание
rm sessions/*.session
python scripts/setup_accounts.py
```

#### 2. Ошибка импорта модулей
```
❌ ModuleNotFoundError: No module named 'telethon'
```

**Причина**: Не установлены зависимости

**Решение**:
```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Или установка конкретного модуля
pip install telethon gspread python-dotenv
```

#### 3. Ошибка Google Sheets
```
❌ Ошибка: 403 Forbidden
```

**Причина**: Неправильные права доступа к таблицам

**Решение**:
1. Проверьте `credentials.json`
2. Убедитесь, что сервисный аккаунт имеет доступ к таблицам
3. Проверьте URLs таблиц в `.env`

### Ошибки рассылки

#### 1. FloodWait ошибки
```
❌ FloodWaitError: A wait of 300 seconds is required
```

**Причина**: Превышен лимит запросов к Telegram API

**Решение**: Система автоматически обработает, подождите

#### 2. Ошибки отправки сообщений
```
❌ Ошибка отправки в чат -1001234567890: Chat not found
```

**Причина**: Чат не найден или бот заблокирован

**Решение**:
1. Проверьте ID чата в `config/targets.py`
2. Убедитесь, что бот добавлен в чат
3. Проверьте права бота в чате

#### 3. Ошибки сессий
```
❌ Ошибка: Session file corrupted
```

**Причина**: Повреждение файла сессии

**Решение**:
```bash
# Удаление поврежденной сессии
rm sessions/acc1.session
python scripts/setup_accounts.py
```

### Проблемы производительности

#### 1. Медленная работа
**Причины**:
- Слишком короткие задержки
- Большое количество чатов
- Проблемы с сетью

**Решение**:
```bash
# Увеличение задержек
DELAY_BETWEEN_CHATS=30
CYCLE_DELAY=1800

# Ограничение количества чатов
# Временно используйте TEST_TARGETS
```

#### 2. Высокое потребление памяти
**Причины**:
- Большое количество сообщений
- Утечки памяти в коде

**Решение**:
```bash
# Ограничение размера логов
LOG_MAX_SIZE=5242880  # 5MB

# Перезапуск системы каждые 6 часов
# Добавьте cron задачу
```

### Диагностические команды

#### Проверка окружения
```bash
python scripts/check_environment.py
```

#### Тестирование компонентов
```bash
# Тест Google Sheets
python tests/test_google_sheets.py

# Тест броудкастеров
python scripts/test_broadcasters.py

# Тест уведомлений
python tests/test_notifications.py
```

#### Анализ логов
```bash
# Просмотр последних ошибок
tail -n 100 logs/bot.log | grep ERROR

# Поиск конкретной ошибки
grep "FloodWait" logs/bot.log

# Анализ производительности
grep "Время выполнения" logs/bot.log
```

### Восстановление после сбоев

#### Автоматическое восстановление
Система автоматически восстанавливается после:
- Сетевых сбоев
- Временных ошибок API
- FloodWait событий

#### Ручное восстановление
```bash
# Остановка всех процессов
pkill -f "python main.py"

# Очистка временных файлов
rm -f *.tmp *.lock

# Перезапуск системы
python main.py
```

#### Восстановление данных
```bash
# Восстановление из бэкапа
cp backup/messages/messages_backup_*.py config/messages.py

# Восстановление сессий
cp backup/sessions/* sessions/
```

## 📈 Масштабирование

### Горизонтальное масштабирование

#### Добавление серверов
1. **Настройка дополнительных серверов**:
   ```bash
   # На каждом сервере
   git clone <repository_url>
   cd SendMessageBot
   pip install -r requirements.txt
   cp .env.example .env
   # Настройте .env для каждого сервера
   ```

2. **Распределение нагрузки**:
   ```python
   # Разные наборы чатов для каждого сервера
   # Сервер 1: чаты 1-100
   # Сервер 2: чаты 101-200
   # Сервер 3: чаты 201-300
   ```

3. **Координация через внешний сервис**:
   ```python
   # Использование Redis для координации
   import redis
   
   redis_client = redis.Redis(host='localhost', port=6379, db=0)
   
   def acquire_lock(lock_name):
       return redis_client.set(lock_name, "locked", nx=True, ex=300)
   
   def release_lock(lock_name):
       redis_client.delete(lock_name)
   ```

#### Балансировка нагрузки
```python
# Пример балансировки между аккаунтами
class LoadBalancer:
    def __init__(self, accounts):
        self.accounts = accounts
        self.current_index = 0
    
    def get_next_account(self):
        account = self.accounts[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.accounts)
        return account
```

### Вертикальное масштабирование

#### Оптимизация производительности
1. **Увеличение количества потоков**:
   ```python
   # В config/settings.py
   @dataclass
   class BroadcastingConfig:
       max_concurrent_sends: int = 5  # Одновременных отправок
       thread_pool_size: int = 10     # Размер пула потоков
   ```

2. **Оптимизация задержек**:
   ```python
   # Динамические задержки в зависимости от нагрузки
   def calculate_delay(base_delay, error_count):
       if error_count > 5:
           return base_delay * 2
       elif error_count > 2:
           return base_delay * 1.5
       return base_delay
   ```

3. **Кэширование данных**:
   ```python
   import functools
   import time
   
   @functools.lru_cache(maxsize=128)
   def get_chat_info(chat_id):
       # Кэширование информации о чатах
       pass
   ```

#### Мониторинг ресурсов
```python
import psutil
import time

class ResourceMonitor:
    def __init__(self):
        self.process = psutil.Process()
    
    def get_stats(self):
        return {
            'cpu_percent': self.process.cpu_percent(),
            'memory_percent': self.process.memory_percent(),
            'memory_mb': self.process.memory_info().rss / 1024 / 1024,
            'open_files': len(self.process.open_files()),
        }
    
    def check_limits(self):
        stats = self.get_stats()
        if stats['memory_percent'] > 80:
            return "HIGH_MEMORY_USAGE"
        if stats['cpu_percent'] > 90:
            return "HIGH_CPU_USAGE"
        return "OK"
```

### Масштабирование данных

#### Оптимизация хранения
1. **Сжатие логов**:
   ```bash
   # Автоматическое сжатие старых логов
   find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
   ```

2. **Архивирование данных**:
   ```python
   import zipfile
   import datetime
   
   def archive_old_data():
       timestamp = datetime.datetime.now().strftime("%Y%m%d")
       with zipfile.ZipFile(f"archive_{timestamp}.zip", 'w') as zipf:
           zipf.write("logs/bot.log")
           zipf.write("data/chat_ids.txt")
   ```

#### Распределенное хранение
```python
# Использование внешней базы данных
import sqlite3
import pymongo

class DatabaseManager:
    def __init__(self, db_type="sqlite"):
        if db_type == "sqlite":
            self.db = sqlite3.connect("bot_data.db")
        elif db_type == "mongodb":
            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.db = self.client["sendmessagebot"]
    
    def save_message_log(self, chat_id, message, status):
        # Сохранение лога сообщений
        pass
    
    def get_statistics(self):
        # Получение статистики
        pass
```

## 📚 API Справочник

### Основные классы

#### `EnhancedBroadcaster`
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
    
    async def start(self):
        """Запуск броудкастера"""
    
    async def stop(self):
        """Остановка броудкастера"""
    
    async def send_messages(self):
        """Отправка сообщений в целевые чаты"""
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики броудкастера"""
    
    def print_stats(self):
        """Вывод статистики в консоль"""
```

#### `ConfigManager`
Менеджер конфигурации системы.

```python
class ConfigManager:
    def __init__(self):
        """Инициализация менеджера конфигурации"""
    
    def load_config(self) -> AppConfig:
        """
        Загрузка конфигурации из переменных окружения
        
        Returns:
            AppConfig: Загруженная конфигурация
        """
    
    def get_config(self) -> AppConfig:
        """Получение текущей конфигурации"""
    
    def reload_config(self):
        """Перезагрузка конфигурации"""
```

#### `GoogleSheetsFetcher`
Класс для работы с Google Sheets.

```python
class GoogleSheetsFetcher:
    def __init__(self, credentials_file: str):
        """
        Инициализация клиента Google Sheets
        
        Args:
            credentials_file: Путь к файлу credentials.json
        """
    
    def fetch_messages(self, sheet_url: str) -> List[str]:
        """
        Получение сообщений из Google Sheets
        
        Args:
            sheet_url: URL таблицы Google Sheets
            
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

#### `MetricsCollector`
Сборщик метрик производительности.

```python
class MetricsCollector:
    def __init__(self):
        """Инициализация сборщика метрик"""
    
    def record_message_sent(self, chat_id: int, success: bool, duration: float):
        """
        Запись метрики отправки сообщения
        
        Args:
            chat_id: ID чата
            success: Успешность отправки
            duration: Время выполнения
        """
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Получение сводной статистики
        
        Returns:
            Dict[str, Any]: Словарь со статистикой
        """
    
    def get_broadcaster_stats(self, broadcaster_name: str) -> Dict[str, Any]:
        """
        Получение статистики конкретного броудкастера
        
        Args:
            broadcaster_name: Имя броудкастера
            
        Returns:
            Dict[str, Any]: Статистика броудкастера
        """
```

#### `TelegramReporter`
Класс для отправки отчетов в Telegram.

```python
class TelegramReporter:
    def __init__(self, bot_token: str, channel_id: str, timezone: str = "Europe/Moscow"):
        """
        Инициализация репортера
        
        Args:
            bot_token: Токен Telegram бота
            channel_id: ID канала для отчетов
            timezone: Часовой пояс
        """
    
    async def send_report(self, stats: Dict[str, Any]):
        """
        Отправка отчета
        
        Args:
            stats: Статистика для отчета
        """
    
    async def start(self, get_broadcasters_func):
        """
        Запуск автоматической отправки отчетов
        
        Args:
            get_broadcasters_func: Функция получения списка броудкастеров
        """
    
    async def stop(self):
        """Остановка отправки отчетов"""
```

### Утилиты

#### `Logger`
Система логирования.

```python
class Logger:
    def __init__(self, name: str, config: LoggingConfig):
        """
        Инициализация логгера
        
        Args:
            name: Имя логгера
            config: Конфигурация логирования
        """
    
    def debug(self, message: str):
        """Отладочное сообщение"""
    
    def info(self, message: str):
        """Информационное сообщение"""
    
    def warning(self, message: str):
        """Предупреждение"""
    
    def error(self, message: str):
        """Ошибка"""
    
    def critical(self, message: str):
        """Критическая ошибка"""
```

#### `SecurityManager`
Менеджер безопасности.

```python
class SecurityManager:
    def __init__(self):
        """Инициализация менеджера безопасности"""
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Шифрование чувствительных данных
        
        Args:
            data: Данные для шифрования
            
        Returns:
            str: Зашифрованные данные
        """
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Расшифровка данных
        
        Args:
            encrypted_data: Зашифрованные данные
            
        Returns:
            str: Расшифрованные данные
        """
    
    def validate_session_file(self, session_path: str) -> bool:
        """
        Валидация файла сессии
        
        Args:
            session_path: Путь к файлу сессии
            
        Returns:
            bool: True если файл валиден
        """
```

### Примеры использования

#### Создание кастомного броудкастера
```python
import asyncio
from config.settings import config_manager
from core.broadcaster import EnhancedBroadcaster

async def custom_broadcaster():
    """Пример создания кастомного броудкастера"""
    config = config_manager.load_config()
    
    # Создание броудкастера
    broadcaster = EnhancedBroadcaster(
        config=config,
        name="Custom_Broadcaster",
        targets=[-1001234567890, -1001234567891],  # Конкретные чаты
        messages=["Кастомное сообщение 1", "Кастомное сообщение 2"],
        session_name="sessions/acc1"
    )
    
    try:
        # Запуск
        await broadcaster.start()
        
        # Ожидание
        await asyncio.sleep(300)  # 5 минут
        
    finally:
        # Остановка
        await broadcaster.stop()

# Запуск
asyncio.run(custom_broadcaster())
```

#### Интеграция с внешним API
```python
import requests
import asyncio
from monitoring.metrics import MetricsCollector

class ExternalAPIIntegration:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.metrics = MetricsCollector()
    
    async def send_to_external_api(self, data: dict):
        """Отправка данных во внешний API"""
        try:
            response = requests.post(
                f"{self.api_url}/messages",
                json=data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            
            # Запись метрики
            self.metrics.record_message_sent(
                chat_id=data.get('chat_id'),
                success=True,
                duration=response.elapsed.total_seconds()
            )
            
            return response.json()
            
        except requests.RequestException as e:
            # Запись ошибки
            self.metrics.record_message_sent(
                chat_id=data.get('chat_id'),
                success=False,
                duration=0
            )
            raise e

# Использование
api = ExternalAPIIntegration("https://api.example.com", "your_api_key")
result = await api.send_to_external_api({
    "chat_id": -1001234567890,
    "message": "Тестовое сообщение"
})
```

#### Создание кастомного мониторинга
```python
import time
import json
from datetime import datetime

class CustomMonitor:
    def __init__(self, log_file: str = "custom_monitor.log"):
        self.log_file = log_file
        self.start_time = time.time()
    
    def log_event(self, event_type: str, data: dict):
        """Логирование события"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
            "uptime": time.time() - self.start_time
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def get_uptime(self) -> float:
        """Получение времени работы"""
        return time.time() - self.start_time
    
    def generate_report(self) -> dict:
        """Генерация отчета"""
        return {
            "uptime_seconds": self.get_uptime(),
            "uptime_hours": self.get_uptime() / 3600,
            "log_file": self.log_file,
            "status": "running"
        }

# Использование
monitor = CustomMonitor()
monitor.log_event("message_sent", {
    "chat_id": -1001234567890,
    "success": True
})

report = monitor.generate_report()
print(f"Система работает {report['uptime_hours']:.2f} часов")
```

## 🎯 Roadmap и развитие

### Текущие возможности (v1.0)

✅ **Реализовано**:
- Множественные броудкастеры (B2B, B2C, AAA, GUS)
- Интеграция с Google Sheets
- Система мониторинга и отчетов
- Автоматическое восстановление после ошибок
- Гибкая конфигурация через переменные окружения
- Система логирования с ротацией
- Ночное тестирование
- Управление через интерактивное меню

### Планы развития (v1.1 - v2.0)

#### v1.1 - Улучшения производительности (Q1 2025)
- [ ] **Оптимизация памяти**: Уменьшение потребления RAM на 30%
- [ ] **Параллельная обработка**: Отправка сообщений в несколько потоков
- [ ] **Умные задержки**: Адаптивные задержки в зависимости от нагрузки
- [ ] **Кэширование**: Кэш для часто используемых данных
- [ ] **Сжатие логов**: Автоматическое сжатие старых логов

#### v1.2 - Расширенная аналитика (Q2 2025)
- [ ] **Дашборд**: Web-интерфейс для мониторинга
- [ ] **Графики**: Визуализация статистики в реальном времени
- [ ] **Алерты**: Настраиваемые уведомления о проблемах
- [ ] **Экспорт данных**: Экспорт статистики в CSV/JSON
- [ ] **A/B тестирование**: Тестирование разных сообщений

#### v1.3 - Интеграции (Q3 2025)
- [ ] **REST API**: API для внешних интеграций
- [ ] **Webhook поддержка**: Расширенные webhook уведомления
- [ ] **CRM интеграция**: Подключение к популярным CRM
- [ ] **Email уведомления**: Отправка отчетов на email
- [ ] **Slack интеграция**: Уведомления в Slack

#### v2.0 - Машинное обучение (Q4 2025)
- [ ] **Оптимизация времени**: ML для выбора оптимального времени отправки
- [ ] **Персонализация**: Адаптация сообщений под аудиторию
- [ ] **Предсказание ошибок**: Предотвращение проблем до их возникновения
- [ ] **Автоматическая сегментация**: Группировка чатов по характеристикам
- [ ] **Рекомендации**: Предложения по улучшению эффективности

### Долгосрочные планы (v3.0+)

#### v3.0 - Мультиплатформенность (2026)
- [ ] **WhatsApp поддержка**: Интеграция с WhatsApp Business API
- [ ] **Viber поддержка**: Рассылки в Viber
- [ ] **Discord поддержка**: Интеграция с Discord
- [ ] **Универсальный API**: Единый интерфейс для всех платформ

#### v3.1 - Облачная платформа (2026)
- [ ] **SaaS версия**: Облачный сервис для пользователей
- [ ] **Мультитенантность**: Поддержка множественных клиентов
- [ ] **Автоматическое масштабирование**: Динамическое управление ресурсами
- [ ] **Глобальная доступность**: Развертывание в разных регионах

#### v4.0 - ИИ и автоматизация (2027)
- [ ] **Генерация контента**: ИИ для создания сообщений
- [ ] **Автоматическое тестирование**: ИИ для тестирования эффективности
- [ ] **Предиктивная аналитика**: Прогнозирование результатов кампаний
- [ ] **Автоматическая оптимизация**: Самооптимизирующаяся система

### Технические улучшения

#### Архитектура
- [ ] **Микросервисная архитектура**: Разделение на независимые сервисы
- [ ] **Контейнеризация**: Docker и Kubernetes поддержка
- [ ] **База данных**: Переход на PostgreSQL/MongoDB
- [ ] **Очереди сообщений**: Redis/RabbitMQ для обработки

#### Безопасность
- [ ] **Шифрование**: Полное шифрование чувствительных данных
- [ ] **Аутентификация**: OAuth2/JWT для API
- [ ] **Аудит**: Подробное логирование всех действий
- [ ] **Соответствие**: GDPR/CCPA соответствие

#### Производительность
- [ ] **Горизонтальное масштабирование**: Поддержка кластеров
- [ ] **Кэширование**: Redis для кэширования
- [ ] **CDN**: Распределение статических ресурсов
- [ ] **Оптимизация**: Профилирование и оптимизация кода

### Пользовательский опыт

#### Интерфейс
- [ ] **Web-интерфейс**: Полнофункциональный веб-интерфейс
- [ ] **Мобильное приложение**: iOS/Android приложения
- [ ] **Темная тема**: Поддержка тем оформления
- [ ] **Локализация**: Поддержка множественных языков

#### Удобство использования
- [ ] **Мастер настройки**: Пошаговая настройка системы
- [ ] **Шаблоны**: Готовые шаблоны конфигураций
- [ ] **Документация**: Интерактивная документация
- [ ] **Поддержка**: Встроенная система поддержки

### Экосистема

#### Партнерства
- [ ] **Интеграции**: Партнерство с популярными сервисами
- [ ] **API маркетплейс**: Магазин готовых интеграций
- [ ] **Сообщество**: Форум и сообщество разработчиков
- [ ] **Сертификация**: Программа сертификации партнеров

#### Образование
- [ ] **Курсы**: Онлайн курсы по использованию системы
- [ ] **Веб-семинары**: Регулярные обучающие веб-семинары
- [ ] **Документация**: Расширенная техническая документация
- [ ] **Примеры**: Библиотека примеров использования

## ❓ FAQ и поддержка

### Часто задаваемые вопросы

#### Общие вопросы

**Q: Сколько сообщений может отправить система за час?**
A: Производительность зависит от настроек задержек и количества чатов. При стандартных настройках (15 сек между чатами, 20 мин между циклами) система может отправить до 240 сообщений в час на один аккаунт.

**Q: Можно ли использовать систему с одним аккаунтом?**
A: Да, система поддерживает работу с одним аккаунтом. Просто настройте один аккаунт и используйте его для всех броудкастеров.

**Q: Безопасно ли хранить API ключи в .env файле?**
A: Да, .env файл не должен попадать в систему контроля версий. Добавьте его в .gitignore для безопасности.

**Q: Можно ли изменить задержки во время работы?**
A: Да, измените переменные окружения и перезапустите систему. Изменения применятся автоматически.

#### Технические вопросы

**Q: Что делать, если система не может подключиться к Google Sheets?**
A: 
1. Проверьте правильность URL таблицы
2. Убедитесь, что сервисный аккаунт имеет доступ к таблице
3. Проверьте файл credentials.json
4. Запустите тест: `python tests/test_google_sheets.py`

**Q: Как увеличить производительность системы?**
A:
1. Уменьшите задержки между сообщениями (осторожно!)
2. Добавьте больше аккаунтов
3. Используйте параллельную обработку
4. Оптимизируйте размер сообщений

**Q: Почему система показывает 0 чатов и 0 сообщений?**
A: Это означает, что конфигурация не загружается правильно. Проверьте:
1. Правильность импортов в config/settings.py
2. Существование файлов messages_*.py
3. Корректность переменных в .env

**Q: Как настроить систему для работы в продакшене?**
A:
1. Используйте продакшн аккаунты Telegram
2. Настройте мониторинг и алерты
3. Настройте автоматические бэкапы
4. Используйте продакшн Google Sheets таблицы
5. Настройте логирование на уровне ERROR

#### Проблемы и решения

**Q: Система постоянно получает FloodWait ошибки**
A: 
1. Увеличьте задержки между сообщениями
2. Уменьшите количество чатов в одном цикле
3. Используйте больше аккаунтов для распределения нагрузки
4. Проверьте, не отправляете ли вы слишком много сообщений

**Q: Сообщения не доставляются в некоторые чаты**
A:
1. Проверьте, что бот добавлен в чат
2. Убедитесь, что у бота есть права на отправку сообщений
3. Проверьте, не заблокирован ли бот в чате
4. Убедитесь, что ID чата правильный

**Q: Система потребляет слишком много памяти**
A:
1. Уменьшите размер логов
2. Ограничьте количество сообщений в памяти
3. Используйте потоковую обработку
4. Перезапускайте систему периодически

**Q: Google Sheets обновления не работают**
A:
1. Проверьте интернет соединение
2. Убедитесь, что Google Sheets API включен
3. Проверьте права доступа к таблицам
4. Проверьте формат данных в таблицах

### Получение поддержки

#### Документация
- **Основная документация**: Этот README файл
- **Детальные руководства**: Папка `docs/`
- **API справочник**: `docs/API_REFERENCE.md`
- **Решение проблем**: `docs/TROUBLESHOOTING.md`

#### Логи и диагностика
- **Основной лог**: `logs/bot.log`
- **Проверка окружения**: `python scripts/check_environment.py`
- **Тестирование компонентов**: `python tests/`

#### Сообщество
- **GitHub Issues**: Создайте issue для багов и предложений
- **Discussions**: Обсуждения и вопросы
- **Wiki**: Дополнительная документация

#### Коммерческая поддержка
- **Email**: support@sendmessagebot.com
- **Telegram**: @SendMessageBotSupport
- **SLA**: 24/7 поддержка для корпоративных клиентов

### Контрибьюция

#### Как внести вклад
1. **Fork** репозитория
2. **Создайте** feature branch
3. **Сделайте** изменения
4. **Добавьте** тесты
5. **Создайте** Pull Request

#### Стандарты кода
- **PEP 8**: Следуйте стандартам Python
- **Типизация**: Используйте type hints
- **Документация**: Добавляйте docstrings
- **Тесты**: Покрывайте код тестами

#### Области для контрибьюции
- **Новые функции**: Предложения новых возможностей
- **Баги**: Исправление ошибок
- **Документация**: Улучшение документации
- **Тесты**: Добавление тестов
- **Оптимизация**: Улучшение производительности

---

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🙏 Благодарности

- **Telethon** - за отличную библиотеку для работы с Telegram API
- **Google Sheets API** - за простую интеграцию с таблицами
- **Сообщество Python** - за множество полезных библиотек
- **Контрибьюторы** - за вклад в развитие проекта

---

**Создано с ❤️ для автоматизации рассылок в Telegram**

*Версия документации: 2.0*  
*Последнее обновление: 2025-01-XX*