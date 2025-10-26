#!/usr/bin/env python3
"""
Упрощенный скрипт для настройки Telegram аккаунтов
"""
import asyncio
import os
import sys
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def setup_account(session_name: str, account_type: str):
    """Настройка одного аккаунта"""
    print(f"\n🔐 НАСТРОЙКА {account_type} АККАУНТА")
    print("=" * 50)
    
    # Получаем API данные
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    
    print(f"📱 Подключение к Telegram для {account_type} аккаунта...")
    print(f"🔑 API_ID: {api_id}")
    print(f"📝 Сессия: {session_name}.session")
    print("\n📞 Введите номер телефона в международном формате (+7XXXXXXXXXX):")
    
    # Создаем клиент
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        # Запускаем клиент (это запросит авторизацию)
        await client.start()
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        account_id = me.id
        account_name = f"{me.first_name or ''} {me.last_name or ''}".strip()
        username = me.username or "без username"
        
        print(f"\n✅ {account_type} аккаунт успешно настроен!")
        print(f"👤 Имя: {account_name}")
        print(f"📱 Username: @{username}")
        print(f"🆔 ID: {account_id}")
        print(f"💾 Сессия сохранена: {session_name}.session")
        
        # Отключаемся
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Ошибка настройки {account_type} аккаунта: {e}")
        try:
            await client.disconnect()
        except:
            pass

async def main():
    """Главная функция"""
    print("🚀 НАСТРОЙКА TELEGRAM АККАУНТОВ")
    print("=" * 50)
    
    # Проверяем API данные
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Ошибка: не найдены API_ID и API_HASH в .env файле")
        return
    
    print("Настройка аккаунтов для броудкастеров:")
    print("• acc1 (ОПТОВЫЙ) - для B2B и AAA броудкастеров")
    print("• acc2 (РОЗНИЧНЫЙ) - для B2C и GUS броудкастеров")
    
    # Настраиваем первый аккаунт
    await setup_account("sessions/acc1", "ОПТОВЫЙ")
    
    input("\nНажмите Enter для настройки второго аккаунта...")
    
    # Настраиваем второй аккаунт
    await setup_account("sessions/acc2", "РОЗНИЧНЫЙ")
    
    print("\n🎉 Настройка завершена!")
    print("Теперь можно запускать main_improved.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Прерывание пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
