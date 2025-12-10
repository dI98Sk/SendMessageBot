# 🔄 Миграция на микросервисную архитектуру

**Дата:** 2025-12-10  
**Версия:** 2.1

---

## ✅ Выполненные изменения

### 1. Реорганизация структуры проекта

**Было:**
```
SendMessageBot/
├── main.py
├── core/
├── config/
├── monitoring/
├── utils/
└── google_sheets_updater/
```

**Стало:**
```
SendMessageBot/
├── broadcaster/              # Broadcaster Service
│   ├── main.py
│   ├── core/
│   ├── config/
│   ├── monitoring/
│   └── utils/
├── google_sheets_updater/    # Google Sheets Updater Service
│   ├── main.py
│   ├── updater/
│   ├── config/
│   └── utils/
└── shared/                   # Общие компоненты
    └── google_sheets/
```

### 2. Обновлены импорты

Все импорты в `broadcaster/` обновлены для использования префикса `broadcaster.`:

- `from config.settings` → `from broadcaster.config.settings`
- `from core.broadcaster` → `from broadcaster.core.broadcaster`
- `from utils.logger` → `from broadcaster.utils.logger`
- `from utils.google_sheets` → `from shared.google_sheets.fetcher`

### 3. Обновлены скрипты запуска

- `scripts/start_all.sh` - запуск обоих сервисов
- `scripts/start_all.bat` - запуск обоих сервисов (Windows)
- `scripts/start_broadcaster.sh` - запуск только broadcaster
- `scripts/start_broadcaster.bat` - запуск только broadcaster (Windows)
- `scripts/stop_all.sh` - остановка всех сервисов
- `scripts/stop_all.bat` - остановка всех сервисов (Windows)

### 4. Созданы общие компоненты

- `shared/google_sheets/client.py` - базовый клиент (для записи)
- `shared/google_sheets/fetcher.py` - для чтения (broadcaster)

---

## 🚀 Запуск после миграции

### Запуск Broadcaster Service

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

### Запуск Google Sheets Updater

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

### Запуск обоих сервисов

```bash
# Linux/Mac
scripts/start_all.sh

# Windows
scripts\start_all.bat
```

---

## ⚠️ Важные изменения

### 1. Пути к файлам

- **Конфигурация:** `broadcaster/config/` вместо `config/`
- **Логи:** остаются в корне (`bot.log`) или `logs/broadcaster.log`
- **Сессии:** остаются в `sessions/` (общие для обоих сервисов)

### 2. Импорты в скриптах

Если у вас есть собственные скрипты, обновите импорты:

```python
# Было:
from config.settings import config_manager

# Стало:
from broadcaster.config.settings import config_manager
```

### 3. Автообновление сообщений

Пути к файлам сообщений обновлены:
- `config/messages_aaa.py` → `broadcaster/config/messages_aaa.py`
- `config/messages_gus.py` → `broadcaster/config/messages_gus.py`
- и т.д.

---

## 🔍 Проверка после миграции

### 1. Проверка структуры

```bash
# Проверить наличие всех файлов
ls broadcaster/main.py
ls broadcaster/core/broadcaster.py
ls broadcaster/config/settings.py
ls google_sheets_updater/main.py
ls shared/google_sheets/fetcher.py
```

### 2. Проверка импортов

```bash
# Проверить синтаксис
python -m py_compile broadcaster/main.py
python -m py_compile google_sheets_updater/main.py
```

### 3. Тестовый запуск

```bash
# Запустить broadcaster (должен запуститься без ошибок импорта)
python broadcaster/main.py

# Запустить updater (должен запуститься без ошибок импорта)
python google_sheets_updater/main.py
```

---

## 📝 Обратная совместимость

### Старые файлы

Старые файлы в корне проекта (`main.py`, `core/`, `config/`, и т.д.) **остаются** для обратной совместимости, но рекомендуется использовать новую структуру.

### Миграция существующих установок

Если у вас уже работает проект:

1. **Обновите код:**
   ```bash
   git pull origin master
   ```

2. **Обновите скрипты запуска:**
   - Используйте новые скрипты из `scripts/`
   - Или обновите пути в существующих скриптах

3. **Проверьте работу:**
   ```bash
   python broadcaster/main.py
   ```

---

## 🔗 Связанные документы

- [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) - архитектура микросервисов
- [RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md) - запуск сервисов
- [broadcaster/README.md](../broadcaster/README.md) - документация Broadcaster Service
- [google_sheets_updater/README.md](../google_sheets_updater/README.md) - документация Updater Service

---

**Дата создания:** 2025-12-10  
**Версия:** 1.0

