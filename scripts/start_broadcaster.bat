@echo off
REM Скрипт запуска Broadcaster Service для Windows

echo 🚀 Запуск Broadcaster Service...

REM Активация виртуального окружения (если есть)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Запуск сервиса
python broadcaster\main.py

pause

