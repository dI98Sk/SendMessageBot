import asyncio
import logging
import os
from dotenv import load_dotenv

from config_mesВ2B import MESSAGESB2B
from config_targ import TEST_TARGETS, TARGETS
from broadcasterB2B import Broadcaster

load_dotenv()

# Общая настройка логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Вывод в консоль
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)

# Вывод в файл
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

configs = [
    {
        "session_name": "acc1",
        "api_id": API_ID,
        "api_hash": API_HASH,
        "targets": TEST_TARGETS,
        "messages": MESSAGESB2B,
        "proxy": None,
        "name": "acc1",
    },
    {
        "session_name": "acc2",
        "api_id": API_ID,
        "api_hash": API_HASH,
        "targets": TEST_TARGETS,
        "messages": MESSAGESB2B,
        "proxy": {
            "mtproto": True,
            "addr": "87.248.134.64",
            "port": 8888,
            "secret": "79e344818749bd7ac519130220c25d09"
        },
        "name": "acc2",
    },
]

async def main():
    broadcasters = [Broadcaster(**cfg) for cfg in configs]
    await asyncio.gather(*(b.run_forever() for b in broadcasters))

if __name__ == "__main__":
    asyncio.run(main())