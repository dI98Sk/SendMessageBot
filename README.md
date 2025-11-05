# 🤖 SendMessageBot

Автоматизированная система рассылки сообщений в Telegram с поддержкой множественных broadcaster'ов, автообновлением из Google Sheets и отчетами.

**Версия:** 1.0 Production Ready  
**Статус:** ✅ Готово к использованию  
**Дата:** 2025-11-04

---

## 🚀 Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Настроить .env файл (см. .env.example)

# 3. Обновить сообщения из Google Sheets
python scripts/update_messages.py

# 4. Запустить бот
python main.py
```

---

## 📊 Возможности

### 4 Broadcaster'а
- **AAA_PRICE** - Прайсы AAA (22 чата, цикл 20 мин)
- **GUS_PRICE** - Прайсы GUS (22 чата, цикл 20 мин)
- **AAA_ADS** - Реклама AAA (11 чатов, цикл 1 час)
- **GUS_ADS** - Реклама GUS (11 чатов, цикл 1 час)

### Автоматизация
- 🔄 **Автообновление сообщений** из Google Sheets каждый час
- 📊 **Отчеты в Telegram** каждые 3 часа
- 🛡️ **Защита от блокировки** - умные задержки и очереди
- ⏰ **Расписание работы** - настраиваемое время запуска и тихий час

### Безопасность
- ✅ Уникальные файлы сессий для каждого broadcaster'а
- ✅ Адаптивные задержки при ошибках
- ✅ Очередь отложенных сообщений (до 5 попыток)
- ✅ Защита от FloodWait

---

## 📁 Структура проекта

```
SendMessageBot/
├── main.py                 # Production версия (PRICE_TARGET, ADS_TARGET)
├── main_test.py           # Тестовая версия (TEST чаты)
│
├── config/                 # Конфигурация
│   ├── settings.py        # Основные настройки
│   ├── targets.py         # Целевые чаты
│   ├── messages_aaa.py    # Прайсы AAA (автообновляется)
│   ├── messages_gus.py    # Прайсы GUS (автообновляется)
│   ├── messages_aaa_ads.py # Реклама AAA (автообновляется)
│   └── messages_gus_ads.py # Реклама GUS (автообновляется)
│
├── core/                   # Ядро приложения
│   ├── broadcaster.py     # Broadcaster с индивидуальными задержками
│   ├── queue.py          # Система очередей
│   └── ...
│
├── utils/                  # Утилиты
│   ├── auto_updater.py   # Автообновление сообщений
│   ├── google_sheets.py  # Работа с Google Sheets
│   └── ...
│
├── monitoring/             # Мониторинг
│   ├── reports.py        # Система отчетов в Telegram
│   ├── metrics.py        # Сбор метрик
│   └── ...
│
├── scripts/                # Скрипты
│   ├── update_messages.py # Обновить ВСЕ сообщения
│   └── ...
│
├── sessions/               # Сессии Telegram
│   ├── acc1_price.session # AAA PRICE
│   ├── acc2_price.session # GUS PRICE
│   ├── acc1_ads.session   # GUS ADS
│   └── acc2_ads.session   # AAA ADS
│
├── docs/                   # Документация
│   ├── setup/             # Настройка и установка
│   ├── guides/            # Руководства
│   ├── troubleshooting/   # Решение проблем
│   └── *.md              # Итоговые документы
│
└── tests/                  # Тесты
    ├── test_new_broadcasters.py
    ├── test_reports.py
    └── ...
```

---

## ⚙️ Настройка

### 1. Переменные окружения (.env)

```bash
# Telegram API
API_ID=your_api_id
API_HASH=your_api_hash

# Google Sheets (все 4 обязательны)
BUY_SELL_PRICE_AAA_SHEET_URL=https://docs.google.com/...
BUY_SELL_PRICE_GUS_SHEET_URL=https://docs.google.com/...
ADS_AAA_SHEET_URL=https://docs.google.com/...
ADS_GUS_SHEET_URL=https://docs.google.com/...
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_UPDATE_INTERVAL=3600  # 1 час

