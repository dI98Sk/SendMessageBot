@echo off
REM Скрипт для остановки всех микросервисов (Windows)

echo 🛑 Остановка всех микросервисов...
echo.

REM Остановка процессов Python с main.py (Broadcaster)
taskkill /FI "WINDOWTITLE eq Broadcaster Service*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *main.py*" /T /F >nul 2>&1

REM Остановка процессов Python с google_sheets_updater/main.py
taskkill /FI "WINDOWTITLE eq Google Sheets Updater*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *google_sheets_updater*main.py*" /T /F >nul 2>&1

echo ✅ Команды остановки выполнены
echo.
echo ℹ️  Если процессы не остановились, используйте Task Manager
echo.

pause

