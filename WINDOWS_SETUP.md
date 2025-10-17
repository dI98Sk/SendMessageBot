# 🪟 Инструкция по настройке на Windows Server

## 📋 Быстрый старт

### 1️⃣ Клонирование проекта

```powershell
cd C:\Users\Administrator\PycharmProjects
git clone https://github.com/dI98Sk/SendMessageBot.git
cd SendMessageBot
```

### 2️⃣ Создание виртуального окружения

```powershell
# Создание виртуального окружения
python -m venv .venv

# Активация
.venv\Scripts\activate

# Проверка
python --version
```

### 3️⃣ Установка зависимостей

```powershell
pip install --upgrade pip
pip install -r requirements_improved.txt
```

### 4️⃣ Настройка файлов

#### A. Создание .env файла

```powershell
# Скопируйте шаблон
copy ENV_TEMPLATE.md .env

# Отредактируйте .env в блокноте
notepad .env
```

Заполните обязательные параметры:
```env
API_ID=ваш_api_id
API_HASH=ваш_api_hash
SESSION_NAME=session
```

#### B. Создание директории sessions

```powershell
# Создайте директорию
mkdir sessions

# Скопируйте файлы сессий
copy acc1.session sessions\
copy acc2.session sessions\

# Проверьте что файлы скопированы
dir sessions\
```

#### C. Настройка credentials.json (опционально)

Если используете Google Sheets:

1. Скачайте `credentials.json` из Google Cloud Console
2. Поместите в корень проекта `C:\Users\Administrator\PycharmProjects\SendMessageBot\`

```powershell
# Проверьте что файл на месте
dir credentials.json
```

### 5️⃣ Диагностика

```powershell
# Запустите проверку окружения
python check_environment.py
```

**Исправьте все ошибки перед продолжением!**

### 6️⃣ Запуск бота

```powershell
# Активируйте виртуальное окружение (если ещё не активировано)
.venv\Scripts\activate

# Запустите бота
python main_improved.py
```

---

## ⚠️ Решение типичных проблем на Windows

### Проблема 1: "unable to open database file"

**Причина:** Директория sessions не существует или нет прав.

**Решение:**
```powershell
# Создайте директорию
mkdir sessions -Force

# Скопируйте файлы сессий
copy acc1.session sessions\ -Force
copy acc2.session sessions\ -Force

# Проверьте права доступа
icacls sessions
```

### Проблема 2: "Invalid JWT Signature"

**Причина:** Время на сервере не синхронизировано.

**Решение:**
```powershell
# Проверьте текущее время
date /t
time /t

# Синхронизируйте время
net start w32time
w32tm /resync

# Перезапустите службу времени
net stop w32time
net start w32time
w32tm /resync /force
```

### Проблема 3: "ModuleNotFoundError"

**Причина:** Не установлены зависимости или не активировано виртуальное окружение.

**Решение:**
```powershell
# Убедитесь что виртуальное окружение активировано
.venv\Scripts\activate

# Переустановите зависимости
pip install --upgrade pip
pip install -r requirements_improved.txt --force-reinstall
```

### Проблема 4: "Permission denied"

**Причина:** Недостаточно прав доступа.

**Решение:**
```powershell
# Запустите PowerShell от имени администратора
# Дайте полные права на папку проекта
$path = "C:\Users\Administrator\PycharmProjects\SendMessageBot"
icacls $path /grant:r "Administrators:(OI)(CI)F" /T
```

---

## 🚀 Автозапуск бота при старте Windows

### Вариант 1: Task Scheduler (Планировщик заданий)

1. Откройте **Task Scheduler** (Планировщик заданий)
2. Создайте новую задачу:
   - **Name:** SendMessageBot
   - **Trigger:** At startup (При запуске системы)
   - **Action:** Start a program
   - **Program:** `C:\Users\Administrator\PycharmProjects\SendMessageBot\.venv\Scripts\python.exe`
   - **Arguments:** `main_improved.py`
   - **Start in:** `C:\Users\Administrator\PycharmProjects\SendMessageBot`

### Вариант 2: Создание службы Windows

```powershell
# Установите NSSM (Non-Sucking Service Manager)
# Скачайте с https://nssm.cc/download

