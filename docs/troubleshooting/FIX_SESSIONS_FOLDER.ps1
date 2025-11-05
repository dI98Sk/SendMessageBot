# PowerShell скрипт для создания папки sessions на сервере
# Запустите: .\FIX_SESSIONS_FOLDER.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  СОЗДАНИЕ ПАПКИ SESSIONS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = Get-Location
Write-Host "Текущая директория: $projectPath" -ForegroundColor Green
Write-Host ""

# Создать папку sessions
$sessionsPath = Join-Path $projectPath "sessions"

if (Test-Path $sessionsPath) {
    Write-Host "Папка sessions уже существует: $sessionsPath" -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Path $sessionsPath -Force | Out-Null
    Write-Host "Создана папка sessions: $sessionsPath" -ForegroundColor Green
}

Write-Host ""

# Проверить права на запись
try {
    $testFile = Join-Path $sessionsPath "test.txt"
    "test" | Out-File $testFile
    Remove-Item $testFile
    Write-Host "Проверка прав: OK - можно создавать файлы" -ForegroundColor Green
} catch {
    Write-Host "Проверка прав: ОШИБКА - нет прав на запись!" -ForegroundColor Red
    Write-Host "Запустите PowerShell от имени администратора" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ГОТОВО! Теперь можно запускать setup_accounts.py" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

