# 🚀 Быстрый старт - Гайд по запуску

**Дата:** 2025-12-13  
**Версия:** 2.1

---

## 📋 Что нужно перед запуском

### 1. Проверка зависимостей

```bash
# Установка зависимостей (если еще не установлены)
pip install -r requirements.txt
```

### 2. Проверка конфигурации

Убедитесь, что файл `.env` существует и содержит все необходимые настройки:

```bash
# Проверка наличия .env
ls -la .env  # Linux/Mac
dir .env     # Windows
```

**Обязательные переменные:**
- `API_ID` - ID Telegram API
- `API_HASH` - Hash Telegram API
- `TELEGRAM_SESSION_NAME` - Имя сессии (по умолчанию)
- Google Sheets URLs (для автообновления сообщений)

---

## 🎯 Варианты запуска

### ✅ Вариант 1: Запуск обоих сервисов одновременно (РЕКОМЕНДУЕТСЯ)

Этот вариант запускает оба сервиса:
- **Broadcaster Service** - рассылка сообщений в Telegram
- **Google Sheets Updater** - автоматическое обновление сообщений из Google Sheets

#### Linux/Mac:

```bash
# Переход в директорию проекта
cd /path/to/SendMessageBot

# Запуск обоих сервисов
bash scripts/start_all.sh

# Или с правами на выполнение
chmod +x scripts/start_all.sh
./scripts/start_all.sh
```

#### Windows:

```cmd
REM Переход в директорию проекта
cd C:\path\to\SendMessageBot

REM Запуск обоих сервисов
scripts\start_all.bat
```

**Что происходит:**
- Оба сервиса запускаются в фоне
- Логи сохраняются в `logs/broadcaster.log` и `logs/updater.log`
- Для остановки нажмите `Ctrl+C` (Linux/Mac) или закройте окна (Windows)

---

### ✅ Вариант 2: Запуск сервисов отдельно

#### 2.1. Только Broadcaster Service (рассылка)

**Linux/Mac:**
```bash
# Способ 1: Через скрипт
bash scripts/start_broadcaster.sh

# Способ 2: Напрямую
python broadcaster/main.py

# Способ 3: Через обертку (обратная совместимость)
python main.py
```

**Windows:**
```cmd
REM Способ 1: Через скрипт
scripts\start_broadcaster.bat

REM Способ 2: Напрямую
python broadcaster\main.py

REM Способ 3: Через обертку
python main.py
```

#### 2.2. Только Google Sheets Updater (обновление)

**Linux/Mac:**
```bash
# Способ 1: Через скрипт
bash scripts/start_updater.sh

# Способ 2: Напрямую
python google_sheets_updater/main.py
```

**Windows:**
```cmd
REM Способ 1: Через скрипт
scripts\start_updater.bat

REM Способ 2: Напрямую
python google_sheets_updater\main.py
```

---

### ✅ Вариант 3: Запуск в отдельных терминалах (для разработки)

Откройте **2 терминала** и запустите каждый сервис отдельно:

#### Терминал 1 - Broadcaster Service:

```bash
cd /path/to/SendMessageBot
python broadcaster/main.py
```

#### Терминал 2 - Google Sheets Updater:

```bash
cd /path/to/SendMessageBot
python google_sheets_updater/main.py
```

**Преимущества:**
- Видны логи обоих сервисов в реальном времени
- Легче отлаживать
- Можно остановить каждый сервис независимо (`Ctrl+C`)

---

## 🛑 Остановка сервисов

### Остановка всех сервисов:

**Linux/Mac:**
```bash
bash scripts/stop_all.sh
```

**Windows:**
```cmd
scripts\stop_all.bat
```

### Остановка вручную:

**Linux/Mac:**
```bash
# Найти процессы
ps aux | grep "broadcaster/main.py"
ps aux | grep "google_sheets_updater/main.py"

# Остановить по PID
kill <PID>

# Или принудительно
kill -9 <PID>
```

**Windows:**
```cmd
REM Найти процессы
tasklist | findstr "python.exe"

REM Остановить по PID
taskkill /PID <PID> /F

REM Или по имени окна
taskkill /FI "WINDOWTITLE eq Broadcaster Service*" /F
taskkill /FI "WINDOWTITLE eq Google Sheets Updater*" /F
```

---

## 📝 Просмотр логов

### В реальном времени:

**Linux/Mac:**
```bash
# Логи Broadcaster Service
tail -f logs/broadcaster.log
# или
tail -f bot.log

# Логи Google Sheets Updater
tail -f logs/updater.log

# Оба лога одновременно
tail -f logs/broadcaster.log logs/updater.log
```

**Windows:**
```cmd
REM Логи Broadcaster Service
type logs\broadcaster.log
REM или в PowerShell
Get-Content logs\broadcaster.log -Wait

REM Логи Google Sheets Updater
Get-Content logs\updater.log -Wait
```

### Последние строки:

