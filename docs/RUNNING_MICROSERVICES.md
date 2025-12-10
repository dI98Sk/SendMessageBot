# 🚀 Запуск микросервисов

**Дата:** 2025-12-10  
**Версия:** 2.1

---

## 📋 Варианты запуска

### 1. Запуск обоих сервисов одновременно

#### Linux/Mac

```bash
# Запуск обоих сервисов
scripts/start_all.sh

# Остановка всех сервисов
scripts/stop_all.sh
```

#### Windows

```cmd
REM Запуск обоих сервисов
scripts\start_all.bat

REM Остановка всех сервисов
scripts\stop_all.bat
```

**Особенности:**
- Оба сервиса запускаются в фоне
- Логи сохраняются в отдельные файлы
- Можно остановить все сервисы одной командой

---

### 2. Запуск сервисов отдельно

#### Broadcaster Service

```bash
# Linux/Mac
python main.py

# Windows
python main.py
```

#### Google Sheets Updater Service

```bash
# Linux/Mac
python google_sheets_updater/main.py
# или
scripts/start_updater.sh

# Windows
python google_sheets_updater\main.py
# или
scripts\start_updater.bat
```

---

### 3. Запуск в отдельных терминалах (рекомендуется для разработки)

#### Терминал 1 - Broadcaster Service

```bash
python main.py
```

#### Терминал 2 - Google Sheets Updater

```bash
python google_sheets_updater/main.py
```

**Преимущества:**
- Видны логи обоих сервисов в реальном времени
- Легче отлаживать
- Можно остановить каждый сервис независимо

---

## 📝 Логирование

### Расположение логов

- **Broadcaster Service:** `bot.log` или `logs/broadcaster.log`
- **Google Sheets Updater:** `logs/updater.log`

### Просмотр логов

```bash
# Просмотр логов Broadcaster в реальном времени
tail -f bot.log
# или
tail -f logs/broadcaster.log

# Просмотр логов Updater в реальном времени
tail -f logs/updater.log

# Просмотр последних 100 строк
tail -n 100 logs/broadcaster.log
tail -n 100 logs/updater.log
```

---

## ⚙️ Конфигурация

### Broadcaster Service

Конфигурация в `.env` или переменных окружения:

```env
# Telegram
API_ID=...
API_HASH=...

# Google Sheets (для чтения)
BUY_SELL_PRICE_AAA_SHEET_URL=...
BUY_SELL_PRICE_GUS_SHEET_URL=...
ADS_AAA_SHEET_URL=...
ADS_GUS_SHEET_URL=...
```

### Google Sheets Updater Service

Конфигурация в `.env.updater` или переменных окружения:

```env
# Google Sheets
GOOGLE_CREDENTIALS_FILE=credentials.json

# Таблицы для обновления
BUY_SELL_PRICE_AAA_SHEET_URL=...
BUY_SELL_PRICE_GUS_SHEET_URL=...
ADS_AAA_SHEET_URL=...
ADS_GUS_SHEET_URL=...

# Интервал обновления (секунды)
UPDATER_UPDATE_INTERVAL=3600

# Логирование
UPDATER_LOG_LEVEL=INFO
UPDATER_LOG_FILE=logs/updater.log
```

---

## 🔄 Как работают сервисы вместе

### Независимая работа

1. **Broadcaster Service:**
   - Читает данные из Google таблиц
   - Отправляет сообщения в Telegram
   - Не зависит от Updater Service

2. **Google Sheets Updater Service:**
   - Обновляет данные в Google таблицах
   - Не зависит от Broadcaster Service
   - Работает по расписанию

### Взаимодействие через Google Sheets

```
┌─────────────────────┐
│  Data Sources       │
│  (API, DB, Files)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Sheets      │
│  Updater Service    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Sheets      │
│  (Таблицы)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Broadcaster        │
│  Service            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Telegram           │
│  (Сообщения)        │
└─────────────────────┘
```

**Важно:** Сервисы не обмениваются данными напрямую, только через Google таблицы.

---

## 🛠️ Мониторинг

### Проверка статуса процессов

#### Linux/Mac

```bash
# Проверка запущенных процессов
ps aux | grep "python.*main.py"
ps aux | grep "google_sheets_updater"

# Или через pgrep
pgrep -f "python.*main.py"
pgrep -f "google_sheets_updater"
```

#### Windows

```cmd
REM Проверка процессов
tasklist | findstr python
```

### Проверка логов на ошибки

```bash
# Ошибки в Broadcaster
grep -i error logs/broadcaster.log | tail -20

# Ошибки в Updater
grep -i error logs/updater.log | tail -20
```

---

## 🚨 Решение проблем

### Сервисы не запускаются

1. **Проверьте виртуальное окружение:**
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

2. **Проверьте зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Проверьте конфигурацию:**
   - `.env` для Broadcaster
   - `.env.updater` для Updater

### Сервисы конфликтуют

- Убедитесь, что используются разные файлы логов
- Проверьте, что нет конфликтов в конфигурации
- Убедитесь, что оба сервиса используют один и тот же `credentials.json`

### Один сервис не работает

- Проверьте логи конкретного сервиса
- Убедитесь, что конфигурация правильная
- Проверьте доступ к Google Sheets API

---

## 📊 Рекомендации для продакшена

### 1. Использование systemd (Linux)

Создайте сервисы systemd для автоматического запуска:

```ini
# /etc/systemd/system/broadcaster.service
[Unit]
Description=Broadcaster Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/SendMessageBot
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Использование supervisor

Настройте supervisor для управления обоими сервисами:

```ini
[program:broadcaster]
command=/path/to/venv/bin/python main.py
directory=/path/to/SendMessageBot
autostart=true
autorestart=true

[program:updater]
command=/path/to/venv/bin/python google_sheets_updater/main.py
directory=/path/to/SendMessageBot
autostart=true
autorestart=true
```

### 3. Docker Compose (опционально)

Можно создать `docker-compose.yml` для запуска обоих сервисов в контейнерах.

---

## 🔗 Связанные документы

- [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) - архитектура микросервисов
- [google_sheets_updater/README.md](../google_sheets_updater/README.md) - документация Updater Service
- [README.md](../README.md) - общая документация проекта

---

**Дата создания:** 2025-12-10  
**Версия:** 1.0

