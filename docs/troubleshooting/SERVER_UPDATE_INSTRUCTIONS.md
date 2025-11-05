# 🔧 Инструкция по обновлению кода на сервере

## ❌ Ошибка на сервере

```
ValueError: invalid literal for int() with base 10: '0.17'
```

**Причина:** На сервере старая версия `config/settings.py`

---

## ✅ Исправление

### Вариант 1: Скопировать исправленный файл

С локальной машины на сервер скопируйте:
```
config/settings.py
```

### Вариант 2: Исправить вручную на сервере

Откройте на сервере файл:
```
C:\Users\Administrator\PycharmProjects\SendMessageBot\config\settings.py
```

**Исправьте 2 строки:**

#### 1️⃣ Строка ~87 (в классе ReportsConfig):

**БЫЛО:**
```python
@dataclass
class ReportsConfig:
    """Конфигурация отчетов"""
    telegram_bot_token: Optional[str] = None
    telegram_channel_id: Optional[str] = None
    enable_reports: bool = False
    report_interval_hours: int = 3  # Отчеты каждые 3 часа
    timezone: str = "Europe/Moscow"
```

**ДОЛЖНО БЫТЬ:**
```python
@dataclass
class ReportsConfig:
    """Конфигурация отчетов"""
    telegram_bot_token: Optional[str] = None
    telegram_channel_id: Optional[str] = None
    enable_reports: bool = False
    report_interval_hours: float = 3.0  # Отчеты каждые 3 часа (поддержка дробных значений)
    timezone: str = "Europe/Moscow"
```

**Изменения:**
- `int` → `float`
- `3` → `3.0`

---

#### 2️⃣ Строка ~217 (в методе load_config, создание ReportsConfig):

**БЫЛО:**
```python
        # Создание конфигурации отчетов
        reports_config = ReportsConfig(
            telegram_bot_token=os.getenv("REPORTS_BOT_TOKEN"),
            telegram_channel_id=os.getenv("REPORTS_CHANNEL_ID"),
            enable_reports=os.getenv("ENABLE_REPORTS", "false").lower() == "true",
            report_interval_hours=int(os.getenv("REPORT_INTERVAL_HOURS", 3)),  # Отчеты каждые 3 часа
            timezone=os.getenv("REPORTS_TIMEZONE", "Europe/Moscow")
        )
```

**ДОЛЖНО БЫТЬ:**
```python
        # Создание конфигурации отчетов
        reports_config = ReportsConfig(
            telegram_bot_token=os.getenv("REPORTS_BOT_TOKEN"),
            telegram_channel_id=os.getenv("REPORTS_CHANNEL_ID"),
            enable_reports=os.getenv("ENABLE_REPORTS", "false").lower() == "true",
            report_interval_hours=float(os.getenv("REPORT_INTERVAL_HOURS", "3.0")),  # Отчеты каждые N часов (поддержка дробных значений)
            timezone=os.getenv("REPORTS_TIMEZONE", "Europe/Moscow")
        )
```

**Изменения:**
- `int(os.getenv(...))` → `float(os.getenv(...))`
- `"REPORT_INTERVAL_HOURS", 3` → `"REPORT_INTERVAL_HOURS", "3.0"`

---

## 🚀 После исправления

Запустите:
```bash
python main.py
```

Должно работать без ошибок!

---

## 📦 Полный список файлов для обновления на сервере

Для полной синхронизации скопируйте с локальной машины:

### Обязательные (исправления):
- `config/settings.py` ⭐ (исправление ошибки)
- `monitoring/reports.py` (исправление timezone)
- `core/broadcaster.py` (добавлен параметр cycle_delay)
- `main.py` (4 broadcaster'а, уникальные сессии, автообновление)

### Новые файлы:
- `utils/auto_updater.py` (автообновление сообщений)
- `config/messages_aaa_ads.py` (реклама AAA)
- `config/messages_gus_ads.py` (реклама GUS)
- `config/targets.py` (добавлен TEST_TARGETS_ADS)
- `main_test.py` (тестовая версия)

### Файлы сессий (если нужно):
- `sessions/acc1_price.session`
- `sessions/acc2_price.session`
- `sessions/acc1_ads.session`
- `sessions/acc2_ads.session`

---

## ⚡ Быстрое решение (минимум изменений)

Если хотите минимальные изменения, достаточно:

1. **Исправить `config/settings.py`** (2 строки выше)
2. Запустить `python main.py`

Остальное можно обновить потом.

---

## 🔍 Проверка после исправления

```bash
python -c "from config.settings import config_manager; c = config_manager.load_config(); print('✅ OK')"
```

Если видите `✅ OK` - всё исправлено!

---

**📝 Исправьте 2 строки в config/settings.py и можно запускать!**

