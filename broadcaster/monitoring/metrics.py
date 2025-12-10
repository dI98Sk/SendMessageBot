"""
Система сбора метрик и статистики
"""
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

@dataclass
class MessageMetric:
    """Метрика отправки сообщения"""
    timestamp: datetime
    chat_id: int
    message_id: int
    success: bool
    error_type: Optional[str] = None
    response_time: float = 0.0
    flood_wait_duration: int = 0

@dataclass
class BroadcastCycleMetric:
    """Метрика цикла рассылки"""
    start_time: datetime
    end_time: datetime
    total_messages: int
    successful_messages: int
    failed_messages: int
    total_duration: float
    flood_waits_count: int

@dataclass
class SystemMetric:
    """Системная метрика"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    queue_size: int

class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # История метрик
        self.message_metrics: deque = deque(maxlen=max_history_size)
        self.cycle_metrics: deque = deque(maxlen=max_history_size // 10)
        self.system_metrics: deque = deque(maxlen=max_history_size // 5)
        
        # Агрегированная статистика
        self.stats = {
            'total_messages_sent': 0,
            'total_messages_failed': 0,
            'total_flood_waits': 0,
            'total_cycles_completed': 0,
            'avg_response_time': 0.0,
            'success_rate': 0.0,
            'last_activity': None
        }
        
        # Статистика по чатам
        self.chat_stats: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            'messages_sent': 0,
            'messages_failed': 0,
            'last_success': None,
            'last_failure': None,
            'error_types': defaultdict(int)
        })
        
        # Статистика по времени
        self.hourly_stats: Dict[int, Dict[str, int]] = defaultdict(lambda: {
            'messages_sent': 0,
            'messages_failed': 0,
            'flood_waits': 0
        })
    
    def record_message(self, metric: MessageMetric):
        """Запись метрики сообщения"""
        self.message_metrics.append(metric)
        
        # Обновление общей статистики
        if metric.success:
            self.stats['total_messages_sent'] += 1
            self.chat_stats[metric.chat_id]['messages_sent'] += 1
            self.chat_stats[metric.chat_id]['last_success'] = metric.timestamp
        else:
            self.stats['total_messages_failed'] += 1
            self.chat_stats[metric.chat_id]['messages_failed'] += 1
            self.chat_stats[metric.chat_id]['last_failure'] = metric.timestamp
            
            if metric.error_type:
                self.chat_stats[metric.chat_id]['error_types'][metric.error_type] += 1
        
        # Обновление статистики по времени
        hour = metric.timestamp.hour
        if metric.success:
            self.hourly_stats[hour]['messages_sent'] += 1
        else:
            self.hourly_stats[hour]['messages_failed'] += 1
        
        if metric.flood_wait_duration > 0:
            self.stats['total_flood_waits'] += 1
            self.hourly_stats[hour]['flood_waits'] += 1
        
        # Обновление времени последней активности
        self.stats['last_activity'] = metric.timestamp
        
        # Пересчет средней скорости ответа
        self._update_avg_response_time()
        self._update_success_rate()
    
    def record_cycle(self, metric: BroadcastCycleMetric):
        """Запись метрики цикла"""
        self.cycle_metrics.append(metric)
        self.stats['total_cycles_completed'] += 1
    
    def record_system_metric(self, metric: SystemMetric):
        """Запись системной метрики"""
        self.system_metrics.append(metric)
    
    def _update_avg_response_time(self):
        """Обновление средней скорости ответа"""
        if not self.message_metrics:
            return
        
        total_time = sum(m.response_time for m in self.message_metrics if m.response_time > 0)
        count = len([m for m in self.message_metrics if m.response_time > 0])
        
        if count > 0:
            self.stats['avg_response_time'] = total_time / count
    
    def _update_success_rate(self):
        """Обновление процента успешности"""
        total = self.stats['total_messages_sent'] + self.stats['total_messages_failed']
        if total > 0:
            self.stats['success_rate'] = (self.stats['total_messages_sent'] / total) * 100
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Получение сводной статистики"""
        return {
            'general': dict(self.stats),
            'top_chats': self._get_top_chats(5),
            'hourly_distribution': dict(self.hourly_stats),
            'recent_errors': self._get_recent_errors(10),
            'performance_metrics': self._get_performance_metrics()
        }
    
    def _get_top_chats(self, limit: int) -> List[Dict[str, Any]]:
        """Получение топ чатов по активности"""
        chat_list = []
        for chat_id, stats in self.chat_stats.items():
            total = stats['messages_sent'] + stats['messages_failed']
            if total > 0:
                chat_list.append({
                    'chat_id': chat_id,
                    'total_messages': total,
                    'success_rate': (stats['messages_sent'] / total) * 100,
                    'last_activity': stats['last_success'] or stats['last_failure']
                })
        
        return sorted(chat_list, key=lambda x: x['total_messages'], reverse=True)[:limit]
    
    def _get_recent_errors(self, limit: int) -> List[Dict[str, Any]]:
        """Получение последних ошибок"""
        errors = []
        for metric in list(self.message_metrics)[-limit:]:
            if not metric.success:
                errors.append({
                    'timestamp': metric.timestamp,
                    'chat_id': metric.chat_id,
                    'error_type': metric.error_type
                })
        
        return sorted(errors, key=lambda x: x['timestamp'], reverse=True)
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        if not self.cycle_metrics:
            return {}
        
        recent_cycles = list(self.cycle_metrics)[-10:]  # Последние 10 циклов
        
        avg_duration = sum(c.total_duration for c in recent_cycles) / len(recent_cycles)
        avg_messages_per_cycle = sum(c.total_messages for c in recent_cycles) / len(recent_cycles)
        
        return {
            'avg_cycle_duration': avg_duration,
            'avg_messages_per_cycle': avg_messages_per_cycle,
            'cycles_per_hour': len(recent_cycles) / (recent_cycles[-1].end_time - recent_cycles[0].start_time).total_seconds() * 3600 if len(recent_cycles) > 1 else 0
        }
    
    def export_metrics(self, format: str = 'json') -> str:
        """Экспорт метрик в различных форматах"""
        if format == 'json':
            return json.dumps({
                'summary': self.get_summary_stats(),
                'message_metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'chat_id': m.chat_id,
                        'success': m.success,
                        'error_type': m.error_type,
                        'response_time': m.response_time
                    } for m in self.message_metrics
                ],
                'cycle_metrics': [
                    {
                        'start_time': c.start_time.isoformat(),
                        'end_time': c.end_time.isoformat(),
                        'total_messages': c.total_messages,
                        'successful_messages': c.successful_messages,
                        'total_duration': c.total_duration
                    } for c in self.cycle_metrics
                ]
            }, indent=2, ensure_ascii=False)
        
        return ""

