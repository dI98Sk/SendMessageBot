# 🔄 Миграция на микросервисную архитектуру

**Дата:** 2025-12-10  
**Версия:** 2.1

---

## ✅ Выполненная реорганизация

Проект реорганизован в микросервисную архитектуру:

### Новая структура:

```
SendMessageBot/
├── broadcaster/                    # Broadcaster Service
│   ├── main.py                    # Точка входа
│   ├── core/                      # Ядро broadcaster'ов
│   │   ├── broadcaster.py
│   │   ├── coordinator.py
│   │   ├── exceptions.py
│   │   ├── queue.py
│   │   └── retry.py
│   ├── config/                     # Конфигурация
│   │   ├── settings.py
│   │   ├── targets.py
│   │   ├── message_updater.py
│   │   └── messages_*.py
│   ├── monitoring/                 # Мониторинг и отчеты
│   │   ├── metrics.py
│   │   ├── notifications.py
│   │   └── reports.py
│   └── utils/                      # Утилиты
│       ├── auto_updater.py
│       ├── chat_validator.py
│       ├── logger.py
│       └── security.py
│
├── google_sheets_updater/          # Google Sheets Updater Service
│   ├── main.py                     # Точка входа
│   ├── updater/                    # Логика обновления
│   │   ├── sheet_updater.py
│   │   ├── scheduled_updater.py
│   │   └── telegram_fetcher.py
│   ├── config/                     # Конфигурация
│   │   └── settings.py
│   └── utils/                      # Утилиты
│       └── logger.py
│
├── shared/                         # Общие компоненты
│   └── google_sheets/              # Google Sheets клиент
│       ├── __init__.py
│       ├── client.py               # Базовый клиент (для updater)
│       └── fetcher.py               # Fetcher (для broadcaster)
│
├── main.py                         # Обертка для обратной совместимости
├── scripts/                        # Скрипты запуска
│   ├── start_broadcaster.sh
│   ├── start_broadcaster.bat
│   ├── start_updater.sh
│   ├── start_updater.bat
│   ├── start_all.sh
│   ├── start_all.bat
│   ├── stop_all.sh
│   └── stop_all.bat
│
├── requirements.txt                # Общие зависимости
├── README.md
└── docs/
```

---

## 🔄 Изменения в импортах

### Broadcaster Service

Все импорты обновлены на абсолютные с префиксом `broadcaster.`:

```python
# Было:
from config.settings import AppConfig
from utils.logger import get_logger
from core.broadcaster import EnhancedBroadcaster
from utils.google_sheets import GoogleSheetsFetcher

# Стало:
from broadcaster.config.settings import AppConfig
from broadcaster.utils.logger import get_logger
from broadcaster.core.broadcaster import EnhancedBroadcaster
from shared.google_sheets.fetcher import GoogleSheetsFetcher
```

### Google Sheets Updater Service

Использует общий клиент из `shared/`:

```python
from shared.google_sheets.client import GoogleSheetsClient
```

---

## 🚀 Запуск сервисов

### 1. Запуск Broadcaster Service

```bash
# Linux/Mac
python broadcaster/main.py
# или
scripts/start_broadcaster.sh

# Windows
python broadcaster\main.py
# или
scripts\start_broadcaster.bat
```

### 2. Запуск Google Sheets Updater Service

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

### 3. Запуск обоих сервисов

```bash
# Linux/Mac
scripts/start_all.sh

# Windows
scripts\start_all.bat
```

### 4. Обратная совместимость

Старый способ запуска все еще работает:

```bash
python main.py  # Автоматически запускает broadcaster/main.py
```

---

## 📝 Конфигурация

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

# Telegram (для получения сообщений)
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_SOURCE_CHANNEL_ID=...

# Таблицы для обновления
BUY_SELL_PRICE_AAA_SHEET_URL=...
BUY_SELL_PRICE_GUS_SHEET_URL=...
```

---

## 🔧 Обновление существующей установки

### Шаг 1: Обновить код

```bash
git pull origin master
```

### Шаг 2: Проверить структуру

Убедитесь, что все файлы на месте:

```bash
ls broadcaster/
ls google_sheets_updater/
ls shared/
```

### Шаг 3: Обновить скрипты запуска

Скрипты уже обновлены, но можно проверить:

```bash
# Проверить скрипты
cat scripts/start_broadcaster.sh
cat scripts/start_updater.sh
```

### Шаг 4: Перезапустить сервисы

```bash
# Остановить старые процессы
scripts/stop_all.sh  # или stop_all.bat

# Запустить новые
scripts/start_all.sh  # или start_all.bat
```

---

## ⚠️ Важные замечания

### 1. Импорты

- Все импорты в `broadcaster/` должны использовать префикс `broadcaster.`
- Общие компоненты импортируются из `shared/`
- Не используйте относительные импорты (`from config`, `from utils`)

### 2. Пути к файлам

- Файлы сессий: `sessions/` (в корне проекта)
- Логи: `logs/` (в корне проекта)
- Конфигурация: `.env` для broadcaster, `.env.updater` для updater

### 3. Обратная совместимость

- `main.py` в корне работает как обертка
- Старые скрипты могут продолжать работать
- Рекомендуется использовать новые скрипты

---

## 🐛 Решение проблем

### Проблема: "ModuleNotFoundError: No module named 'broadcaster'"

**Решение:**
- Убедитесь, что запускаете из корневой директории проекта
- Проверьте, что `broadcaster/` существует
- Проверьте `PYTHONPATH`

### Проблема: "ModuleNotFoundError: No module named 'shared'"

**Решение:**
- Убедитесь, что `shared/` существует в корне проекта
- Проверьте импорты в файлах

### Проблема: Старые скрипты не работают

**Решение:**
- Используйте новые скрипты из `scripts/`
- Или обновите пути в старых скриптах

---

## 📊 Преимущества новой архитектуры

1. **Четкое разделение:**
   - Каждый сервис в своей директории
   - Общие компоненты в `shared/`

2. **Независимость:**
   - Сервисы можно запускать отдельно
   - Легче тестировать и отлаживать

3. **Масштабируемость:**
   - Легко добавить новые сервисы
   - Легко разделить на контейнеры (Docker)

4. **Поддерживаемость:**
   - Четкая структура
   - Легче найти нужный код

---

## 🔗 Связанные документы

- [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) - архитектура микросервисов
- [RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md) - запуск сервисов
- [README.md](../README.md) - общая документация

---

**Дата создания:** 2025-12-10  
**Версия:** 1.0
