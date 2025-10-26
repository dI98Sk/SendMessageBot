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

@dataclass
class DeferredMessage:
    """Отложенное сообщение для отправки в следующий цикл"""
    chat_id: int
    message: str
    message_idx: int
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3

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
        
        # 🕐 Rate limiting: отслеживание последних отправок в каждый чат
        # Формат: {chat_id: datetime последней отправки}
        self._last_send_times: Dict[int, datetime] = {}
        
        # 📬 Очередь отложенных сообщений (для отправки в следующий цикл)
        self._deferred_messages: List[DeferredMessage] = []
        
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
            
            # Проверяем и создаем директорию для сессий
            from pathlib import Path
            session_path = Path(self.session_name)
            session_dir = session_path.parent
            
            if session_dir and str(session_dir) != '.':
                session_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Директория для сессий: {session_dir}")
            
            # Проверяем существование файла сессии
            session_file = Path(f"{self.session_name}.session")
            if not session_file.exists():
                self.logger.warning(f"⚠️  Файл сессии {session_file} не найден")
                self.logger.warning(f"При первом запуске потребуется авторизация")
            else:
                self.logger.info(f"✅ Файл сессии найден: {session_file}")
            
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
            self.logger.error(f"Проверьте:")
            self.logger.error(f"  1. Существует ли директория для сессии")
            self.logger.error(f"  2. Есть ли права на запись в директорию")
            self.logger.error(f"  3. Правильно ли указан путь к сессии: {self.session_name}")
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

        # 📬 Обработка отложенных сообщений из предыдущего цикла
        if self._deferred_messages:
            self.logger.info(f"📬 Обрабатываем {len(self._deferred_messages)} отложенных сообщений")
            deferred_to_retry = []
            
            for deferred_msg in self._deferred_messages:
                # Проверяем, прошло ли достаточно времени
                can_send, wait_time = self._can_send_to_chat(
                    deferred_msg.chat_id, 
                    min_interval_seconds=self.config.broadcasting.min_interval_per_chat
                )
                
                if can_send:
                    # Пытаемся отправить
                    deferred_msg.attempts += 1
                    success = await self._send_single_message(
                        deferred_msg.chat_id, 
                        deferred_msg.message, 
                        deferred_msg.message_idx
                    )
                    
                    if success:
                        self._update_chat_send_time(deferred_msg.chat_id)
                        self.logger.info(
                            f"✅ Отложенное сообщение для чата {deferred_msg.chat_id} успешно отправлено "
                            f"(попытка {deferred_msg.attempts}/{deferred_msg.max_attempts})"
                        )
                    elif deferred_msg.attempts < deferred_msg.max_attempts:
                        # Сохраняем для следующей попытки
                        deferred_to_retry.append(deferred_msg)
                        self.logger.warning(
                            f"⚠️ Отложенное сообщение для чата {deferred_msg.chat_id} не отправлено. "
                            f"Останется на попытку {deferred_msg.attempts}/{deferred_msg.max_attempts}"
                        )
                    else:
                        self.logger.error(
                            f"❌ Отложенное сообщение для чата {deferred_msg.chat_id} не удалось отправить "
                            f"после {deferred_msg.max_attempts} попыток. Удаляется из очереди."
                        )
                else:
                    # Ещё рано - оставляем в очереди
                    deferred_to_retry.append(deferred_msg)
            
            # Обновляем очередь отложенных
            self._deferred_messages = deferred_to_retry
            
            if deferred_to_retry:
                self.logger.info(f"📬 В очереди осталось {len(deferred_to_retry)} отложенных сообщений")

        total_messages = len(self.messages) * len(self.targets)
        successful_messages = 0
        failed_messages = 0
        flood_waits_count = 0
        
        for idx, message in enumerate(self.messages, start=1):
            # Проверяем, не наступил ли тихий час во время рассылки
            if self._is_quiet_hour():
                self.logger.info(f"🌙 Наступил тихий час во время рассылки. Прерываем текущий цикл.")
                break
            
            self.logger.info(f"Отправляем сообщение №{idx} из {len(self.messages)}")
            
            # Отправляем во все целевые чаты
            for target in self.targets:
                # Проверяем тихий час перед каждым сообщением
                if self._is_quiet_hour():
                    self.logger.info(f"🌙 Наступил тихий час. Останавливаем рассылку.")
                    break
                
                # 🕐 Проверка rate limiting: не отправляем в один чат чаще чем установленный интервал
                min_interval = self.config.broadcasting.min_interval_per_chat
                can_send, wait_time = self._can_send_to_chat(target, min_interval_seconds=min_interval)
                if not can_send:
                    self.logger.info(
                        f"⏳ Пропускаем чат {target}: прошло только {min_interval - wait_time:.1f} сек с последней отправки. "
                        f"Нужно подождать ещё {wait_time:.1f} сек. (Интервал: {min_interval} сек)"
                    )
                    # 📬 Откладываем сообщение для отправки в следующем цикле
                    self._defer_message(target, message, idx)
                    continue
                
                success = await self._send_single_message(target, message, idx)
                
                # Обновляем время последней отправки и статистику только при успехе
                if success:
                    self._update_chat_send_time(target)
                    successful_messages += 1
                else:
                    failed_messages += 1
                
                # 🕐 ЗАДЕРЖКА МЕЖДУ ЧАТАМИ - здесь примените задержку между отправками в разные чаты
                # Используется значение из: config.broadcasting.delay_between_chats (по умолчанию 15 сек)
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
            f"FloodWait: {self.stats.flood_waits}, "
            f"отложенных: {len(self._deferred_messages)}"
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
    
    def _is_quiet_hour(self) -> bool:
        """Проверка, находимся ли мы в тихом часе"""
        if not self.config.broadcasting.enable_quiet_hours:
            return False
        
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(moscow_tz)
        current_hour = now.hour
        
        quiet_start = self.config.broadcasting.quiet_hour_start
        quiet_end = self.config.broadcasting.quiet_hour_end
        
        # Проверка, находится ли текущее время в диапазоне тихого часа
        return quiet_start <= current_hour < quiet_end
    
    def _can_send_to_chat(self, chat_id: int, min_interval_seconds: int = 120) -> tuple[bool, float]:
        """
        Проверка, можно ли отправить сообщение в чат (не чаще чем раз в N секунд)
        
        Args:
            chat_id: ID чата
            min_interval_seconds: Минимальный интервал между отправками в секундах (по умолчанию 120 = 2 минуты)
        
        Returns:
            tuple[bool, float]: (можно ли отправить, сколько секунд нужно подождать)
        """
        now = datetime.now()
        
        # Если чат не в истории - можно отправлять сразу
        if chat_id not in self._last_send_times:
            return True, 0
        
        # Вычисляем время с последней отправки
        last_send_time = self._last_send_times[chat_id]
        time_since_last = (now - last_send_time).total_seconds()
        
        # Если прошло достаточно времени - можно отправлять
        if time_since_last >= min_interval_seconds:
            return True, 0
        
        # Нужно подождать
        wait_time = min_interval_seconds - time_since_last
        return False, wait_time
    
    def _update_chat_send_time(self, chat_id: int):
        """Обновление времени последней отправки в чат"""
        self._last_send_times[chat_id] = datetime.now()
    
    def _defer_message(self, chat_id: int, message: str, message_idx: int):
        """Сохранить сообщение в очередь отложенных для отправки в следующем цикле"""
        deferred = DeferredMessage(
            chat_id=chat_id,
            message=message,
            message_idx=message_idx,
            created_at=datetime.now(),
            attempts=0,
            max_attempts=3
        )
        self._deferred_messages.append(deferred)
        self.logger.info(
            f"📬 Сообщение для чата {chat_id} отложено. Всего отложенных: {len(self._deferred_messages)}"
        )
    
    def _wait_until_quiet_hour_ends(self) -> float:
        """Вычисление времени ожидания до окончания тихого часа"""
        if not self._is_quiet_hour():
            return 0
        
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(moscow_tz)
        end_time = now.replace(
            hour=self.config.broadcasting.quiet_hour_end,
            minute=0,
            second=0,
            microsecond=0
        )
        
        seconds_to_wait = (end_time - now).total_seconds()
        self.logger.info(
            f"🌙 Тихий час (с {self.config.broadcasting.quiet_hour_start:02d}:00 до {self.config.broadcasting.quiet_hour_end:02d}:00). "
            f"Сейчас {now.strftime('%H:%M')}, ждём до {end_time.strftime('%H:%M')} "
            f"({seconds_to_wait/60:.1f} мин.)"
        )
        
        return seconds_to_wait
    
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
            username = me.username or "без username"
            
            # Определяем тип аккаунта по имени broadcaster'а
            account_type = "ОПТОВЫЙ" if "B2B" in self.name or "AAA" in self.name else "РОЗНИЧНЫЙ"
            
            self.logger.info(f"✅ Подключено как {account_name} (@{username})")
            self.logger.info(f"📱 ID аккаунта: {account_id}")
            self.logger.info(f"🏷️  Тип аккаунта: {account_type}")
            self.logger.info(f"📊 Broadcaster: {self.name}")
            self.logger.info(f"🎯 Целевых чатов: {len(self.targets)}")
            self.logger.info(f"💬 Сообщений: {len(self.messages)}")
            
            print(f"✅ {self.name} подключен: {account_name} (@{username})")
            print(f"📱 ID: {account_id} | Тип: {account_type}")
            print(f"🎯 Чатов: {len(self.targets)} | 💬 Сообщений: {len(self.messages)}")
    
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
                    # Проверка тихого часа перед началом цикла
                    quiet_wait_time = self._wait_until_quiet_hour_ends()
                    if quiet_wait_time > 0:
                        await asyncio.sleep(quiet_wait_time)
                        continue  # После окончания тихого часа начинаем новый цикл
                    
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

