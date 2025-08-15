import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient
from telethon.errors import FloodWaitError, RPCError
from config import TEST_TARGETS, TARGETS, MESSAGES

# ==================
# НАСТРОЙКА ЛОГГЕРА
# ==================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # лог в файл
        logging.StreamHandler()  # вывод в консоль
    ]
)

logger = logging.getLogger(__name__)

api_id = 20308310
api_hash = 'd50674e451f373a5bde51e2f29c2e221'

client = TelegramClient('session_name', api_id, api_hash)

# Server: 87.248.134.64
# Port: 8888
# Secret: 79e344818749bd7ac519130220c25d09

# Если хотите использовать MTProto Proxy:
proxy = ('87.248.134.64', 8888, '79e344818749bd7ac519130220c25d09')  # пример формата (IP, порт, секрет)

# Используем либо тестовые цели, либо реальные
# targets = TEST_TARGETS  # можно заменить на TARGETS когда будем отправлять в реальные чаты
targets = TARGETS  # можно заменить на TARGETS когда будем отправлять в реальные чаты

# ==================
# ВРЕМЕННОЕ ОГРАНИЧЕНИЕ
# ==================
moscow_tz = pytz.timezone("Europe/Moscow")

def wait_until_start_time():
    """Ждёт до 06:00 по Москве, если сейчас ночь."""
    now = datetime.now(moscow_tz)
    start_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # Если время после полуночи, а до 06:00
    if now.hour < 6:
        seconds_to_wait = (start_time - now).total_seconds()
        logger.info(f"Сейчас {now.strftime('%H:%M')}, ждём до 06:00 ({seconds_to_wait/60:.1f} мин.)")
        return seconds_to_wait
    elif now.hour >= 0 and now.hour < 6:
        seconds_to_wait = (start_time - now).total_seconds()
        logger.info(f"Ждём до 06:00, осталось {seconds_to_wait/60:.1f} мин.")
        return seconds_to_wait
    elif now.hour >= 0 and now.hour < 24:
        return 0  # Рабочее время
    return 0


async def send_messages():
    # Внешний цикл — по сообщениям
    for idx, message in enumerate(MESSAGES, start=1):
        logger.info(f"Начинаем рассылку сообщения №{idx}")
        # Внутренний цикл — по чатам
        for target in targets:
            try:
                await client.send_message(target, message)
                # print(f"Отправлено сообщение №{idx} в {target}")
                logger.info(f"Отправлено сообщение №{idx} в {target}")
            except FloodWaitError as e:
                logger.warning(f"FloodWait: ждем {e.seconds} секунд перед отправкой в {target}")
                await asyncio.sleep(e.seconds)
            except RPCError as e:
                logger.error(f"Ошибка RPC при отправке сообщения №{idx} в {target}: {e}")
            except Exception as e:
                logger.error(f"Неизвестная ошибка при отправке сообщения №{idx} в {target}: {e}")
            await asyncio.sleep(5)  # пауза между чатами

async def main():
    while True:
        wait_time = wait_until_start_time()
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        try:
            print("Подключаемся к Telegram...")
            logger.info("Подключаемся к Telegram...")
            await client.start()
            print("Подключение успешно!")
            logger.info("Подключение успешно!")
            await send_messages()
            print("Цикл завершён. Ждём 15 минут...")
            logger.info("Цикл завершён. Ждём 15 минут...")
            await asyncio.sleep(15 * 60)  # 15 минут между циклами
        except Exception as e:
            print(f"Ошибка подключения или выполнения: {e}. Переподключаемся через 60 секунд...")
            logger.error(f"Ошибка подключения или выполнения: {e}. Переподключаемся через 60 секунд...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())