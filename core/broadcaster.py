"""
Улучшенный класс Broadcaster с расширенной функциональностью
"""
import asyncio
import signal
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import pytz
from telethon import TelegramClient
from telethon.errors import FloodWaitError, RPCError, ChatWriteForbiddenError
from telethon.network.connection.tcpmtproxy import ConnectionTcpMTProxyIntermediate

from config.settings import TelegramConfig, BroadcastingConfig, AppConfig
from utils.logger import get_logger
from core.exceptions import BroadcastingError, ConfigurationError
from core.retry import retry_with_backoff
from monitoring.metrics import MetricsCollector, MessageMetric, BroadcastCycleMetric

@dataclass
class MessageStats:
    """Статистика отправки сообщений"""
    total_sent: int = 0
    total_failed: int = 0
    flood_waits: int = 0
    last_sent_time: Optional[datetime] = None
    errors: Dict[str, int] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = {}

class EnhancedBroadcaster:
    """Улучшенный класс для рассылки сообщений"""
    
    def __init__(self, config: AppConfig, name: str, targets: List[int], messages: List[str], session_name: Optional[str] = None):
        self.config = config
        self.name = name
        self.targets = targets
        self.messages = messages
        self.session_name = session_name or config.telegram.session_name
        
        # Статистика
        self.stats = MessageStats()
        self.metrics = MetricsCollector()
        
        # Состояние
        self._running = False
        self._client: Optional[TelegramClient] = None
        self._task: Optional[asyncio.Task] = None
        self._cycle_start_time: Optional[datetime] = None
        
        # Логгер
        self.logger = get_logger(f"broadcaster.{name}", config.logging)
        
        # Инициализация клиента
        self._init_client()
        
        # Регистрация обработчиков сигналов для graceful shutdown
        self._setup_signal_handlers()
    
    def _init_client(self):
        """Инициализация Telegram клиента"""
        try:
            telegram_config = self.config.telegram
            
            if telegram_config.proxy and telegram_config.proxy.enabled:
                if telegram_config.proxy.protocol == "mtproto":
                    self._client = TelegramClient(
                        self.session_name,
                        telegram_config.api_id,
                        telegram_config.api_hash,
                        connection=ConnectionTcpMTProxyIntermediate,
                        proxy=(
                            telegram_config.proxy.addr,
                            telegram_config.proxy.port,
                            telegram_config.proxy.secret
                        ),
                    )
                else:
                    # Поддержка других типов прокси
                    self._client = TelegramClient(
                        self.session_name,
                        telegram_config.api_id,
                        telegram_config.api_hash,
                        proxy=telegram_config.proxy
                    )
            else:
                self._client = TelegramClient(
                    self.session_name,
                    telegram_config.api_id,
                    telegram_config.api_hash
                )
                
            self.logger.info(f"Клиент {self.name} инициализирован с сессией {self.session_name}")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации клиента {self.name}: {e}")
            raise BroadcastingError(f"Не удалось инициализировать клиент: {e}")
    
    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов"""
        def signal_handler(signum, frame):
            self.logger.info(f"Получен сигнал {signum}, завершаем работу...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    @retry_with_backoff(max_retries=3, base_delay=1)
    async def _send_single_message(self, target: int, message: str, message_idx: int) -> bool:
        """Отправка одного сообщения с retry логикой"""
        start_time = datetime.now()
        response_time = 0.0
        flood_wait_duration = 0
        error_type = None
        success = False

        try:
            await self._client.send_message(target, message)
            self.stats.total_sent += 1
            self.stats.last_sent_time = datetime.now()
            success = True
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(
                f"Отправлено сообщение №{message_idx} в {target} "
                f"(всего отправлено: {self.stats.total_sent})"
            )

            
        except FloodWaitError as e:
            self.stats.flood_waits += 1
            wait_time = e.seconds
            flood_wait_duration = wait_time
            error_type = "FloodWaitError"
            
            self.logger.warning(
                f"FloodWait: ждём {wait_time} секунд для {target}. "
                f"Всего FloodWait: {self.stats.flood_waits}"
            )
            
            await asyncio.sleep(wait_time)
            # Повторяем отправку после ожидания
            return await self._send_single_message(target, message, message_idx)
            
        except ChatWriteForbiddenError as e:
            self.stats.total_failed += 1
            self.stats.errors["ChatWriteForbidden"] = self.stats.errors.get("ChatWriteForbidden", 0) + 1
            error_type = "ChatWriteForbiddenError"
            self.logger.error(f"Нет прав на отправку в чат {target}")

            
        except RPCError as e:
            self.stats.total_failed += 1
            error_type = f"RPCError_{e.code}"
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            self.logger.error(f"RPC ошибка при отправке в {target}: {e}")
            
        except Exception as e:
            self.stats.total_failed += 1
            error_type = type(e).__name__
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            self.logger.error(f"Неожиданная ошибка при отправке в {target}: {e}")

        finally:
            # Записываем метрику
            metric = MessageMetric(
                timestamp=start_time,
                chat_id=target,
                message_id=message_idx,
                success=success,
                error_type=error_type,
                response_time=response_time,
                flood_wait_duration=flood_wait_duration
            )
            self.metrics.record_message(metric)

        return success
    
    async def _send_messages_cycle(self):
        """Выполнение одного цикла рассылки"""
        cycle_start = datetime.now()
        self._cycle_start_time = cycle_start

        self.logger.info(f"Начинаем цикл рассылки для {self.name}")

        total_messages = len(self.messages) * len(self.targets)
        successful_messages = 0
        failed_messages = 0
        flood_waits_count = 0
        
        for idx, message in enumerate(self.messages, start=1):
            self.logger.info(f"Отправляем сообщение №{idx} из {len(self.messages)}")
            
            # Отправляем во все целевые чаты
            for target in self.targets:
                success = await self._send_single_message(target, message, idx)
                if success:
                    successful_messages += 1
                else:
                    failed_messages += 1
                
                # Задержка между чатами
                if self.config.broadcasting.delay_between_chats > 0:
                    await asyncio.sleep(self.config.broadcasting.delay_between_chats)



        # Записываем метрику цикла
        cycle_end = datetime.now()
        cycle_duration = (cycle_end - cycle_start).total_seconds()

        cycle_metric = BroadcastCycleMetric(
            start_time=cycle_start,
            end_time=cycle_end,
            total_messages=total_messages,
            successful_messages=successful_messages,
            failed_messages=failed_messages,
            total_duration=cycle_duration,
            flood_waits_count=flood_waits_count
        )
        self.metrics.record_cycle(cycle_metric)

        # Логируем статистику
        self._log_stats()
    
    def _log_stats(self):
        """Логирование статистики"""
        self.logger.info(
            f"Статистика {self.name}: "
            f"отправлено: {self.stats.total_sent}, "
            f"ошибок: {self.stats.total_failed}, "
            f"FloodWait: {self.stats.flood_waits}"
        )
        
        if self.stats.errors:
            self.logger.info(f"Типы ошибок: {dict(self.stats.errors)}")
    
    def _wait_until_start_time(self) -> float:
        """Ожидание времени начала рассылки"""
        if not self.config.broadcasting.enable_scheduling:
            return 0
        
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(moscow_tz)
        start_time = now.replace(
            hour=self.config.broadcasting.start_time_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        if now.hour < self.config.broadcasting.start_time_hour:
            seconds_to_wait = (start_time - now).total_seconds()
            self.logger.info(
                f"Сейчас {now.strftime('%H:%M')}, "
                f"ждём до {start_time.strftime('%H:%M')} "
                f"({seconds_to_wait/60:.1f} мин.)"
            )
            return seconds_to_wait
        
        return 0
    
    @retry_with_backoff(max_retries=3, base_delay=5)
    async def _ensure_connection(self):
        """Обеспечение подключения к Telegram"""
        if not self._client or not self._client.is_connected():
            self.logger.info(f"Подключаемся к Telegram для {self.name}...")
            await self._client.start()
            
            # Получаем информацию о текущем пользователе
            me = await self._client.get_me()
            account_id = me.id
            account_name = f"{me.first_name or ''} {me.last_name or ''}".strip()
            
            self.logger.info(f"Подключение {self.name} установлено: ID={account_id}, Name={account_name}")
            print(f"✅ {self.name} подключен: ID={account_id}, Name={account_name}")
    
    async def start(self):
        """Запуск broadcaster"""
        if self._running:
            self.logger.warning(f"Broadcaster {self.name} уже запущен")
            return
        
        self._running = True
        self.logger.info(f"Запуск broadcaster {self.name}")
        
        try:
            # Ожидание времени начала
            wait_time = self._wait_until_start_time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # Основной цикл
            while self._running:
                try:
                    await self._ensure_connection()
                    await self._send_messages_cycle()
                    
                    self.logger.info(
                        f"Цикл завершён. Ждём {self.config.broadcasting.cycle_delay} секунд..."
                    )
                    await asyncio.sleep(self.config.broadcasting.cycle_delay)
                    
                except Exception as e:
                    self.logger.exception(f"Ошибка в цикле рассылки: {e}")
                    await asyncio.sleep(self.config.broadcasting.retry_delay)
                    
        except asyncio.CancelledError:
            self.logger.info(f"Broadcaster {self.name} получил сигнал остановки")
        except Exception as e:
            self.logger.exception(f"Критическая ошибка в broadcaster {self.name}: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановка broadcaster"""
        if not self._running:
            return
        
        self.logger.info(f"Остановка broadcaster {self.name}")
        self._running = False
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._client and self._client.is_connected():
            await self._client.disconnect()
            self.logger.info(f"Broadcaster {self.name} отключен")
        
        # Финальная статистика
        self._log_stats()
    
    def run(self) -> asyncio.Task:
        """Запуск broadcaster в фоновом режиме"""
        if self._task and not self._task.done():
            self.logger.warning(f"Broadcaster {self.name} уже запущен")
            return self._task
        
        self._task = asyncio.create_task(self.start())
        return self._task
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики"""
        return {
            "name": self.name,
            "running": self._running,
            "total_sent": self.stats.total_sent,
            "total_failed": self.stats.total_failed,
            "flood_waits": self.stats.flood_waits,
            "last_sent_time": self.stats.last_sent_time.isoformat() if self.stats.last_sent_time else None,
            "errors": dict(self.stats.errors),
            "targets_count": len(self.targets),
            "messages_count": len(self.messages)
        }

    def get_detailed_stats(self) -> Dict[str, Any]:
        """Получение детальной статистики с метриками"""
        basic_stats = self.get_stats()
        metrics_summary = self.metrics.get_summary_stats()

        return {
            "basic": basic_stats,
            "metrics": metrics_summary,
            "performance": {
                "avg_response_time": self.metrics.stats.get('avg_response_time', 0),
                "success_rate": self.metrics.stats.get('success_rate', 0),
                "cycles_completed": self.metrics.stats.get('total_cycles_completed', 0),
                "last_activity": self.metrics.stats.get('last_activity')
            }
        }

    def print_stats(self):
        """Вывод статистики в консоль"""
        stats = self.get_detailed_stats()

        print(f"\n📊 Статистика {self.name}")
        print("=" * 50)

        # Базовая статистика
        basic = stats["basic"]
        print(f"🎯 Целевых чатов: {basic['targets_count']}")
        print(f"💬 Сообщений: {basic['messages_count']}")
        print(f"✅ Отправлено: {basic['total_sent']}")
        print(f"❌ Ошибок: {basic['total_failed']}")
        print(f"⏳ FloodWait: {basic['flood_waits']}")

        # Производительность
        perf = stats["performance"]
        print(f"📈 Процент успешности: {perf['success_rate']:.1f}%")
        print(f"⚡ Среднее время ответа: {perf['avg_response_time']:.2f}с")
        print(f"🔄 Циклов завершено: {perf['cycles_completed']}")

        # Ошибки
        if basic['errors']:
            print(f"🚨 Типы ошибок:")
            for error_type, count in basic['errors'].items():
                print(f"   - {error_type}: {count}")

        print("=" * 50)

