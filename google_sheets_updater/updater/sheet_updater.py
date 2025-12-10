"""
Основной класс для обновления Google таблиц
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from google_sheets_updater.config.settings import UpdaterConfig
from google_sheets_updater.utils.logger import get_logger
from shared.google_sheets.client import GoogleSheetsClient


class SheetUpdater:
    """Класс для автоматического обновления Google таблиц"""
    
    def __init__(self, config: UpdaterConfig):
        """
        Инициализация updater
        
        Args:
            config: Конфигурация сервиса
        """
        self.config = config
        self.logger = get_logger(config.logging)
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
        # Инициализация Google Sheets клиента
        try:
            self.sheets_client = GoogleSheetsClient(config.google_sheets.credentials_file)
            self.logger.info("✅ Google Sheets клиент инициализирован")
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Google Sheets клиента: {e}")
            raise
    
    async def start(self):
        """Запуск сервиса обновления"""
        if self.running:
            self.logger.warning("Сервис уже запущен")
            return
        
        self.running = True
        self.logger.info("🚀 Запуск Google Sheets Updater Service")
        self.logger.info(f"⏰ Интервал обновления: {self.config.update_interval_seconds} секунд")
        
        if self.config.enable_auto_update:
            # Запускаем цикл автоматического обновления
            self._task = asyncio.create_task(self._update_loop())
            await self._task
        else:
            # Выполняем одно обновление
            await self.update_all_sheets()
    
    async def stop(self):
        """Остановка сервиса"""
        if not self.running:
            return
        
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("🛑 Google Sheets Updater Service остановлен")
    
    async def _update_loop(self):
        """Основной цикл обновления"""
        try:
            # Первоначальное обновление
            await self.update_all_sheets()
            
            # Циклическое обновление
            while self.running:
                await asyncio.sleep(self.config.update_interval_seconds)
                if self.running:
                    await self.update_all_sheets()
        except asyncio.CancelledError:
            self.logger.info("Цикл обновления остановлен")
        except Exception as e:
            self.logger.exception(f"Ошибка в цикле обновления: {e}")
    
    async def update_all_sheets(self):
        """Обновление всех таблиц"""
        self.logger.info("=" * 60)
        self.logger.info("🔄 Начало обновления всех таблиц")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        updated_count = 0
        error_count = 0
        
        # Список таблиц для обновления
        sheets_to_update = [
            ("Прайсы AAA", self.config.google_sheets.price_aaa_sheet_url),
            ("Прайсы GUS", self.config.google_sheets.price_gus_sheet_url),
            ("Реклама AAA", self.config.google_sheets.ads_aaa_sheet_url),
            ("Реклама GUS", self.config.google_sheets.ads_gus_sheet_url),
        ]
        
        for sheet_name, sheet_url in sheets_to_update:
            if not sheet_url:
                self.logger.debug(f"⏭️  Пропуск {sheet_name}: URL не указан")
                continue
            
            try:
                success = await self.update_sheet(sheet_name, sheet_url)
                if success:
                    updated_count += 1
                else:
                    error_count += 1
            except Exception as e:
                self.logger.error(f"❌ Ошибка обновления {sheet_name}: {e}")
                error_count += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info("=" * 60)
        self.logger.info(f"✅ Обновление завершено: {updated_count} успешно, {error_count} ошибок")
        self.logger.info(f"⏱️  Время выполнения: {duration:.2f} секунд")
        self.logger.info("=" * 60)
    
    async def update_sheet(self, sheet_name: str, sheet_url: str) -> bool:
        """
        Обновление одной таблицы
        
        Args:
            sheet_name: Название таблицы (для логирования)
            sheet_url: URL таблицы
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            self.logger.info(f"📊 Обновление таблицы: {sheet_name}")
            
            # TODO: Здесь будет логика получения данных из источника
            # Пока заглушка
            data = await self._fetch_data_for_sheet(sheet_name)
            
            if not data:
                self.logger.warning(f"⚠️  Нет данных для обновления {sheet_name}")
                return False
            
            # Обновление таблицы
            await self._write_to_sheet(sheet_url, data)
            
            self.logger.info(f"✅ Таблица {sheet_name} обновлена: {len(data)} строк")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления таблицы {sheet_name}: {e}")
            return False
    
    async def _fetch_data_for_sheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        Получение данных для таблицы из источника
        
        Args:
            sheet_name: Название таблицы
            
        Returns:
            List[Dict]: Данные для записи
        """
        # TODO: Реализовать получение данных из источников
        # Это будет зависеть от конкретных источников данных
        self.logger.debug(f"Получение данных для {sheet_name}...")
        
        # Заглушка - возвращаем пустой список
        return []
    
    async def _write_to_sheet(self, sheet_url: str, data: List[Dict[str, Any]]):
        """
        Запись данных в Google таблицу
        
        Args:
            sheet_url: URL таблицы
            data: Данные для записи
        """
        # TODO: Реализовать запись в таблицу
        # Использовать self.sheets_client для записи
        self.logger.debug(f"Запись {len(data)} строк в таблицу...")
        
        # Заглушка
        pass

