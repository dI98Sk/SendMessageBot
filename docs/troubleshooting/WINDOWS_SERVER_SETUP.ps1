# PowerShell скрипт для настройки сервера
# Запустите в PowerShell: .\WINDOWS_SERVER_SETUP.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  НАСТРОЙКА СЕРВЕРА ДЛЯ SENDMESSAGEBOT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\Users\Administrator\PycharmProjects\SendMessageBot"

# Проверка пути
if (-not (Test-Path $projectPath)) {
    Write-Host "Ошибка: Путь $projectPath не найден!" -ForegroundColor Red
    exit 1
}

Set-Location $projectPath
Write-Host "Текущая директория: $projectPath" -ForegroundColor Green
Write-Host ""

# Шаг 1: Создание копий файлов сессий
Write-Host "Шаг 1: Создание уникальных файлов сессий..." -ForegroundColor Yellow
Write-Host ""

$sessionsPath = "$projectPath\sessions"

if (Test-Path "$sessionsPath\acc1.session") {
    Copy-Item "$sessionsPath\acc1.session" "$sessionsPath\acc1_price.session" -Force
    Write-Host "  Создано: acc1_price.session" -ForegroundColor Green
    
    Copy-Item "$sessionsPath\acc1.session" "$sessionsPath\acc1_ads.session" -Force
    Write-Host "  Создано: acc1_ads.session" -ForegroundColor Green
} else {
    Write-Host "  ВНИМАНИЕ: acc1.session не найден!" -ForegroundColor Yellow
}

if (Test-Path "$sessionsPath\acc2.session") {
    Copy-Item "$sessionsPath\acc2.session" "$sessionsPath\acc2_price.session" -Force
    Write-Host "  Создано: acc2_price.session" -ForegroundColor Green
    
    Copy-Item "$sessionsPath\acc2.session" "$sessionsPath\acc2_ads.session" -Force
    Write-Host "  Создано: acc2_ads.session" -ForegroundColor Green
} else {
    Write-Host "  ВНИМАНИЕ: acc2.session не найден!" -ForegroundColor Yellow
}

Write-Host ""

# Шаг 2: Проверка файлов сессий
Write-Host "Шаг 2: Проверка файлов сессий..." -ForegroundColor Yellow
Write-Host ""

$sessionFiles = @(
    "acc1_price.session",
    "acc2_price.session",
    "acc1_ads.session",
    "acc2_ads.session"
)

$allSessionsOk = $true
foreach ($file in $sessionFiles) {
    $fullPath = "$sessionsPath\$file"
    if (Test-Path $fullPath) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  НЕТ: $file" -ForegroundColor Red
        $allSessionsOk = $false
    }
}

Write-Host ""

# Шаг 3: Проверка обязательных файлов
Write-Host "Шаг 3: Проверка обязательных файлов..." -ForegroundColor Yellow
Write-Host ""

$requiredFiles = @(
    "main.py",
    "config\settings.py",
    "core\broadcaster.py",
    "utils\auto_updater.py",
    "config\messages_aaa_ads.py",
    "config\messages_gus_ads.py"
)

$allFilesOk = $true
foreach ($file in $requiredFiles) {
    $fullPath = "$projectPath\$file"
    if (Test-Path $fullPath) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  НЕТ: $file - НУЖНО СКОПИРОВАТЬ!" -ForegroundColor Red
        $allFilesOk = $false
    }
}

Write-Host ""

# Шаг 4: Тест импорта
Write-Host "Шаг 4: Тест конфигурации..." -ForegroundColor Yellow
Write-Host ""

try {
    python -c "from config.settings import config_manager; c = config_manager.load_config(); print('  OK: Конфигурация загружается')"
    Write-Host "  Конфигурация: OK" -ForegroundColor Green
} catch {
    Write-Host "  Конфигурация: ОШИБКА!" -ForegroundColor Red
    Write-Host "  Проверьте config\settings.py" -ForegroundColor Yellow
    $allFilesOk = $false
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Итог
if ($allSessionsOk -and $allFilesOk) {
    Write-Host "  ВСЁ ГОТОВО К ЗАПУСКУ!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Запустите: python main.py" -ForegroundColor Green
} else {
    Write-Host "  ОБНАРУЖЕНЫ ПРОБЛЕМЫ!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Скопируйте недостающие файлы с локальной машины" -ForegroundColor Yellow
    Write-Host "  или обновите весь проект." -ForegroundColor Yellow
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

