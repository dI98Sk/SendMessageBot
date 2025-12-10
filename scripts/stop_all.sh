#!/bin/bash
# Скрипт для остановки всех микросервисов

echo "🛑 Остановка всех микросервисов..."

# Поиск процессов
BROADCASTER_PIDS=$(ps aux | grep "[p]ython.*main.py" | awk '{print $2}')
UPDATER_PIDS=$(ps aux | grep "[p]ython.*google_sheets_updater/main.py" | awk '{print $2}')

if [ -z "$BROADCASTER_PIDS" ] && [ -z "$UPDATER_PIDS" ]; then
    echo "ℹ️  Сервисы не запущены"
    exit 0
fi

# Остановка Broadcaster Service
if [ ! -z "$BROADCASTER_PIDS" ]; then
    echo "📡 Остановка Broadcaster Service (PIDs: $BROADCASTER_PIDS)..."
    kill $BROADCASTER_PIDS 2>/dev/null
fi

# Остановка Google Sheets Updater
if [ ! -z "$UPDATER_PIDS" ]; then
    echo "📊 Остановка Google Sheets Updater (PIDs: $UPDATER_PIDS)..."
    kill $UPDATER_PIDS 2>/dev/null
fi

# Ожидание завершения
sleep 2

# Принудительная остановка, если процессы еще работают
BROADCASTER_PIDS=$(ps aux | grep "[p]ython.*main.py" | awk '{print $2}')
UPDATER_PIDS=$(ps aux | grep "[p]ython.*google_sheets_updater/main.py" | awk '{print $2}')

if [ ! -z "$BROADCASTER_PIDS" ]; then
    echo "⚠️  Принудительная остановка Broadcaster Service..."
    kill -9 $BROADCASTER_PIDS 2>/dev/null
fi

if [ ! -z "$UPDATER_PIDS" ]; then
    echo "⚠️  Принудительная остановка Google Sheets Updater..."
    kill -9 $UPDATER_PIDS 2>/dev/null
fi

echo "✅ Все сервисы остановлены"

