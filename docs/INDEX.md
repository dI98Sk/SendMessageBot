# 📚 Документация SendMessageBot

**Версия:** 2.1 Microservices Architecture  
**Последнее обновление:** 2025-12-13

---

## 🚀 Быстрый старт

### ⭐ Начните отсюда

1. **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** ⭐⭐ - **БЫСТРЫЙ СТАРТ** - гайд по запуску с командами
2. **[QUICK_COMMANDS.md](../QUICK_COMMANDS.md)** - краткая шпаргалка с командами
3. **[RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md)** ⭐ - запуск обоих микросервисов
4. **[STARTUP_TROUBLESHOOTING.md](STARTUP_TROUBLESHOOTING.md)** ⭐ - решение проблем при запуске

---

## 📖 Структура документации

### 🏗️ Архитектура и структура

#### Микросервисная архитектура
- **[MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md)** ⭐ - архитектура микросервисов
- **[MICROSERVICES_MIGRATION.md](MICROSERVICES_MIGRATION.md)** ⭐ - миграция на микросервисную архитектуру
- **[MICROSERVICES_REORGANIZATION_COMPLETE.md](MICROSERVICES_REORGANIZATION_COMPLETE.md)** - итоговая сводка реорганизации
- **[ARCHITECTURE_FLOW.md](ARCHITECTURE_FLOW.md)** - как работает архитектура

#### Структура проекта
- **[PROJECT_REORGANIZATION_PLAN.md](PROJECT_REORGANIZATION_PLAN.md)** - план реорганизации проекта

---

### 🛠️ Настройка и установка

#### Быстрый старт
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** ⭐⭐ - **БЫСТРЫЙ СТАРТ** - гайд по запуску с командами
- **[QUICK_COMMANDS.md](../QUICK_COMMANDS.md)** - краткая шпаргалка с командами
- **[setup/START_HERE.md](setup/START_HERE.md)** - начните отсюда (старая версия)
- **[setup/QUICK_START.md](setup/QUICK_START.md)** - быстрый старт в 3 команды

#### Установка
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - подробное руководство по установке
- **[ACCOUNT_SETUP_GUIDE.md](ACCOUNT_SETUP_GUIDE.md)** - настройка Telegram аккаунтов
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - установка на Windows
- **[scripts/README_START_WINDOWS.md](../scripts/README_START_WINDOWS.md)** ⭐ - скрипты первоначального запуска на Windows
- **[ANACONDA_UPDATE_AND_RUN.md](ANACONDA_UPDATE_AND_RUN.md)** ⭐ - обновление и запуск в Anaconda Prompt

#### Конфигурация
- **[ENV_VARIABLES.md](ENV_VARIABLES.md)** - описание переменных окружения
- **[ENV_TEMPLATE.md](ENV_TEMPLATE.md)** - шаблон .env файла

---

### 🚀 Запуск и работа

#### Запуск сервисов
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** ⭐⭐ - **БЫСТРЫЙ СТАРТ** - гайд по запуску с командами
- **[RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md)** ⭐ - запуск обоих микросервисов
- **[STARTUP_TROUBLESHOOTING.md](STARTUP_TROUBLESHOOTING.md)** ⭐ - решение проблем при запуске

#### Broadcaster Service
- **[guides/BROADCASTERS_SETUP.md](guides/BROADCASTERS_SETUP.md)** - настройка broadcaster'ов
- **[BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)** - система координации broadcaster'ов
- **[ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md)** - как добавить новый broadcaster
- **[ALL_BROADCASTERS_ANALYSIS.md](ALL_BROADCASTERS_ANALYSIS.md)** ⭐ - полный анализ всех broadcaster'ов и рекомендации
- **[OPTIMIZED_CYCLES_CONFIG.md](OPTIMIZED_CYCLES_CONFIG.md)** ⭐ - оптимизированная конфигурация циклов (130-150 циклов/сутки)
- **[B2C_MIDSLOW_BROADCASTER.md](B2C_MIDSLOW_BROADCASTER.md)** - документация GUS_B2C_MIDSLOW_Broadcaster
- **[GUS_B2C_CYCLE_ANALYSIS.md](GUS_B2C_CYCLE_ANALYSIS.md)** - детальный анализ цикла GUS_B2C
- **[B2C_CYCLE_RECALCULATION.md](B2C_CYCLE_RECALCULATION.md)** - пересчет цикла B2C
- **[guides/CYCLE_DELAYS_GUIDE.md](guides/CYCLE_DELAYS_GUIDE.md)** - настройка задержек между циклами

