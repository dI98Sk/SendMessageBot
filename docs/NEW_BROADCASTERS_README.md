# 🔥 Новые Броудкастеры AAA и GUS

## 📋 Обзор

Добавлены два новых броудкастера для работы с дополнительными таблицами Google Sheets:

- **AAA Broadcaster** - использует аккаунт `acc1` (ОПТОВЫЙ) для сообщений из таблицы AAA Store
- **GUS Broadcaster** - использует аккаунт `acc2` (РОЗНИЧНЫЙ) для сообщений из таблицы Яблочный Гусь

## 🗂️ Структура файлов

### Конфигурационные файлы
- `config_mesAAA.py` - сообщения для AAA Store
- `config_mesGUS.py` - сообщения для Яблочный Гусь

### Скрипты обновления
- `update_configAAA.py` - обновление сообщений AAA из Google Sheets
- `update_configGUS.py` - обновление сообщений GUS из Google Sheets
- `update_all_messages.py` - обновление всех сообщений сразу

### Тестирование
- `test_new_broadcasters.py` - тестирование новых броудкастеров

## ⚙️ Настройка

### 1. Переменные окружения (.env)

Добавлены новые переменные в `.env` файл:

```bash
#_____Buy/Sell/Price_AAA________
BUY_SELL_PRICE_AAA_SHEET_URL=https://docs.google.com/spreadsheets/d/1cx5ekHadMQVqBTPlRI6V4KVdqQoieH1wPUtJTjPJvSo/edit?gid=0#gid=0

#_____Buy/Sell/Price_Gus________
BUY_SELL_PRICE_GUS_SHEET_URL=https://docs.google.com/spreadsheets/d/1-4PgtSW0EpCGPfHLgjBmQCwzKpvo5_ABZmSrIq-Y3OI/edit?gid=0#gid=0
```

### 2. Обновление конфигурации

Обновлен файл `config/settings.py` для поддержки новых броудкастеров:

- Добавлены поля `aaa_sheet_url` и `gus_sheet_url` в `GoogleSheetsConfig`
- Добавлены поля `aaa_messages` и `gus_messages` в `AppConfig`
- Обновлена загрузка конфигурации для новых переменных

### 3. Обновление main_improved.py

Добавлены новые броудкастеры в основной файл:

```python
# AAA Broadcaster - использует аккаунт acc1 (ID: ОПТОВЫЙ)
aaa_broadcaster = EnhancedBroadcaster(
    config=self.config,
    name="AAA_Broadcaster",
    targets=self.config.targets,
    messages=self.config.aaa_messages,
    session_name="sessions/acc1"
)

# GUS Broadcaster - использует аккаунт acc2 (ID: РОЗНИЧНЫЙ)
gus_broadcaster = EnhancedBroadcaster(
    config=self.config,
    name="GUS_Broadcaster",
    targets=self.config.targets,
    messages=self.config.gus_messages,
    session_name="sessions/acc2"
)
```

## 🚀 Использование

### 1. Обновление сообщений

```bash
# Обновить все сообщения сразу
python update_all_messages.py

# Или обновить по отдельности
python update_configAAA.py
python update_configGUS.py
```

### 2. Тестирование

```bash
# Тестирование новых броудкастеров
python test_new_broadcasters.py

# Или через главное меню
python run_bot.py
# Выберите опцию 11
```

### 3. Запуск полной системы

```bash
# Запуск всех броудкастеров (включая новые)
python main_improved.py
```

## 📊 Информация об аккаунтах

При авторизации система теперь отображает подробную информацию:

```
✅ AAA_Broadcaster подключен: Имя Фамилия (@username)
📱 ID: 123456789 | Тип: ОПТОВЫЙ
🎯 Чатов: 2 | 💬 Сообщений: 5

✅ GUS_Broadcaster подключен: Имя Фамилия (@username)
📱 ID: 987654321 | Тип: РОЗНИЧНЫЙ
🎯 Чатов: 2 | 💬 Сообщений: 3
```

## 🎯 Распределение аккаунтов

| Broadcaster | Аккаунт | Тип | Таблица |
|-------------|---------|-----|---------|
| B2B_Broadcaster | acc1 | ОПТОВЫЙ | B2B Sheet |
| B2C_Broadcaster | acc2 | РОЗНИЧНЫЙ | B2C Sheet |
| AAA_Broadcaster | acc1 | ОПТОВЫЙ | AAA Sheet |
| GUS_Broadcaster | acc2 | РОЗНИЧНЫЙ | GUS Sheet |

## 🔧 Устранение неполадок

### 1. Ошибки подключения к Google Sheets

```bash
# Проверьте credentials.json
ls -la credentials.json

# Проверьте доступ к таблицам
python test_google_sheets.py
```

### 2. Ошибки авторизации

```bash
# Проверьте файлы сессий
ls -la sessions/

# Удалите старые сессии при необходимости
rm sessions/acc1.session
rm sessions/acc2.session
```

### 3. Пустые сообщения

```bash
# Обновите сообщения из Google Sheets
python update_all_messages.py

# Проверьте содержимое файлов
cat config_mesAAA.py
cat config_mesGUS.py
```

## 📈 Мониторинг

Все новые броудкастеры интегрированы в систему мониторинга:

- Статистика отправки сообщений
- Обработка ошибок и FloodWait
- Логирование всех операций
- Уведомления о статусе

## 🎉 Готово!

Теперь у вас есть 4 броудкастера:
- **B2B** (оптовые сообщения)
- **B2C** (розничные сообщения)  
- **AAA** (сообщения AAA Store)
- **GUS** (сообщения Яблочный Гусь)

Все работают с тестовыми чатами и готовы к использованию!
