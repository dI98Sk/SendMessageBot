# 🤖 SendMessageBot

Проект состоит из двух независимых микросервисов:

1. **Broadcaster Service** - автоматизированная система рассылки сообщений в Telegram
2. **Google Sheets Updater Service** - автоматическое обновление Google таблиц

**Версия:** 2.1 Microservices Architecture  
**Статус:** ✅ Готово к использованию  
**Дата:** 2025-12-13

---

## 🚀 Быстрый старт

### Архитектура микросервисов

Проект состоит из двух независимых сервисов:

- **Broadcaster Service** (`broadcaster/main.py`) - рассылка сообщений в Telegram
- **Google Sheets Updater Service** (`google_sheets_updater/main.py`) - обновление таблиц

**Подробнее:** [docs/MICROSERVICES_ARCHITECTURE.md](docs/MICROSERVICES_ARCHITECTURE.md)

### Запуск Broadcaster Service

#### Windows (автоматический)

```cmd
# Запустите скрипт для первоначальной настройки
scripts\start_windows.bat
```

Скрипт автоматически выполнит:
1. ✅ Создание виртуального окружения
2. ✅ Активацию venv
3. ✅ Установку зависимостей
4. ✅ Настройку Telegram аккаунтов
5. ✅ Запуск broadcaster service

**Подробнее:** [scripts/README_START_WINDOWS.md](scripts/README_START_WINDOWS.md)

#### Linux/Mac (ручной)

```bash
# 1. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить .env файл (см. .env.example)

# 4. Настроить аккаунты
python scripts/setup_accounts.py

# 5. Запустить broadcaster service
python broadcaster/main.py
# или
scripts/start_broadcaster.sh
```

**Подробнее:** [broadcaster/README.md](broadcaster/README.md)

### Запуск Google Sheets Updater Service

```bash
# Windows
scripts\start_updater.bat

# Linux/Mac
scripts/start_updater.sh

# Или напрямую
python google_sheets_updater/main.py
```

**Подробнее:** [google_sheets_updater/README.md](google_sheets_updater/README.md)

### Запуск обоих сервисов одновременно

```bash
# Windows
scripts\start_all.bat

# Linux/Mac
scripts/start_all.sh

# Остановка всех сервисов
scripts\stop_all.bat    # Windows
scripts/stop_all.sh     # Linux/Mac
```

**Подробнее:** 
- [docs/QUICK_START_GUIDE.md](docs/QUICK_START_GUIDE.md) ⭐⭐ - **БЫСТРЫЙ СТАРТ** с командами
- [QUICK_COMMANDS.md](QUICK_COMMANDS.md) - краткая шпаргалка
- [docs/RUNNING_MICROSERVICES.md](docs/RUNNING_MICROSERVICES.md) - подробное руководство

---

## 📊 Возможности

### 6 Broadcaster'ов
- **AAA_PRICE** - Прайсы AAA (27 чатов, цикл 30 мин) - ОПТОВЫЙ
- **GUS_PRICE** - Прайсы GUS (27 чатов, цикл 30 мин) - РОЗНИЧНЫЙ
- **AAA_ADS** - Реклама AAA (16 чатов, цикл 50 мин) - ОПТОВЫЙ
- **GUS_ADS** - Реклама GUS (16 чатов, цикл 50 мин) - РОЗНИЧНЫЙ
- **GUS_B2C** - Розничные сообщения (73 чата, цикл 1.5 часа) - РОЗНИЧНЫЙ
- **GUS_B2C_MIDSLOW** - Розничные сообщения MIDSLOW (52 чата, цикл 2.67 часа) - РОЗНИЧНЫЙ ⭐ НОВЫЙ

### Автоматизация
- 🔄 **Автообновление сообщений** из Google Sheets (настраиваемый интервал)
- 📊 **Отчеты в Telegram** каждые 3 часа
- 🛡️ **Система координации** - предотвращение конфликтов между broadcaster'ами
- ⏰ **Расписание работы** - настраиваемое время запуска и тихий час