#### Google Sheets Updater Service
- **[TELEGRAM_TO_SHEETS_UPDATE.md](TELEGRAM_TO_SHEETS_UPDATE.md)** ⭐ - обновление таблиц из Telegram канала
- **[guides/AUTO_UPDATE_GUIDE.md](guides/AUTO_UPDATE_GUIDE.md)** - автообновление сообщений из Google Sheets

#### Автоматизация
- **[guides/HOW_TO_USE_REPORTS.md](guides/HOW_TO_USE_REPORTS.md)** - система отчетов в Telegram

---

### 🔧 Решение проблем

#### Общие проблемы
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - общее руководство по решению проблем
- **[STARTUP_TROUBLESHOOTING.md](STARTUP_TROUBLESHOOTING.md)** ⭐ - решение проблем при запуске
- **[ERROR_ANALYSIS.md](ERROR_ANALYSIS.md)** - анализ ошибок и рекомендации

#### Специфичные проблемы
- **[DATABASE_LOCKED_SOLUTION.md](DATABASE_LOCKED_SOLUTION.md)** ⭐ - решение проблемы "database is locked"
- **[BROADCASTER_CONNECTION_FIX.md](BROADCASTER_CONNECTION_FIX.md)** ⭐ - исправление проблем с подключением
- **[CYCLE_DEBUGGING_GUIDE.md](CYCLE_DEBUGGING_GUIDE.md)** ⭐ - диагностика циклов рассылки (0 отправлено, 0 циклов)
- **[INVALID_CHAT_ID_FIX.md](INVALID_CHAT_ID_FIX.md)** - решение проблемы InvalidChatId
- **[WINDOWS_LOG_ROTATION_FIX.md](WINDOWS_LOG_ROTATION_FIX.md)** - решение проблемы ротации логов на Windows
- **[LOG_ANALYSIS_STARTUP_ISSUES.md](LOG_ANALYSIS_STARTUP_ISSUES.md)** - анализ проблем при запуске
- **[STARTUP_FIXES_SUMMARY.md](STARTUP_FIXES_SUMMARY.md)** - сводка всех исправлений при запуске
- **[DATABASE_LOCKED_FIX.md](DATABASE_LOCKED_FIX.md)** - исправление database is locked (старая версия)

#### Серверные проблемы
- **[troubleshooting/SERVER_DIAGNOSTIC.md](troubleshooting/SERVER_DIAGNOSTIC.md)** - диагностика проблем на сервере
- **[troubleshooting/SESSION_FILES_FIX.md](troubleshooting/SESSION_FILES_FIX.md)** - проблемы с файлами сессий
- **[troubleshooting/SYNC_TO_SERVER.md](troubleshooting/SYNC_TO_SERVER.md)** - синхронизация с сервером
- **[troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md](troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md)** - обновление на сервере
- **[troubleshooting/WINDOWS_SERVER_SETUP.ps1](troubleshooting/WINDOWS_SERVER_SETUP.ps1)** - скрипт настройки Windows сервера

---

### 🚀 Деплой и продакшен

- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - инструкции по деплою в продакшен
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - общее руководство по деплою
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - чек-лист перед продакшеном
- **[FINAL_CHECKLIST.md](FINAL_CHECKLIST.md)** - финальный чек-лист

---

### 📊 API и техническая документация

- **[API_REFERENCE.md](API_REFERENCE.md)** - справочник API
- **[NEW_BROADCASTERS_README.md](NEW_BROADCASTERS_README.md)** - описание новых broadcaster'ов

---

### 📈 Оптимизация и улучшения

- **[OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)** - руководство по оптимизации
- **[IMPROVEMENT_ROADMAP.md](IMPROVEMENT_ROADMAP.md)** - план улучшений

---

### 📝 Отчеты и мониторинг

- **[REPORTS_SETUP.md](REPORTS_SETUP.md)** - настройка системы отчетов
- **[REPORTS_FIX.md](REPORTS_FIX.md)** - исправление проблем с отчетами
- **[REPORTS_FIX_SUMMARY.md](REPORTS_FIX_SUMMARY.md)** - сводка исправлений отчетов

