#!/bin/bash
# Скрипт запуска Google Sheets Updater Service

echo "🚀 Запуск Google Sheets Updater Service..."

# Активация виртуального окружения (если есть)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Запуск сервиса
python google_sheets_updater/main.py

