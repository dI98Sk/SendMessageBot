# 📚 Документация SendMessageBot

**Версия:** 2.0  
**Последнее обновление:** 2025-11-16

---

## 🚀 Быстрый старт

1. **[setup/START_HERE.md](setup/START_HERE.md)** ⭐ - начните отсюда
2. **[setup/QUICK_START.md](setup/QUICK_START.md)** - быстрый старт в 3 команды
3. **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)** - инструкции по деплою
4. **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - чек-лист перед запуском

---

## 📖 Структура документации

### 🛠️ Настройка и установка

#### Начало работы
- **[setup/START_HERE.md](setup/START_HERE.md)** ⭐ - с чего начать (обязательно к прочтению)
- **[setup/QUICK_START.md](setup/QUICK_START.md)** - быстрая настройка за 3 шага
- **[setup/INDEX.md](setup/INDEX.md)** - полный индекс настройки

#### Установка
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - подробное руководство по установке
- **[ACCOUNT_SETUP_GUIDE.md](ACCOUNT_SETUP_GUIDE.md)** - настройка Telegram аккаунтов
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - установка на Windows
- **[scripts/README_START_WINDOWS.md](../scripts/README_START_WINDOWS.md)** ⭐ - скрипты первоначального запуска на Windows
- **[ANACONDA_UPDATE_AND_RUN.md](ANACONDA_UPDATE_AND_RUN.md)** ⭐ - обновление и запуск в Anaconda Prompt
- **[ENV_VARIABLES.md](ENV_VARIABLES.md)** - описание переменных окружения
- **[ENV_TEMPLATE.md](ENV_TEMPLATE.md)** - шаблон .env файла

---

### 📘 Руководства по использованию

#### Broadcaster'ы
- **[guides/BROADCASTERS_SETUP.md](guides/BROADCASTERS_SETUP.md)** - настройка broadcaster'ов
- **[BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)** - система координации broadcaster'ов
- **[ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md)** - как добавить новый broadcaster
- **[ALL_BROADCASTERS_ANALYSIS.md](ALL_BROADCASTERS_ANALYSIS.md)** ⭐ - полный анализ всех broadcaster'ов и рекомендации
- **[OPTIMIZED_CYCLES_CONFIG.md](OPTIMIZED_CYCLES_CONFIG.md)** ⭐ - оптимизированная конфигурация циклов (130-150 циклов/сутки)
- **[B2C_MIDSLOW_BROADCASTER.md](B2C_MIDSLOW_BROADCASTER.md)** - документация GUS_B2C_MIDSLOW_Broadcaster
- **[GUS_B2C_CYCLE_ANALYSIS.md](GUS_B2C_CYCLE_ANALYSIS.md)** - детальный анализ цикла GUS_B2C
- **[guides/CYCLE_DELAYS_GUIDE.md](guides/CYCLE_DELAYS_GUIDE.md)** - настройка задержек между циклами

#### Автоматизация
- **[guides/AUTO_UPDATE_GUIDE.md](guides/AUTO_UPDATE_GUIDE.md)** - автообновление сообщений из Google Sheets
- **[guides/HOW_TO_USE_REPORTS.md](guides/HOW_TO_USE_REPORTS.md)** - система отчетов в Telegram

#### Тестирование
- **[NIGHT_TESTING_GUIDE.md](NIGHT_TESTING_GUIDE.md)** - ночное тестирование
- **[README_TESTING.md](README_TESTING.md)** - общее руководство по тестированию

---

### 🔧 Решение проблем

