from telethon import TelegramClient
from dotenv import load_dotenv
import os

# =======================
# Загружаем переменные из .env
# =======================
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
telegram_session_name = os.getenv("SESSION_NAME")

client = TelegramClient(telegram_session_name, api_id, api_hash)

async def main():
    await client.start()
    async for dialog in client.iter_dialogs():
        username = getattr(dialog.entity, 'username', None)
        print(f'Name: {dialog.name}, ID: {dialog.id}, Username: {username}')

with client:
    client.loop.run_until_complete(main())
