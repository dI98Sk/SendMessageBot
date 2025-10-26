# 🔍 Руководство по устранению неполадок

## 📋 Содержание

- [🚨 Критические ошибки](#-критические-ошибки)
- [⚠️ Ошибки авторизации](#️-ошибки-авторизации)
- [📊 Ошибки Google Sheets](#-ошибки-google-sheets)
- [💬 Ошибки рассылки](#-ошибки-рассылки)
- [🔧 Ошибки системы](#-ошибки-системы)
- [📈 Проблемы производительности](#-проблемы-производительности)
- [🛠️ Диагностические команды](#️-диагностические-команды)

## 🚨 Критические ошибки

### 1. Ошибка: "attempt to write a readonly database"

**Симптомы**:
```
❌ Ошибка настройки ОПТОВЫЙ аккаунта: attempt to write a readonly database
❌ Критическая ошибка: attempt to write a readonly database
```

**Причина**: Файлы сессий имеют неправильные права доступа

**Решение**:
```bash
# Исправление прав доступа
chmod 644 sessions/*.session

# Или удаление и пересоздание
rm sessions/*.session
python scripts/setup_accounts.py
```

### 2. Ошибка: "ModuleNotFoundError"

**Симптомы**:
```
❌ ModuleNotFoundError: No module named 'telethon'
❌ ModuleNotFoundError: No module named 'gspread'
```

**Причина**: Не установлены зависимости

**Решение**:
```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Или установка конкретного модуля
pip install telethon gspread python-dotenv
```

### 3. Ошибка: "FileNotFoundError: .env"

**Симптомы**:
```
❌ FileNotFoundError: [Errno 2] No such file or directory: '.env'
```

**Причина**: Отсутствует файл конфигурации

**Решение**:
```bash
# Создание .env файла
cp .env.example .env
# Отредактируйте .env файл с вашими данными
```

## ⚠️ Ошибки авторизации

### 1. Ошибка: "Invalid phone number"

**Симптомы**:
```
❌ Invalid phone number
```

**Причина**: Неправильный формат номера телефона

**Решение**:
- Используйте международный формат: `+7XXXXXXXXXX`
- Убедитесь, что номер активен
- Проверьте, что номер зарегистрирован в Telegram

### 2. Ошибка: "Invalid code"

**Симптомы**:
```
❌ Invalid code
```

**Причина**: Неправильный код подтверждения

**Решение**:
- Проверьте код в SMS или Telegram
- Убедитесь, что код не истек
- Попробуйте запросить новый код

### 3. Ошибка: "Two-factor authentication required"

**Симптомы**:
```
❌ Two-factor authentication required
```

**Причина**: Включена двухфакторная аутентификация

**Решение**:
- Введите пароль двухфакторной аутентификации
- Убедитесь, что пароль правильный
- Если забыли пароль, сбросьте его в настройках Telegram

### 4. Ошибка: "Session expired"

**Симптомы**:
```
❌ Session expired
```

**Причина**: Сессия истекла или повреждена

**Решение**:
```bash
# Удаление старой сессии
rm sessions/acc1.session

# Настройка новой сессии
python scripts/setup_accounts.py
```

## 📊 Ошибки Google Sheets

### 1. Ошибка: "403 Forbidden"

**Симптомы**:
```
❌ 403 Forbidden
❌ Ошибка обновления B2B: 403 Forbidden
```

**Причина**: Нет доступа к таблице

**Решение**:
1. Проверьте `credentials.json`
2. Убедитесь, что сервисный аккаунт добавлен в таблицу
3. Проверьте права доступа (должны быть "Редактор")

### 2. Ошибка: "404 Not Found"

**Симптомы**:
```
❌ 404 Not Found
```

**Причина**: Неправильный URL таблицы

**Решение**:
1. Проверьте URL в `.env` файле
2. Убедитесь, что таблица существует
3. Проверьте, что таблица не удалена

### 3. Ошибка: "expected string or bytes-like object"

**Симптомы**:
```
❌ Ошибка обновления B2B: expected string or bytes-like object
```

**Причина**: Пустые ячейки или неправильный формат данных

**Решение**:
1. Проверьте, что в таблице есть данные
2. Убедитесь, что сообщения в первом столбце
3. Проверьте, что нет пустых ячеек

### 4. Ошибка: "Authentication failed"

**Симптомы**:
```
❌ Authentication failed
```

**Причина**: Неправильные учетные данные

**Решение**:
1. Проверьте `credentials.json`
2. Убедитесь, что файл не поврежден
3. Пересоздайте сервисный аккаунт

## 💬 Ошибки рассылки

### 1. Ошибка: "FloodWaitError"

**Симптомы**:
```
❌ FloodWaitError: A wait of X seconds is required
```

**Причина**: Превышен лимит отправки сообщений

**Решение**:
- Система автоматически обработает
- Подождите указанное время
- Увеличьте задержку между сообщениями

### 2. Ошибка: "Chat not found"

**Симптомы**:
```
❌ Chat not found
```

**Причина**: Неправильный ID чата или чат удален

**Решение**:
1. Проверьте ID чата в `config/targets.py`
2. Убедитесь, что чат существует
3. Проверьте, что бот добавлен в чат

### 3. Ошибка: "Not enough rights"

**Симптомы**:
```
❌ Not enough rights to send messages
```

**Причина**: Недостаточно прав для отправки сообщений

**Решение**:
1. Убедитесь, что аккаунт добавлен в чат
2. Проверьте права администратора
3. Убедитесь, что чат не заблокирован

### 4. Ошибка: "Message too long"

**Симптомы**:
```
❌ Message too long
```

**Причина**: Сообщение превышает лимит Telegram

**Решение**:
1. Разбейте сообщение на части
2. Удалите лишние символы
3. Используйте более короткие сообщения

## 🔧 Ошибки системы

### 1. Ошибка: "Permission denied"

**Симптомы**:
```
❌ PermissionError: [Errno 13] Permission denied
```

**Причина**: Недостаточно прав для записи файлов

**Решение**:
```bash
# Исправление прав доступа
chmod 644 sessions/*.session
chmod 644 logs/*.log
chmod 755 scripts/*.py
```

### 2. Ошибка: "Port already in use"

**Симптомы**:
```
❌ Port already in use
```

**Причина**: Порт уже используется другим процессом

**Решение**:
```bash
# Поиск процесса
lsof -i :PORT

# Завершение процесса
kill -9 PID
```

### 3. Ошибка: "Out of memory"

**Симптомы**:
```
❌ Out of memory
```

**Причина**: Недостаточно оперативной памяти

**Решение**:
1. Закройте другие приложения
2. Увеличьте объем памяти
3. Оптимизируйте код

### 4. Ошибка: "Disk space full"

**Симптомы**:
```
❌ No space left on device
```

**Причина**: Недостаточно места на диске

**Решение**:
```bash
# Очистка логов
rm logs/*.log

# Очистка кэша
rm -rf __pycache__/
```

## 📈 Проблемы производительности

### 1. Медленная рассылка

**Симптомы**: Сообщения отправляются очень медленно

**Решение**:
1. Уменьшите задержку между сообщениями
2. Увеличьте количество потоков
3. Оптимизируйте код

### 2. Высокое использование CPU

**Симптомы**: Система тормозит

**Решение**:
1. Уменьшите количество потоков
2. Оптимизируйте алгоритмы
3. Используйте профилирование

### 3. Высокое использование памяти

**Симптомы**: Система использует много памяти

**Решение**:
1. Очистите кэш
2. Оптимизируйте структуры данных
3. Используйте генераторы

## 🛠️ Диагностические команды

### 1. Проверка окружения

```bash
# Полная проверка системы
python scripts/check_environment.py

# Проверка зависимостей
pip list

# Проверка версии Python
python --version
```

### 2. Проверка Google Sheets

```bash
# Тест подключения к таблицам
python tests/test_google_sheets.py

# Проверка конкретной таблицы
python -c "
from utils.google_sheets import GoogleSheetsFetcher
fetcher = GoogleSheetsFetcher()
messages = fetcher.fetch_messages('YOUR_SHEET_URL')
print(f'Найдено {len(messages)} сообщений')
"
```

### 3. Проверка аккаунтов

```bash
# Тест броудкастеров
python scripts/test_broadcasters.py

# Проверка сессий
ls -la sessions/

# Проверка прав доступа
ls -la sessions/*.session
```

### 4. Проверка логов

```bash
# Просмотр последних ошибок
tail -n 100 logs/bot.log | grep ERROR

# Поиск конкретной ошибки
grep "FloodWaitError" logs/bot.log

# Статистика ошибок
grep -c "ERROR" logs/bot.log
```

### 5. Проверка конфигурации

```bash
# Проверка .env файла
python -c "
from dotenv import load_dotenv
load_dotenv()
import os
print('API_ID:', os.getenv('API_ID'))
print('API_HASH:', os.getenv('API_HASH'))
"

# Проверка целей
python -c "
from config.targets import TEST_TARGETS, PRODUCTION_TARGETS
print('Тестовые чаты:', len(TEST_TARGETS))
print('Основные чаты:', len(PRODUCTION_TARGETS))
"
```

## 📞 Получение помощи

### 1. Сбор информации для отчета

```bash
# Создание отчета о системе
python scripts/check_environment.py > system_report.txt

# Сбор логов
cp logs/bot.log error_log.txt

# Сбор конфигурации
cp .env config_backup.txt
```

### 2. Создание минимального примера

```python
# test_minimal.py
from telethon import TelegramClient
import asyncio

async def test_connection():
    client = TelegramClient('test_session', API_ID, API_HASH)
    await client.start()
    me = await client.get_me()
    print(f"Подключен как: {me.first_name}")
    await client.disconnect()

asyncio.run(test_connection())
```

### 3. Обращение за помощью

При обращении за помощью предоставьте:
- Описание проблемы
- Сообщения об ошибках
- Логи системы
- Конфигурацию
- Шаги для воспроизведения

---

**Удачного устранения неполадок! 🔧**