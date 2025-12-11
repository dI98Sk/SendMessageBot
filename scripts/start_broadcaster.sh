#!/bin/bash
# Скрипт запуска Broadcaster Service

echo "🚀 Запуск Broadcaster Service..."

# Активация виртуального окружения (если есть)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запуск сервиса
python broadcaster/main.py