# Отчеты
ENABLE_REPORTS=true
REPORTS_BOT_TOKEN=your_bot_token
REPORTS_CHANNEL_ID=your_channel_id
REPORT_INTERVAL_HOURS=3.0

# Расписание
ENABLE_SCHEDULING=true
START_TIME_HOUR=6
ENABLE_QUIET_HOURS=true
QUIET_HOUR_START=0
QUIET_HOUR_END=7

# Задержки
DELAY_BETWEEN_CHATS=40
MIN_INTERVAL_PER_CHAT=600  # 10 минут
```

### 2. Файлы сессий

```bash
# Создать уникальные сессии из существующих:
cd sessions
cp acc1.session acc1_price.session
cp acc1.session acc1_ads.session
cp acc2.session acc2_price.session
cp acc2.session acc2_ads.session
```

---

## 🧪 Тестирование

```bash
# Проверка конфигурации
python test_new_broadcasters.py

# Тест отчетов
python test_reports.py

# Тест автообновления
python test_auto_update.py

# Полный тест на тестовых чатах
python main_test.py
```

---

## 📚 Документация

### Начало работы
- **[docs/setup/START_HERE.md](docs/setup/START_HERE.md)** ⭐ - начните отсюда
- **[docs/setup/QUICK_START.md](docs/setup/QUICK_START.md)** - быстрый старт
- **[docs/setup/INDEX.md](docs/setup/INDEX.md)** - индекс всей документации

### Руководства
- **[docs/guides/BROADCASTERS_SETUP.md](docs/guides/BROADCASTERS_SETUP.md)** - настройка broadcaster'ов
- **[docs/guides/AUTO_UPDATE_GUIDE.md](docs/guides/AUTO_UPDATE_GUIDE.md)** - автообновление
- **[docs/guides/HOW_TO_USE_REPORTS.md](docs/guides/HOW_TO_USE_REPORTS.md)** - система отчетов
- **[docs/guides/CYCLE_DELAYS_GUIDE.md](docs/guides/CYCLE_DELAYS_GUIDE.md)** - задержки между циклами

### Решение проблем
- **[docs/troubleshooting/SERVER_DIAGNOSTIC.md](docs/troubleshooting/SERVER_DIAGNOSTIC.md)** - диагностика
- **[docs/troubleshooting/SESSION_FILES_FIX.md](docs/troubleshooting/SESSION_FILES_FIX.md)** - проблемы с сессиями
- **[docs/troubleshooting/SYNC_TO_SERVER.md](docs/troubleshooting/SYNC_TO_SERVER.md)** - синхронизация с сервером

### Итоговые документы
- **[docs/COMPLETE_SUMMARY.md](docs/COMPLETE_SUMMARY.md)** - полная сводка
- **[docs/FINAL_STATUS.md](docs/FINAL_STATUS.md)** - финальный статус
- **[docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md)** - чек-лист

---

## 🔄 Обновление сообщений

### Автоматически (в main.py)
Сообщения автоматически обновляются каждый час из Google Sheets.

### Вручную
```bash
python scripts/update_messages.py
```

Обновляет все 4 типа:
- ✅ AAA прайсы
- ✅ GUS прайсы
- ✅ AAA реклама
- ✅ GUS реклама

---

## 📊 Мониторинг

### Логи
```bash
tail -f bot.log
```

### Отчеты
Автоматически отправляются в Telegram каждые 3 часа.

### Статистика
```bash
python show_stats.py
```

---

## 🎯 Broadcaster'ы

| Broadcaster | Аккаунт | Чаты | Цикл | Сообщения |
|-------------|---------|------|------|-----------|
| AAA_PRICE | acc1 | 22 | 20 мин | 13 |
| GUS_PRICE | acc2 | 22 | 20 мин | 13 |
| AAA_ADS | acc2 | 11 | 1 час | 21 |
| GUS_ADS | acc1 | 11 | 1 час | 16 |

**Итого:** 63 сообщения в 33 чата

---

## 🆘 Проблемы?

Смотрите [docs/troubleshooting/](docs/troubleshooting/) для решения типичных проблем.

---

## 📝 Лицензия

Приватный проект

---

**Made with ❤️ for efficient Telegram broadcasting**
