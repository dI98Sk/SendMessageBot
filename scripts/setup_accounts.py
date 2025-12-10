#!/usr/bin/env python3
"""
Скрипт для настройки Telegram аккаунтов и создания файлов сессий
для всех broadcaster'ов
"""
import asyncio
import os
import sys
import shutil
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def create_session_copies(base_session: str, account_name: str):
    """Создает копии файла сессии для broadcaster'ов"""
    print(f"\n📋 Создание копий сессии для {account_name}...")
    
    base_file = Path(f"{base_session}.session")
    
    if not base_file.exists():
        print(f"❌ Файл {base_file} не существует!")
        return False
    
    # Определяем какие копии нужны (acc1 или acc2)
    if "acc1" in base_session:
        # acc1 = Яблочный Гусь → GUS бренд
        copies = [
            ("sessions/acc1_price", "GUS_PRICE_Broadcaster"),
            ("sessions/acc1_ads", "GUS_ADS_Broadcaster"),
            ("sessions/acc1_b2c", "GUS_B2C_Broadcaster"),
            ("sessions/acc1_b2c_midslow", "GUS_B2C_MIDSLOW_Broadcaster")
        ]
    else:
        # acc2 = Анна Макарова → AAA бренд
        copies = [
            ("sessions/acc2_price", "AAA_PRICE_Broadcaster"),
            ("sessions/acc2_ads", "AAA_ADS_Broadcaster")
        ]
    
    # Создаем копии
    for copy_path, broadcaster_name in copies:
        copy_file = Path(f"{copy_path}.session")
        
        # Проверяем существование
        if copy_file.exists():
            print(f"   ⏭️  {copy_file.name} уже существует (пропущено)")
        else:
            try:
                shutil.copy2(base_file, copy_file)
                print(f"   ✅ {copy_file.name} создан для {broadcaster_name}")
            except Exception as e:
                print(f"   ❌ Ошибка при создании {copy_file.name}: {e}")
                return False
    
    return True

async def setup_account(session_name: str, account_type: str, expected_name: str):
    """Настройка одного аккаунта"""
    print(f"\n{'=' * 70}")
    print(f"🔐 НАСТРОЙКА {account_type} АККАУНТА")
    print(f"{'=' * 70}")
    print(f"📝 Ожидаемый аккаунт: {expected_name}")
    print(f"💾 Файл сессии: {session_name}.session")
    
    # Проверяем существование файла
    session_file = Path(f"{session_name}.session")
    if session_file.exists():
        print(f"\n⚠️  Файл сессии уже существует!")
        response = input("Хотите пересоздать? (y/n): ").strip().lower()
        if response != 'y':
            print("⏭️  Пропущено")
            return None
    
    # Получаем API данные
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    
    print(f"\n📱 Подключение к Telegram...")
    print(f"🔑 API_ID: {api_id}")
    print(f"\n📞 Введите номер телефона в международном формате (+7XXXXXXXXXX):")
    
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
        
        # Проверяем соответствие ожидаемому аккаунту
        if expected_name.lower() not in account_name.lower():
            print(f"\n⚠️  ВНИМАНИЕ! Ожидался аккаунт: {expected_name}")
            print(f"⚠️  Подключен аккаунт: {account_name}")
            response = input("\nВсё равно использовать этот аккаунт? (y/n): ").strip().lower()
            if response != 'y':
                await client.disconnect()
                return None
        
        # Отключаемся
        await client.disconnect()
        return account_name
        
    except Exception as e:
        print(f"❌ Ошибка настройки {account_type} аккаунта: {e}")
        try:
            await client.disconnect()
        except:
            pass
        return None

async def main():
    """Главная функция"""
    print("\n" + "=" * 70)
    print("🚀 НАСТРОЙКА TELEGRAM АККАУНТОВ ДЛЯ BROADCASTER'ОВ")
    print("=" * 70)
    
    # Проверяем API данные
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    
    if not api_id or not api_hash:
        print("❌ Ошибка: не найдены API_ID и API_HASH в .env файле")
        return
    
    # Проверяем/создаем папку sessions
    sessions_dir = Path("sessions")
    if not sessions_dir.exists():
        sessions_dir.mkdir(parents=True)
        print(f"✅ Создана папка: {sessions_dir}")
    
    print("\n📊 СТРУКТУРА BROADCASTER'ОВ:")
    print("-" * 70)
    print("acc1 (Яблочный Гусь Менеджер) - РОЗНИЧНЫЙ:")
    print("  • GUS_PRICE_Broadcaster      → sessions/acc1_price.session")
    print("  • GUS_ADS_Broadcaster        → sessions/acc1_ads.session")
    print("  • GUS_B2C_Broadcaster        → sessions/acc1_b2c.session")
    print("  • GUS_B2C_MIDSLOW_Broadcaster → sessions/acc1_b2c_midslow.session")
    print()
    print("acc2 (Анна Макарова) - ОПТОВЫЙ:")
    print("  • AAA_PRICE_Broadcaster → sessions/acc2_price.session")
    print("  • AAA_ADS_Broadcaster   → sessions/acc2_ads.session")
    print("-" * 70)
    
    print("\n📝 Сначала настроим БАЗОВЫЕ аккаунты (acc1, acc2),")
    print("    затем автоматически создадим копии для broadcaster'ов.")
    
    input("\nНажмите Enter для начала...")
    
    # Настраиваем первый аккаунт (Яблочный Гусь)
    acc1_name = await setup_account(
        "sessions/acc1", 
        "acc1", 
        "Яблочный Гусь Менеджер"
    )
    
    if acc1_name:
        # Создаем копии для acc1
        create_session_copies("sessions/acc1", acc1_name)
    
    input("\n\nНажмите Enter для настройки второго аккаунта...")
    
    # Настраиваем второй аккаунт (Анна Макарова)
    acc2_name = await setup_account(
        "sessions/acc2", 
        "acc2", 
        "Анна Макарова"
    )
    
    if acc2_name:
        # Создаем копии для acc2
        create_session_copies("sessions/acc2", acc2_name)
    
    # Финальная сводка
    print("\n" + "=" * 70)
    print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
    print("=" * 70)
    
    # Проверяем все файлы
    print("\n📁 Проверка созданных файлов:")
    required_files = [
        ("sessions/acc1.session", "База для Яблочный Гусь"),
        ("sessions/acc1_price.session", "GUS_PRICE_Broadcaster"),
        ("sessions/acc1_ads.session", "GUS_ADS_Broadcaster"),
        ("sessions/acc1_b2c.session", "GUS_B2C_Broadcaster"),
        ("sessions/acc1_b2c_midslow.session", "GUS_B2C_MIDSLOW_Broadcaster"),
        ("sessions/acc2.session", "База для Анна Макарова"),
        ("sessions/acc2_price.session", "AAA_PRICE_Broadcaster"),
        ("sessions/acc2_ads.session", "AAA_ADS_Broadcaster"),
    ]
    
    all_ok = True
    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path:<30} ({description})")
        else:
            print(f"   ❌ {file_path:<30} ОТСУТСТВУЕТ!")
            all_ok = False
    
    if all_ok:
        print("\n✅ Все файлы сессий готовы!")
        print("🚀 Теперь можно запускать: python broadcaster/main.py")
    else:
        print("\n⚠️  Некоторые файлы отсутствуют. Проверьте логи выше.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Прерывание пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