---

### 🧪 Тестирование

- **[NIGHT_TESTING_GUIDE.md](NIGHT_TESTING_GUIDE.md)** - ночное тестирование
- **[README_TESTING.md](README_TESTING.md)** - общее руководство по тестированию

---

### 📚 Исторические документы

- **[CHANGELOG.md](CHANGELOG.md)** - история изменений
- **[MIGRATION_REPORT.md](MIGRATION_REPORT.md)** - отчет о миграции
- **[COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md)** - полная сводка работы
- **[FINAL_STATUS.md](FINAL_STATUS.md)** - финальный статус проекта
- **[FINAL_SETUP.md](FINAL_SETUP.md)** - финальная настройка
- **[LOG_ANALYSIS_AND_FIXES.md](LOG_ANALYSIS_AND_FIXES.md)** - анализ логов и исправления

---

## 🎯 Навигация по задачам

### Я хочу...

#### 🚀 Запустить систему
1. **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** ⭐⭐ - быстрый старт с командами
2. **[RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md)** ⭐ - запуск обоих микросервисов
3. **[STARTUP_TROUBLESHOOTING.md](STARTUP_TROUBLESHOOTING.md)** ⭐ - если что-то не работает

#### ⚙️ Настроить систему с нуля
1. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - подробное руководство
2. **[ACCOUNT_SETUP_GUIDE.md](ACCOUNT_SETUP_GUIDE.md)** - настройка Telegram аккаунтов
3. **[ENV_VARIABLES.md](ENV_VARIABLES.md)** - переменные окружения

#### ➕ Добавить новый broadcaster
1. **[ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md)** - пошаговая инструкция
2. **[BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)** - система координации

#### 🔧 Разобраться с ошибками
1. **[STARTUP_TROUBLESHOOTING.md](STARTUP_TROUBLESHOOTING.md)** ⭐ - проблемы при запуске
2. **[DATABASE_LOCKED_SOLUTION.md](DATABASE_LOCKED_SOLUTION.md)** ⭐ - database is locked
3. **[BROADCASTER_CONNECTION_FIX.md](BROADCASTER_CONNECTION_FIX.md)** ⭐ - проблемы с подключением
4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - общее руководство
5. **[ERROR_ANALYSIS.md](ERROR_ANALYSIS.md)** - анализ ошибок

#### 🚀 Задеплоить в продакшен
1. **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - инструкции по деплою
2. **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - чек-лист перед запуском
3. **[troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md](troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md)** - обновление на сервере

#### 🔄 Обновить существующий проект
1. **[ANACONDA_UPDATE_AND_RUN.md](ANACONDA_UPDATE_AND_RUN.md)** ⭐ - обновление через git и запуск
2. **[MICROSERVICES_MIGRATION.md](MICROSERVICES_MIGRATION.md)** ⭐ - миграция на микросервисы
3. **[troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md](troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md)** - обновление на сервере

#### 📊 Настроить автообновление
1. **[TELEGRAM_TO_SHEETS_UPDATE.md](TELEGRAM_TO_SHEETS_UPDATE.md)** ⭐ - обновление из Telegram
2. **[guides/AUTO_UPDATE_GUIDE.md](guides/AUTO_UPDATE_GUIDE.md)** - автообновление из Google Sheets

#### 📈 Настроить отчеты
1. **[REPORTS_SETUP.md](REPORTS_SETUP.md)** - настройка системы отчетов
2. **[guides/HOW_TO_USE_REPORTS.md](guides/HOW_TO_USE_REPORTS.md)** - использование отчетов

#### 🏗️ Понять архитектуру
1. **[MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md)** ⭐ - архитектура микросервисов
2. **[ARCHITECTURE_FLOW.md](ARCHITECTURE_FLOW.md)** - как работает архитектура
3. **[BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)** - система координации

---

## 📊 Текущая конфигурация

### Broadcaster'ы (6 шт.)

