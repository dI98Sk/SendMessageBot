"""
Система отчетов для мониторинга работы бота
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pytz

from broadcaster.config.settings import LoggingConfig, config_manager
from broadcaster.utils.logger import get_logger
from broadcaster.monitoring.metrics import MetricsCollector

# Получаем конфигурацию для логгера
config = config_manager.load_config()
logger = get_logger(__name__, config.logging)

@dataclass
class ReportData:
    """Данные для отчета"""
    timestamp: datetime
    total_sent: int
    total_failed: int
    total_flood_waits: int
    success_rate: float
    avg_response_time: float
    cycles_completed: int
    active_broadcasters: int
    last_activity: Optional[datetime]
    errors_summary: Dict[str, int]
    top_chats: List[Dict[str, Any]]

class TelegramReporter:
    """Класс для отправки отчетов в Telegram"""
    
    def __init__(self, bot_token: str, channel_id: str, timezone: str = "Europe/Moscow"):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.timezone = pytz.timezone(timezone)
        self.last_report_time: Optional[datetime] = None
        self.report_interval_hours: float = 3.0  # Отчеты каждые N часов (поддержка дробных значений для тестирования)
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.logger = get_logger("telegram_reporter", config.logging)
        
        # Статистика отчетов
        self.reports_sent = 0
        self.last_report_data: Optional[ReportData] = None
        
        # Функция для получения актуального списка broadcaster'ов
        self.get_broadcasters_func = None
    
    async def _send_telegram_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Отправка сообщения в Telegram канал"""
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            self.logger.debug(f"Отправка отчета в канал: {self.channel_id}")
            self.logger.debug(f"Длина сообщения: {len(message)} символов")
            
            data = {
                "chat_id": self.channel_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        self.logger.info("✅ Отчет успешно отправлен в Telegram")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Ошибка отправки в Telegram:")
                        self.logger.error(f"   Статус: {response.status}")
                        self.logger.error(f"   Ответ: {error_text}")
                        self.logger.error(f"   URL: {url}")
                        self.logger.error(f"   Channel ID: {self.channel_id}")
                        
                        # Попробуем распарсить JSON ошибку
                        try:
                            import json
                            error_json = json.loads(error_text)
                            if 'description' in error_json:
                                self.logger.error(f"   Описание ошибки: {error_json['description']}")
                        except:
                            pass
                        
                        return False
                        
        except Exception as e:
            self.logger.error(f"❌ Исключение при отправке отчета в Telegram: {e}")
            self.logger.exception("Полный traceback:")
            return False
    
    def _format_report_message(self, report_data: ReportData) -> str:
        """Форматирование сообщения отчета"""
        timestamp = report_data.timestamp.astimezone(self.timezone)
        
        # Эмодзи для статуса
        if report_data.success_rate >= 95:
            status_emoji = "🟢"
            status_text = "Отлично"
        elif report_data.success_rate >= 80:
            status_emoji = "🟡"
            status_text = "Хорошо"
        else:
            status_emoji = "🔴"
            status_text = "Требует внимания"
        
        # Время с последней активности
        if report_data.last_activity:
            # Убедимся, что оба объекта datetime имеют timezone
            now_tz = datetime.now(self.timezone)
            last_activity_tz = report_data.last_activity
            
            # Если last_activity без timezone, добавляем timezone
            if last_activity_tz.tzinfo is None:
                last_activity_tz = self.timezone.localize(last_activity_tz)
            
            time_since_activity = (now_tz - last_activity_tz).total_seconds()
            if time_since_activity < 3600:  # Менее часа
                activity_text = f"{time_since_activity/60:.0f} мин назад"
            elif time_since_activity < 86400:  # Менее суток
                activity_text = f"{time_since_activity/3600:.0f} ч назад"
            else:
                activity_text = f"{time_since_activity/86400:.0f} дн назад"
        else:
            activity_text = "Нет данных"
        
        # Топ ошибок
        errors_text = ""
        if report_data.errors_summary:
            top_errors = sorted(report_data.errors_summary.items(), key=lambda x: x[1], reverse=True)[:3]
            errors_text = "\n🚨 Топ ошибок:\n"
            for error_type, count in top_errors:
                errors_text += f"   • {error_type}: {count}\n"
        
        # Топ чатов
        chats_text = ""
        if report_data.top_chats:
            chats_text = "\n📊 Топ чатов:\n"
            for i, chat in enumerate(report_data.top_chats[:3], 1):
                chats_text += f"   {i}. {chat['chat_id']}: {chat['total_messages']} сообщений\n"
        
        message = f"""
📈 <b>ОТЧЕТ SendMessageBot</b> {status_emoji}

⏰ <b>Время:</b> {timestamp.strftime('%d.%m.%Y %H:%M')}
📊 <b>Статус:</b> {status_text}

📤 <b>Статистика за период:</b>
   • Отправлено: {report_data.total_sent}
   • Ошибок: {report_data.total_failed}
   • FloodWait: {report_data.total_flood_waits}
   • Успешность: {report_data.success_rate:.1f}%
   • Среднее время ответа: {report_data.avg_response_time:.2f}с

🔄 <b>Производительность:</b>
   • Циклов завершено: {report_data.cycles_completed}
   • Активных broadcaster'ов: {report_data.active_broadcasters}
   • Последняя активность: {activity_text}
{errors_text}{chats_text}
💡 <i>Следующий отчет через {self.report_interval_hours} часа</i>
"""
        return message.strip()
    
    def _collect_report_data(self, broadcasters: List[Any]) -> ReportData:
        """Сбор данных для отчета"""
        total_sent = sum(b.stats.total_sent for b in broadcasters)
        total_failed = sum(b.stats.total_failed for b in broadcasters)
        total_flood_waits = sum(b.stats.flood_waits for b in broadcasters)
        
        # Расчет успешности
        total_attempts = total_sent + total_failed
        success_rate = (total_sent / total_attempts * 100) if total_attempts > 0 else 0
        
        # Среднее время ответа
        all_response_times = []
        for b in broadcasters:
            if hasattr(b, 'metrics') and b.metrics.message_metrics:
                times = [m.response_time for m in b.metrics.message_metrics if m.response_time > 0]
                all_response_times.extend(times)
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        
        # Количество циклов
        cycles_completed = sum(b.metrics.stats.get('total_cycles_completed', 0) for b in broadcasters if hasattr(b, 'metrics'))
        
        # Последняя активность
        last_activities = [b.stats.last_sent_time for b in broadcasters if b.stats.last_sent_time]
        last_activity = max(last_activities) if last_activities else None
        
        # Сводка ошибок
        errors_summary = {}
        for b in broadcasters:
            if hasattr(b, 'metrics'):
                for chat_id, chat_stats in b.metrics.chat_stats.items():
                    for error_type, count in chat_stats['error_types'].items():
                        errors_summary[error_type] = errors_summary.get(error_type, 0) + count
        
        # Топ чатов
        top_chats = []
        for b in broadcasters:
            if hasattr(b, 'metrics'):
                top_chats.extend(b.metrics._get_top_chats(5))
        
        # Сортируем по общему количеству сообщений
        top_chats = sorted(top_chats, key=lambda x: x['total_messages'], reverse=True)[:5]
        
        return ReportData(
            timestamp=datetime.now(self.timezone),
            total_sent=total_sent,
            total_failed=total_failed,
            total_flood_waits=total_flood_waits,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            cycles_completed=cycles_completed,
            active_broadcasters=len([b for b in broadcasters if b._running]),
            last_activity=last_activity,
            errors_summary=errors_summary,
            top_chats=top_chats
        )
    
    async def send_report(self, broadcasters: List[Any]) -> bool:
        """Отправка отчета"""
        try:
            self.logger.info("Формирование отчета...")
            
            # Собираем данные
            report_data = self._collect_report_data(broadcasters)
            
            # Проверяем, есть ли данные для отправки (пропускаем пустые отчеты)
            if report_data.total_sent == 0 and report_data.total_failed == 0:
                self.logger.info("Пропуск отчета: нет данных для отправки (broadcaster'ы еще не начали работу)")
                # НЕ устанавливаем last_report_time, чтобы отчет отправился позже, когда появятся данные
                return False
            
            self.last_report_data = report_data
            
            # Форматируем сообщение
            message = self._format_report_message(report_data)
            
            self.logger.info(f"Отправка отчета: {report_data.total_sent} отправлено, {report_data.total_failed} ошибок")
            
            # Отправляем
            success = await self._send_telegram_message(message)
            
            if success:
                self.last_report_time = datetime.now(self.timezone)
                self.reports_sent += 1
                self.logger.info(f"✅ Отчет #{self.reports_sent} отправлен успешно в канал {self.channel_id}")
            else:
                self.logger.error(f"❌ Не удалось отправить отчет в канал {self.channel_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке отчета: {e}")
            return False
    
    def should_send_report(self) -> bool:
        """Проверка, нужно ли отправлять отчет"""
        if self.last_report_time is None:
            return True
        
        time_since_last = datetime.now(self.timezone) - self.last_report_time
        return time_since_last.total_seconds() >= (self.report_interval_hours * 3600)
    
    async def _report_loop(self):
        """Основной цикл отправки отчетов"""
        self.logger.info(f"🚀 Запуск системы отчетов (интервал: {self.report_interval_hours} часов)")
        self.logger.info(f"📊 Канал для отчетов: {self.channel_id}")
        
        # Вычисляем интервал проверки (минимум 5 минут, максимум 1 час)
        check_interval = min(max(self.report_interval_hours * 3600 / 6, 300), 3600)  
        self.logger.info(f"⏰ Проверка каждые {check_interval/60:.1f} минут")
        
        while self.running:
            try:
                # Проверяем, нужно ли отправлять отчет
                if self.should_send_report():
                    self.logger.info("📈 Пора отправлять отчет...")
                    # Получаем актуальный список broadcaster'ов
                    broadcasters = self.get_broadcasters_func() if self.get_broadcasters_func else []
                    if broadcasters:
                        self.logger.info(f"📡 Broadcaster'ов активно: {len([b for b in broadcasters if b._running])}/{len(broadcasters)}")
                        await self.send_report(broadcasters)
                    else:
                        self.logger.warning("⚠️ Нет broadcaster'ов для отчета")
                else:
                    # Вычисляем время до следующего отчета
                    if self.last_report_time:
                        time_since_last = (datetime.now(self.timezone) - self.last_report_time).total_seconds()
                        time_until_next = (self.report_interval_hours * 3600) - time_since_last
                        self.logger.debug(f"⏳ До следующего отчета: {time_until_next/60:.1f} минут")
                
                # Ждем до следующей проверки
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("🛑 Система отчетов остановлена")
                break
            except Exception as e:
                self.logger.error(f"❌ Ошибка в цикле отчетов: {e}")
                await asyncio.sleep(check_interval)
    
    async def start(self, get_broadcasters_func):
        """Запуск системы отчетов
        
        Args:
            get_broadcasters_func: Функция, которая возвращает актуальный список broadcaster'ов
        """
        if self.running:
            self.logger.warning("Система отчетов уже запущена")
            return
        
        if not self.bot_token or not self.channel_id:
            self.logger.warning("Не настроены bot_token или channel_id для отчетов")
            return
        
        self.get_broadcasters_func = get_broadcasters_func
        self.running = True
        self.task = asyncio.create_task(self._report_loop())
        self.logger.info("Система отчетов запущена")
    
    async def stop(self):
        """Остановка системы отчетов"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Система отчетов остановлена")
    
    def force_send_report(self):
        """Принудительная отправка отчета"""
        if self.running and self.get_broadcasters_func:
            self.logger.info("Запуск принудительного отчета")
            broadcasters = self.get_broadcasters_func()
            asyncio.create_task(self.send_report(broadcasters))
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы отчетов"""
        next_report_time = None
        if self.last_report_time:
            next_report_time = self.last_report_time + timedelta(hours=self.report_interval_hours)
        
        return {
            'running': self.running,
            'reports_sent': self.reports_sent,
            'last_report_time': self.last_report_time.isoformat() if self.last_report_time else None,
            'next_report_time': next_report_time.isoformat() if next_report_time else None,
            'report_interval_hours': self.report_interval_hours,
            'channel_id': self.channel_id
        }
