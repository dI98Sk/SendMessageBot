# 📋 План реорганизации проекта SendMessageBot

## 🎯 Цели реорганизации
1. Структурировать файлы по логическим папкам
2. Убрать дублирующиеся и устаревшие файлы
3. Создать полную документацию
4. Упростить настройку и запуск

## 📁 Предлагаемая структура проекта

```
SendMessageBot/
├── 📁 core/                    # Основная логика
│   ├── broadcaster.py          # Класс броудкастера
│   ├── exceptions.py           # Исключения
│   ├── queue.py               # Очереди сообщений
│   └── retry.py               # Логика повторных попыток
│
├── 📁 config/                  # Конфигурация
│   ├── settings.py            # Основные настройки
│   ├── targets.py             # Целевые чаты
│   ├── messages.py            # Сообщения B2B/B2C
│   ├── message_updater.py     # Обновление сообщений
│   ├── messages_aaa.py        # Сообщения AAA Store
│   └── messages_gus.py        # Сообщения Яблочный Гусь
│
├── 📁 utils/                   # Утилиты
│   ├── logger.py              # Логирование
│   ├── google_sheets.py       # Работа с Google Sheets
│   ├── security.py            # Безопасность
│   └── helpers.py             # Вспомогательные функции
│
├── 📁 monitoring/              # Мониторинг и отчеты
│   ├── metrics.py             # Сбор метрик
│   ├── notifications.py       # Уведомления
│   └── reports.py             # Отчеты
│
├── 📁 scripts/                 # Скрипты управления
│   ├── setup_accounts.py      # Настройка аккаунтов
│   ├── update_messages.py     # Обновление сообщений
│   ├── test_broadcasters.py   # Тестирование
│   └── manage_sessions.py     # Управление сессиями
│
├── 📁 sessions/                # Файлы сессий Telegram
│   ├── acc1.session           # Оптовый аккаунт
│   └── acc2.session           # Розничный аккаунт
│
├── 📁 logs/                    # Логи
│   └── bot.log                # Основной лог
│
├── 📁 docs/                    # Документация
│   ├── README.md              # Основная документация
│   ├── SETUP_GUIDE.md         # Руководство по настройке
│   ├── TROUBLESHOOTING.md     # Решение проблем
│   └── API_REFERENCE.md       # Справочник API
│
├── 📁 tests/                   # Тесты
│   ├── test_broadcasters.py
│   └── test_google_sheets.py
│
├── 📄 main.py                  # Главный файл запуска
├── 📄 run.py                   # Скрипт запуска с меню
├── 📄 requirements.txt         # Зависимости
├── 📄 .env                     # Переменные окружения
└── 📄 credentials.json         # Google Sheets credentials
```

## 🗑️ Файлы для удаления/перемещения

### Удалить (дублирующиеся/устаревшие):
- `config_mesВ2B.py` → переместить в `config/messages_b2b.py`
- `config_mesВ2C.py` → переместить в `config/messages_b2c.py`
- `config_targ.py` → удалить (дублирует targets.py)
- `broadcasterB2B.py` → удалить (заменен на core/broadcaster.py)
- `get_allChatID.py` → переместить в `scripts/get_chat_ids.py`
- `google_sheet_fetch.py` → удалить (заменен на utils/google_sheets.py)
- `allChatID.txt` → переместить в `data/chat_ids.txt`
- `notification_session.session` → удалить (временный файл)

### Переместить в scripts/:
- `setup_accounts_simple.py` → `scripts/setup_accounts.py`
- `setup_new_accounts.py` → удалить (заменен на scripts/setup_accounts.py)
- `test_new_broadcasters.py` → `scripts/test_broadcasters.py`
- `update_all_messages.py` → `scripts/update_messages.py`
- `update_configAAA.py` → удалить (заменен на scripts/update_messages.py)
- `update_configGUS.py` → удалить (заменен на scripts/update_messages.py)
- `update_configB2B.py` → удалить (заменен на scripts/update_messages.py)
- `update_configB2C.py` → удалить (заменен на scripts/update_messages.py)
- `manage_reports.py` → `scripts/manage_reports.py`
- `switch_targets.py` → `scripts/switch_targets.py`
- `show_stats.py` → `scripts/show_stats.py`
- `test_google_sheets.py` → `tests/test_google_sheets.py`
- `test_notifications.py` → `tests/test_notifications.py`
- `migrate_project.py` → `scripts/migrate_project.py`
- `check_environment.py` → `scripts/check_environment.py`
- `generate_password.py` → `scripts/generate_password.py`

### Переместить в docs/:
- Все `.md` файлы кроме `README.md`

## 🔧 План выполнения

### Этап 1: Создание новой структуры
1. Создать папки: `scripts/`, `tests/`, `docs/`
2. Переместить файлы в соответствующие папки
3. Обновить импорты в файлах

### Этап 2: Очистка и объединение
1. Удалить дублирующиеся файлы
2. Объединить похожие скрипты
3. Обновить пути в коде

### Этап 3: Создание документации
1. Создать основной README.md
2. Создать руководство по настройке
3. Создать справочник по API
4. Создать руководство по устранению неполадок

### Этап 4: Тестирование
1. Проверить работоспособность после реорганизации
2. Обновить скрипты запуска
3. Протестировать все функции

## ⚠️ Важные замечания

1. **Не удалять файлы сразу** - сначала переместить и проверить
2. **Обновить все импорты** после перемещения файлов
3. **Сохранить работоспособность** на каждом этапе
4. **Создать резервную копию** перед началом реорганизации

## 🎯 Результат

После реорганизации проект будет:
- ✅ Структурированным и понятным
- ✅ Легким в настройке и запуске
- ✅ Хорошо документированным
- ✅ Готовым к масштабированию
- ✅ Простым в поддержке
