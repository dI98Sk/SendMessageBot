from telethon import TelegramClient, sync

api_id = 20308310  # api_id
api_hash = 'd50674e451f373a5bde51e2f29c2e221'  # замените на свой api_hash (строка)
phone = '+79850194274'  # номер телефона в международном формате

client = TelegramClient('session_name', api_id, api_hash)


async def main():
    await client.start(phone)

    # Название чата или его ID, куда нужно отправить сообщение
    target = -1002679672234 # Name: ТЕСТ Рассылок 2, ID: -1002679672234, Username: send2message


    message = "Привет! Это тестовое рекламное сообщение."

    await client.send_message(target, message)
    print("Сообщение отправлено!")


with client:
    client.loop.run_until_complete(main())