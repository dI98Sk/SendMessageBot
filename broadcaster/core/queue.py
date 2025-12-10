"""
Система очередей для масштабируемой рассылки
"""
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import json

class Priority(Enum):
    """Приоритеты сообщений"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class QueueItem:
    """Элемент очереди"""
    id: str
    chat_id: int
    message: str
    priority: Priority
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class QueueStats:
    """Статистика очереди"""
    total_items: int = 0
    pending_items: int = 0
    processing_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    avg_processing_time: float = 0.0

class MessageQueue:
    """Очередь сообщений с приоритетами"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        
        # Очереди по приоритетам
        self.queues = {
            Priority.LOW: deque(),
            Priority.NORMAL: deque(),
            Priority.HIGH: deque(),
            Priority.CRITICAL: deque()
        }
        
        # Статистика
        self.stats = QueueStats()
        
        # Элементы в обработке
        self.processing: Dict[str, QueueItem] = {}
        
        # История
        self.history: deque = deque(maxlen=1000)
        
        # Блокировки
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
    
    async def put(self, item: QueueItem) -> bool:
        """Добавление элемента в очередь"""
        async with self._lock:
            if self.stats.total_items >= self.max_size:
                return False
            
            self.queues[item.priority].append(item)
            self.stats.total_items += 1
            self.stats.pending_items += 1
            
            # Уведомляем ожидающих
            self._condition.notify()
            return True
    
    async def get(self, timeout: Optional[float] = None) -> Optional[QueueItem]:
        """Получение элемента из очереди"""
        async with self._condition:
            # Ждем элемент с наивысшим приоритетом
            while True:
                for priority in [Priority.CRITICAL, Priority.HIGH, Priority.NORMAL, Priority.LOW]:
                    if self.queues[priority]:
                        item = self.queues[priority].popleft()
                        self.stats.pending_items -= 1
                        self.stats.processing_items += 1
                        
                        # Добавляем в обработку
                        self.processing[item.id] = item
                        return item
                
                # Если очередь пуста, ждем
                try:
                    await asyncio.wait_for(self._condition.wait(), timeout=timeout)
                except asyncio.TimeoutError:
                    return None
    
    async def mark_completed(self, item_id: str, processing_time: float):
        """Отметить элемент как завершенный"""
        async with self._lock:
            if item_id in self.processing:
                item = self.processing.pop(item_id)
                self.stats.processing_items -= 1
                self.stats.completed_items += 1
                
                # Обновляем среднее время обработки
                total_completed = self.stats.completed_items + self.stats.failed_items
                if total_completed > 0:
                    self.stats.avg_processing_time = (
                        (self.stats.avg_processing_time * (total_completed - 1) + processing_time) 
                        / total_completed
                    )
                
                # Добавляем в историю
                self.history.append({
                    'item': item,
                    'completed_at': datetime.now(),
                    'processing_time': processing_time,
                    'status': 'completed'
                })
    
    async def mark_failed(self, item_id: str, error: str, processing_time: float):
        """Отметить элемент как неудачный"""
        async with self._lock:
            if item_id in self.processing:
                item = self.processing.pop(item_id)
                self.stats.processing_items -= 1
                
                item.attempts += 1
                
                # Если не превышено максимальное количество попыток, возвращаем в очередь
                if item.attempts < item.max_attempts:
                    self.queues[item.priority].append(item)
                    self.stats.pending_items += 1
                else:
                    self.stats.failed_items += 1
                
                # Добавляем в историю
                self.history.append({
                    'item': item,
                    'failed_at': datetime.now(),
                    'processing_time': processing_time,
                    'status': 'failed',
                    'error': error
                })
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики очереди"""
        return {
            'total_items': self.stats.total_items,
            'pending_items': self.stats.pending_items,
            'processing_items': self.stats.processing_items,
            'completed_items': self.stats.completed_items,
            'failed_items': self.stats.failed_items,
            'avg_processing_time': self.stats.avg_processing_time,
            'queue_sizes': {
                priority.name: len(queue) for priority, queue in self.queues.items()
            }
        }
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение истории"""
        return list(self.history)[-limit:]

class QueueProcessor:
    """Процессор очереди"""
    
    def __init__(self, queue: MessageQueue, worker_count: int = 5):
        self.queue = queue
        self.worker_count = worker_count
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.processor_func: Optional[Callable] = None
    
    def set_processor(self, processor_func: Callable):
        """Установка функции обработки"""
        self.processor_func = processor_func
    
    async def start(self):
        """Запуск процессора"""
        if self.running:
            return
        
        if not self.processor_func:
            raise ValueError("Функция обработки не установлена")
        
        self.running = True
        
        # Запускаем воркеры
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        """Остановка процессора"""
        if not self.running:
            return
        
        self.running = False
        
        # Останавливаем воркеры
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
    
    async def _worker(self, worker_name: str):
        """Воркер для обработки очереди"""
        while self.running:
            try:
                # Получаем элемент из очереди
                item = await self.queue.get(timeout=1.0)
                if not item:
                    continue
                
                start_time = time.time()
                
                try:
                    # Обрабатываем элемент
                    await self.processor_func(item)
                    
                    # Отмечаем как завершенный
                    processing_time = time.time() - start_time
                    await self.queue.mark_completed(item.id, processing_time)
                    
                except Exception as e:
                    # Отмечаем как неудачный
                    processing_time = time.time() - start_time
                    await self.queue.mark_failed(item.id, str(e), processing_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка в воркере {worker_name}: {e}")
                await asyncio.sleep(1)

class QueueManager:
    """Менеджер очередей"""
    
    def __init__(self):
        self.queues: Dict[str, MessageQueue] = {}
        self.processors: Dict[str, QueueProcessor] = {}
    
    def create_queue(self, name: str, max_size: int = 10000) -> MessageQueue:
        """Создание очереди"""
        if name in self.queues:
            raise ValueError(f"Очередь {name} уже существует")
        
        queue = MessageQueue(max_size)
        self.queues[name] = queue
        return queue
    
    def get_queue(self, name: str) -> Optional[MessageQueue]:
        """Получение очереди"""
        return self.queues.get(name)
    
    def create_processor(
        self, 
        queue_name: str, 
        worker_count: int = 5,
        processor_func: Optional[Callable] = None
    ) -> QueueProcessor:
        """Создание процессора для очереди"""
        if queue_name not in self.queues:
            raise ValueError(f"Очередь {queue_name} не существует")
        
        processor = QueueProcessor(self.queues[queue_name], worker_count)
        if processor_func:
            processor.set_processor(processor_func)
        
        self.processors[queue_name] = processor
        return processor
    
    async def start_all_processors(self):
        """Запуск всех процессоров"""
        tasks = []
        for processor in self.processors.values():
            tasks.append(processor.start())
        
        await asyncio.gather(*tasks)
    
    async def stop_all_processors(self):
        """Остановка всех процессоров"""
        tasks = []
        for processor in self.processors.values():
            tasks.append(processor.stop())
        
        await asyncio.gather(*tasks)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получение статистики всех очередей"""
        return {
            name: queue.get_stats() 
            for name, queue in self.queues.items()
        }

# Глобальный менеджер очередей
queue_manager = QueueManager()
