@echo off
REM Скрипт запуска Google Sheets Updater Service для Windows

echo 🚀 Запуск Google Sheets Updater Service...

REM Активация виртуального окружения (если есть)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Запуск сервиса
python google_sheets_updater\main.py

pause

