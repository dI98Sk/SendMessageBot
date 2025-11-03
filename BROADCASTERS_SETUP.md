# 📡 Настройка broadcaster'ов

## 📊 Текущая конфигурация

### Итого: 4 broadcaster'а

1. **AAA_PRICE_Broadcaster** (acc1) - Прайсы AAA
2. **GUS_PRICE_Broadcaster** (acc2) - Прайсы GUS  
3. **AAA_ADS_Broadcaster** (acc1) - Реклама AAA
4. **GUS_ADS_Broadcaster** (acc2) - Реклама GUS

## 🎯 Целевые чаты

### PRICE_TARGET (22 чата)
Используется для отправки прайсов (AAA и GUS)

### ADS_TARGET (11 чатов)
Используется для отправки рекламы (AAA и GUS)

### TEST_TARGETS (2 чата)
Используется для тестирования

## 📝 Сообщения

### Прайсы
- **AAA**: `config/messages_aaa.py` (13 сообщений)
  - Обновляется из Google Sheets: `BUY_SELL_PRICE_AAA_SHEET_URL`
  - Скрипт обновления: `scripts/update_messages.py`

- **GUS**: `config/messages_gus.py` (4 сообщения)
  - Обновляется из Google Sheets: `BUY_SELL_PRICE_GUS_SHEET_URL`
  - Скрипт обновления: `scripts/update_messages.py`

### Реклама
- **AAA ADS**: `config/messages_aaa_ads.py`
  - Обновляется из Google Sheets: `ADS_AAA_SHEET_URL`
  - Скрипт обновления: `scripts/update_ads_messages.py`

- **GUS ADS**: `config/messages_gus_ads.py`
  - Обновляется из Google Sheets: `ADS_GUS_SHEET_URL`
  - Скрипт обновления: `scripts/update_ads_messages.py`

## 🔧 Настройка .env

```bash
# Google Sheets URLs
BUY_SELL_PRICE_AAA_SHEET_URL=https://docs.google.com/...
BUY_SELL_PRICE_GUS_SHEET_URL=https://docs.google.com/...
ADS_AAA_SHEET_URL=https://docs.google.com/...
ADS_GUS_SHEET_URL=https://docs.google.com/...

# Credentials
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## 📥 Обновление сообщений

### Обновление ПРАЙСОВ
```bash
python scripts/update_messages.py
```

Обновляет:
- `config/messages_aaa.py` (из BUY_SELL_PRICE_AAA_SHEET_URL)
- `config/messages_gus.py` (из BUY_SELL_PRICE_GUS_SHEET_URL)

### Обновление РЕКЛАМЫ
```bash
python scripts/update_ads_messages.py
```

Обновляет:
- `config/messages_aaa_ads.py` (из ADS_AAA_SHEET_URL)
- `config/messages_gus_ads.py` (из ADS_GUS_SHEET_URL)

### Обновление ВСЕГО
```bash
python scripts/update_messages.py && python scripts/update_ads_messages.py
```

## 🚀 Запуск

### Тестирование конфигурации
```bash
python test_new_broadcasters.py
```

### Запуск бота
```bash
python main.py
```

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                     SendMessageBot                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐       │
│  │  AAA_PRICE       │          │  GUS_PRICE       │       │
│  │  Broadcaster     │          │  Broadcaster     │       │
│  │  (acc1)          │          │  (acc2)          │       │
│  │  ────────────    │          │  ────────────    │       │
│  │  22 чата         │          │  22 чата         │       │
│  │  13 сообщений    │          │  4 сообщения     │       │
│  └──────────────────┘          └──────────────────┘       │
│                                                             │
│  ┌──────────────────┐          ┌──────────────────┐       │
│  │  AAA_ADS         │          │  GUS_ADS         │       │
│  │  Broadcaster     │          │  Broadcaster     │       │
│  │  (acc1)          │          │  (acc2)          │       │
│  │  ────────────    │          │  ────────────    │       │
│  │  11 чатов        │          │  11 чатов        │       │
│  │  N сообщений     │          │  N сообщений     │       │
│  └──────────────────┘          └──────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Рабочий процесс

1. **Подготовка сообщений**
   - Обновляются таблицы в Google Sheets
   - Запускаются скрипты обновления (`update_messages.py`, `update_ads_messages.py`)
   - Сообщения сохраняются в Python файлы

2. **Запуск бота**
   - Бот загружает конфигурацию из .env
   - Импортирует targets и messages
   - Создает 4 broadcaster'а
   - Запускает систему отчетов

3. **Работа broadcaster'ов**
   - Каждый broadcaster работает независимо
   - Отправляет сообщения в свои целевые чаты
   - Соблюдает задержки и ограничения
   - Собирает статистику

4. **Мониторинг**
   - Отчеты отправляются в Telegram канал
   - Логи сохраняются в `bot.log`
   - Статистика доступна через `show_stats.py`

## 🎛️ Управление

### Добавление нового broadcaster'а

1. **Создайте файл с сообщениями** (например, `config/messages_new.py`)
2. **Добавьте в `config/settings.py`**:
   ```python
   # В GoogleSheetsConfig
   new_sheet_url: Optional[str] = None
   
   # В AppConfig
   new_messages: List[str] = field(default_factory=list)
   
   # В load_config импорт
   from .messages_new import MESSAGES_NEW
   
   # В AppConfig создание
   new_messages=MESSAGES_NEW
   ```

3. **Создайте broadcaster в `main.py`**:
   ```python
   new_broadcaster = EnhancedBroadcaster(
       config=self.config,
       name="NEW_Broadcaster",
       targets=self.config.targets,  # или свои targets
       messages=self.config.new_messages,
       session_name="sessions/acc1"  # или acc2
   )
   self.broadcasters.append(new_broadcaster)
   ```

4. **Протестируйте**: `python test_new_broadcasters.py`

### Изменение целевых чатов

Редактируйте `config/targets.py`:
```python
ADS_TARGET = [
    -1001234567890,  # Новый чат
    -1001234567891,  # Еще один
]
```

### Изменение расписания

В `.env`:
```bash
# Время начала работы (час)
START_TIME_HOUR=6

