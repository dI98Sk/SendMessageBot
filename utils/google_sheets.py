""""
Модуль для работы с Google Sheets
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets"""

    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.client: Optional[gspread.Client] = None
        self.last_update = None
        self.cached_messages = {
            'b2b': [],
            'b2c': []
        }

    def _authenticate(self) -> bool:
        """Аутентификация в Google Sheets"""
        try:
            credentials_path = Path(self.credentials_file)
            
            if not credentials_path.exists():
                logger.error(f"❌ Файл учетных данных не найден: {self.credentials_file}")
                logger.error(f"Полный путь: {credentials_path.absolute()}")
                logger.error(f"Текущая директория: {Path.cwd()}")
                logger.error(f"Проверьте наличие файла credentials.json в корне проекта")
                return False
            
            # Проверяем размер файла
            file_size = credentials_path.stat().st_size
            if file_size == 0:
                logger.error(f"❌ Файл credentials.json пустой")
                return False
            
            logger.info(f"✅ Файл credentials.json найден: {credentials_path.absolute()}")

            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scope
            )
            self.client = gspread.authorize(creds)
            logger.info("✅ Успешная аутентификация в Google Sheets")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка аутентификации Google Sheets: {e}")
            
            # Специфичные советы для разных типов ошибок
            error_str = str(e).lower()
            if 'invalid jwt signature' in error_str or 'invalid_grant' in error_str:
                logger.error(f"")
                logger.error(f"🔧 Проблема с JWT подписью. Возможные причины:")
                logger.error(f"  1. Время на сервере не синхронизировано (проверьте: date)")
                logger.error(f"  2. Файл credentials.json поврежден или неправильный")
                logger.error(f"  3. Service Account удален или отозван")
                logger.error(f"  4. Скачайте новый файл credentials.json из Google Cloud Console")
                logger.error(f"")
            elif 'permission denied' in error_str:
                logger.error(f"")
                logger.error(f"🔧 Проблема с правами доступа:")
                logger.error(f"  1. Проверьте права на файл credentials.json")
                logger.error(f"  2. Service Account должен иметь доступ к таблице")
                logger.error(f"  3. Поделитесь таблицей с email из credentials.json")
                logger.error(f"")
            
            return False

    def _get_sheet_data(self, sheet_url: str, column: int = 1) -> List[str]:
        """Получение данных из столбца таблицы"""
        if not self.client:
            if not self._authenticate():
                return []

        try:
            sheet = self.client.open_by_url(sheet_url).sheet1
            values = sheet.col_values(column)

            # Фильтруем пустые значения
            messages = [msg.strip() for msg in values if msg.strip()]
            logger.info(f"Получено {len(messages)} сообщений из Google Sheets")
            return messages

        except Exception as e:
            logger.error(f"Ошибка получения данных из Google Sheets: {e}")
            return []

    async def fetch_messages_async(self, b2b_url: str, b2c_url: str) -> Dict[str, List[str]]:
        """Асинхронное получение сообщений"""
        def _fetch():
            b2b_messages = self._get_sheet_data(b2b_url) if b2b_url else []
            b2c_messages = self._get_sheet_data(b2c_url) if b2c_url else []
            return {
                'b2b': b2b_messages,
                'b2c': b2c_messages
            }

        # Выполняем в отдельном потоке, чтобы не блокировать event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _fetch)

        # Кэшируем результат
        self.cached_messages = result
        self.last_update = datetime.now()

        return result

    def get_cached_messages(self) -> Dict[str, List[str]]:
        """Получение кэшированных сообщений"""
        return self.cached_messages.copy()

    def is_update_needed(self, interval_hours: int = 24) -> bool:
        """Проверка, нужно ли обновление"""
        if not self.last_update:
            return True

        time_since_update = datetime.now() - self.last_update
        return time_since_update.total_seconds() >= (interval_hours * 3600)

    def get_last_update_info(self) -> Dict[str, Any]:
        """Информация о последнем обновлении"""
        return {
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'cached_b2b_count': len(self.cached_messages['b2b']),
            'cached_b2c_count': len(self.cached_messages['b2c']),
            'update_needed': self.is_update_needed()
        }

class MessageUpdater:
    """Класс для обновления сообщений в конфигурации"""

    def __init__(self, google_sheets_manager: GoogleSheetsManager):
        self.gs_manager = google_sheets_manager
        self.update_callbacks = []

    def add_update_callback(self, callback):
        """Добавление callback'а для обновления сообщений"""
        self.update_callbacks.append(callback)

    async def update_messages_from_sheets(self, b2b_url: str, b2c_url: str):
        """Обновление сообщений из Google Sheets"""
        try:
            logger.info("Начинаем обновление сообщений из Google Sheets...")

            # Получаем новые сообщения
            new_messages = await self.gs_manager.fetch_messages_async(b2b_url, b2c_url)

            if not new_messages['b2b'] and not new_messages['b2c']:
                logger.warning("Не удалось получить сообщения из Google Sheets")
                return False

            # Уведомляем все callback'и об обновлении
            for callback in self.update_callbacks:
                try:
                    await callback(new_messages)
                except Exception as e:
                    logger.error(f"Ошибка в callback обновления: {e}")

            logger.info(f"Сообщения обновлены: B2B={len(new_messages['b2b'])}, B2C={len(new_messages['b2c'])}")
            return True

        except Exception as e:
            logger.error(f"Ошибка обновления сообщений: {e}")
            return False

    async def start_periodic_updates(self, b2b_url: str, b2c_url: str, interval_hours: int = 24):
        """Запуск периодических обновлений"""
        logger.info(f"Запуск периодических обновлений каждые {interval_hours} часов")

        while True:
            try:
                if self.gs_manager.is_update_needed(interval_hours):
                    await self.update_messages_from_sheets(b2b_url, b2c_url)

                # Ждем 1 час перед следующей проверкой
                await asyncio.sleep(3600)

            except asyncio.CancelledError:
                logger.info("Периодические обновления остановлены")
                break
            except Exception as e:
                logger.error(f"Ошибка в периодических обновлениях: {e}")
                await asyncio.sleep(3600)  # Ждем час перед повтором
