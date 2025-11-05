# 🎯 Финальная настройка broadcaster'ов

## 📊 Итоговая конфигурация (4 broadcaster'а)

### Распределение по аккаунтам:

| Broadcaster | Тип | Аккаунт | Session | Чаты | Сообщения |
|-------------|-----|---------|---------|------|-----------|
| **AAA_PRICE** | Прайсы | acc1 (Яблочный Гусь) | sessions/acc1 | 22 | 13 |
| **GUS_PRICE** | Прайсы | acc2 (Анна Макарова) | sessions/acc2 | 22 | 4 |
| **AAA_ADS** | Реклама | acc2 (Анна Макарова) | sessions/acc2 | 11 | N |
| **GUS_ADS** | Реклама | acc1 (Яблочный Гусь) | sessions/acc1 | 11 | N |

### Логика распределения:

**ПРАЙСЫ:**
- AAA → acc1 (Яблочный Гусь Менеджер)
- GUS → acc2 (Анна Макарова)

**РЕКЛАМА (противоположно):**
- AAA → acc2 (Анна Макарова) ✨
- GUS → acc1 (Яблочный Гусь Менеджер) ✨

## 🎯 Целевые чаты

### Production чаты:

- **PRICE_TARGET** (22 чата) - для прайсов AAA и GUS
- **ADS_TARGET** (11 чатов) - для рекламы AAA и GUS

### Тестовые чаты:

- **TEST_TARGETS** (2 чата) - общие тесты
  - `-1002679672234` (ТЕСТ Рассылок 2)
  - `-1002805990284` (ТЕСТ РАССЫЛОК 1)

- **TEST_TARGETS_ADS** (2 чата) - тесты рекламы
  - `-5042413579` ([ТЕСТ РЕКЛАМЫ 2](https://t.me/+viHvvuAuyNs2Yjli))
  - `-4918385916` ([ТЕСТ РЕКЛАМЫ 1](https://t.me/+KQvsVWUl8j4xYzJi))

## 📝 Сообщения

### Источники (Google Sheets):

1. **Прайсы AAA**: `BUY_SELL_PRICE_AAA_SHEET_URL` → `config/messages_aaa.py`
2. **Прайсы GUS**: `BUY_SELL_PRICE_GUS_SHEET_URL` → `config/messages_gus.py`
3. **Реклама AAA**: `ADS_AAA_SHEET_URL` → `config/messages_aaa_ads.py`
4. **Реклама GUS**: `ADS_GUS_SHEET_URL` → `config/messages_gus_ads.py`

### Обновление сообщений:

```bash
# Прайсы
python scripts/update_messages.py

# Реклама
python scripts/update_ads_messages.py

# Все сразу
python scripts/update_messages.py && python scripts/update_ads_messages.py
```

## 🧪 Тестирование

### 1. Тест всех broadcaster'ов
```bash
python test_new_broadcasters.py
```

Ожидается:
```
✅ ВСЕ BROADCASTER'Ы СОЗДАНЫ УСПЕШНО!
🎯 Всего broadcaster'ов: 4
```

### 2. Тест только рекламных (на тестовых чатах)
```bash
python test_ads_broadcasters.py
```

Будет работать 3 минуты и отправит сообщения в TEST_TARGETS_ADS.

### 3. Проверка ID чатов
```bash
python scripts/get_chat_ids.py
```

Полезно для получения ID новых чатов из ссылок-приглашений.

## 🚀 Запуск

### Production
```bash
python main.py
```

При запуске увидите:
```
✅ AAA PRICE Broadcaster создан (acc1): 22 чатов, 13 сообщений
✅ GUS PRICE Broadcaster создан (acc2): 22 чатов, 4 сообщений
✅ AAA ADS Broadcaster создан (acc2): 11 чатов, N сообщений
✅ GUS ADS Broadcaster создан (acc1): 11 чатов, N сообщений
📊 Всего broadcaster'ов: 4
```

## 📊 Мониторинг

### Логи
```bash
tail -f bot.log
```

### Фильтры логов
```bash
# Только AAA broadcaster'ы
tail -f bot.log | grep AAA

# Только GUS broadcaster'ы  
tail -f bot.log | grep GUS

# Только реклама
tail -f bot.log | grep ADS

# Только прайсы
tail -f bot.log | grep PRICE

# Успешные отправки
tail -f bot.log | grep "✅ Отправлено сообщение"
```

### Отчеты в Telegram
Автоматически каждые 3 часа (или по настройке `REPORT_INTERVAL_HOURS`)

## ⚙️ Настройки .env

### Обязательные
```bash
# Telegram API
API_ID=your_api_id
API_HASH=your_api_hash

# Google Sheets
BUY_SELL_PRICE_AAA_SHEET_URL=https://docs.google.com/...
BUY_SELL_PRICE_GUS_SHEET_URL=https://docs.google.com/...
ADS_AAA_SHEET_URL=https://docs.google.com/...
ADS_GUS_SHEET_URL=https://docs.google.com/...
GOOGLE_CREDENTIALS_FILE=credentials.json

# Отчеты
ENABLE_REPORTS=true
REPORTS_BOT_TOKEN=your_bot_token
REPORTS_CHANNEL_ID=your_channel_id
REPORT_INTERVAL_HOURS=3.0
```

### Опциональные
```bash
# Расписание
ENABLE_SCHEDULING=true
START_TIME_HOUR=6
ENABLE_QUIET_HOURS=true
QUIET_HOUR_START=0
QUIET_HOUR_END=7

# Задержки
DELAY_BETWEEN_CHATS=40
CYCLE_DELAY=3600
MIN_INTERVAL_PER_CHAT=600
```

## 🔧 Изменение конфигурации

### Добавить чаты
Редактируйте `config/targets.py`:
```python
ADS_TARGET = [
    -1001055908983,
    -1001774846066,
    # добавьте новый чат
    -1001234567890,
]
```

### Поменять аккаунт для broadcaster'а
В `main.py` измените `session_name`:
```python
aaa_ads_broadcaster = EnhancedBroadcaster(
    ...
    session_name="sessions/acc1"  # было acc2
)
```

### Изменить интервал отчетов
В `.env`:
```bash
REPORT_INTERVAL_HOURS=1.0  # каждый час
```

## ✅ Чек-лист перед запуском

- [ ] Все URL Google Sheets настроены в .env
- [ ] credentials.json существует
- [ ] Обновлены сообщения из Google Sheets
  - [ ] `python scripts/update_messages.py`
  - [ ] `python scripts/update_ads_messages.py`
- [ ] Тест пройден (`python test_new_broadcasters.py`)
- [ ] Файлы сессий существуют
  - [ ] `sessions/acc1.session`
  - [ ] `sessions/acc2.session`
- [ ] Настроена система отчетов
- [ ] Проверены целевые чаты

## 🎉 Итого

**4 broadcaster'а готовы к работе:**

1. ✅ AAA PRICE (acc1) → 22 чата, прайсы
2. ✅ GUS PRICE (acc2) → 22 чата, прайсы
3. ✅ AAA ADS (acc2) → 11 чатов, реклама
4. ✅ GUS ADS (acc1) → 11 чатов, реклама

**Все протестировано и готово к запуску! 🚀**

---
*Дата: 2025-11-04*
*Версия: Final*


