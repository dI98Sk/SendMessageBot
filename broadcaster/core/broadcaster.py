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
import traceback

from broadcaster.config.settings import TelegramConfig, BroadcastingConfig, AppConfig
from broadcaster.utils.logger import get_logger
from broadcaster.core.exceptions import BroadcastingError, ConfigurationError
from broadcaster.core.retry import retry_with_backoff
from broadcaster.monitoring.metrics import MetricsCollector, MessageMetric, BroadcastCycleMetric
from broadcaster.core.coordinator import get_coordinator

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
    max_attempts: int = 5  # Увеличено с 3 до 5 попыток

class EnhancedBroadcaster:
    """Улучшенный класс для рассылки сообщений"""
    
    def __init__(self, config: AppConfig, name: str, targets: List[int], messages: List[str], 
                 session_name: Optional[str] = None, cycle_delay: Optional[int] = None,
                 delay_between_chats: Optional[float] = None, start_offset_seconds: int = 0):
        self.config = config
        self.name = name
        self.targets = targets
        self.messages = messages
        self.session_name = session_name or config.telegram.session_name
        
        # Индивидуальная задержка между циклами (если не указана - берем из конфигурации)
        self.cycle_delay = cycle_delay if cycle_delay is not None else config.broadcasting.cycle_delay
        
        # Индивидуальная задержка между чатами (если не указана - берем из конфигурации)
        self._custom_delay_between_chats = delay_between_chats
        
        # Смещение времени старта (для распределения нагрузки между broadcaster'ами)
        self._start_offset_seconds = start_offset_seconds
        
        # Для всех broadcaster'ов: отправляем одно случайное сообщение в каждый чат за цикл
        # Это оптимизирует время цикла и обеспечивает разнообразие сообщений
        self._use_single_random_message = True
        
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
        
        # 🎯 Адаптивная задержка: динамическое изменение задержек на основе ошибок
        # Используем индивидуальную задержку, если указана, иначе из конфигурации
        base_delay = self._custom_delay_between_chats if self._custom_delay_between_chats is not None else float(config.broadcasting.delay_between_chats)
        self._current_delay_between_chats: float = base_delay
        
        # Координатор для синхронизации с другими broadcaster'ами
        self._coordinator = None
        self._account_id = None  # Будет установлен при подключении
        self._error_streak: int = 0  # Количество последовательных ошибок
        self._success_streak: int = 0  # Количество последовательных успешных отправок
        self._last_flood_wait_time: Optional[datetime] = None
        
        # 📋 Список недоступных чатов (для пропуска в следующих циклах)
        self._blocked_chats: Dict[int, str] = {}  # {chat_id: reason}
        
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
    
    def _is_valid_chat_id(self, chat_id: int) -> bool:
        """
        Валидация chat_id перед отправкой
        
        Args:
            chat_id: ID чата для проверки
            
        Returns:
            bool: True если chat_id валиден и не заблокирован
        """
        # Проверка что chat_id это число
        if not isinstance(chat_id, int):
            self.logger.error(f"❌ Невалидный chat_id: {chat_id} (не является числом)")
            return False
        
        # Проверка формата Telegram chat_id
        # Для групп/каналов chat_id должен быть отрицательным
        # Обычно начинается с -100 для супергрупп/каналов
        if chat_id > 0:
            self.logger.error(
                f"❌ Невалидный chat_id: {chat_id} | "
                f"Группы/каналы должны иметь отрицательный ID (начинаться с -100) | "
                f"Положительные ID используются только для пользователей"
            )
            return False
        
        # Проверка что это не слишком короткий ID (минимальная длина для групп)
        # Telegram группы обычно имеют ID длиннее 10 цифр
        if abs(chat_id) < 1000000000:
            # Это может быть старая группа, но проверим
            if abs(chat_id) < 1000000:
                self.logger.warning(
                    f"⚠️ Подозрительный chat_id: {chat_id} | "
                    f"ID слишком короткий, возможно это не группа/канал"
                )
                # Не блокируем, но предупреждаем
        
        # Проверка что чат не в списке заблокированных
        if chat_id in self._blocked_chats:
            reason = self._blocked_chats[chat_id]
            self.logger.debug(f"⏭️  Пропускаем заблокированный чат {chat_id}: {reason}")
            return False
        
        return True
    
    def _adjust_delay_on_error(self):
        """
        Увеличение задержки после ошибки (адаптивная задержка)
        """
        if not self.config.broadcasting.adaptive_delay_enabled:
            return
        
        self._error_streak += 1
        self._success_streak = 0
        
        # Увеличиваем задержку при серии ошибок
        if self._error_streak >= 3:
            old_delay = self._current_delay_between_chats
            self._current_delay_between_chats = min(
                self._current_delay_between_chats * self.config.broadcasting.adaptive_delay_multiplier,
                self.config.broadcasting.max_delay_between_chats
            )
            
            if old_delay != self._current_delay_between_chats:
                self.logger.warning(
                    f"⚠️ Адаптивная задержка: увеличена с {old_delay:.1f}с до {self._current_delay_between_chats:.1f}с "
                    f"(серия ошибок: {self._error_streak})"
                )
    
    def _adjust_delay_on_success(self):
        """
        Уменьшение задержки после успешных отправок (адаптивная задержка)
        """
        if not self.config.broadcasting.adaptive_delay_enabled:
            return
        
        self._success_streak += 1
        self._error_streak = 0
        
        # Постепенно уменьшаем задержку при серии успехов
        if self._success_streak >= 10:
            old_delay = self._current_delay_between_chats
            base_delay = float(self.config.broadcasting.delay_between_chats)
            
            # Уменьшаем задержку, но не ниже базовой
            self._current_delay_between_chats = max(
                self._current_delay_between_chats / self.config.broadcasting.adaptive_delay_multiplier,
                base_delay
            )
            
            if old_delay != self._current_delay_between_chats:
                self.logger.info(
                    f"✅ Адаптивная задержка: уменьшена с {old_delay:.1f}с до {self._current_delay_between_chats:.1f}с "
                    f"(серия успехов: {self._success_streak})"
                )
            
            # Сбрасываем счетчик успехов
            self._success_streak = 0
    
    def _block_chat(self, chat_id: int, reason: str):
        """
        Добавление чата в список заблокированных (для пропуска в будущих циклах)
        
        Args:
            chat_id: ID чата
            reason: Причина блокировки
        """
        if chat_id not in self._blocked_chats:
            self._blocked_chats[chat_id] = reason
            self.logger.warning(f"🚫 Чат {chat_id} добавлен в список заблокированных: {reason}")
    
    @retry_with_backoff(max_retries=3, base_delay=1)
    async def _send_single_message(self, target: int, message: str, message_idx: int) -> bool:
        """Отправка одного сообщения с retry логикой"""
        start_time = datetime.now()
        response_time = 0.0
        flood_wait_duration = 0
        error_type = None
        error_details = None
        success = False

        # 🔍 Валидация chat_id перед отправкой
        if not self._is_valid_chat_id(target):
            self.stats.total_failed += 1
            error_type = "InvalidChatId"
            
            # Детальная диагностика
            if target > 0:
                error_details = f"Положительный ID {target} - это ID пользователя, а не группы/канала. Группы должны иметь отрицательный ID (начинаться с -100)"
            elif abs(target) < 1000000:
                error_details = f"ID {target} слишком короткий - возможно это не группа/канал или старая группа"
            elif target in self._blocked_chats:
                error_details = f"Чат {target} заблокирован: {self._blocked_chats[target]}"
            else:
                error_details = f"Чат {target} невалиден по неизвестной причине"
            
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            
            self.logger.error(
                f"❌ [{self.name}] InvalidChatId: {target} | "
                f"Сообщение №{message_idx} | "
                f"Причина: {error_details} | "
                f"Всего InvalidChatId: {self.stats.errors.get(error_type, 0)}"
            )
            
            # Блокируем чат, чтобы не пытаться отправлять снова
            if target not in self._blocked_chats:
                self._block_chat(target, error_details)
            
            return False

        try:
            # Проверяем подключение перед отправкой
            if not self._client or not self._client.is_connected():
                self.logger.warning(
                    f"⚠️ [{self.name}] Клиент не подключен для чата {target}, "
                    f"пытаемся переподключиться..."
                )
                await self._ensure_connection()
            
            # Получаем блокировку чата через координатор (если доступен)
            chat_lock_acquired = False
            if self._coordinator:
                try:
                    await self._coordinator.acquire_chat_lock(target)
                    chat_lock_acquired = True
                except Exception as e:
                    self.logger.debug(f"Не удалось получить блокировку чата {target}: {e}")
            
            try:
                await self._client.send_message(target, message)
                self.stats.total_sent += 1
                self.stats.last_sent_time = datetime.now()
                success = True
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Записываем отправку в координатор
                if self._coordinator:
                    try:
                        self._coordinator.record_send(self.name, target)
                    except Exception as e:
                        self.logger.debug(f"Не удалось записать отправку в координатор: {e}")
            finally:
                # Освобождаем блокировку
                if chat_lock_acquired and self._coordinator:
                    try:
                        self._coordinator.release_chat_lock(target)
                    except Exception as e:
                        self.logger.debug(f"Не удалось освободить блокировку чата {target}: {e}")
            
            # ✅ Адаптивная задержка при успехе
            self._adjust_delay_on_success()
            
            self.logger.info(
                f"✅ [{self.name}] Отправлено сообщение №{message_idx} в {target} | "
                f"Время ответа: {response_time:.2f}с | "
                f"Всего отправлено: {self.stats.total_sent} | "
                f"Задержка: {self._current_delay_between_chats:.1f}с"
            )

            
        except FloodWaitError as e:
            self.stats.flood_waits += 1
            wait_time = e.seconds
            flood_wait_duration = wait_time
            error_type = "FloodWaitError"
            error_details = f"Требуется ожидание {wait_time} секунд"
            self._last_flood_wait_time = datetime.now()
            
            self.logger.warning(
                f"⏳ [{self.name}] FloodWait для чата {target} | "
                f"Сообщение №{message_idx} | "
                f"Ожидание: {wait_time} сек | "
                f"Всего FloodWait: {self.stats.flood_waits} | "
                f"Текущая задержка: {self._current_delay_between_chats:.1f}с"
            )
            
            # 🎯 Увеличиваем задержку после FloodWait
            self._adjust_delay_on_error()
            
            await asyncio.sleep(wait_time)
            # Повторяем отправку после ожидания
            return await self._send_single_message(target, message, message_idx)
            
        except ChatWriteForbiddenError as e:
            self.stats.total_failed += 1
            self.stats.errors["ChatWriteForbidden"] = self.stats.errors.get("ChatWriteForbidden", 0) + 1
            error_type = "ChatWriteForbiddenError"
            error_details = "Нет прав на отправку сообщений в этот чат"
            
            # 🚫 Блокируем чат - нет смысла пытаться снова
            self._block_chat(target, error_details)
            self._adjust_delay_on_error()
            
            self.logger.error(
                f"❌ [{self.name}] ChatWriteForbidden для чата {target} | "
                f"Сообщение №{message_idx} | "
                f"Причина: {error_details} | "
                f"Чат заблокирован | "
                f"Всего ошибок: {self.stats.total_failed} | "
                f"Ошибок этого типа: {self.stats.errors.get('ChatWriteForbidden', 0)}"
            )

            
        except RPCError as e:
            self.stats.total_failed += 1
            error_type = f"RPCError_{e.code}"
            error_details = f"Код: {e.code}, Сообщение: {str(e)}"
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            
            # Детальная информация об ошибке
            error_info = {
                'code': e.code,
                'message': str(e),
                'type': type(e).__name__
            }
            
            # 🚫 Блокируем чат при определенных ошибках
            if e.code == 400:
                # Ошибка 400 часто означает невалидный чат или пользователь заблокировал бота
                block_reason = f"RPC Error 400: {str(e)}"
                self._block_chat(target, block_reason)
                
                self.logger.error(
                    f"❌ [{self.name}] RPC 400 ошибка для чата {target} | "
                    f"Сообщение №{message_idx} | "
                    f"Детали: {error_details} | "
                    f"Чат заблокирован | "
                    f"Всего RPCError_400: {self.stats.errors.get('RPCError_400', 0)} | "
                    f"Всего ошибок: {self.stats.total_failed}"
                )
            elif e.code == 403:
                # Ошибка 403 - запрещено (часто означает требование оплаты или нет доступа)
                # Блокируем чат, особенно если это ALLOW_PAYMENT_REQUIRED_1
                error_str = str(e).lower()
                if "payment" in error_str or "allow_payment" in error_str:
                    block_reason = f"RPC Error 403: Требуется оплата - {str(e)}"
                    self._block_chat(target, block_reason)
                    self.logger.error(
                        f"❌ [{self.name}] RPC 403 (Forbidden) для чата {target} | "
                        f"Сообщение №{message_idx} | "
                        f"Детали: {error_details} | "
                        f"Чат заблокирован (требуется оплата) | "
                        f"Всего RPCError_403: {self.stats.errors.get('RPCError_403', 0)}"
                    )
                else:
                    # Другие 403 ошибки - тоже блокируем, так как доступ запрещен
                    block_reason = f"RPC Error 403: Доступ запрещен - {str(e)}"
                    self._block_chat(target, block_reason)
                    self.logger.error(
                        f"❌ [{self.name}] RPC 403 (Forbidden) для чата {target} | "
                        f"Сообщение №{message_idx} | "
                        f"Детали: {error_details} | "
                        f"Чат заблокирован | "
                        f"Всего RPCError_403: {self.stats.errors.get('RPCError_403', 0)}"
                    )
            elif e.code == 500:
                # Ошибка 500 - внутренняя ошибка сервера Telegram
                self.logger.error(
                    f"❌ [{self.name}] RPC 500 (Server Error) для чата {target} | "
                    f"Сообщение №{message_idx} | "
                    f"Детали: {error_details} | "
                    f"Всего RPCError_500: {self.stats.errors.get('RPCError_500', 0)}"
                )
            else:
                self.logger.error(
                    f"❌ [{self.name}] RPC ошибка для чата {target} | "
                    f"Сообщение №{message_idx} | "
                    f"Код: {e.code} | "
                    f"Детали: {error_details} | "
                    f"Всего {error_type}: {self.stats.errors.get(error_type, 0)}"
                )
            
            self._adjust_delay_on_error()
            
        except (ConnectionError, OSError, TimeoutError) as e:
            # Обработка ошибок подключения с улучшенным retry
            self.stats.total_failed += 1
            error_type = type(e).__name__
            error_details = f"Ошибка подключения: {str(e)}"
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            self._adjust_delay_on_error()
            
            # Пытаемся переподключиться с несколькими попытками
            reconnected = False
            max_reconnect_attempts = 3
            for reconnect_attempt in range(1, max_reconnect_attempts + 1):
                try:
                    self.logger.warning(
                        f"⚠️ [{self.name}] Ошибка подключения для чата {target} | "
                        f"Сообщение №{message_idx} | "
                        f"Тип: {error_type} | "
                        f"Детали: {error_details} | "
                        f"Попытка переподключения {reconnect_attempt}/{max_reconnect_attempts}..."
                    )
                    
                    # Отключаемся перед переподключением
                    if self._client and self._client.is_connected():
                        try:
                            await self._client.disconnect()
                        except:
                            pass
                    
                    # Ждем перед переподключением
                    await asyncio.sleep(reconnect_attempt * 2)
                    
                    # Переподключаемся
                    await self._ensure_connection()
                    reconnected = True
                    self.logger.info(f"✅ [{self.name}] Успешно переподключился после {error_type}")
                    break
                    
                except Exception as reconnect_error:
                    self.logger.warning(
                        f"⚠️ [{self.name}] Попытка переподключения {reconnect_attempt}/{max_reconnect_attempts} "
                        f"не удалась: {reconnect_error}"
                    )
                    if reconnect_attempt < max_reconnect_attempts:
                        await asyncio.sleep(reconnect_attempt * 2)
            
            if not reconnected:
                self.logger.error(
                    f"❌ [{self.name}] Не удалось переподключиться после {max_reconnect_attempts} попыток | "
                    f"Последняя ошибка: {reconnect_error if 'reconnect_error' in locals() else 'неизвестна'}"
                )
            
            self.logger.error(
                f"❌ [{self.name}] {error_type} для чата {target} | "
                f"Сообщение №{message_idx} | "
                f"Детали: {error_details} | "
                f"Переподключение: {'✅' if reconnected else '❌'} | "
                f"Всего {error_type}: {self.stats.errors.get(error_type, 0)} | "
                f"Всего ошибок: {self.stats.total_failed}"
            )
            
        except ValueError as e:
            self.stats.total_failed += 1
            error_type = "ValueError"
            error_details = f"Невалидные данные: {str(e)}"
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            
            # ValueError часто означает невалидные данные
            self._block_chat(target, error_details)
            self._adjust_delay_on_error()
            
            self.logger.error(
                f"❌ [{self.name}] ValueError для чата {target} | "
                f"Сообщение №{message_idx} | "
                f"Детали: {error_details} | "
                f"Чат заблокирован | "
                f"Всего ValueError: {self.stats.errors.get('ValueError', 0)}"
            )
            
        except Exception as e:
            self.stats.total_failed += 1
            error_type = type(e).__name__
            error_details = f"Неожиданная ошибка: {str(e)}"
            error_msg = str(e).lower()
            self.stats.errors[error_type] = self.stats.errors.get(error_type, 0) + 1
            
            # Специальная обработка для OperationalError "database is locked"
            if "operationalerror" in error_type.lower() or "database is locked" in error_msg:
                # Это временная ошибка, не блокируем чат, но логируем
                self.logger.warning(
                    f"⚠️ [{self.name}] OperationalError (database is locked) для чата {target} | "
                    f"Сообщение №{message_idx} | "
                    f"Детали: {error_details} | "
                    f"Сообщение будет отложено | "
                    f"Всего OperationalError: {self.stats.errors.get('OperationalError', 0)}"
                )
                # Не блокируем чат, так как это временная ошибка
                # Сообщение будет отложено и отправлено позже
            else:
                self._adjust_delay_on_error()
            
            # Логируем полный traceback для неожиданных ошибок
            self.logger.error(
                f"❌ [{self.name}] Неожиданная ошибка для чата {target} | "
                f"Сообщение №{message_idx} | "
                f"Тип: {error_type} | "
                f"Детали: {error_details} | "
                f"Всего {error_type}: {self.stats.errors.get(error_type, 0)}"
            )
            self.logger.debug(
                f"Traceback для чата {target}:\n{traceback.format_exc()}"
            )

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

        self.logger.info(f"🔄 [{self.name}] ========== НАЧАЛО ЦИКЛА РАССЫЛКИ ==========")
        self.logger.info(
            f"🔄 [{self.name}] Начинаем цикл рассылки | "
            f"Целевых чатов: {len(self.targets)} | "
            f"Сообщений: {len(self.messages)} | "
            f"Заблокированных: {len(self._blocked_chats)} | "
            f"Отложенных: {len(self._deferred_messages)} | "
            f"Текущая задержка: {self._current_delay_between_chats:.1f}с"
        )
        self.logger.info(f"🔄 [{self.name}] Время начала цикла: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Проверка наличия целей и сообщений
        if not self.targets:
            self.logger.warning(f"⚠️ [{self.name}] Нет целевых чатов для рассылки!")
            return
        
        if not self.messages:
            self.logger.warning(f"⚠️ [{self.name}] Нет сообщений для рассылки!")
            return
        
        self.logger.info(f"✅ [{self.name}] Проверка пройдена: есть {len(self.targets)} чатов и {len(self.messages)} сообщений")

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

        # Для B2C: отправляем одно случайное сообщение в каждый чат
        if self._use_single_random_message:
            import random
            selected_message = random.choice(self.messages)
            total_messages = len(self.targets)  # Одно сообщение на чат
            successful_messages = 0
            failed_messages = 0
            flood_waits_count = 0
            
            self.logger.info(
                f"📨 [{self.name}] Отправляем одно случайное сообщение (из {len(self.messages)}) "
                f"в каждый из {len(self.targets)} чатов"
            )
            
            # Отправляем одно сообщение во все чаты
            self.logger.info(f"📨 [{self.name}] Начинаем отправку в {len(self.targets)} чатов...")
            target_idx = 0
            for target in self.targets:
                target_idx += 1
                self.logger.info(f"📨 [{self.name}] Обработка чата {target_idx}/{len(self.targets)}: {target}")
                
                # Проверяем тихий час перед каждым сообщением
                if self._is_quiet_hour():
                    self.logger.info(f"🌙 [{self.name}] Наступил тихий час. Останавливаем рассылку.")
                    break
                
                # 🕐 Проверка rate limiting
                min_interval = self.config.broadcasting.min_interval_per_chat
                
                # Сначала проверяем глобальный координатор (если доступен)
                global_can_send = True
                if self._coordinator:
                    try:
                        global_can_send, global_wait_time = await self._coordinator.can_send_to_chat(
                            self.name, target, min_interval_seconds=min_interval
                        )
                        if not global_can_send:
                            self.logger.debug(
                                f"⏳ [{self.name}] Глобальная блокировка для чата {target} | "
                                f"Нужно подождать: {global_wait_time:.1f}с (координатор)"
                            )
                            self._defer_message(target, selected_message, 0)
                            continue
                    except Exception as e:
                        self.logger.debug(f"Ошибка проверки координатора: {e}")
                
                # Затем проверяем локальный rate limiting
                can_send, wait_time = self._can_send_to_chat(target, min_interval_seconds=min_interval)
                if not can_send:
                    self.logger.debug(
                        f"⏳ [{self.name}] Пропускаем чат {target} | "
                        f"Нужно подождать: {wait_time:.1f}с | "
                        f"Интервал: {min_interval}с"
                    )
                    self._defer_message(target, selected_message, 0)
                    continue
                
                self.logger.info(f"📤 [{self.name}] Отправка сообщения в чат {target} ({target_idx}/{len(self.targets)})...")
                success = await self._send_single_message(target, selected_message, 0)
                
                # Обновляем время последней отправки и статистику только при успехе
                if success:
                    self._update_chat_send_time(target)
                    successful_messages += 1
                    self.logger.info(f"✅ [{self.name}] Сообщение успешно отправлено в чат {target} ({successful_messages} успешных из {target_idx})")
                else:
                    failed_messages += 1
                    self.logger.warning(f"❌ [{self.name}] Не удалось отправить сообщение в чат {target} ({failed_messages} неудачных из {target_idx})")
                
                # 🕐 АДАПТИВНАЯ ЗАДЕРЖКА МЕЖДУ ЧАТАМИ
                if self._current_delay_between_chats > 0:
                    self.logger.debug(f"⏳ [{self.name}] Задержка {self._current_delay_between_chats:.1f}с перед следующим чатом...")
                    await asyncio.sleep(self._current_delay_between_chats)
        else:
            # Стандартная логика: все сообщения во все чаты
            total_messages = len(self.messages) * len(self.targets)
            successful_messages = 0
            failed_messages = 0
            flood_waits_count = 0
            
            for idx, message in enumerate(self.messages, start=1):
                # Проверяем, не наступил ли тихий час во время рассылки
                if self._is_quiet_hour():
                    self.logger.info(
                        f"🌙 [{self.name}] Наступил тихий час во время рассылки. "
                        f"Прерываем текущий цикл."
                    )
                    break
                
                self.logger.info(
                    f"📨 [{self.name}] Отправляем сообщение №{idx} из {len(self.messages)} | "
                    f"Длина сообщения: {len(message)} символов"
                )
                
                # Отправляем во все целевые чаты
                for target in self.targets:
                    # Проверяем тихий час перед каждым сообщением
                    if self._is_quiet_hour():
                        self.logger.info(f"🌙 Наступил тихий час. Останавливаем рассылку.")
                        break
                
                # 🕐 Проверка rate limiting: не отправляем в один чат чаще чем установленный интервал
                min_interval = self.config.broadcasting.min_interval_per_chat
                
                # Сначала проверяем глобальный координатор (если доступен)
                global_can_send = True
                if self._coordinator:
                    try:
                        global_can_send, global_wait_time = await self._coordinator.can_send_to_chat(
                            self.name, target, min_interval_seconds=min_interval
                        )
                        if not global_can_send:
                            self.logger.debug(
                                f"⏳ [{self.name}] Глобальная блокировка для чата {target} | "
                                f"Нужно подождать: {global_wait_time:.1f}с (координатор)"
                            )
                            self._defer_message(target, message, idx)
                            continue
                    except Exception as e:
                        self.logger.debug(f"Ошибка проверки координатора: {e}")
                
                # Затем проверяем локальный rate limiting
                can_send, wait_time = self._can_send_to_chat(target, min_interval_seconds=min_interval)
                if not can_send:
                    self.logger.debug(
                        f"⏳ [{self.name}] Пропускаем чат {target} | "
                        f"Сообщение №{idx} | "
                        f"Прошло: {min_interval - wait_time:.1f}с | "
                        f"Нужно подождать: {wait_time:.1f}с | "
                        f"Интервал: {min_interval}с"
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
                
                # 🕐 АДАПТИВНАЯ ЗАДЕРЖКА МЕЖДУ ЧАТАМИ
                # Используется динамическая задержка, которая изменяется на основе ошибок и успехов
                if self._current_delay_between_chats > 0:
                    await asyncio.sleep(self._current_delay_between_chats)



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
        total_attempts = self.stats.total_sent + self.stats.total_failed
        success_rate = (self.stats.total_sent / total_attempts * 100) if total_attempts > 0 else 0
        
        self.logger.info(
            f"📊 [{self.name}] Статистика цикла: "
            f"✅ отправлено: {self.stats.total_sent} | "
            f"❌ ошибок: {self.stats.total_failed} | "
            f"⏳ FloodWait: {self.stats.flood_waits} | "
            f"📬 отложенных: {len(self._deferred_messages)} | "
            f"📈 Успешность: {success_rate:.1f}%"
        )
        
        # Адаптивная задержка
        if self.config.broadcasting.adaptive_delay_enabled:
            base_delay = self.config.broadcasting.delay_between_chats
            self.logger.info(
                f"🎯 [{self.name}] Адаптивная задержка: "
                f"текущая={self._current_delay_between_chats:.1f}с | "
                f"базовая={base_delay}с | "
                f"серия ошибок={self._error_streak} | "
                f"серия успехов={self._success_streak}"
            )
        
        # Заблокированные чаты
        if self._blocked_chats:
            blocked_count = len(self._blocked_chats)
            blocked_percent = (blocked_count / len(self.targets) * 100) if self.targets else 0
            self.logger.warning(
                f"🚫 [{self.name}] Заблокировано чатов: {blocked_count} из {len(self.targets)} "
                f"({blocked_percent:.1f}%)"
            )
            
            # Показываем топ-5 причин блокировки
            if blocked_count <= 5:
                for chat_id, reason in list(self._blocked_chats.items())[:5]:
                    self.logger.warning(f"   • Чат {chat_id}: {reason}")
            else:
                # Группируем по причинам
                reasons_count = {}
                for reason in self._blocked_chats.values():
                    # Берем первые 50 символов причины
                    short_reason = reason[:50] + "..." if len(reason) > 50 else reason
                    reasons_count[short_reason] = reasons_count.get(short_reason, 0) + 1
                
                top_reasons = sorted(reasons_count.items(), key=lambda x: x[1], reverse=True)[:5]
                self.logger.warning(f"   Топ причин блокировки:")
                for reason, count in top_reasons:
                    self.logger.warning(f"   • {reason}: {count} чатов")
        
        # Детальная статистика по ошибкам
        if self.stats.errors:
            total_errors = sum(self.stats.errors.values())
            self.logger.warning(
                f"🚨 [{self.name}] Детальная статистика ошибок (всего: {total_errors}):"
            )
            
            # Сортируем ошибки по количеству
            sorted_errors = sorted(self.stats.errors.items(), key=lambda x: x[1], reverse=True)
            for error_type, count in sorted_errors[:10]:  # Топ-10 ошибок
                error_percent = (count / total_errors * 100) if total_errors > 0 else 0
                self.logger.warning(
                    f"   • {error_type}: {count} ({error_percent:.1f}% от всех ошибок)"
                )
        
        # Статистика по проблемным чатам (из метрик)
        if hasattr(self, 'metrics') and self.metrics.chat_stats:
            problem_chats = []
            for chat_id, stats in self.metrics.chat_stats.items():
                total_chat_attempts = stats['messages_sent'] + stats['messages_failed']
                if total_chat_attempts > 0:
                    chat_success_rate = (stats['messages_sent'] / total_chat_attempts * 100)
                    if chat_success_rate < 50 or stats['messages_failed'] > 5:
                        problem_chats.append({
                            'chat_id': chat_id,
                            'success_rate': chat_success_rate,
                            'failed': stats['messages_failed'],
                            'sent': stats['messages_sent'],
                            'errors': dict(stats['error_types'])
                        })
            
            if problem_chats:
                # Сортируем по проценту ошибок
                problem_chats.sort(key=lambda x: x['success_rate'])
                self.logger.warning(
                    f"⚠️ [{self.name}] Проблемные чаты (успешность < 50% или > 5 ошибок):"
                )
                for chat in problem_chats[:10]:  # Топ-10 проблемных чатов
                    self.logger.warning(
                        f"   • Чат {chat['chat_id']}: "
                        f"успешность {chat['success_rate']:.1f}% | "
                        f"✅ {chat['sent']} | "
                        f"❌ {chat['failed']} | "
                        f"Ошибки: {chat['errors']}"
                    )
    
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
            max_attempts=5  # Увеличено до 5 попыток для большей надежности
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
    
    async def _ensure_connection(self, retry_count: int = 0, max_retries: int = 3):
        """Обеспечение подключения к Telegram с улучшенной обработкой ошибок"""
        try:
            # Проверяем подключение
            if self._client and self._client.is_connected():
                # Проверяем, что соединение действительно работает
                try:
                    self.logger.debug(f"🔍 [{self.name}] Проверка работоспособности соединения (get_me)...")
                    await asyncio.wait_for(self._client.get_me(), timeout=10.0)
                    self.logger.debug(f"✅ [{self.name}] Соединение работает, возвращаемся")
                    return  # Соединение работает
                except asyncio.TimeoutError:
                    self.logger.warning(f"⚠️ [{self.name}] Таймаут при проверке соединения, переподключаемся...")
                    try:
                        await self._client.disconnect()
                    except:
                        pass
                except Exception as e:
                    self.logger.warning(f"⚠️ [{self.name}] Соединение не работает, переподключаемся: {e}")
                    try:
                        await self._client.disconnect()
                    except:
                        pass
            
            if retry_count >= max_retries:
                raise Exception(f"Не удалось подключиться после {max_retries} попыток")
            
            if retry_count > 0:
                wait_time = min(2 ** retry_count, 30)  # Экспоненциальная задержка до 30 секунд
                self.logger.info(f"⏳ [{self.name}] Ожидание {wait_time}с перед переподключением (попытка {retry_count + 1}/{max_retries})...")
                await asyncio.sleep(wait_time)
            
            self.logger.info(f"🔌 [{self.name}] Подключаемся к Telegram... (попытка {retry_count + 1}/{max_retries})")
            
            # Используем глобальную блокировку подключений для предотвращения "database is locked"
            connection_lock_acquired = False
            try:
                # Получаем координатор, если еще не получен
                if not self._coordinator:
                    self._coordinator = await get_coordinator()
                
                if self._coordinator:
                    self.logger.debug(f"🔒 [{self.name}] Получение блокировки подключения...")
                    await self._coordinator.acquire_connection_lock()
                    connection_lock_acquired = True
                    self.logger.debug(f"✅ [{self.name}] Блокировка подключения получена")
                
                self.logger.debug(f"🚀 [{self.name}] Запуск Telegram клиента...")
                try:
                    # Проверяем, что сессия существует перед запуском
                    session_file = Path(f"{self.session_name}.session")
                    if not session_file.exists():
                        raise Exception(f"Файл сессии не найден: {session_file}. Запустите broadcaster в интерактивном режиме для создания сессии.")
                    
                    # Добавляем таймаут для start() чтобы не зависать
                    # Увеличено до 60 секунд, так как start() может долго ждать при database locked
                    await asyncio.wait_for(self._client.start(), timeout=60.0)
                    self.logger.debug(f"✅ [{self.name}] Telegram клиент запущен успешно")
                except asyncio.TimeoutError:
                    self.logger.error(f"❌ [{self.name}] Таймаут при запуске клиента (30 секунд)")
                    raise Exception(f"Таймаут при запуске Telegram клиента")
                except Exception as start_err:
                    self.logger.error(f"❌ [{self.name}] Ошибка при запуске клиента: {start_err}")
                    raise
            except Exception as start_error:
                error_msg = str(start_error).lower()
                if "database is locked" in error_msg or "locked" in error_msg:
                    # Если database is locked при start(), ждем и повторяем
                    wait_time = min(5 * (retry_count + 1), 15)  # Увеличено до 15 секунд максимум
                    self.logger.warning(
                        f"⚠️ [{self.name}] База данных заблокирована при запуске, "
                        f"ожидание {wait_time}с... (попытка {retry_count + 1}/{max_retries + 3})"
                    )
                    await asyncio.sleep(wait_time)
                    if retry_count < max_retries + 3:  # Увеличено количество попыток
                        return await self._ensure_connection(retry_count + 1, max_retries + 3)
                    else:
                        raise Exception(f"Не удалось запустить клиент из-за блокировки базы данных после {max_retries + 2} попыток")
                else:
                    raise  # Пробрасываем другие ошибки
            finally:
                # Освобождаем блокировку подключения в любом случае
                if connection_lock_acquired and self._coordinator:
                    self._coordinator.release_connection_lock()
            
            # Получаем информацию о текущем пользователе
            self.logger.debug(f"👤 [{self.name}] Получение информации о пользователе...")
            try:
                me = await asyncio.wait_for(self._client.get_me(), timeout=10.0)
                account_id = me.id
                self._account_id = str(account_id)  # Сохраняем для координатора
                account_name = f"{me.first_name or ''} {me.last_name or ''}".strip()
                username = me.username or "без username"
                self.logger.debug(f"✅ [{self.name}] Информация о пользователе получена: {account_name} (@{username})")
            except asyncio.TimeoutError:
                self.logger.error(f"❌ [{self.name}] Таймаут при получении информации о пользователе")
                raise Exception("Таймаут при получении информации о пользователе")
            except Exception as get_me_err:
                self.logger.error(f"❌ [{self.name}] Ошибка при получении информации о пользователе: {get_me_err}")
                raise
            
            # Определяем тип аккаунта по имени broadcaster'а
            account_type = "ОПТОВЫЙ" if "B2B" in self.name or "AAA" in self.name else "РОЗНИЧНЫЙ"
            
            # Регистрация в координаторе
            try:
                self._coordinator = await get_coordinator()
                self._coordinator.register_broadcaster(
                    broadcaster_name=self.name,
                    account_id=self._account_id,
                    chat_ids=self.targets
                )
                self.logger.info(f"✅ Broadcaster '{self.name}' зарегистрирован в координаторе")
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось зарегистрироваться в координаторе: {e}")
            
            self.logger.info(f"✅ Подключено как {account_name} (@{username})")
            self.logger.info(f"📱 ID аккаунта: {account_id}")
            self.logger.info(f"🏷️  Тип аккаунта: {account_type}")
            self.logger.info(f"📊 Broadcaster: {self.name}")
            self.logger.info(f"🎯 Целевых чатов: {len(self.targets)}")
            self.logger.info(f"💬 Сообщений: {len(self.messages)}")
            
            print(f"✅ {self.name} подключен: {account_name} (@{username})")
            print(f"📱 ID: {account_id} | Тип: {account_type}")
            print(f"🎯 Чатов: {len(self.targets)} | 💬 Сообщений: {len(self.messages)}")
            
        except Exception as e:
            error_msg = str(e).lower()
            is_database_locked = "database is locked" in error_msg or "locked" in error_msg
            
            if is_database_locked:
                # Специальная обработка для database is locked
                # Увеличиваем задержку и количество попыток для этой ошибки
                wait_time = min(5 * (retry_count + 1), 15)  # От 5 до 15 секунд (увеличено)
                self.logger.warning(
                    f"⚠️ [{self.name}] База данных заблокирована (возможно, другой broadcaster подключается), "
                    f"ожидание {wait_time}с перед повторной попыткой (попытка {retry_count + 1}/{max_retries + 3})..."
                )
                await asyncio.sleep(wait_time)
                # Увеличиваем max_retries для database is locked
                if retry_count < max_retries + 3:
                    return await self._ensure_connection(retry_count + 1, max_retries + 3)
                else:
                    raise Exception(f"Не удалось подключиться из-за блокировки базы данных после {max_retries + 2} попыток")
            else:
                self.logger.error(f"❌ [{self.name}] Ошибка подключения: {e}")
                if retry_count < max_retries:
                    # Рекурсивный retry
                    return await self._ensure_connection(retry_count + 1, max_retries)
                else:
                    raise
    
    async def start(self):
        """Запуск broadcaster"""
        if self._running:
            self.logger.warning(f"Broadcaster {self.name} уже запущен")
            return
        
        self._running = True
        self.logger.info(f"🚀 [{self.name}] Запуск broadcaster начат")
        self.logger.info(f"📊 [{self.name}] Статус: running={self._running}, targets={len(self.targets)}, messages={len(self.messages)}")
        
        try:
            # Ожидание времени начала
            self.logger.info(f"⏰ [{self.name}] Проверка времени старта...")
            wait_time = self._wait_until_start_time()
            self.logger.info(f"⏰ [{self.name}] Время старта: wait_time={wait_time}с, enable_scheduling={self.config.broadcasting.enable_scheduling}")
            if wait_time > 0:
                self.logger.info(f"⏰ [{self.name}] Ожидание времени старта: {wait_time}с ({wait_time/60:.1f} мин)")
                await asyncio.sleep(wait_time)
                self.logger.info(f"⏰ [{self.name}] Время старта наступило, продолжаем...")
            
            # Добавляем смещение времени старта (для распределения нагрузки)
            if self._start_offset_seconds > 0:
                self.logger.info(
                    f"⏰ [{self.name}] Применяется смещение времени старта: {self._start_offset_seconds}с"
                )
                await asyncio.sleep(self._start_offset_seconds)
                self.logger.info(f"⏰ [{self.name}] Смещение времени старта завершено")
            
            # Основной цикл
            cycle_number = 0
            self.logger.info(f"🔄 [{self.name}] Вход в основной цикл рассылки...")
            while self._running:
                cycle_number += 1
                self.logger.info(f"🔄 [{self.name}] === НАЧАЛО ЦИКЛА #{cycle_number} ===")
                try:
                    # Проверка тихого часа перед началом цикла
                    self.logger.info(f"🌙 [{self.name}] Проверка тихого часа...")
                    is_quiet = self._is_quiet_hour()
                    self.logger.info(f"🌙 [{self.name}] Тихий час: is_quiet={is_quiet}, enable_quiet_hours={self.config.broadcasting.enable_quiet_hours}")
                    quiet_wait_time = self._wait_until_quiet_hour_ends()
                    self.logger.info(f"🌙 [{self.name}] Время ожидания тихого часа: {quiet_wait_time}с")
                    if quiet_wait_time > 0:
                        self.logger.info(f"🌙 [{self.name}] Тихий час активен, ожидание {quiet_wait_time}с...")
                        await asyncio.sleep(quiet_wait_time)
                        self.logger.info(f"🌙 [{self.name}] Тихий час завершен, продолжаем цикл...")
                        continue  # После окончания тихого часа начинаем новый цикл
                    
                    self.logger.info(f"🔌 [{self.name}] Проверка подключения перед циклом...")
                    await self._ensure_connection()
                    self.logger.info(f"✅ [{self.name}] Подключение подтверждено, начинаем цикл отправки...")
                    
                    self.logger.info(f"📨 [{self.name}] Вызов _send_messages_cycle()...")
                    await self._send_messages_cycle()
                    self.logger.info(f"✅ [{self.name}] _send_messages_cycle() завершен успешно")
                    
                    self.logger.info(
                        f"✅ [{self.name}] Цикл #{cycle_number} завершён. Ждём {self.cycle_delay} секунд ({self.cycle_delay/60:.0f} минут)..."
                    )
                    await asyncio.sleep(self.cycle_delay)
                    self.logger.info(f"⏰ [{self.name}] Ожидание между циклами завершено, начинаем следующий цикл...")
                    
                except Exception as e:
                    self.logger.exception(f"❌ [{self.name}] Ошибка в цикле #{cycle_number}: {e}")
                    self.logger.error(f"❌ [{self.name}] Traceback: {traceback.format_exc()}")
                    self.logger.info(f"⏳ [{self.name}] Ожидание {self.config.broadcasting.retry_delay}с перед повтором...")
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
        print(f"🚫 Заблокированных чатов: {len(self._blocked_chats)}")
        print(f"💬 Сообщений: {basic['messages_count']}")
        print(f"✅ Отправлено: {basic['total_sent']}")
        print(f"❌ Ошибок: {basic['total_failed']}")
        print(f"⏳ FloodWait: {basic['flood_waits']}")
        print(f"📬 Отложенных: {len(self._deferred_messages)}")

        # Производительность
        perf = stats["performance"]
        print(f"📈 Процент успешности: {perf['success_rate']:.1f}%")
        print(f"⚡ Среднее время ответа: {perf['avg_response_time']:.2f}с")
        print(f"🔄 Циклов завершено: {perf['cycles_completed']}")

        # Адаптивная задержка
        if self.config.broadcasting.adaptive_delay_enabled:
            base_delay = self.config.broadcasting.delay_between_chats
            print(f"🎯 Задержка между чатами: {self._current_delay_between_chats:.1f}с (базовая: {base_delay}с)")

        # Ошибки
        if basic['errors']:
            print(f"🚨 Типы ошибок:")
            for error_type, count in basic['errors'].items():
                print(f"   - {error_type}: {count}")

        print("=" * 50)

