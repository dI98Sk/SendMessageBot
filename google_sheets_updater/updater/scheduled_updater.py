"""
Планировщик для обновления таблиц по расписанию
"""
import asyncio
from datetime import datetime, time
from typing import Optional
import pytz

from google_sheets_updater.config.settings import UpdaterConfig
from google_sheets_updater.updater.telegram_fetcher import TelegramFetcher
from google_sheets_updater.updater.sheet_updater import SheetUpdater
from google_sheets_updater.utils.logger import get_logger


class ScheduledUpdater:
    """Класс для обновления таблиц по расписанию из Telegram канала"""
    
    def __init__(self, config: UpdaterConfig, sheet_updater: SheetUpdater):
        """
        Инициализация планировщика
        
        Args:
            config: Конфигурация сервиса
            sheet_updater: Экземпляр SheetUpdater для записи в таблицы
        """
        self.config = config
        self.sheet_updater = sheet_updater
        self.logger = get_logger(config.logging)
        self.telegram_fetcher = TelegramFetcher(config)
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
        # Время обновления: 11:00 по МСК
        self.update_time = time(11, 0)
        self.timezone = pytz.timezone('Europe/Moscow')  # МСК
    
    async def start(self):
        """Запуск планировщика"""
        if self.running:
            self.logger.warning("Планировщик уже запущен")
            return
        
        self.running = True
        await self.telegram_fetcher.initialize()
        
        self.logger.info("🚀 Запуск планировщика обновления из Telegram")
        self.logger.info(f"⏰ Время обновления: {self.update_time.strftime('%H:%M')} МСК")
        
        self._task = asyncio.create_task(self._scheduler_loop())
        await self._task
    
    async def stop(self):
        """Остановка планировщика"""
        if not self.running:
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.telegram_fetcher.close()
        self.logger.info("🛑 Планировщик остановлен")
    
    async def _scheduler_loop(self):
        """Основной цикл планировщика"""
        try:
            while self.running:
                # Вычисляем время до следующего обновления
                wait_seconds = self._get_seconds_until_update()
                
                if wait_seconds > 0:
                    self.logger.info(f"⏳ До следующего обновления: {wait_seconds/3600:.1f} часов")
                    await asyncio.sleep(wait_seconds)
                
                if self.running:
                    await self._perform_update()
                    
        except asyncio.CancelledError:
            self.logger.info("Цикл планировщика остановлен")
        except Exception as e:
            self.logger.exception(f"Ошибка в цикле планировщика: {e}")
    
    def _get_seconds_until_update(self) -> float:
        """
        Вычисление секунд до времени обновления (по МСК)
        
        Returns:
            float: Количество секунд до обновления
        """
        # Получаем текущее время в МСК
        now_moscow = datetime.now(self.timezone)
        
        # Создаем datetime для обновления сегодня в МСК
        update_datetime = self.timezone.localize(
            datetime.combine(now_moscow.date(), self.update_time)
        )
        
        # Если время уже прошло сегодня, планируем на завтра
        if update_datetime <= now_moscow:
            from datetime import timedelta
            tomorrow = now_moscow.date() + timedelta(days=1)
            update_datetime = self.timezone.localize(
                datetime.combine(tomorrow, self.update_time)
            )
        
        delta = (update_datetime - now_moscow).total_seconds()
        return delta
    
    async def _perform_update(self):
        """Выполнение обновления таблиц из Telegram канала"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🔄 Начало обновления таблиц из Telegram канала")
            self.logger.info("=" * 60)
            
            # Получаем ID канала из конфигурации
            import os
            channel_id = os.getenv("TELEGRAM_SOURCE_CHANNEL_ID")
            
            if not channel_id:
                self.logger.error("❌ TELEGRAM_SOURCE_CHANNEL_ID не установлен в конфигурации")
                return
            
            # Получаем последние 3 сообщения
            messages = await self.telegram_fetcher.get_latest_messages(channel_id, limit=3)
            
            if not messages:
                self.logger.warning("⚠️  Не получено сообщений из канала")
                return
            
            # Обрабатываем сообщения (удаляем последние 3 строки)
            processed_messages = []
            for msg in messages:
                processed = self.telegram_fetcher.process_message(msg)
                if processed.strip():  # Добавляем только непустые сообщения
                    processed_messages.append(processed)
            
            if not processed_messages:
                self.logger.warning("⚠️  После обработки не осталось сообщений")
                return
            
            self.logger.info(f"✅ Обработано {len(processed_messages)} сообщений")
            
            # Записываем в таблицы
            await self._write_to_sheets(processed_messages)
            
            self.logger.info("=" * 60)
            self.logger.info("✅ Обновление таблиц завершено успешно")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.exception(f"❌ Ошибка при обновлении таблиц: {e}")
    
    async def _write_to_sheets(self, messages: List[str]):
        """
        Запись сообщений в Google таблицы
        
        Args:
            messages: Список обработанных сообщений
        """
        import os
        
        # Таблицы для обновления
        sheets_to_update = [
            ("Прайсы AAA", os.getenv("BUY_SELL_PRICE_AAA_SHEET_URL")),
            ("Прайсы GUS", os.getenv("BUY_SELL_PRICE_GUS_SHEET_URL")),
        ]
        
        for sheet_name, sheet_url in sheets_to_update:
            if not sheet_url:
                self.logger.warning(f"⏭️  Пропуск {sheet_name}: URL не указан")
                continue
            
            try:
                await self._write_to_sheet(sheet_name, sheet_url, messages)
            except Exception as e:
                self.logger.error(f"❌ Ошибка записи в {sheet_name}: {e}")
    
    async def _write_to_sheet(self, sheet_name: str, sheet_url: str, messages: List[str]):
        """
        Запись сообщений в одну таблицу
        
        Args:
            sheet_name: Название таблицы (для логирования)
            sheet_url: URL таблицы
            messages: Список обработанных сообщений для записи
        """
        try:
            self.logger.info(f"📝 Запись в таблицу: {sheet_name}")
            
            # Открываем таблицу
            sheet = self.sheet_updater.sheets_client.open_sheet(sheet_url)
            worksheet = sheet.sheet1
            
            # Подготавливаем данные для записи
            # Записываем в первые 3 ячейки первого столбца (A1, A2, A3)
            data = []
            for message in messages[:3]:  # Берем максимум 3 сообщения
                # Записываем все сообщение целиком (уже обработанное, без последних 3 строк)
                data.append([message])
            
            # Если сообщений меньше 3, заполняем пустыми строками
            while len(data) < 3:
                data.append([''])
            
            # Записываем в первые 3 ячейки столбца A
            # Формат: [[message1], [message2], [message3]]
            worksheet.update('A1:A3', data)
            
            self.logger.info(f"✅ Таблица {sheet_name} обновлена: записано {len(data)} сообщений")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка записи в таблицу {sheet_name}: {e}")
            raise

