"""
Система повторных попыток с экспоненциальным backoff
"""
import asyncio
import random
from functools import wraps
from typing import Callable, Any, Type, Tuple, Union

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Декоратор для повторных попыток с экспоненциальным backoff
    
    Args:
        max_retries: Максимальное количество попыток
        base_delay: Базовая задержка в секундах
        max_delay: Максимальная задержка в секундах
        exponential_base: База для экспоненциального роста
        jitter: Добавлять случайность к задержке
        exceptions: Типы исключений для повторной попытки
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Вычисляем задержку
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Добавляем jitter для избежания thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    await asyncio.sleep(delay)
            
            # Если все попытки исчерпаны, поднимаем последнее исключение
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Для синхронных функций используем time.sleep
                    import time
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        # Возвращаем соответствующую обертку в зависимости от типа функции
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class RetryConfig:
    """Конфигурация для системы повторных попыток"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

# Предустановленные конфигурации
QUICK_RETRY = RetryConfig(max_retries=2, base_delay=0.5, max_delay=5.0)
STANDARD_RETRY = RetryConfig(max_retries=3, base_delay=1.0, max_delay=30.0)
PERSISTENT_RETRY = RetryConfig(max_retries=5, base_delay=2.0, max_delay=120.0)
