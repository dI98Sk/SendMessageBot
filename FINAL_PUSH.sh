#!/bin/bash
# Финальный push в GitHub

echo "════════════════════════════════════════════════════════════════════"
echo "  🚀 PUSH В GITHUB"
echo "════════════════════════════════════════════════════════════════════"
echo ""

cd /Users/papaskakun/PycharmProjects/SendMessageBot

# Настроить credential helper
git config --global credential.helper osxkeychain

# Push
echo "Выполняется push в GitHub..."
git push origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════════"
    echo "  ✅ УСПЕШНО ЗАПУШЕНО В GITHUB!"
    echo "════════════════════════════════════════════════════════════════════"
    echo ""
    echo "📝 ТЕПЕРЬ НА СЕРВЕРЕ ВЫПОЛНИТЕ:"
    echo ""
    echo "   cd C:\Users\Administrator\PycharmProjects\SendMessageBot_v2"
    echo "   mkdir sessions"
    echo "   git pull origin master"
    echo "   python main.py"
    echo ""
    echo "════════════════════════════════════════════════════════════════════"
    echo "  🎉 ГОТОВО К ЗАПУСКУ НА СЕРВЕРЕ!"
    echo "════════════════════════════════════════════════════════════════════"
else
    echo ""
    echo "════════════════════════════════════════════════════════════════════"
    echo "  ❌ ОШИБКА PUSH"
    echo "════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Возможные причины:"
    echo "  1. Нет доступа к GitHub (проверьте SSH ключ или токен)"
    echo "  2. Нет интернета"
    echo "  3. Проблемы с авторизацией"
    echo ""
    echo "Попробуйте вручную:"
    echo "  git push origin master"
fi