class HealthChecker:
    """Проверка здоровья системы"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.last_health_check = None
    
    def check_health(self) -> Dict[str, Any]:
        """Проверка состояния системы"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Проверка последней активности
        last_activity = self.metrics.stats.get('last_activity')
        if last_activity:
            time_since_activity = (datetime.now() - last_activity).total_seconds()
            if time_since_activity > 3600:  # 1 час без активности
                health_status['checks']['activity'] = {
                    'status': 'warning',
                    'message': f'Нет активности {time_since_activity/60:.1f} минут'
                }
            else:
                health_status['checks']['activity'] = {
                    'status': 'ok',
                    'message': f'Последняя активность {time_since_activity/60:.1f} минут назад'
                }
        else:
            health_status['checks']['activity'] = {
                'status': 'error',
                'message': 'Нет данных об активности'
            }
        
        # Проверка процента успешности
        success_rate = self.metrics.stats.get('success_rate', 0)
        if success_rate < 80:
            health_status['checks']['success_rate'] = {
                'status': 'warning',
                'message': f'Низкий процент успешности: {success_rate:.1f}%'
            }
        else:
            health_status['checks']['success_rate'] = {
                'status': 'ok',
                'message': f'Процент успешности: {success_rate:.1f}%'
            }
        
        # Проверка FloodWait
        flood_waits = self.metrics.stats.get('total_flood_waits', 0)
        if flood_waits > 10:  # Много FloodWait
            health_status['checks']['flood_waits'] = {
                'status': 'warning',
                'message': f'Много FloodWait: {flood_waits}'
            }
        else:
            health_status['checks']['flood_waits'] = {
                'status': 'ok',
                'message': f'FloodWait: {flood_waits}'
            }
        
        # Определение общего статуса
        if any(check['status'] == 'error' for check in health_status['checks'].values()):
            health_status['status'] = 'error'
        elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
            health_status['status'] = 'warning'
        
        self.last_health_check = datetime.now()
        return health_status
