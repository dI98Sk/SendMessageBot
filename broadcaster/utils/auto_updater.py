"""
Автоматический обновлятель всех сообщений из Google Sheets
Обновляет: прайсы AAA/GUS и рекламу AAA/GUS
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import logging

from shared.google_sheets.fetcher import GoogleSheetsFetcher
from broadcaster.utils.logger import get_logger

class AutoMessageUpdater:
    """Автоматический обновлятель всех сообщений"""
    
    def __init__(self, credentials_file: str, config):
        self.credentials_file = credentials_file
        self.config = config
        self.fetcher = GoogleSheetsFetcher(credentials_file)
        self.logger = get_logger("auto_updater", config.logging)
        
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.last_update_time: Optional[datetime] = None
        self.update_callback: Optional[Callable] = None
        
        # Счетчики обновлений
        self.updates_count = 0
        self.errors_count = 0
    
    def set_update_callback(self, callback: Callable):
        """Установить callback для уведомления об обновлениях"""
        self.update_callback = callback
    
    async def update_all_messages(self) -> Dict[str, Any]:
        """Обновить все типы сообщений"""
        self.logger.info("🔄 Начинаем обновление всех сообщений из Google Sheets...")
        
        results = {
            'aaa_price': {'success': False, 'count': 0, 'error': None},
            'gus_price': {'success': False, 'count': 0, 'error': None},
            'aaa_ads': {'success': False, 'count': 0, 'error': None},
            'gus_ads': {'success': False, 'count': 0, 'error': None},
        }
        
        messages_updated = False
        
        # Обновление прайсов AAA
        if self.config.google_sheets.aaa_sheet_url:
            try:
                self.logger.info("📥 Загрузка прайсов AAA...")
                # fetch_messages не async, убираем await
                aaa_messages = self.fetcher.fetch_messages(
                    self.config.google_sheets.aaa_sheet_url
                )
                
                if aaa_messages:
                    await self._save_messages_to_file(
                        aaa_messages, 
                        'config/messages_aaa.py',
                        'MESSAGESAAA',
                        'Прайсы AAA'
                    )
                    results['aaa_price'] = {'success': True, 'count': len(aaa_messages), 'error': None}
                    messages_updated = True
                    self.logger.info(f"✅ Прайсы AAA обновлены: {len(aaa_messages)} сообщений")
            except Exception as e:
                self.logger.error(f"❌ Ошибка обновления прайсов AAA: {e}")
                results['aaa_price']['error'] = str(e)
        
        # Обновление прайсов GUS
        if self.config.google_sheets.gus_sheet_url:
            try:
                self.logger.info("📥 Загрузка прайсов GUS...")
                # fetch_messages не async, убираем await
                gus_messages = self.fetcher.fetch_messages(
                    self.config.google_sheets.gus_sheet_url
                )
                
                if gus_messages:
                    await self._save_messages_to_file(
                        gus_messages,
                        'config/messages_gus.py',
                        'MESSAGESGUS',
                        'Прайсы GUS'
                    )
                    results['gus_price'] = {'success': True, 'count': len(gus_messages), 'error': None}
                    messages_updated = True
                    self.logger.info(f"✅ Прайсы GUS обновлены: {len(gus_messages)} сообщений")
            except Exception as e:
                self.logger.error(f"❌ Ошибка обновления прайсов GUS: {e}")
                results['gus_price']['error'] = str(e)
        
        # Обновление рекламы AAA
        if self.config.google_sheets.aaa_ads_sheet_url:
            try:
                self.logger.info("📥 Загрузка рекламы AAA...")
                # fetch_messages не async, убираем await
                aaa_ads_messages = self.fetcher.fetch_messages(
                    self.config.google_sheets.aaa_ads_sheet_url
                )
                
                if aaa_ads_messages:
                    await self._save_messages_to_file(
                        aaa_ads_messages,
                        'config/messages_aaa_ads.py',
                        'MESSAGES_AAA_ADS',
                        'Реклама AAA'
                    )
                    results['aaa_ads'] = {'success': True, 'count': len(aaa_ads_messages), 'error': None}
                    messages_updated = True
                    self.logger.info(f"✅ Реклама AAA обновлена: {len(aaa_ads_messages)} сообщений")
            except Exception as e:
                self.logger.error(f"❌ Ошибка обновления рекламы AAA: {e}")
                results['aaa_ads']['error'] = str(e)
        
        # Обновление рекламы GUS
        if self.config.google_sheets.gus_ads_sheet_url:
            try:
                self.logger.info("📥 Загрузка рекламы GUS...")
                # fetch_messages не async, убираем await
                gus_ads_messages = self.fetcher.fetch_messages(
                    self.config.google_sheets.gus_ads_sheet_url
                )
                
                if gus_ads_messages:
                    await self._save_messages_to_file(
                        gus_ads_messages,
                        'config/messages_gus_ads.py',
                        'MESSAGES_GUS_ADS',
                        'Реклама GUS'
                    )
                    results['gus_ads'] = {'success': True, 'count': len(gus_ads_messages), 'error': None}
                    messages_updated = True
                    self.logger.info(f"✅ Реклама GUS обновлена: {len(gus_ads_messages)} сообщений")
            except Exception as e:
                self.logger.error(f"❌ Ошибка обновления рекламы GUS: {e}")
                results['gus_ads']['error'] = str(e)
        
        # Обновляем счетчики
        if messages_updated:
            self.updates_count += 1
            self.last_update_time = datetime.now()
            
            # Вызываем callback если установлен
            if self.update_callback:
                try:
                    await self.update_callback(results)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback обновления: {e}")
        else:
            self.errors_count += 1
        
        return results
    
    async def _save_messages_to_file(self, messages: list, file_path: str, 
                                     var_name: str, description: str):
        """Сохранить сообщения в Python файл"""
        full_path = Path(__file__).parent.parent / file_path
        
        # Создаем содержимое файла
        content = f'"""\n{description}\n'
        content += 'Автоматически обновлено из Google Sheets\n'
        content += f'Дата обновления: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        content += '"""\n\n'
        content += f'{var_name} = [\n'
        
        for i, msg in enumerate(messages, 1):
            # Экранируем кавычки и специальные символы
            escaped_msg = msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            content += f'    # Сообщение {i}\n'
            content += f'    "{escaped_msg}",\n\n'
        
        content += ']\n'
        
        # Сохраняем файл
        full_path.write_text(content, encoding='utf-8')
        self.logger.debug(f"Файл {file_path} обновлен")
    
    async def _update_loop(self, interval_hours: float):
        """Основной цикл обновления"""
        self.logger.info(f"🔄 Запущен автоматический обновлятель сообщений")
        self.logger.info(f"⏰ Интервал обновления: {interval_hours} часов")
        
        # Первое обновление сразу при запуске
        try:
            self.logger.info("📊 Выполняем первоначальное обновление...")
            results = await self.update_all_messages()
            
            success_count = sum(1 for r in results.values() if r['success'])
            self.logger.info(f"✅ Первоначальное обновление завершено: {success_count}/4 типов")
        except Exception as e:
            self.logger.error(f"❌ Ошибка первоначального обновления: {e}")
        
        # ⚠️ ВРЕМЕННО ОТКЛЮЧЕНО: Периодические обновления отключены для стабильности
        # Сообщения обновляются только при запуске приложения
        self.logger.info("⚠️ Периодическое обновление временно отключено для стабильности")
        self.logger.info("ℹ️ Сообщения обновлены при запуске, дальнейшие обновления не выполняются")
        
        # Ожидаем завершения задачи (но не выполняем обновления)
        while self.running:
            try:
                # Ждем долго, чтобы задача не завершалась, но не выполняем обновления
                await asyncio.sleep(3600)  # 1 час
                
                if not self.running:
                    break
                
            except asyncio.CancelledError:
                self.logger.info("🛑 Автообновление остановлено")
                break
            except Exception as e:
                self.logger.error(f"❌ Ошибка в цикле обновления: {e}")
                await asyncio.sleep(60)  # Подождать минуту перед повтором
    
    async def start(self, interval_hours: float = 1.0):
        """Запустить автоматическое обновление"""
        if self.running:
            self.logger.warning("Автообновление уже запущено")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._update_loop(interval_hours))
        self.logger.info("✅ Автоматический обновлятель запущен")
    
    async def stop(self):
        """Остановить автоматическое обновление"""
        if not self.running:
            return
        
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("🛑 Автоматический обновлятель остановлен")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус обновлятеля"""
        return {
            'running': self.running,
            'last_update': self.last_update_time.isoformat() if self.last_update_time else None,
            'updates_count': self.updates_count,
            'errors_count': self.errors_count,
        }


