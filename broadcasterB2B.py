# broadcast_refactor.py
"""
Refactor: Broadcaster class to encapsulate message-sending logic with Telethon.
Usage:
  - Place this file in your project (e.g. lib/broadcast_refactor.py)
  - Create a small `runner` script (example below) which creates several Broadcaster
    instances (one per account) and runs them concurrently with asyncio.gather.

Notes/choices made:
  - The class keeps its own TelegramClient instance so you can run many in parallel.
  - You pass session name, api_id, api_hash and other runtime options when creating the object.
  - The class exposes `start()` and `run_forever()` coroutines. `run_forever()` contains
    the main send loop and can be used with asyncio.create_task or asyncio.gather.
  - Basic error handling (FloodWaitError, RPCError, generic exceptions) is kept.
  - Scheduling (update_config) is left to the runner; the class will call update_config once on start by default.

Do not forget to install telethon and pytz if you haven't:
    pip install telethon pytz python-dotenv schedule

"""
import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient
from telethon.errors import FloodWaitError, RPCError
from telethon.network.connection.tcpmtproxy import ConnectionTcpMTProxyIntermediate
import socks  # для SOCKS/HTTP прокси
from update_configB2B import update_config  # подтягиваем из корня проекта

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class Broadcaster:
    def __init__(
        self,
        session_name: str,
        api_id,
        api_hash,
        targets,
        messages,
        proxy=None,
        moscow_tz=pytz.timezone("Europe/Moscow"),
        delay_between_chats: int = 5,
        cycle_delay: int = 15 * 60,
        run_update_config_on_start: bool = True,
        name: str | None = None,
    ):
        self.session_name = session_name
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.targets = list(targets)
        self.messages = list(messages)
        self.proxy = proxy
        self.moscow_tz = moscow_tz
        self.delay_between_chats = delay_between_chats
        self.cycle_delay = cycle_delay
        self.name = name or session_name
        self.run_update_config_on_start = run_update_config_on_start

        self._client = self._init_client(proxy)
        self._running = False
        self._task = None

        self.logger = logging.getLogger(f"broadcaster.{self.name}")


    def _init_client(self, proxy):
        """Создаём клиент с учётом типа прокси."""
        if proxy and isinstance(proxy, dict) and proxy.get("mtproto"):
            return TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash,
                connection=ConnectionTcpMTProxyIntermediate,
                proxy=(proxy["addr"], proxy["port"], proxy["secret"]),
            )
        else:
            return TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash,
                proxy=proxy,
            )

    def wait_until_start_time(self) -> float:
        now = datetime.now(self.moscow_tz)
        start_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now.hour < 6:
            seconds_to_wait = (start_time - now).total_seconds()
            self.logger.info(
                f"{self.name}: Сейчас {now.strftime('%H:%M')}, ждём до 06:00 ({seconds_to_wait/60:.1f} мин.)"
            )
            return seconds_to_wait
        return 0

    async def _send_messages_once(self):
        for idx, message in enumerate(self.messages, start=1):
            self.logger.info(f"{self.name}: Начинаем рассылку сообщения №{idx}")
            for target in self.targets:
                try:
                    await self._client.send_message(target, message)
                    self.logger.info(f"{self.name}: Отправлено сообщение №{idx} в {target}")
                except FloodWaitError as e:
                    self.logger.warning(f"{self.name}: FloodWait: ждём {e.seconds} секунд")
                    await asyncio.sleep(e.seconds)
                except RPCError as e:
                    self.logger.error(f"{self.name}: Ошибка RPC: {e}")
                except Exception as e:
                    self.logger.exception(f"{self.name}: Неизвестная ошибка: {e}")
                await asyncio.sleep(self.delay_between_chats)

    async def start(self):
        if not self._client.is_connected():
            self.logger.info(f"{self.name}: Подключаемся к Telegram...")
            await self._client.start()
            self.logger.info(f"{self.name}: Подключено")

    async def stop(self):
        self._running = False
        if self._client.is_connected():
            await self._client.disconnect()
            self.logger.info(f"{self.name}: Отключен")

    async def run_forever(self):
        self._running = True
        if self.run_update_config_on_start:
            try:
                update_config()
            except Exception:
                self.logger.exception(f"{self.name}: Ошибка в update_config() на старте")

        while self._running:
            # Закоментил что бы потестить ночью
            # wait_time = self.wait_until_start_time()
            # if wait_time > 0:
            #     await asyncio.sleep(wait_time)

            try:
                await self.start()
                await self._send_messages_once()
                self.logger.info(f"{self.name}: Цикл завершён. Ждём {self.cycle_delay} секунд...")
                await asyncio.sleep(self.cycle_delay)
            except Exception as e:
                self.logger.exception(f"{self.name}: Ошибка: {e}. Переподключение через 60 сек...")
                await asyncio.sleep(60)

    def run(self) -> asyncio.Task:
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self.run_forever())
        return self._task


# If you want to run this module directly for quick manual testing:
# if __name__ == "__main__":
#     import os
#     from dotenv import load_dotenv
#
#     load_dotenv()
#     logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
#
#     async def demo():
#         api_id = int(os.getenv("API_ID"))
#         api_hash = os.getenv("API_HASH")
#         # two different session files for demo; change to real ones for real accounts
#         configs = [
#             {"session_name": "session_account_1", "api_id": api_id, "api_hash": api_hash, "name": "acc1"},
#             {"session_name": "session_account_2", "api_id": api_id, "api_hash": api_hash, "name": "acc2"},
#         ]
#         broadcasters = make_broadcasters(configs)
#         # run all broadcasters concurrently
#         await asyncio.gather(*(b.run_forever() for b in broadcasters))
#
#     asyncio.run(demo())
