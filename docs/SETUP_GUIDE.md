# 🔧 Руководство по настройке SendMessageBot

## 📋 Содержание

- [🚀 Быстрая настройка](#-быстрая-настройка)
- [⚙️ Детальная настройка](#️-детальная-настройка)
- [🔐 Настройка аккаунтов Telegram](#-настройка-аккаунтов-telegram)
- [📊 Настройка Google Sheets](#-настройка-google-sheets)
- [🎯 Настройка целевых чатов](#-настройка-целевых-чатов)
- [📝 Настройка сообщений](#-настройка-сообщений)
- [🔍 Проверка настройки](#-проверка-настройки)
- [🚨 Устранение проблем](#-устранение-проблем)

## 🚀 Быстрая настройка

### 1. Клонирование и установка
```bash
git clone <repository_url>
cd SendMessageBot
pip install -r requirements.txt
```

### 2. Настройка окружения
```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 3. Настройка аккаунтов
```bash
python scripts/setup_accounts.py
```

### 4. Запуск
```bash
python main.py
```

## ⚙️ Детальная настройка

### Шаг 1: Подготовка окружения

#### Установка Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS
brew install python3

# Windows
# Скачайте с python.org
```

#### Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

#### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Шаг 2: Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# Telegram API (получите на https://my.telegram.org/apps)
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=+7XXXXXXXXXX

# Google Sheets URLs
BUY_SELL_PRICE_B2B_SHEET_URL=https://docs.google.com/spreadsheets/d/...
BUY_SELL_PRICE_B2C_SHEET_URL=https://docs.google.com/spreadsheets/d/...
BUY_SELL_PRICE_AAA_SHEET_URL=https://docs.google.com/spreadsheets/d/...
BUY_SELL_PRICE_GUS_SHEET_URL=https://docs.google.com/spreadsheets/d/...

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Настройки рассылки
MESSAGE_DELAY=1
MAX_RETRIES=3
FLOOD_WAIT_DELAY=60

# Настройки отчетов
REPORT_INTERVAL=12
REPORT_EMAIL=your@email.com
```

### Шаг 3: Настройка Google Sheets

#### 1. Создание проекта в Google Cloud Console

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API
4. Перейдите в "Credentials" → "Create Credentials" → "Service Account"
5. Создайте сервисный аккаунт
6. Скачайте JSON файл с ключами
7. Переименуйте файл в `credentials.json` и поместите в корень проекта

#### 2. Настройка доступа к таблицам

1. Откройте ваши Google Sheets
2. Нажмите "Поделиться" (Share)
3. Добавьте email сервисного аккаунта (из credentials.json)
4. Дайте права "Редактор" (Editor)

#### 3. Получение URL таблиц

1. Откройте таблицу
2. Скопируйте URL из адресной строки
3. Добавьте в `.env` файл

### Шаг 4: Настройка аккаунтов Telegram

#### Получение API данных

1. Перейдите на [my.telegram.org](https://my.telegram.org/)
2. Войдите в свой аккаунт
3. Перейдите в "API development tools"
4. Создайте новое приложение
5. Скопируйте `api_id` и `api_hash`

#### Настройка аккаунтов через скрипт

```bash
python scripts/setup_accounts.py
```

Выберите опции:
- **1**: Настроить ОПТОВЫЙ аккаунт (acc1)
- **2**: Настроить РОЗНИЧНЫЙ аккаунт (acc2)
- **3**: Настроить оба аккаунта

#### Ручная настройка аккаунтов

```python
from telethon import TelegramClient
import asyncio

async def setup_account():
    client = TelegramClient('sessions/acc1', API_ID, API_HASH)
    await client.start()
    await client.disconnect()

asyncio.run(setup_account())
```

## 🔐 Настройка аккаунтов Telegram

### Типы аккаунтов

| Аккаунт | Назначение | Броудкастеры |
|---------|------------|--------------|
| acc1 (ОПТОВЫЙ) | Оптовые сообщения | B2B, AAA |
| acc2 (РОЗНИЧНЫЙ) | Розничные сообщения | B2C, GUS |

### Процесс авторизации

1. **Ввод номера телефона** в международном формате (+7XXXXXXXXXX)
2. **Ввод кода подтверждения** из SMS или Telegram
3. **Ввод пароля двухфакторной аутентификации** (если включен)

### Управление сессиями

```bash
# Просмотр сессий
ls -la sessions/

# Удаление сессии
rm sessions/acc1.session

# Исправление прав доступа
chmod 644 sessions/*.session
```

## 📊 Настройка Google Sheets

### Структура таблиц

Таблицы должны содержать сообщения в первом столбце:

| A (Сообщения) |
|---------------|
| Сообщение 1   |
| Сообщение 2   |
| Сообщение 3   |

### Настройка доступа

1. **Откройте таблицу**
2. **Нажмите "Поделиться"**
3. **Добавьте email сервисного аккаунта**
4. **Установите права "Редактор"**

### Тестирование подключения

```bash
python tests/test_google_sheets.py
```

## 🎯 Настройка целевых чатов

### Редактирование целей

Откройте `config/targets.py`:

```python
# Тестовые чаты (для отладки)
TEST_TARGETS = [
    -1002679672234,  # ТЕСТ Рассылок 2
    -1002805990284,  # ТЕСТ РАССЫЛОК 1
]

# Основные чаты (для продакшена)
PRODUCTION_TARGETS = [
    -1001234567890,  # Основной чат 1
    -1001234567891,  # Основной чат 2
]
```

### Получение ID чатов

```bash
python scripts/get_chat_ids.py
```

### Переключение между тестовыми и основными чатами

```bash
python scripts/switch_targets.py
```

## 📝 Настройка сообщений

### Источники сообщений

1. **Google Sheets** - автоматическое обновление
2. **Локальные файлы** - ручное редактирование

### Обновление сообщений

```bash
# Обновление всех сообщений
python scripts/update_messages.py

# Обновление конкретного источника
python scripts/update_messages.py --source b2b
python scripts/update_messages.py --source b2c
python scripts/update_messages.py --source aaa
python scripts/update_messages.py --source gus
```

### Ручное редактирование

Откройте файлы в `config/`:
- `messages_b2b.py` - B2B сообщения
- `messages_b2c.py` - B2C сообщения
- `messages_aaa.py` - AAA сообщения
- `messages_gus.py` - GUS сообщения

## 🔍 Проверка настройки

### 1. Проверка окружения

```bash
python scripts/check_environment.py
```

### 2. Проверка Google Sheets

```bash
python tests/test_google_sheets.py
```

### 3. Проверка аккаунтов

```bash
python scripts/test_broadcasters.py
```

### 4. Полная проверка

```bash
python run.py
# Выберите опцию "Проверка системы"
```

## 🚨 Устранение проблем

### Проблема: Ошибка авторизации

```
❌ Ошибка: attempt to write a readonly database
```

**Решение**:
```bash
# Удалите файлы сессий
rm sessions/*.session

# Настройте заново
python scripts/setup_accounts.py
```

### Проблема: Ошибка Google Sheets

```
❌ Ошибка: 403 Forbidden
```

**Решение**:
1. Проверьте `credentials.json`
2. Убедитесь, что сервисный аккаунт имеет доступ к таблицам
3. Проверьте URL таблиц в `.env`

### Проблема: Ошибка импорта

```
❌ ModuleNotFoundError: No module named 'telethon'
```

**Решение**:
```bash
pip install -r requirements.txt
```

### Проблема: Ошибка прав доступа

```
❌ PermissionError: [Errno 13] Permission denied
```

**Решение**:
```bash
chmod 644 sessions/*.session
chmod 644 logs/*.log
```

### Проблема: FloodWait

```
❌ FloodWaitError: A wait of X seconds is required
```

**Решение**: Система автоматически обработает, подождите указанное время

## 📞 Поддержка

Если возникли проблемы:

1. **Проверьте логи**: `logs/bot.log`
2. **Запустите диагностику**: `python scripts/check_environment.py`
3. **Обратитесь к документации**: `docs/`
4. **Создайте issue** в репозитории

---

**Удачной настройки! 🚀**

