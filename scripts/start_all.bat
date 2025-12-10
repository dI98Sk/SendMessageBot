@echo off
REM Скрипт для запуска обоих микросервисов одновременно (Windows)

echo 🚀 Запуск всех микросервисов...
echo.

REM Проверка виртуального окружения
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано
)

REM Создание директории для логов, если не существует
if not exist logs mkdir logs

echo 📡 Запуск Broadcaster Service...
start "Broadcaster Service" /MIN python broadcaster\main.py
echo    Логи: logs\broadcaster.log

timeout /t 2 /nobreak >nul

echo 📊 Запуск Google Sheets Updater Service...
start "Google Sheets Updater" /MIN python google_sheets_updater\main.py
echo    Логи: logs\updater.log

echo.
echo ✅ Оба сервиса запущены в отдельных окнах!
echo.
echo 📝 Для просмотра логов откройте:
echo    - logs\broadcaster.log
echo    - logs\updater.log
echo.
echo 🛑 Для остановки закройте окна сервисов или используйте Task Manager
echo.

pause