**Linux/Mac:**
```bash
# Последние 50 строк
tail -n 50 logs/broadcaster.log

# Поиск ошибок
grep -i error logs/broadcaster.log
grep -i error logs/updater.log
```

**Windows:**
```cmd
REM Последние строки
powershell "Get-Content logs\broadcaster.log -Tail 50"

REM Поиск ошибок
findstr /i "error" logs\broadcaster.log
```

---

## ✅ Проверка работы

### 1. Проверка Broadcaster Service:

После запуска должны появиться логи:
```
✅ AAA_PRICE_Broadcaster подключен: ...
✅ GUS_PRICE_Broadcaster подключен: ...
✅ AAA_ADS_Broadcaster подключен: ...
...
🔄 [AAA_PRICE_Broadcaster] Начинаем цикл рассылки...
```

### 2. Проверка Google Sheets Updater:

После запуска должны появиться логи:
```
✅ Google Sheets Updater запущен
⏰ Следующее обновление: 2025-12-13 11:05:00 MSK
```

### 3. Проверка процессов:

**Linux/Mac:**
```bash
# Проверка запущенных процессов
ps aux | grep python | grep -E "(broadcaster|updater)"
```

**Windows:**
```cmd
tasklist | findstr "python.exe"
```

---

## 🔧 Решение проблем

### Проблема: "ModuleNotFoundError"

**Решение:**
```bash
# Установить зависимости
pip install -r requirements.txt

# Или в виртуальном окружении
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Проблема: "database is locked"

**Решение:**
- Убедитесь, что не запущено несколько экземпляров программы
- Проверьте, что файлы сессий не используются другим процессом
- Подождите несколько секунд и попробуйте снова

### Проблема: "Файл сессии не найден"

**Решение:**
- При первом запуске потребуется авторизация
- Следуйте инструкциям в консоли
- Введите код из Telegram

### Проблема: Broadcaster'ы не начинают отправку

**Решение:**
- Проверьте логи на наличие ошибок
- Убедитесь, что не включен тихий час
- Проверьте настройки времени старта
- См. [BROADCASTER_CONNECTION_FIX.md](BROADCASTER_CONNECTION_FIX.md)

---

## 📊 Что делает каждый сервис

### Broadcaster Service (`broadcaster/main.py`)

- ✅ Отправляет сообщения в Telegram чаты
- ✅ 6 broadcaster'ов работают параллельно:
  - AAA_PRICE (прайсы AAA)
  - GUS_PRICE (прайсы GUS)
  - AAA_ADS (реклама AAA)
  - GUS_ADS (реклама GUS)
  - GUS_B2C (розничные сообщения)
  - GUS_B2C_MIDSLOW (розничные сообщения медленные)
- ✅ Автоматически обновляет сообщения из Google Sheets
- ✅ Отправляет отчеты в Telegram каждые 3 часа

### Google Sheets Updater (`google_sheets_updater/main.py`)

- ✅ Обновляет Google Sheets из Telegram канала
- ✅ Работает по расписанию (11:05 MSK ежедневно)
- ✅ Получает последние 3 сообщения из канала
- ✅ Записывает в первые 3 ячейки таблиц AAA и GUS

---

## 🎯 Рекомендуемый порядок запуска

1. **Проверьте конфигурацию:**
   ```bash
   # Убедитесь, что .env файл существует
   cat .env  # Linux/Mac
   type .env  # Windows
   ```

2. **Запустите оба сервиса:**
   ```bash
   # Linux/Mac
   bash scripts/start_all.sh
   
   # Windows
   scripts\start_all.bat
   ```

3. **Проверьте логи:**
   ```bash
   # Подождите 10-20 секунд и проверьте логи
   tail -f logs/broadcaster.log
   ```

4. **Убедитесь, что все работает:**
   - Broadcaster'ы подключились
   - Начались циклы рассылки
   - Google Sheets Updater запущен

---

## 📚 Дополнительная документация

- [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) - архитектура микросервисов
- [RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md) - подробное руководство по запуску
- [BROADCASTER_CONNECTION_FIX.md](BROADCASTER_CONNECTION_FIX.md) - решение проблем с подключением
- [README.md](../README.md) - общая документация проекта

---

## 💡 Полезные команды

### Проверка статуса:

```bash
# Linux/Mac
ps aux | grep python | grep -E "(broadcaster|updater)"

# Windows
tasklist | findstr "python.exe"
```

### Очистка логов:

```bash
# Linux/Mac
> logs/broadcaster.log
> logs/updater.log

# Windows
type nul > logs\broadcaster.log
type nul > logs\updater.log
```

### Перезапуск сервисов:

```bash
# Linux/Mac
bash scripts/stop_all.sh
sleep 2
bash scripts/start_all.sh

# Windows
scripts\stop_all.bat
timeout /t 2
scripts\start_all.bat
```

---

**Дата создания:** 2025-12-13  
**Версия:** 1.0

