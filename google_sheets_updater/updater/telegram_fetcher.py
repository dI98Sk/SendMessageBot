"""
Модуль для получения сообщений из Telegram канала
"""
import asyncio
from typing import List, Optional
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError

from google_sheets_updater.config.settings import UpdaterConfig
from google_sheets_updater.utils.logger import get_logger


class TelegramFetcher:
    """Класс для получения сообщений из Telegram канала"""
    
    def __init__(self, config: UpdaterConfig):
        """
        Инициализация Telegram клиента
        
        Args:
            config: Конфигурация сервиса
        """
        self.config = config
        self.logger = get_logger(config.logging)
        self._client: Optional[TelegramClient] = None
        self._initialized = False
    
    async def initialize(self):
        """Инициализация Telegram клиента"""
        if self._initialized:
            return
        
        try:
            # Получаем конфигурацию Telegram из переменных окружения
            import os
            api_id = os.getenv("TELEGRAM_API_ID")
            api_hash = os.getenv("TELEGRAM_API_HASH")
            session_name = os.getenv("TELEGRAM_SESSION_NAME", "sessions/updater_session")
            
            if not api_id or not api_hash:
                raise ValueError("TELEGRAM_API_ID и TELEGRAM_API_HASH должны быть установлены")
            
            self.logger.info("🔌 Инициализация Telegram клиента для получения сообщений...")
            
            # Создаем клиент
            self._client = TelegramClient(
                session_name,
                int(api_id),
                api_hash
            )
            
            # Подключаемся
            await self._client.start()
            
            # Проверяем авторизацию
            if not await self._client.is_user_authorized():
                raise ValueError("Telegram клиент не авторизован. Запустите setup_accounts.py")
            
            me = await self._client.get_me()
            self.logger.info(f"✅ Telegram клиент подключен: {me.first_name} (@{me.username})")
            
            self._initialized = True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Telegram клиента: {e}")
            raise
    
    async def get_latest_messages(self, channel_id: str, limit: int = 3) -> List[str]:
        """
        Получение последних сообщений из канала
        
        Args:
            channel_id: ID канала (может быть числом или username)
            limit: Количество сообщений для получения
            
        Returns:
            List[str]: Список текстов сообщений
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"📥 Получение последних {limit} сообщений из канала {channel_id}...")
            
            # Получаем канал
            try:
                # Пробуем как числовой ID
                if channel_id.lstrip('-').isdigit():
                    entity = await self._client.get_entity(int(channel_id))
                else:
                    # Пробуем как username
                    entity = await self._client.get_entity(channel_id)
            except Exception as e:
                self.logger.error(f"❌ Ошибка получения канала {channel_id}: {e}")
                raise
            
            # Получаем последние сообщения
            messages = []
            async for message in self._client.iter_messages(entity, limit=limit):
                if message.text:
                    messages.append(message.text)
            
            # Переворачиваем список, чтобы получить в хронологическом порядке (старые -> новые)
            messages.reverse()
            
            self.logger.info(f"✅ Получено {len(messages)} сообщений из канала")
            return messages
            
        except ChannelPrivateError:
            self.logger.error(f"❌ Канал {channel_id} приватный или недоступен")
            raise
        except ChatAdminRequiredError:
            self.logger.error(f"❌ Нет прав доступа к каналу {channel_id}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения сообщений из канала: {e}")
            raise
    
    def process_message(self, message: str) -> str:
        """
        Обработка сообщения: удаление последних 3 строк
        
        Args:
            message: Исходное сообщение
            
        Returns:
            str: Обработанное сообщение (без последних 3 строк)
        """
        if not message or not message.strip():
            return ""
        
        lines = message.split('\n')
        
        # Удаляем последние 3 строки
        if len(lines) > 3:
            processed_lines = lines[:-3]
            processed_message = '\n'.join(processed_lines)
        else:
            # Если строк меньше или равно 3, возвращаем пустую строку
            # (так как все строки будут удалены)
            processed_message = ""
        
        return processed_message
    
    async def close(self):
        """Закрытие Telegram клиента"""
        if self._client:
            await self._client.disconnect()
            self.logger.info("🔌 Telegram клиент отключен")

