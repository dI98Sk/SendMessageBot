#!/usr/bin/env python3
"""
Скрипт для получения ID чатов из ссылок-приглашений
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
from config.settings import config_manager

async def get_chat_ids():
    """Получение ID чатов из ссылок"""
    print("=" * 70)
    print("🔍 ПОЛУЧЕНИЕ ID ЧАТОВ ИЗ ССЫЛОК-ПРИГЛАШЕНИЙ")
    print("=" * 70)
    
    # Ссылки на чаты
    invite_links = [
        "https://t.me/+viHvvuAuyNs2Yjli",  # ТЕСТ РЕКЛАМЫ 2
        "https://t.me/+KQvsVWUl8j4xYzJi",  # ТЕСТ РЕКЛАМЫ 1
    ]
    
    # Извлекаем хэши из ссылок
    invite_hashes = []
    for link in invite_links:
        # Убираем префикс https://t.me/+
        hash_part = link.replace("https://t.me/+", "").replace("https://t.me/joinchat/", "")
        invite_hashes.append(hash_part)
        print(f"📎 Ссылка: {link}")
        print(f"   Hash: {hash_part}")
    
    print("\n🔌 Подключение к Telegram...")
    
    # Загрузка конфигурации
    config = config_manager.load_config()
    
    # Создаем клиент (используем acc1)
    client = TelegramClient(
        "sessions/acc1",
        config.telegram.api_id,
        config.telegram.api_hash
    )
    
    try:
        await client.start()
        
        me = await client.get_me()
        print(f"✅ Подключено как: {me.first_name} (@{me.username or 'без username'})")
        
        chat_ids = []
        
        for i, (link, hash_code) in enumerate(zip(invite_links, invite_hashes), 1):
            print(f"\n{'='*70}")
            print(f"📱 Чат {i}: {link}")
            print(f"{'='*70}")
            
            try:
                # Сначала проверяем информацию о чате
                print("   🔍 Проверка чата...")
                try:
                    invite_info = await client(CheckChatInviteRequest(hash=hash_code))
                    print(f"   ℹ️  Название: {invite_info.title if hasattr(invite_info, 'title') else 'N/A'}")
                    
                    # Если уже состоим в чате
                    if hasattr(invite_info, 'chat'):
                        chat = invite_info.chat
                        chat_id = -chat.id if hasattr(chat, 'id') else None
                        if chat_id:
                            print(f"   ✅ Вы уже в этом чате!")
                            print(f"   🆔 ID: {chat_id}")
                            chat_ids.append(chat_id)
                            continue
                except Exception as e:
                    print(f"   ⚠️  Не удалось проверить: {e}")
                
                # Пробуем присоединиться
                print("   📥 Присоединение к чату...")
                result = await client(ImportChatInviteRequest(hash=hash_code))
                
                # Получаем информацию о чате
                if hasattr(result, 'chats') and result.chats:
                    chat = result.chats[0]
                    # Для групп и каналов ID отрицательный
                    if hasattr(chat, 'id'):
                        # Для supergroup/channel добавляем префикс -100
                        if hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast'):
                            chat_id = -1000000000000 - chat.id
                        else:
                            chat_id = -chat.id
                        
                        print(f"   ✅ Успешно присоединились!")
                        print(f"   📝 Название: {chat.title}")
                        print(f"   🆔 ID: {chat_id}")
                        chat_ids.append(chat_id)
                    else:
                        print(f"   ⚠️  Не удалось получить ID чата")
                else:
                    print(f"   ⚠️  Не удалось получить информацию о чате")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                # Пробуем альтернативный способ - поиск в диалогах
                print(f"   🔄 Пробуем найти чат в диалогах...")
                try:
                    async for dialog in client.iter_dialogs():
                        if hash_code in str(dialog.entity) or link in str(dialog.entity):
                            chat_id = dialog.id
                            print(f"   ✅ Найдено в диалогах!")
                            print(f"   📝 Название: {dialog.title}")
                            print(f"   🆔 ID: {chat_id}")
                            chat_ids.append(chat_id)
                            break
                except Exception as e2:
                    print(f"   ❌ Не удалось найти: {e2}")
        
        print(f"\n{'='*70}")
        print("📊 РЕЗУЛЬТАТ")
        print(f"{'='*70}")
        
        if chat_ids:
            print(f"\n✅ Получено ID чатов: {len(chat_ids)}")
            print("\n📋 Для добавления в config/targets.py:")
            print("\nTEST_TARGETS_ADS = [")
            for chat_id in chat_ids:
                print(f"    {chat_id},")
            print("]")
            
            # Сохраняем в файл
            output_file = Path(__file__).parent.parent / "test_ads_chat_ids.txt"
            with open(output_file, 'w') as f:
                f.write("TEST_TARGETS_ADS = [\n")
                for chat_id in chat_ids:
                    f.write(f"    {chat_id},\n")
                f.write("]\n")
            
            print(f"\n💾 Сохранено в: {output_file}")
        else:
            print("\n❌ Не удалось получить ID чатов")
            print("\n💡 Попробуйте:")
            print("   1. Убедитесь что аккаунт уже состоит в этих чатах")
            print("   2. Или используйте ID напрямую если они известны")
        
    finally:
        await client.disconnect()
        print("\n🔌 Отключено от Telegram")

if __name__ == "__main__":
    asyncio.run(get_chat_ids())