| Broadcaster | Аккаунт | Тип | Цикл | Задержка | Чатов | Сообщений |
|------------|---------|-----|------|----------|-------|-----------|
| **AAA_PRICE** | acc2 | ОПТОВЫЙ | 30 мин | 60с | 25 | 13 |
| **GUS_PRICE** | acc1 | РОЗНИЧНЫЙ | 30 мин | 60с | 25 | 13 |
| **AAA_ADS** | acc2 | ОПТОВЫЙ | 50 мин | 60с | 15 | 21 |
| **GUS_ADS** | acc1 | РОЗНИЧНЫЙ | 50 мин | 60с | 15 | 16 |
| **GUS_B2C** | acc1 | РОЗНИЧНЫЙ | 1.5 часа | 60с | 71 | 29 |
| **GUS_B2C_MIDSLOW** | acc1 | РОЗНИЧНЫЙ | 2.67 часа | 60с | 52 | 29 ⭐ |

### Микросервисы

- **Broadcaster Service** (`broadcaster/main.py`) - рассылка сообщений
- **Google Sheets Updater Service** (`google_sheets_updater/main.py`) - обновление таблиц

### Автоматизация

- 🔄 **Автообновление сообщений** из Google Sheets (каждые 1 час)
- 📊 **Отчеты в Telegram** каждые 3 часа
- 🛡️ **Система координации** - предотвращение конфликтов между broadcaster'ами
- ⏰ **Расписание работы** - настраиваемое время запуска и тихий час
- 📥 **Обновление из Telegram** - ежедневно в 11:05 MSK

### Безопасность

- ✅ Уникальные файлы сессий для каждого broadcaster'а
- ✅ Адаптивные задержки при ошибках
- ✅ Очередь отложенных сообщений (до 5 попыток)
- ✅ Защита от FloodWait
- ✅ Валидация chat_id при загрузке
- ✅ Глобальная координация отправок
- ✅ Обработка "database is locked" с retry логикой

---

## 🔍 Быстрый поиск

### По проблемам
- **Проблемы при запуске** → [STARTUP_TROUBLESHOOTING.md](STARTUP_TROUBLESHOOTING.md) ⭐
- **database is locked** → [DATABASE_LOCKED_SOLUTION.md](DATABASE_LOCKED_SOLUTION.md) ⭐
- **Проблемы с подключением** → [BROADCASTER_CONNECTION_FIX.md](BROADCASTER_CONNECTION_FIX.md) ⭐
- **InvalidChatId ошибки** → [INVALID_CHAT_ID_FIX.md](INVALID_CHAT_ID_FIX.md)
- **Ошибка ротации логов на Windows** → [WINDOWS_LOG_ROTATION_FIX.md](WINDOWS_LOG_ROTATION_FIX.md)
- **Проблемы с сессиями** → [troubleshooting/SESSION_FILES_FIX.md](troubleshooting/SESSION_FILES_FIX.md)
- **Проблемы на сервере** → [troubleshooting/SERVER_DIAGNOSTIC.md](troubleshooting/SERVER_DIAGNOSTIC.md)

### По функциям
- **Запуск системы** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) ⭐⭐
- **Добавить broadcaster** → [ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md)
- **Настроить координацию** → [BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)
- **Настроить автообновление** → [guides/AUTO_UPDATE_GUIDE.md](guides/AUTO_UPDATE_GUIDE.md)
- **Настроить отчеты** → [REPORTS_SETUP.md](REPORTS_SETUP.md)
- **Обновление из Telegram** → [TELEGRAM_TO_SHEETS_UPDATE.md](TELEGRAM_TO_SHEETS_UPDATE.md) ⭐

---

## 📝 Последние обновления

### Версия 2.1 (2025-12-13)
- ✅ Реорганизация в микросервисную архитектуру
- ✅ Улучшена обработка "database is locked"
- ✅ Добавлено детальное логирование подключений
- ✅ Улучшена проверка сессий перед запуском
- ✅ Создан Google Sheets Updater Service
- ✅ Добавлена документация по запуску и решению проблем

### Версия 2.0 (2025-11-16)
- ✅ Добавлен GUS_B2C_MIDSLOW_Broadcaster (6-й broadcaster)
- ✅ Обновлен B2C_TARGET (73 чата)
- ✅ Все broadcaster'ы используют логику случайных сообщений
- ✅ Оптимизированы циклы для всех broadcaster'ов

---

**Вернуться к:** [Главному README](../README.md)
