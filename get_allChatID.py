from telethon import TelegramClient

api_id = 20308310
api_hash = 'd50674e451f373a5bde51e2f29c2e221'

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()
    async for dialog in client.iter_dialogs():
        username = getattr(dialog.entity, 'username', None)
        print(f'Name: {dialog.name}, ID: {dialog.id}, Username: {username}')

with client:
    client.loop.run_until_complete(main())
