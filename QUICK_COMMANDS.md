# ⚡ Быстрые команды - Шпаргалка

## 🚀 Запуск

### Оба сервиса одновременно (РЕКОМЕНДУЕТСЯ)

```bash
# Linux/Mac
bash scripts/start_all.sh

# Windows
scripts\start_all.bat
```

### Только рассылка (Broadcaster)

```bash
# Linux/Mac
python broadcaster/main.py

# Windows
python broadcaster\main.py
```

### Только обновление (Google Sheets Updater)

```bash
# Linux/Mac
python google_sheets_updater/main.py

# Windows
python google_sheets_updater\main.py
```

---

## 🛑 Остановка

```bash
# Linux/Mac
bash scripts/stop_all.sh

# Windows
scripts\stop_all.bat
```

---

## 📝 Логи

```bash
# Просмотр логов рассылки
tail -f logs/broadcaster.log

# Просмотр логов обновления
tail -f logs/updater.log

# Оба лога одновременно
tail -f logs/broadcaster.log logs/updater.log
```

---

## ✅ Проверка работы

```bash
# Проверка процессов
ps aux | grep python | grep -E "(broadcaster|updater)"

# Windows
tasklist | findstr "python.exe"
```

---

**Подробнее:** [docs/QUICK_START_GUIDE.md](docs/QUICK_START_GUIDE.md)

