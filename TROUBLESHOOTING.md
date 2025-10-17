# 🔧 Решение проблем (Troubleshooting)

## 🚀 Быстрая диагностика

Перед запуском бота запустите скрипт диагностики:

```bash
python check_environment.py
```

Этот скрипт проверит все необходимые компоненты и покажет, что нужно исправить.

---

## ❌ Типичные ошибки и их решение

### 1. "unable to open database file"

**Причина:** Не может открыть файл сессии Telegram.

**Решение:**

#### Windows:
```bash
# Создайте директорию sessions если её нет
mkdir sessions

# Скопируйте файлы сессий
copy acc1.session sessions\
copy acc2.session sessions\
```

#### Linux/Mac:
```bash
# Создайте директорию sessions
mkdir -p sessions

# Скопируйте файлы сессий
cp acc1.session sessions/
cp acc2.session sessions/
```

**Проверьте права доступа:**
- У пользователя должны быть права на чтение/запись в директории `sessions/`
- Файлы сессий должны существовать и не быть пустыми

---

### 2. "Invalid JWT Signature" / "invalid_grant"

**Причина:** Проблема с аутентификацией Google Sheets.

**Решение:**

#### A. Проверьте системное время

**Windows:**
```bash
# Проверить текущее время
date /t && time /t

# Синхронизировать время
net start w32time
w32tm /resync
```

**Linux:**
```bash
# Проверить текущее время
date

# Синхронизировать время
sudo ntpdate pool.ntp.org
# или
sudo timedatectl set-ntp true
```

#### B. Перезагрузите credentials.json

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Перейдите в **IAM & Admin** → **Service Accounts**
3. Найдите ваш Service Account
4. **Создайте новый ключ**: Actions → Manage Keys → Add Key → Create new key → JSON
5. Скачайте новый файл и замените старый `credentials.json`

#### C. Проверьте права Service Account

1. Откройте вашу Google таблицу
2. Нажмите **Share** (Поделиться)
3. Добавьте email из `credentials.json` (поле `client_email`)
4. Дайте права **Editor** (Редактор)

#### D. Временно отключите Google Sheets

Если нужно срочно запустить бота, можно временно отключить интеграцию с Google Sheets.

В файле `.env`:
```env
# Закомментируйте или удалите эти строки
# SHEET_URL_B2B=...
# SHEET_URL_B2C=...
```

Бот будет использовать сообщения из `config/messages.py`.

---

### 3. Бот использует неправильный аккаунт

**Проблема:** Оба broadcaster'а используют один и тот же аккаунт.

**Решение:** Убедитесь что у вас есть ОБА файла сессий:
- `sessions/acc1.session` - для B2B (ID: 8108419249)
- `sessions/acc2.session` - для B2C (ID: 8497033180)

**Проверка аккаунтов:**
```bash
python -c "
import asyncio
from telethon import TelegramClient
import os

async def check():
    for name in ['sessions/acc1', 'sessions/acc2']:
        client = TelegramClient(name, int(os.getenv('API_ID')), os.getenv('API_HASH'))
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f'{name}: ID={me.id}, Name={me.first_name}')
        await client.disconnect()

asyncio.run(check())
"
```

---

### 4. "Permission denied" / "Access denied"

**Причина:** Нет прав доступа к файлам или директориям.

**Решение:**

#### Windows:
```bash
# Дайте полные права на папку проекта
icacls "C:\Users\Administrator\PycharmProjects\SendMessageBot" /grant:r "Administrators:(OI)(CI)F" /T
```

#### Linux:
```bash
# Дайте права на выполнение
chmod +x *.py

# Дайте права на чтение/запись
chmod 755 sessions/
chmod 644 sessions/*.session
chmod 644 credentials.json
```

---

### 5. Модули не найдены

**Ошибка:**
```
ModuleNotFoundError: No module named 'telethon'
```

**Решение:**
```bash
# Убедитесь что используете правильный Python
python --version

# Установите зависимости
pip install -r requirements_improved.txt

# Или для виртуального окружения
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements_improved.txt
```

---

## 🔍 Детальная диагностика

### Проверка конфигурации

```bash
# Проверьте что .env файл существует
ls -la .env  # Linux/Mac
dir .env     # Windows

# Проверьте переменные окружения
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API_ID:', os.getenv('API_ID'))"
```

### Проверка файлов сессий

```bash
# Проверьте существование файлов
ls -lh sessions/  # Linux/Mac
dir sessions\     # Windows

# Проверьте размер файлов (должны быть > 0 байт)
du -sh sessions/*.session  # Linux/Mac
```

### Проверка credentials.json

```bash
# Проверьте что файл валидный JSON
python -c "import json; print(json.load(open('credentials.json')).get('type'))"

# Должен вывести: service_account
```

---

## 📱 Логи и отладка

### Включение детального логирования

В `.env`:
```env
LOG_LEVEL=DEBUG
LOG_CONSOLE=true
```

### Просмотр логов

```bash
# Linux/Mac
tail -f logs/bot.log

# Windows PowerShell
Get-Content logs\bot.log -Wait -Tail 50
```

---

## 🆘 Контрольный список перед запуском

- [ ] Python 3.8+ установлен
- [ ] Все зависимости установлены (`pip install -r requirements_improved.txt`)
- [ ] Файл `.env` создан и заполнен (см. `ENV_TEMPLATE.md`)
- [ ] Директория `sessions/` существует
- [ ] Файлы `acc1.session` и `acc2.session` находятся в `sessions/`
- [ ] Файл `credentials.json` существует и валиден (если используете Google Sheets)
- [ ] Время на сервере синхронизировано
- [ ] Права доступа к файлам корректны
- [ ] Запущен `python check_environment.py` без ошибок

---

## 📞 Получение помощи

Если проблема не решена:

1. **Запустите диагностику:**
   ```bash
   python check_environment.py > diagnostic.txt
   ```

2. **Соберите логи:**
   ```bash
   # Последние 100 строк лога
   tail -n 100 logs/bot.log > error.log  # Linux/Mac
   ```

3. **Опишите проблему:**
   - Что пытались сделать
   - Какую ошибку получили
   - Вывод `check_environment.py`
   - Содержимое логов

---

## 🔐 Безопасность

**ВАЖНО:** Никогда не делитесь:
- Файлом `.env`
- Файлом `credentials.json`
- Файлами сессий (`.session`)
- API_ID и API_HASH
- Логами с чувствительными данными

Перед публикацией логов убедитесь что в них нет:
- API ключей
- ID чатов
- Номеров телефонов
- Токенов

