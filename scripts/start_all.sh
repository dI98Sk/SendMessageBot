#!/bin/bash
# Скрипт для запуска обоих микросервисов одновременно

echo "🚀 Запуск всех микросервисов..."
echo ""

# Проверка виртуального окружения
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Виртуальное окружение активировано"
fi

# Создание директории для логов, если не существует
mkdir -p logs

# Функция для обработки сигналов
cleanup() {
    echo ""
    echo "🛑 Остановка всех сервисов..."
    kill $BROADCASTER_PID $UPDATER_PID 2>/dev/null
    wait $BROADCASTER_PID $UPDATER_PID 2>/dev/null
    echo "✅ Все сервисы остановлены"
    exit 0
}

# Регистрация обработчика сигналов
trap cleanup SIGINT SIGTERM

# Запуск Broadcaster Service в фоне
echo "📡 Запуск Broadcaster Service..."
python broadcaster/main.py > logs/broadcaster.log 2>&1 &
BROADCASTER_PID=$!
echo "   PID: $BROADCASTER_PID"
echo "   Логи: logs/broadcaster.log"

# Небольшая задержка перед запуском второго сервиса
sleep 2

# Запуск Google Sheets Updater Service в фоне
echo "📊 Запуск Google Sheets Updater Service..."
python google_sheets_updater/main.py > logs/updater.log 2>&1 &
UPDATER_PID=$!
echo "   PID: $UPDATER_PID"
echo "   Логи: logs/updater.log"

echo ""
echo "✅ Оба сервиса запущены!"
echo ""
echo "📋 Статус:"
echo "   - Broadcaster Service: PID $BROADCASTER_PID"
echo "   - Google Sheets Updater: PID $UPDATER_PID"
echo ""
echo "📝 Логи:"
echo "   - Broadcaster: tail -f logs/broadcaster.log"
echo "   - Updater: tail -f logs/updater.log"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

# Ожидание завершения процессов
wait $BROADCASTER_PID $UPDATER_PID

