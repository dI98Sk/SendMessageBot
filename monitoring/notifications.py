"""
Система уведомлений и алертов
"""
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class NotificationLevel(Enum):
    """Уровни уведомлений"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Notification:
    """Уведомление"""
    level: NotificationLevel
    title: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class NotificationChannel:
    """Базовый класс для каналов уведомлений"""
    
    async def send(self, notification: Notification) -> bool:
        """Отправка уведомления"""
        raise NotImplementedError

class TelegramNotificationChannel(NotificationChannel):
    """Канал уведомлений через Telegram"""
    
    def __init__(self, client, admin_chat_id: int):
        self.client = client
        self.admin_chat_id = admin_chat_id
    
    async def send(self, notification: Notification) -> bool:
        """Отправка уведомления в Telegram"""
        try:
            emoji_map = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨"
            }
            
            emoji = emoji_map.get(notification.level, "📢")
            
            message = f"{emoji} **{notification.title}**\n\n{notification.message}"
            
            if notification.metadata:
                message += "\n\n**Детали:**"
                for key, value in notification.metadata.items():
                    message += f"\n• {key}: {value}"
            
            message += f"\n\n⏰ {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            await self.client.send_message(self.admin_chat_id, message, parse_mode='markdown')
            return True
            
        except Exception as e:
            print(f"Ошибка отправки Telegram уведомления: {e}")
            return False

class WebhookNotificationChannel(NotificationChannel):
    """Канал уведомлений через Webhook"""
    
    def __init__(self, webhook_url: str, timeout: int = 30):
        self.webhook_url = webhook_url
        self.timeout = timeout
    
    async def send(self, notification: Notification) -> bool:
        """Отправка уведомления через Webhook"""
        try:
            payload = {
                "level": notification.level.value,
                "title": notification.title,
                "message": notification.message,
                "timestamp": notification.timestamp.isoformat(),
                "metadata": notification.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            print(f"Ошибка отправки Webhook уведомления: {e}")
            return False

class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self):
        self.channels: List[NotificationChannel] = []
        self.notification_history: List[Notification] = []
        self.rate_limits: Dict[str, datetime] = {}
        self.enabled = True
    
    def add_channel(self, channel: NotificationChannel):
        """Добавление канала уведомлений"""
        self.channels.append(channel)
    
    def remove_channel(self, channel: NotificationChannel):
        """Удаление канала уведомлений"""
        if channel in self.channels:
            self.channels.remove(channel)
    
    async def send_notification(
        self,
        level: NotificationLevel,
        title: str,
        message: str,
        metadata: Dict[str, Any] = None,
        rate_limit_key: Optional[str] = None,
        rate_limit_seconds: int = 300  # 5 минут
    ) -> bool:
        """Отправка уведомления"""
        if not self.enabled:
            return False
        
        # Проверка rate limit
        if rate_limit_key:
            now = datetime.now()
            last_sent = self.rate_limits.get(rate_limit_key)
            if last_sent and (now - last_sent).total_seconds() < rate_limit_seconds:
                return False  # Пропускаем из-за rate limit
            
            self.rate_limits[rate_limit_key] = now
        
        # Создание уведомления
        notification = Notification(
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Добавление в историю
        self.notification_history.append(notification)
        
        # Отправка через все каналы
        success_count = 0
        for channel in self.channels:
            try:
                if await channel.send(notification):
                    success_count += 1
            except Exception as e:
                print(f"Ошибка отправки через канал {type(channel).__name__}: {e}")
        
        return success_count > 0
    
    async def send_info(self, title: str, message: str, **kwargs):
        """Отправка информационного уведомления"""
        return await self.send_notification(NotificationLevel.INFO, title, message, **kwargs)
    
    async def send_warning(self, title: str, message: str, **kwargs):
        """Отправка предупреждения"""
        return await self.send_notification(NotificationLevel.WARNING, title, message, **kwargs)
    
    async def send_error(self, title: str, message: str, **kwargs):
        """Отправка ошибки"""
        return await self.send_notification(NotificationLevel.ERROR, title, message, **kwargs)
    
    async def send_critical(self, title: str, message: str, **kwargs):
        """Отправка критического уведомления"""
        return await self.send_notification(NotificationLevel.CRITICAL, title, message, **kwargs)
    
    def get_notification_history(self, limit: int = 50) -> List[Notification]:
        """Получение истории уведомлений"""
        return self.notification_history[-limit:]
    
    def clear_history(self):
        """Очистка истории уведомлений"""
        self.notification_history.clear()
    
    def enable(self):
        """Включение уведомлений"""
        self.enabled = True
    
    def disable(self):
        """Отключение уведомлений"""
        self.enabled = False

class AlertManager:
    """Менеджер алертов на основе метрик"""
    
    def __init__(self, notification_manager: NotificationManager):
        self.notification_manager = notification_manager
        self.alert_rules: List[Dict[str, Any]] = []
        self.last_checks: Dict[str, datetime] = {}
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Добавление правила алерта"""
        self.alert_rules.append(rule)
    
    def add_default_rules(self):
        """Добавление стандартных правил алертов"""
        default_rules = [
            {
                "name": "low_success_rate",
                "condition": lambda metrics: metrics.get('success_rate', 100) < 80,
                "level": NotificationLevel.WARNING,
                "title": "Низкий процент успешности",
                "message_template": "Процент успешности рассылки: {success_rate:.1f}%"
            },
            {
                "name": "high_flood_waits",
                "condition": lambda metrics: metrics.get('total_flood_waits', 0) > 20,
                "level": NotificationLevel.WARNING,
                "title": "Много FloodWait",
                "message_template": "Обнаружено {total_flood_waits} FloodWait ограничений"
            },
            {
                "name": "no_activity",
                "condition": lambda metrics: self._check_no_activity(metrics),
                "level": NotificationLevel.ERROR,
                "title": "Нет активности",
                "message_template": "Рассылка неактивна более 2 часов"
            },
            {
                "name": "connection_errors",
                "condition": lambda metrics: self._check_connection_errors(metrics),
                "level": NotificationLevel.ERROR,
                "title": "Ошибки подключения",
                "message_template": "Обнаружены ошибки подключения к Telegram"
            }
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def _check_no_activity(self, metrics: Dict[str, Any]) -> bool:
        """Проверка отсутствия активности"""
        last_activity = metrics.get('last_activity')
        if not last_activity:
            return True
        
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        
        return (datetime.now() - last_activity).total_seconds() > 7200  # 2 часа
    
    def _check_connection_errors(self, metrics: Dict[str, Any]) -> bool:
        """Проверка ошибок подключения"""
        # Здесь можно добавить логику проверки ошибок подключения
        return False
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """Проверка алертов на основе метрик"""
        for rule in self.alert_rules:
            rule_name = rule['name']
            
            # Проверка частоты проверок
            check_interval = rule.get('check_interval', 300)  # 5 минут по умолчанию
            now = datetime.now()
            last_check = self.last_checks.get(rule_name)
            
            if last_check and (now - last_check).total_seconds() < check_interval:
                continue
            
            # Проверка условия
            try:
                if rule['condition'](metrics):
                    message = rule['message_template'].format(**metrics)
                    await self.notification_manager.send_notification(
                        level=rule['level'],
                        title=rule['title'],
                        message=message,
                        rate_limit_key=f"alert_{rule_name}",
                        rate_limit_seconds=rule.get('rate_limit', 1800)  # 30 минут по умолчанию
                    )
                    
                self.last_checks[rule_name] = now
                
            except Exception as e:
                print(f"Ошибка проверки правила алерта {rule_name}: {e}")

# Глобальный менеджер уведомлений
notification_manager = NotificationManager()
alert_manager = AlertManager(notification_manager)