# Тихий час (когда не работают)
ENABLE_QUIET_HOURS=true
QUIET_HOUR_START=0
QUIET_HOUR_END=7

# Задержки
DELAY_BETWEEN_CHATS=40  # секунд между чатами
CYCLE_DELAY=3600  # секунд между циклами (1 час)
MIN_INTERVAL_PER_CHAT=600  # минимум 10 минут между отправками в один чат
```

## 📈 Мониторинг

### Просмотр логов
```bash
tail -f bot.log
```

### Статистика
```bash
python show_stats.py
```

### Отчеты в Telegram
Настройте в `.env`:
```bash
ENABLE_REPORTS=true
REPORTS_BOT_TOKEN=<токен>
REPORTS_CHANNEL_ID=<ID_канала>
REPORT_INTERVAL_HOURS=3.0
```

## ❓ Решение проблем

### Broadcaster'ы не созданы
```bash
# Проверьте конфигурацию
python test_new_broadcasters.py
```

### Нет сообщений
```bash
# Обновите сообщения из Google Sheets
python scripts/update_messages.py
python scripts/update_ads_messages.py
```

### Ошибки импорта
```bash
# Проверьте что файлы существуют
ls -la config/messages*.py

# Проверьте синтаксис
python -m py_compile config/messages_aaa_ads.py
python -m py_compile config/messages_gus_ads.py
```

## ✅ Чек-лист перед запуском

- [ ] Все URL Google Sheets настроены в .env
- [ ] Файлы credentials.json существует
- [ ] Обновлены сообщения из Google Sheets
- [ ] Тест пройден успешно (`python test_new_broadcasters.py`)
- [ ] Файлы сессий существуют (`sessions/acc1.session`, `sessions/acc2.session`)
- [ ] Настроена система отчетов
- [ ] Проверены целевые чаты в `config/targets.py`

---

**Дата обновления: 2025-11-04**