#### Диагностика и исправление
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - общее руководство по решению проблем
- **[ERROR_ANALYSIS.md](ERROR_ANALYSIS.md)** - анализ ошибок и рекомендации
- **[INVALID_CHAT_ID_FIX.md](INVALID_CHAT_ID_FIX.md)** - решение проблемы InvalidChatId
- **[WINDOWS_LOG_ROTATION_FIX.md](WINDOWS_LOG_ROTATION_FIX.md)** - решение проблемы ротации логов на Windows
- **[LOG_ANALYSIS_STARTUP_ISSUES.md](LOG_ANALYSIS_STARTUP_ISSUES.md)** ⭐ - анализ проблем при запуске (database is locked, phone attribute)
- **[STARTUP_FIXES_SUMMARY.md](STARTUP_FIXES_SUMMARY.md)** - сводка всех исправлений при запуске

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
- **[ANACONDA_UPDATE_AND_RUN.md](ANACONDA_UPDATE_AND_RUN.md)** ⭐ - обновление и запуск в Anaconda Prompt
- **[RUNNING_MICROSERVICES.md](RUNNING_MICROSERVICES.md)** ⭐ - запуск обоих микросервисов
- **[MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md)** ⭐ - архитектура микросервисов
- **[MICROSERVICES_MIGRATION.md](MICROSERVICES_MIGRATION.md)** ⭐ - миграция на микросервисную архитектуру
- **[TELEGRAM_TO_SHEETS_UPDATE.md](TELEGRAM_TO_SHEETS_UPDATE.md)** ⭐ - обновление таблиц из Telegram канала

---

### 📊 Архитектура и API

- **[ARCHITECTURE_FLOW.md](ARCHITECTURE_FLOW.md)** - как работает архитектура
- **[API_REFERENCE.md](API_REFERENCE.md)** - справочник API
- **[NEW_BROADCASTERS_README.md](NEW_BROADCASTERS_README.md)** - описание новых broadcaster'ов

---

### 📈 Оптимизация и улучшения

- **[OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)** - руководство по оптимизации
- **[IMPROVEMENT_ROADMAP.md](IMPROVEMENT_ROADMAP.md)** - план улучшений
- **[PROJECT_REORGANIZATION_PLAN.md](PROJECT_REORGANIZATION_PLAN.md)** - план реорганизации проекта

---

### 📝 Отчеты и мониторинг

- **[REPORTS_SETUP.md](REPORTS_SETUP.md)** - настройка системы отчетов
- **[REPORTS_FIX.md](REPORTS_FIX.md)** - исправление проблем с отчетами
- **[REPORTS_FIX_SUMMARY.md](REPORTS_FIX_SUMMARY.md)** - сводка исправлений отчетов

---

### 📚 Исторические документы

- **[CHANGELOG.md](CHANGELOG.md)** - история изменений
- **[MIGRATION_REPORT.md](MIGRATION_REPORT.md)** - отчет о миграции
- **[COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md)** - полная сводка работы
- **[FINAL_STATUS.md](FINAL_STATUS.md)** - финальный статус проекта
- **[FINAL_SETUP.md](FINAL_SETUP.md)** - финальная настройка

---

## 🎯 Навигация по задачам

### Я хочу...

