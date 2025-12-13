# 🔧 Решение проблем при запуске

**Дата:** 2025-12-13

---

## ❌ Проблема: `ModuleNotFoundError: No module named 'broadcaster'`

### Симптомы:
```
Traceback (most recent call last):
  File "broadcaster/main.py", line 18, in <module>
    from broadcaster.config.settings import config_manager, AppConfig
ModuleNotFoundError: No module named 'broadcaster'
```

### Причина:
Неправильный путь к корневой директории проекта в `broadcaster/main.py`.

### Решение:
✅ **Исправлено** - путь изменен с `Path(__file__).parent` на `Path(__file__).parent.parent`

### Проверка:
```bash
# Должно работать без ошибок
python -c "import sys; sys.path.insert(0, '.'); from broadcaster.config.settings import config_manager; print('OK')"
```

---

## ❌ Проблема: `NameError: name 'List' is not defined`

### Симптомы:
```
File "google_sheets_updater/updater/scheduled_updater.py", line 158
    async def _write_to_sheets(self, messages: List[str]):
                                               ^^^^
NameError: name 'List' is not defined. Did you mean: 'list'?
```

### Причина:
Отсутствует импорт `List` из модуля `typing`.

### Решение:
✅ **Исправлено** - добавлен импорт `List` в `scheduled_updater.py`:
```python
from typing import Optional, List
```

---

## ✅ Как проверить, что сервисы работают

### 1. Проверка процессов:

```bash
# Linux/Mac
ps aux | grep python | grep -E "(broadcaster|updater)"

# Должны быть видны процессы:
# - python broadcaster/main.py
# - python google_sheets_updater/main.py
```

### 2. Проверка логов:

```bash
# Логи Broadcaster
tail -f logs/broadcaster.log

# Должны быть логи:
# - ✅ Подключено как ...
# - 🔄 Начинаем цикл рассылки...

# Логи Updater
tail -f logs/updater.log

# Должны быть логи:
# - ✅ Google Sheets Updater запущен
# - ⏰ Следующее обновление: ...
```

### 3. Проверка ошибок:

```bash
# Поиск ошибок в логах
grep -i error logs/broadcaster.log
grep -i error logs/updater.log

# Поиск исключений
grep -i "exception\|traceback" logs/broadcaster.log
```

---

## 🔄 Перезапуск после исправлений

### 1. Остановить все сервисы:

```bash
bash scripts/stop_all.sh
```

### 2. Проверить, что процессы остановлены:

```bash
ps aux | grep python | grep -E "(broadcaster|updater)"
# Не должно быть процессов
```

### 3. Запустить заново:

```bash
bash scripts/start_all.sh
```

### 4. Проверить логи:

```bash
# Подождать 10-20 секунд
sleep 20

# Проверить логи
tail -n 50 logs/broadcaster.log
tail -n 50 logs/updater.log
```

---

## 📋 Чек-лист проверки

- [ ] Процессы запущены (`ps aux | grep python`)
- [ ] Нет ошибок в логах (`grep -i error logs/*.log`)
- [ ] Broadcaster'ы подключились (логи "✅ Подключено")
- [ ] Начались циклы рассылки (логи "🔄 Начинаем цикл")
- [ ] Google Sheets Updater запущен (логи "✅ запущен")

---

## 🆘 Если проблема сохраняется

1. **Проверьте Python путь:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

2. **Проверьте рабочую директорию:**
   ```bash
   pwd
   # Должно быть: /path/to/SendMessageBot
   ```

3. **Проверьте установку зависимостей:**
   ```bash
   pip list | grep -E "(telethon|gspread|pytz)"
   ```

4. **Проверьте конфигурацию:**
   ```bash
   ls -la .env
   cat .env | grep -E "(API_ID|API_HASH)"
   ```

---

**Дата создания:** 2025-12-13  
**Версия:** 1.0

