# ========================================
# Скрипт первоначального запуска SendMessageBot на Windows (PowerShell)
# ========================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 ПЕРВОНАЧАЛЬНЫЙ ЗАПУСК SendMessageBot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия Python
Write-Host "Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка: Python не найден!" -ForegroundColor Red
    Write-Host "   Установите Python 3.8+ и добавьте его в PATH" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host ""

# Шаг 1: Создание виртуального окружения
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📦 ШАГ 1: Создание виртуального окружения" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "⚠️  Виртуальное окружение уже существует" -ForegroundColor Yellow
    Write-Host "   Пропускаем создание..." -ForegroundColor Yellow
} else {
    Write-Host "Создаем виртуальное окружение..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Ошибка при создании виртуального окружения!" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    Write-Host "✅ Виртуальное окружение создано" -ForegroundColor Green
}
Write-Host ""

# Шаг 2: Активация виртуального окружения
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔌 ШАГ 2: Активация виртуального окружения" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при активации виртуального окружения!" -ForegroundColor Red
    Write-Host "   Возможно, нужно разрешить выполнение скриптов:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "✅ Виртуальное окружение активировано" -ForegroundColor Green
Write-Host ""

# Шаг 3: Установка зависимостей
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📥 ШАГ 3: Установка зависимостей" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Ошибка: файл requirements.txt не найден!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "Устанавливаем зависимости из requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при установке зависимостей!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "✅ Зависимости установлены" -ForegroundColor Green
Write-Host ""

# Шаг 4: Настройка аккаунтов (опционально)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔐 ШАГ 4: Настройка Telegram аккаунтов" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "sessions\acc1.session") {
    Write-Host "⚠️  Файлы сессий уже существуют" -ForegroundColor Yellow
    Write-Host "   Пропускаем настройку аккаунтов..." -ForegroundColor Yellow
    Write-Host "   Если нужно пересоздать сессии, удалите папку sessions" -ForegroundColor Yellow
} else {
    Write-Host "Настраиваем Telegram аккаунты..." -ForegroundColor Yellow
    Write-Host "   (Этот шаг можно пропустить, нажав Ctrl+C)" -ForegroundColor Yellow
    Write-Host ""
    python scripts\setup_accounts.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Ошибка при настройке аккаунтов (можно продолжить)" -ForegroundColor Yellow
        Write-Host "   Убедитесь, что файлы сессий созданы вручную" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Аккаунты настроены" -ForegroundColor Green
    }
}
Write-Host ""

# Шаг 5: Проверка .env файла
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "⚙️  ШАГ 5: Проверка конфигурации" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  ВНИМАНИЕ: файл .env не найден!" -ForegroundColor Yellow
    Write-Host "   Создайте файл .env на основе .env.example" -ForegroundColor Yellow
    Write-Host "   Или настройте переменные окружения" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Продолжить без .env? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Прервано пользователем" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "✅ Файл .env найден" -ForegroundColor Green
}
Write-Host ""

# Шаг 6: Запуск бота
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 ШАГ 6: Запуск SendMessageBot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Все готово! Запускаем бота..." -ForegroundColor Green
Write-Host "   Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Бот завершился с ошибкой" -ForegroundColor Red
    Write-Host "   Проверьте логи в папке logs/" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Read-Host "Нажмите Enter для выхода"

