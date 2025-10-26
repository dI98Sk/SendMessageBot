# 📋 ВСЕ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ДЛЯ SENDMESSAGEBOT

## 🔧 **ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ**

### **Telegram API (ОБЯЗАТЕЛЬНО)**
```bash
API_ID=12345678                    # ID вашего приложения Telegram
API_HASH=abcdef1234567890...       # Hash вашего приложения Telegram
SESSION_NAME=production_session    # Имя файла сессии
```

## 📱 **TELEGRAM НАСТРОЙКИ**

### **Основные настройки**
```bash
PHONE=+1234567890                  # Номер телефона для авторизации
```

### **Прокси (опционально)**
```bash
PROXY_ENABLED=false                # Включить прокси (true/false)
PROXY_ADDR=proxy.example.com       # Адрес прокси сервера
PROXY_PORT=8080                    # Порт прокси сервера
PROXY_SECRET=your_proxy_secret     # Секрет прокси
PROXY_PROTOCOL=mtproto             # Протокол прокси
```

## 📊 **НАСТРОЙКИ РАССЫЛКИ**

### **Производительность**
```bash
DELAY_BETWEEN_CHATS=5              # Задержка между чатами (секунды)
CYCLE_DELAY=900                    # Задержка между циклами (секунды)
MAX_RETRIES=3                      # Максимум повторных попыток
RETRY_DELAY=60                     # Задержка при повторе (секунды)
```

### **Планирование**
```bash
START_TIME_HOUR=6                  # Час начала работы
ENABLE_SCHEDULING=true             # Включить планирование
```

## 📋 **GOOGLE SHEETS ИНТЕГРАЦИЯ**

```bash
GOOGLE_CREDENTIALS_FILE=credentials.json
SHEET_URL_B2B=https://docs.google.com/spreadsheets/d/B2B_SHEET_ID/edit
SHEET_URL_B2C=https://docs.google.com/spreadsheets/d/B2C_SHEET_ID/edit
GOOGLE_UPDATE_INTERVAL=3600        # Интервал обновления (секунды)
```

## 📈 **СИСТЕМА ОТЧЕТОВ**

```bash
ENABLE_REPORTS=true                # Включить отчеты
REPORTS_BOT_TOKEN=1234567890:ABC... # Токен бота для отчетов
REPORTS_CHANNEL_ID=@your_channel   # ID канала для отчетов
REPORT_INTERVAL_HOURS=12           # Интервал отчетов (часы)
REPORTS_TIMEZONE=Europe/Moscow     # Часовой пояс
```

## 🔔 **СИСТЕМА УВЕДОМЛЕНИЙ**

### **Telegram уведомления**
```bash
ENABLE_TELEGRAM_NOTIFICATIONS=true # Включить Telegram уведомления
ADMIN_TELEGRAM_ID=123456789        # ID администратора
NOTIFICATION_LEVEL=INFO            # Уровень уведомлений
```

### **Webhook уведомления**
```bash
ENABLE_WEBHOOK_NOTIFICATIONS=false # Включить Webhook уведомления
WEBHOOK_URL=https://your-webhook.com # URL для webhook
```

## 📝 **ЛОГИРОВАНИЕ**

```bash
LOG_LEVEL=INFO                     # Уровень логов (DEBUG/INFO/WARNING/ERROR/CRITICAL)
LOG_FILE=bot.log                   # Файл логов
LOG_MAX_SIZE=10485760              # Максимальный размер файла (байты)
LOG_BACKUP_COUNT=5                 # Количество резервных копий
LOG_CONSOLE=false                  # Вывод в консоль
```

## 🚀 **МИНИМАЛЬНЫЙ .env ДЛЯ БАЗОВОЙ РАБОТЫ**

```bash
# Обязательные переменные
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
SESSION_NAME=production_session

# Для уведомлений
ENABLE_TELEGRAM_NOTIFICATIONS=true
ADMIN_TELEGRAM_ID=123456789

# Для отчетов
ENABLE_REPORTS=true
REPORTS_BOT_TOKEN=1234567890:ABCDEFghijklmnopqrstuvwxyz1234567890
REPORTS_CHANNEL_ID=@your_reports_channel
```

## 🔍 **КАК ПОЛУЧИТЬ ЗНАЧЕНИЯ**

### **API_ID и API_HASH:**
1. Перейдите на https://my.telegram.org/apps
2. Войдите с номером телефона
3. Создайте приложение
4. Скопируйте api_id и api_hash

### **ADMIN_TELEGRAM_ID:**
1. Напишите @userinfobot в Telegram
2. Он пришлет ваш ID

### **REPORTS_BOT_TOKEN:**
1. Напишите @BotFather
2. Создайте бота командой `/newbot`
3. Скопируйте токен

### **REPORTS_CHANNEL_ID:**
1. Создайте канал в Telegram
2. Добавьте бота как администратора
3. Скопируйте ID канала

## ✅ **ПРОВЕРКА НАСТРОЕК**

После создания `.env` файла:
```bash
# Тест уведомлений
python test_notifications.py

# Тест отчетов  
python manage_reports.py

# Запуск бота
python main_improved.py
```