### Безопасность и надежность
- ✅ Уникальные файлы сессий для каждого broadcaster'а
- ✅ Адаптивные задержки при ошибках
- ✅ Очередь отложенных сообщений (до 5 попыток)
- ✅ Защита от FloodWait
- ✅ Глобальная координация отправок (предотвращение конфликтов)
- ✅ Валидация chat_id при загрузке
- ✅ Детальное логирование ошибок
- ✅ Автоматическая обработка ConnectionError

---

## 📁 Структура проекта (Микросервисная архитектура)

```
SendMessageBot/
├── broadcaster/                    # Broadcaster Service
│   ├── main.py                    # Точка входа
│   ├── core/                      # Ядро broadcaster'ов
│   ├── config/                    # Конфигурация
│   ├── monitoring/                # Мониторинг и отчеты
│   └── utils/                     # Утилиты
│
├── google_sheets_updater/          # Google Sheets Updater Service
│   ├── main.py                    # Точка входа
│   ├── updater/                   # Логика обновления
│   ├── config/                    # Конфигурация
│   └── utils/                     # Утилиты
│
├── shared/                         # Общие компоненты
│   └── google_sheets/              # Google Sheets клиент
│
├── scripts/                        # Скрипты запуска
├── sessions/                       # Файлы сессий Telegram
├── logs/                           # Логи
├── main.py                         # Обертка для обратной совместимости
└── requirements.txt                # Зависимости
```

**Подробнее:** [docs/MICROSERVICES_ARCHITECTURE.md](docs/MICROSERVICES_ARCHITECTURE.md)

## 📁 Старая структура проекта (для справки)

```
SendMessageBot/
├── broadcaster/            # Broadcaster Service (микросервис)
│   ├── main.py            # Точка входа
│   ├── core/              # Ядро broadcaster'ов
│   ├── config/            # Конфигурация
│   ├── monitoring/       # Мониторинг и отчеты
│   └── utils/             # Утилиты
│
├── google_sheets_updater/  # Google Sheets Updater Service (микросервис)
│   ├── main.py            # Точка входа
│   ├── updater/           # Логика обновления
│   ├── config/            # Конфигурация
│   └── utils/             # Утилиты
│
├── shared/                 # Общие компоненты
│   └── google_sheets/     # Google Sheets клиент
│       ├── client.py     # Базовый клиент (для записи)
│       └── fetcher.py    # Для чтения (broadcaster)
│
├── scripts/                # Скрипты запуска
│   ├── start_broadcaster.sh/bat
│   ├── start_updater.sh/bat
│   └── start_all.sh/bat
│
├── docs/                   # Документация
└── requirements.txt       # Общие зависимости
```
│   ├── google_sheets.py  # Работа с Google Sheets
│   ├── chat_validator.py # Валидация chat_id
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
│   ├── acc1_price.session # GUS PRICE (Яблочный Гусь)
│   ├── acc1_ads.session   # GUS ADS (Яблочный Гусь)
│   ├── acc1_b2c.session   # GUS B2C (Яблочный Гусь)
│   ├── acc1_b2c_midslow.session # GUS B2C MIDSLOW (Яблочный Гусь) ⭐ НОВЫЙ
│   ├── acc2_price.session # AAA PRICE (Анна Макарова)
│   └── acc2_ads.session   # AAA ADS (Анна Макарова)
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

**Автоматически (рекомендуется):**
```bash
python scripts/setup_accounts.py
```