# Создайте службу
nssm install SendMessageBot "C:\Users\Administrator\PycharmProjects\SendMessageBot\.venv\Scripts\python.exe"
nssm set SendMessageBot AppDirectory "C:\Users\Administrator\PycharmProjects\SendMessageBot"
nssm set SendMessageBot AppParameters "main_improved.py"
nssm set SendMessageBot DisplayName "Send Message Bot"
nssm set SendMessageBot Description "Telegram broadcasting bot for B2B and B2C messages"
nssm set SendMessageBot Start SERVICE_AUTO_START

# Запустите службу
nssm start SendMessageBot

# Проверьте статус
nssm status SendMessageBot
```

---

## 📊 Мониторинг на Windows

### Просмотр логов в реальном времени

```powershell
# PowerShell
Get-Content logs\bot.log -Wait -Tail 50

# Или используйте notepad++, tail для Windows и т.д.
```

### Проверка статуса бота

```powershell
# Проверьте запущен ли процесс Python
tasklist | findstr python.exe

# Или более детально
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

### Остановка бота

```powershell
# Найдите PID процесса
tasklist | findstr python.exe

# Остановите процесс по PID
taskkill /PID <номер_процесса> /F

# Или остановите все процессы Python (осторожно!)
taskkill /IM python.exe /F
```

---

## 🔄 Обновление бота на сервере

```powershell
# Перейдите в директорию проекта
cd C:\Users\Administrator\PycharmProjects\SendMessageBot

# Остановите бота (если запущен)
# См. раздел "Остановка бота" выше

# Подтяните изменения из Git
git pull

# Активируйте виртуальное окружение
.venv\Scripts\activate

# Обновите зависимости (если изменились)
pip install -r requirements_improved.txt --upgrade

# Запустите проверку
python check_environment.py

# Запустите бота
python main_improved.py
```

---

## 📝 Полезные команды PowerShell

```powershell
# Проверка версии Python
python --version

# Проверка установленных пакетов
pip list

# Проверка переменных окружения
Get-Content .env

# Размер директории
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum

# Поиск файлов
Get-ChildItem -Recurse -Filter "*.session"

# Очистка __pycache__
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse

# Архивация логов
Compress-Archive -Path logs\* -DestinationPath "logs_backup_$(Get-Date -Format 'yyyyMMdd').zip"
```

---

## 🔐 Безопасность на Windows Server

### Настройка брандмауэра

Если бот работает через прокси, убедитесь что порты открыты:

```powershell
# Проверьте правила брандмауэра
netsh advfirewall firewall show rule name=all | findstr "Python"

# Добавьте правило для Python (если нужно)
netsh advfirewall firewall add rule name="Python Bot" dir=out action=allow program="C:\Users\Administrator\PycharmProjects\SendMessageBot\.venv\Scripts\python.exe" enable=yes
```

### Ограничение доступа к файлам

```powershell
# Ограничьте доступ к секретным файлам
icacls .env /inheritance:r /grant:r "Administrators:F"
icacls credentials.json /inheritance:r /grant:r "Administrators:F"
icacls sessions /inheritance:r /grant:r "Administrators:(OI)(CI)F"
```

---

## 🆘 Экстренная помощь

Если бот перестал работать на сервере:

1. **Проверьте логи:**
   ```powershell
   notepad logs\bot.log
   ```

2. **Запустите диагностику:**
   ```powershell
   python check_environment.py > diagnostic.txt
   notepad diagnostic.txt
   ```

3. **Проверьте процессы:**
   ```powershell
   tasklist | findstr python
   ```

4. **Перезапустите бота:**
   ```powershell
   # Остановите
   taskkill /IM python.exe /F
   
   # Запустите заново
   .venv\Scripts\activate
   python main_improved.py
   ```

5. **Проверьте системные события:**
   ```powershell
   # Откройте Event Viewer
   eventvwr.msc
   ```

---

## 📞 Контакты и поддержка

Если проблема не решена после выполнения всех шагов:

1. Сохраните вывод `python check_environment.py`
2. Сохраните последние 100 строк из `logs\bot.log`
3. Опишите что делали и что пошло не так
4. Свяжитесь с разработчиком

**ВАЖНО:** Не отправляйте файлы `.env`, `credentials.json` или `.session`!