#### Настроить систему с нуля
1. [setup/START_HERE.md](setup/START_HERE.md)
2. [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. [ACCOUNT_SETUP_GUIDE.md](ACCOUNT_SETUP_GUIDE.md)

#### Добавить новый broadcaster
1. [ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md)
2. [BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)

#### Разобраться с ошибками
1. [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md)
2. [INVALID_CHAT_ID_FIX.md](INVALID_CHAT_ID_FIX.md)
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

#### Задеплоить в продакшен
1. [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)
2. [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
3. [troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md](troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md)

#### Обновить существующий проект
1. [ANACONDA_UPDATE_AND_RUN.md](ANACONDA_UPDATE_AND_RUN.md) ⭐ - обновление через git и запуск
2. [troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md](troubleshooting/SERVER_UPDATE_INSTRUCTIONS.md) - обновление на сервере

#### Настроить автообновление
1. [guides/AUTO_UPDATE_GUIDE.md](guides/AUTO_UPDATE_GUIDE.md)

#### Настроить отчеты
1. [REPORTS_SETUP.md](REPORTS_SETUP.md)
2. [guides/HOW_TO_USE_REPORTS.md](guides/HOW_TO_USE_REPORTS.md)

#### Понять архитектуру
1. [ARCHITECTURE_FLOW.md](ARCHITECTURE_FLOW.md)
2. [BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)

---

## 📊 Текущая конфигурация

### Broadcaster'ы (6 шт.)

| Broadcaster | Аккаунт | Тип | Цикл | Задержка | Чатов | Сообщений |
|------------|---------|-----|------|----------|-------|-----------|
| **AAA_PRICE** | acc2 | ОПТОВЫЙ | 30 мин | 60с | 27 | ~30 |
| **GUS_PRICE** | acc1 | РОЗНИЧНЫЙ | 30 мин | 60с | 27 | ~30 |
| **AAA_ADS** | acc2 | ОПТОВЫЙ | 50 мин | 60с | 16 | ~20 |
| **GUS_ADS** | acc1 | РОЗНИЧНЫЙ | 50 мин | 60с | 16 | ~20 |
| **GUS_B2C** | acc1 | РОЗНИЧНЫЙ | 1.5 часа | 60с | 73 | ~29 |
| **GUS_B2C_MIDSLOW** | **acc1** | **РОЗНИЧНЫЙ** | **2.67 часа** | **60с** | **52** | **~29** ⭐ |

### Автоматизация
- 🔄 **Автообновление сообщений** из Google Sheets (настраиваемый интервал)
- 📊 **Отчеты в Telegram** каждые 3 часа
- 🛡️ **Система координации** - предотвращение конфликтов между broadcaster'ами
- ⏰ **Расписание работы** - настраиваемое время запуска и тихий час

### Безопасность
- ✅ Уникальные файлы сессий для каждого broadcaster'а
- ✅ Адаптивные задержки при ошибках
- ✅ Очередь отложенных сообщений (до 5 попыток)
- ✅ Защита от FloodWait
- ✅ Валидация chat_id при загрузке
- ✅ Глобальная координация отправок

---

## 🔍 Быстрый поиск

### По проблемам
- **InvalidChatId ошибки** → [INVALID_CHAT_ID_FIX.md](INVALID_CHAT_ID_FIX.md)
- **Ошибка ротации логов на Windows** → [WINDOWS_LOG_ROTATION_FIX.md](WINDOWS_LOG_ROTATION_FIX.md)
- **Много ошибок в отчетах** → [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md)
- **Проблемы с сессиями** → [troubleshooting/SESSION_FILES_FIX.md](troubleshooting/SESSION_FILES_FIX.md)
- **Проблемы на сервере** → [troubleshooting/SERVER_DIAGNOSTIC.md](troubleshooting/SERVER_DIAGNOSTIC.md)

### По функциям
- **Добавить broadcaster** → [ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md)
- **Настроить координацию** → [BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md)
- **Настроить автообновление** → [guides/AUTO_UPDATE_GUIDE.md](guides/AUTO_UPDATE_GUIDE.md)
- **Настроить отчеты** → [REPORTS_SETUP.md](REPORTS_SETUP.md)

---

## 📝 Последние обновления

### Версия 2.1 (2025-11-16)
- ✅ Добавлен GUS_B2C_MIDSLOW_Broadcaster (6-й broadcaster)
- ✅ Обновлен B2C_TARGET (73 чата)
- ✅ Все broadcaster'ы используют логику случайных сообщений
- ✅ Оптимизированы циклы для всех broadcaster'ов

### Версия 2.0 (2025-11-16)
- ✅ Добавлен GUS_B2C_Broadcaster
- ✅ Создана система координации broadcaster'ов
- ✅ Улучшено логирование ошибок
- ✅ Исправлена валидация chat_id
- ✅ Исправлена ротация логов на Windows
- ✅ Добавлена документация по всем новым функциям

### Новые документы
- [BROADCASTER_COORDINATION.md](BROADCASTER_COORDINATION.md) - система координации
- [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md) - анализ ошибок
- [INVALID_CHAT_ID_FIX.md](INVALID_CHAT_ID_FIX.md) - решение InvalidChatId
- [WINDOWS_LOG_ROTATION_FIX.md](WINDOWS_LOG_ROTATION_FIX.md) - решение ротации логов
- [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) - инструкции по деплою
- [ADD_NEW_BROADCASTER.md](ADD_NEW_BROADCASTER.md) - добавление нового broadcaster'а

---

**Вернуться к:** [Главному README](../README.md)
