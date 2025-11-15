"""
Координатор для синхронизации работы нескольких broadcaster'ов
Предотвращает конфликты при параллельной работе
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List
from collections import defaultdict
import pytz

class BroadcasterCoordinator:
    """Координатор для управления несколькими broadcaster'ами"""
    
    _instance: Optional['BroadcasterCoordinator'] = None
    _lock = asyncio.Lock()
    _initialized = False
    
    def __init__(self):
        if BroadcasterCoordinator._initialized:
            return
        BroadcasterCoordinator._initialized = True
        # Отслеживание последних отправок в каждый чат (глобально для всех broadcaster'ов)
        # Формат: {chat_id: datetime последней отправки}
        self._global_last_send_times: Dict[int, datetime] = {}
        
        # Отслеживание активных broadcaster'ов по аккаунту
        # Формат: {account_id: [broadcaster_names]}
        self._account_broadcasters: Dict[str, List[str]] = defaultdict(list)
        
        # Отслеживание чатов по broadcaster'ам
        # Формат: {broadcaster_name: set(chat_ids)}
        self._broadcaster_chats: Dict[str, Set[int]] = {}
        
        # Блокировки для каждого чата (предотвращение одновременной отправки)
        self._chat_locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        # Минимальный интервал между отправками в один чат (глобально)
        self._min_interval_seconds: int = 300  # 5 минут по умолчанию
        
    @classmethod
    async def get_instance(cls) -> 'BroadcasterCoordinator':
        """Получение singleton экземпляра"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def register_broadcaster(self, broadcaster_name: str, account_id: str, chat_ids: List[int]):
        """Регистрация broadcaster'а в координаторе"""
        self._account_broadcasters[account_id].append(broadcaster_name)
        self._broadcaster_chats[broadcaster_name] = set(chat_ids)
        
        # Проверка пересечений чатов
        self._check_chat_overlaps(broadcaster_name, chat_ids)
    
    def _check_chat_overlaps(self, broadcaster_name: str, chat_ids: List[int]):
        """Проверка пересечений чатов между broadcaster'ами"""
        overlaps = []
        for other_name, other_chats in self._broadcaster_chats.items():
            if other_name == broadcaster_name:
                continue
            overlap = set(chat_ids) & other_chats
            if overlap:
                overlaps.append((other_name, overlap))
        
        if overlaps:
            print(f"⚠️  ВНИМАНИЕ: Broadcaster '{broadcaster_name}' имеет пересекающиеся чаты:")
            for other_name, overlap_chats in overlaps:
                print(f"   • С '{other_name}': {len(overlap_chats)} общих чатов")
                print(f"     Рекомендуется: увеличить задержки или разделить чаты")
    
    async def can_send_to_chat(self, broadcaster_name: str, chat_id: int, 
                               min_interval_seconds: Optional[int] = None) -> tuple[bool, float]:
        """
        Проверка, можно ли отправить сообщение в чат
        
        Args:
            broadcaster_name: Имя broadcaster'а
            chat_id: ID чата
            min_interval_seconds: Минимальный интервал (если None - используется глобальный)
        
        Returns:
            tuple[bool, float]: (можно ли отправить, сколько секунд нужно подождать)
        """
        interval = min_interval_seconds or self._min_interval_seconds
        now = datetime.now()
        
        # Проверяем глобальное время последней отправки
        if chat_id in self._global_last_send_times:
            last_send_time = self._global_last_send_times[chat_id]
            time_since_last = (now - last_send_time).total_seconds()
            
            if time_since_last < interval:
                wait_time = interval - time_since_last
                return False, wait_time
        
        return True, 0
    
    async def acquire_chat_lock(self, chat_id: int):
        """Получение блокировки для чата (предотвращение одновременной отправки)"""
        await self._chat_locks[chat_id].acquire()
        return True
    
    def release_chat_lock(self, chat_id: int):
        """Освобождение блокировки для чата"""
        if chat_id in self._chat_locks:
            try:
                if self._chat_locks[chat_id].locked():
                    self._chat_locks[chat_id].release()
            except Exception:
                pass  # Игнорируем ошибки при освобождении
    
    def record_send(self, broadcaster_name: str, chat_id: int):
        """Запись факта отправки сообщения"""
        self._global_last_send_times[chat_id] = datetime.now()
    
    def set_min_interval(self, seconds: int):
        """Установка минимального интервала между отправками"""
        self._min_interval_seconds = seconds
    
    def get_statistics(self) -> Dict:
        """Получение статистики координатора"""
        return {
            'total_chats_tracked': len(self._global_last_send_times),
            'account_broadcasters': dict(self._account_broadcasters),
            'broadcaster_chats': {name: len(chats) for name, chats in self._broadcaster_chats.items()},
            'min_interval_seconds': self._min_interval_seconds
        }

# Глобальный экземпляр координатора
coordinator: Optional[BroadcasterCoordinator] = None

async def get_coordinator() -> BroadcasterCoordinator:
    """Получение глобального координатора"""
    global coordinator
    if coordinator is None:
        coordinator = await BroadcasterCoordinator.get_instance()
    return coordinator