**Вручную:**
```bash
# Создать уникальные сессии из существующих:
cd sessions
cp acc1.session acc1_price.session
cp acc1.session acc1_ads.session
cp acc1.session acc1_b2c.session  # ⭐ НОВЫЙ
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

**📖 [Полный индекс документации](docs/INDEX.md)** - структурированная навигация по всей документации

### 🚀 Быстрый старт
- **[docs/setup/START_HERE.md](docs/setup/START_HERE.md)** ⭐ - начните отсюда
- **[docs/setup/QUICK_START.md](docs/setup/QUICK_START.md)** - быстрый старт
- **[docs/DEPLOYMENT_INSTRUCTIONS.md](docs/DEPLOYMENT_INSTRUCTIONS.md)** - деплой в продакшен

### 📘 Руководства
- **[docs/ADD_NEW_BROADCASTER.md](docs/ADD_NEW_BROADCASTER.md)** - как добавить новый broadcaster
- **[docs/BROADCASTER_COORDINATION.md](docs/BROADCASTER_COORDINATION.md)** - система координации
- **[docs/guides/BROADCASTERS_SETUP.md](docs/guides/BROADCASTERS_SETUP.md)** - настройка broadcaster'ов
- **[docs/guides/AUTO_UPDATE_GUIDE.md](docs/guides/AUTO_UPDATE_GUIDE.md)** - автообновление
- **[docs/guides/HOW_TO_USE_REPORTS.md](docs/guides/HOW_TO_USE_REPORTS.md)** - система отчетов
- **[docs/guides/CYCLE_DELAYS_GUIDE.md](docs/guides/CYCLE_DELAYS_GUIDE.md)** - задержки между циклами

### 🔧 Решение проблем
- **[docs/ERROR_ANALYSIS.md](docs/ERROR_ANALYSIS.md)** - анализ ошибок и рекомендации
- **[docs/INVALID_CHAT_ID_FIX.md](docs/INVALID_CHAT_ID_FIX.md)** - решение InvalidChatId
- **[docs/WINDOWS_LOG_ROTATION_FIX.md](docs/WINDOWS_LOG_ROTATION_FIX.md)** - ротация логов на Windows
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - общее руководство
- **[docs/troubleshooting/SERVER_DIAGNOSTIC.md](docs/troubleshooting/SERVER_DIAGNOSTIC.md)** - диагностика сервера
- **[docs/troubleshooting/SESSION_FILES_FIX.md](docs/troubleshooting/SESSION_FILES_FIX.md)** - проблемы с сессиями

---

## 🔄 Обновление сообщений

### Автоматически (в main.py)
Сообщения автоматически обновляются каждый час из Google Sheets.

### Вручную
```bash
python scripts/update_messages.py
```

Обновляет все типы сообщений:
- ✅ AAA прайсы
- ✅ GUS прайсы
- ✅ AAA реклама
- ✅ GUS реклама
- ✅ B2C сообщения (если настроено)

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

| Broadcaster | Аккаунт | Тип | Чаты | Цикл | Задержка | Сообщений |
|-------------|---------|-----|------|------|----------|-----------|
| AAA_PRICE | acc2 | ОПТОВЫЙ | 27 | 30 мин | 60с | ~30 |
| GUS_PRICE | acc1 | РОЗНИЧНЫЙ | 27 | 30 мин | 60с | ~30 |
| AAA_ADS | acc2 | ОПТОВЫЙ | 16 | 50 мин | 60с | ~20 |
| GUS_ADS | acc1 | РОЗНИЧНЫЙ | 16 | 50 мин | 60с | ~20 |
| GUS_B2C | acc1 | РОЗНИЧНЫЙ | 73 | 1.5 часа | 60с | ~29 |
| **GUS_B2C_MIDSLOW** | **acc1** | **РОЗНИЧНЫЙ** | **52** | **2.67 часа** | **60с** | **~29** ⭐ |

**Итого:** 6 broadcaster'ов, ~178.6 циклов в сутки

### Особенности
- ✅ **Система координации** - предотвращение конфликтов между broadcaster'ами
- ✅ **Индивидуальные задержки** - каждый broadcaster может иметь свои настройки
- ✅ **Смещение времени старта** - распределение нагрузки во времени

---

## 🆘 Проблемы?

### Частые проблемы
- **InvalidChatId ошибки** → [docs/INVALID_CHAT_ID_FIX.md](docs/INVALID_CHAT_ID_FIX.md)
- **Ошибка ротации логов на Windows** → [docs/WINDOWS_LOG_ROTATION_FIX.md](docs/WINDOWS_LOG_ROTATION_FIX.md)
- **Много ошибок в отчетах** → [docs/ERROR_ANALYSIS.md](docs/ERROR_ANALYSIS.md)
- **Проблемы с сессиями** → [docs/troubleshooting/SESSION_FILES_FIX.md](docs/troubleshooting/SESSION_FILES_FIX.md)

**Полный список:** [docs/INDEX.md](docs/INDEX.md) → Решение проблем

---

## 📝 Лицензия

Приватный проект

---

**Made with ❤️ for efficient Telegram broadcasting**
