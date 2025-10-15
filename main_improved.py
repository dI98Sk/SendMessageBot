"""
Улучшенная версия главного файла приложения
"""
import asyncio
import signal
import sys
from pathlib import Path
from typing import List
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import config_manager, AppConfig
from utils.logger import get_logger
from core.broadcaster import EnhancedBroadcaster
from utils.google_sheets import GoogleSheetsManager, MessageUpdater
from config.message_updater import MessageConfigUpdater
from monitoring.reports import TelegramReporter
from core.queue import queue_manager, Priority, QueueItem
from monitoring.metrics import MetricsCollector, HealthChecker
from monitoring.notifications import (
    notification_manager, alert_manager,
    TelegramNotificationChannel, WebhookNotificationChannel
)
from utils.security import security_manager

class SendMessageBotApp:
    """Основной класс приложения"""

    def __init__(self):
        self.config: AppConfig = None
        self.logger = None
        self.broadcasters: List[EnhancedBroadcaster] = []
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker(self.metrics_collector)
        self.running = False
        self.tasks: List[asyncio.Task] = []

        # Google Sheets интеграция
        self.google_sheets_manager = None
        self.message_updater = None
        self.config_updater = None

        # Система отчетов
        self.telegram_reporter = None



    async def initialize(self):
        """Инициализация приложения"""
        try:
            # Загрузка конфигурации
            self.config = config_manager.load_config()

            # Инициализация логгера
            self.logger = get_logger("main", self.config.logging)

            self.logger.info("Инициализация SendMessageBot...")

            # Валидация конфигурации
            await self._validate_config()

            # Настройка уведомлений
            await self._setup_notifications()

            # Инициализация очередей
            await self._setup_queues()

            # Инициализация Google Sheets
            await self._setup_google_sheets()

            # Инициализация системы отчетов
            await self._setup_reports()

            # Создание broadcaster'ов
            await self._create_broadcasters()

            # Настройка обработчиков сигналов
            self._setup_signal_handlers()

            self.logger.info("Инициализация завершена успешно")

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Ошибка инициализации: {e}")
            else:
                print(f"Ошибка инициализации: {e}")
            raise

    async def _validate_config(self):
        """Валидация конфигурации"""
        # Проверка обязательных параметров
        if not self.config.telegram.api_id or not self.config.telegram.api_hash:
            raise ValueError("API_ID и API_HASH обязательны")

        # Проверка файлов сессий
        session_file = Path(f"{self.config.telegram.session_name}.session")
        if not session_file.exists():
            self.logger.warning(f"Файл сессии {session_file} не найден")

        # Проверка Google Sheets конфигурации
        if self.config.google_sheets.b2b_sheet_url or self.config.google_sheets.b2c_sheet_url:
            creds_file = Path(self.config.google_sheets.credentials_file)
            if not creds_file.exists():
                self.logger.warning(f"Файл учетных данных {creds_file} не найден")

    async def _setup_notifications(self):
        """Настройка системы уведомлений"""
        admin_id = self.config.telegram.api_id  # В реальном приложении должен быть отдельный параметр

        # Telegram уведомления
        if admin_id:
            # Здесь нужен клиент для отправки уведомлений
            # Для упрощения пропускаем
            pass

        # Webhook уведомления (отключены для тестирования)
        webhook_url = self.config.notifications.webhook_url
        if webhook_url and webhook_url != "https://your-webhook-url.com":
            webhook_channel = WebhookNotificationChannel(webhook_url)
            notification_manager.add_channel(webhook_channel)
            self.logger.info(f"Webhook уведомления включены: {webhook_url}")
        else:
            self.logger.info("Webhook уведомления отключены")

        # Настройка алертов
        alert_manager.add_default_rules()

    async def _setup_queues(self):
        """Настройка очередей"""
        # Создаем очереди для разных типов сообщений
        queue_manager.create_queue("b2b_messages", max_size=5000)
        queue_manager.create_queue("b2c_messages", max_size=5000)
        queue_manager.create_queue("priority_messages", max_size=1000)

    async def _create_broadcasters(self):
        """Создание broadcaster'ов"""
        print("📱 Создание broadcaster'ов...")

        # B2B Broadcaster
        b2b_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="B2B_Broadcaster",
            targets=self.config.test_targets,  # В реальном приложении: TARGETS
            messages=self.config.b2b_messages
        )
        self.broadcasters.append(b2b_broadcaster)
        print(f"✅ B2B Broadcaster создан: {len(self.config.test_targets)} чатов, {len(self.config.b2b_messages)} сообщений")

        # B2C Broadcaster
        b2c_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="B2C_Broadcaster",
            targets=self.config.test_targets,
            messages=self.config.b2c_messages
        )
        self.broadcasters.append(b2c_broadcaster)
        print(f"✅ B2C Broadcaster создан: {len(self.config.test_targets)} чатов, {len(self.config.b2c_messages)} сообщений")

    async def _setup_google_sheets(self):
        """Настройка Google Sheets интеграции"""
        try:
            # Инициализация Google Sheets менеджера
            self.google_sheets_manager = GoogleSheetsManager(
                credentials_file=self.config.google_sheets.credentials_file
            )

            # Инициализация обновлятеля сообщений
            self.config_updater = MessageConfigUpdater()

            # Инициализация MessageUpdater
            self.message_updater = MessageUpdater(self.google_sheets_manager)

            # Добавляем callback для обновления конфигурации
            self.message_updater.add_update_callback(self._on_messages_updated)

            self.logger.info("Google Sheets интеграция настроена")

            # Первоначальное обновление сообщений, если нужно
            if (self.config.google_sheets.b2b_sheet_url or self.config.google_sheets.b2c_sheet_url):
                try:
                    await self._initial_message_update()
                except Exception as e:
                    self.logger.warning(f"Не удалось выполнить первоначальное обновление Google Sheets: {e}")
                    self.logger.info("Продолжаем работу с текущими сообщениями")

        except Exception as e:
            self.logger.error(f"Ошибка настройки Google Sheets: {e}")

    async def _initial_message_update(self):
        """Первоначальное обновление сообщений"""
        try:
            self.logger.info("Выполняем первоначальное обновление сообщений...")

            success = await self.message_updater.update_messages_from_sheets(
                self.config.google_sheets.b2b_sheet_url,
                self.config.google_sheets.b2c_sheet_url
            )

            if success:
                self.logger.info("Первоначальное обновление сообщений завершено")
                # Перезагружаем конфигурацию с новыми сообщениями
                self.config = config_manager.load_config()
                # Пересоздаем broadcaster'ы с новыми сообщениями
                await self._recreate_broadcasters()
            else:
                self.logger.warning("Первоначальное обновление сообщений не удалось")

        except Exception as e:
            self.logger.error(f"Ошибка первоначального обновления: {e}")

    async def _on_messages_updated(self, new_messages):
        """Callback для обновления сообщений"""
        try:
            self.logger.info("Получены новые сообщения из Google Sheets")

            # Обновляем файл конфигурации
            self.config_updater.update_messages_file(
                new_messages['b2b'],
                new_messages['b2c']
            )

            # Перезагружаем модуль сообщений
            self.config_updater.reload_messages_module()

            # Перезагружаем конфигурацию
            self.config = config_manager.load_config()

            # Пересоздаем broadcaster'ы с новыми сообщениями
            await self._recreate_broadcasters()

            # Отправляем уведомление
            await notification_manager.send_info(
                "Сообщения обновлены",
                f"Получены новые сообщения: B2B={len(new_messages['b2b'])}, B2C={len(new_messages['b2c'])}"
            )

        except Exception as e:
            self.logger.error(f"Ошибка в callback обновления сообщений: {e}")

    async def _recreate_broadcasters(self):
        """Пересоздание broadcaster'ов с новыми сообщениями"""
        try:
            # Останавливаем старые broadcaster'ы
            for broadcaster in self.broadcasters:
                await broadcaster.stop()

            # Очищаем список
            self.broadcasters.clear()

            # Создаем новые broadcaster'ы
            await self._create_broadcasters()

            self.logger.info("Broadcaster'ы пересозданы с новыми сообщениями")

        except Exception as e:
            self.logger.error(f"Ошибка пересоздания broadcaster'ов: {e}")

    async def _setup_reports(self):
        """Настройка системы отчетов"""
        try:
            if not self.config.reports.enable_reports:
                self.logger.info("Система отчетов отключена")
                return

            if not self.config.reports.telegram_bot_token or not self.config.reports.telegram_channel_id:
                self.logger.warning("Не настроены REPORTS_BOT_TOKEN или REPORTS_CHANNEL_ID")
                return

            # Инициализация Telegram репортера
            self.telegram_reporter = TelegramReporter(
                bot_token=self.config.reports.telegram_bot_token,
                channel_id=self.config.reports.telegram_channel_id,
                timezone=self.config.reports.timezone
            )

            self.logger.info("Система отчетов настроена")

        except Exception as e:
            self.logger.error(f"Ошибка настройки системы отчетов: {e}")

    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов"""
        def signal_handler(signum, frame):
            self.logger.info(f"Получен сигнал {signum}, завершаем работу...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def _health_check_task(self):
        """Задача проверки здоровья системы"""
        while self.running:
            try:
                # Сбор метрик
                health_status = self.health_checker.check_health()

                # Проверка алертов
                stats = self.metrics_collector.get_summary_stats()
                await alert_manager.check_alerts(stats['general'])

                # Отправка уведомления о статусе
                if health_status['status'] != 'healthy':
                    await notification_manager.send_warning(
                        "Проблемы с системой",
                        f"Статус: {health_status['status']}",
                        rate_limit_key="health_check",
                        rate_limit_seconds=1800  # 30 минут
                    )

                await asyncio.sleep(300)  # Проверка каждые 5 минут

            except Exception as e:
                self.logger.exception(f"Ошибка в health check: {e}")
                await asyncio.sleep(60)

    async def _metrics_collection_task(self):
        """Задача сбора метрик"""
        while self.running:
            try:
                # Сбор статистики от broadcaster'ов
                for broadcaster in self.broadcasters:
                    stats = broadcaster.get_stats()
                    # Здесь можно добавить метрики в collector

                await asyncio.sleep(60)  # Сбор каждую минуту

            except Exception as e:
                self.logger.exception(f"Ошибка сбора метрик: {e}")
                await asyncio.sleep(60)

    async def start(self):
        """Запуск приложения"""
        if self.running:
            self.logger.warning("Приложение уже запущено")
            return

        self.running = True
        self.logger.info("Запуск SendMessageBot...")

        try:
            # Запуск broadcaster'ов
            broadcaster_tasks = []
            for broadcaster in self.broadcasters:
                task = asyncio.create_task(broadcaster.start())
                broadcaster_tasks.append(task)
                self.tasks.append(task)

            # Запуск фоновых задач
            health_task = asyncio.create_task(self._health_check_task())
            metrics_task = asyncio.create_task(self._metrics_collection_task())

            self.tasks.extend([health_task, metrics_task])

            # Отправка уведомления о запуске
            await notification_manager.send_info(
                "SendMessageBot запущен",
                "Система рассылки успешно запущена"
            )

            self.logger.info("SendMessageBot запущен успешно")
            print("🚀 SendMessageBot запущен успешно!")
            print(f"📊 Запущено broadcaster'ов: {len(self.broadcasters)}")
            print(f"🎯 Используются тестовые чаты: {len(self.config.test_targets)}")
            print("💬 Начинаем рассылку...")

            print("\n💡 Для просмотра статистики в реальном времени запустите:")
            print("   python watch_stats.py")
            print("   или python show_stats.py")

            print("\n💡 Для просмотра статистики в реальном времени запустите:")
            print("   python watch_stats.py")
            print("   или python show_stats.py")

            # Запуск задачи для периодического вывода статистики
            stats_task = asyncio.create_task(self._stats_display_task())
            self.tasks.append(stats_task)


            # Запуск задачи периодического обновления сообщений
            if self.message_updater and (
                    self.config.google_sheets.b2b_sheet_url or self.config.google_sheets.b2c_sheet_url):
                update_task = asyncio.create_task(
                    self.message_updater.start_periodic_updates(
                        self.config.google_sheets.b2b_sheet_url,
                        self.config.google_sheets.b2c_sheet_url,
                        self.config.google_sheets.update_interval // 3600  # Конвертируем секунды в часы
                    )
                )
                self.tasks.append(update_task)
                print("📊 Автоматическое обновление сообщений из Google Sheets включено")

            # Запуск системы отчетов
            if self.telegram_reporter:
                report_task = asyncio.create_task(
                    self.telegram_reporter.start(self.broadcasters)
                )
                self.tasks.append(report_task)
                self.logger.info(
                    f"Система отчетов запущена (интервал: {self.config.reports.report_interval_hours} часов)")
                print(
                    f"📈 Система отчетов запущена (отчеты каждые {self.config.reports.report_interval_hours} часов)")

            # Ожидание завершения всех задач
            await asyncio.gather(*self.tasks, return_exceptions=True)

        except Exception as e:
            self.logger.exception(f"Ошибка в главном цикле: {e}")
            await notification_manager.send_critical(
                "Критическая ошибка",
                f"Приложение остановлено из-за ошибки: {e}"
            )
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Корректное завершение приложения"""
        if not self.running:
            return

        self.logger.info("Завершение работы SendMessageBot...")
        self.running = False

        # Остановка broadcaster'ов
        for broadcaster in self.broadcasters:
            await broadcaster.stop()

        # Остановка системы отчетов
        if self.telegram_reporter:
            await self.telegram_reporter.stop()

        # Отмена всех задач
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Ожидание завершения задач
        await asyncio.gather(*self.tasks, return_exceptions=True)

        # Отправка уведомления о завершении
        await notification_manager.send_info(
            "SendMessageBot остановлен",
            "Система рассылки корректно остановлена"
        )

        self.logger.info("SendMessageBot завершен")

    async def _stats_display_task(self):
        """Задача для периодического отображения статистики"""
        try:
            while self.running:
                await asyncio.sleep(30)  # Каждые 30 секунд

                if not self.running:
                    break

                print(f"\n{'=' * 60}")
                print(f"📊 СТАТИСТИКА ({datetime.now().strftime('%H:%M:%S')})")
                print(f"{'=' * 60}")

                # Общая статистика
                total_sent = sum(b.stats.total_sent for b in self.broadcasters)
                total_failed = sum(b.stats.total_failed for b in self.broadcasters)
                total_flood_waits = sum(b.stats.flood_waits for b in self.broadcasters)

                print(f"🎯 Всего чатов: {len(self.config.test_targets)}")
                print(f"✅ Отправлено: {total_sent}")
                print(f"❌ Ошибок: {total_failed}")
                print(f"⏳ FloodWait: {total_flood_waits}")

                if total_sent + total_failed > 0:
                    success_rate = (total_sent / (total_sent + total_failed)) * 100
                    print(f"📈 Успешность: {success_rate:.1f}%")

                # Статистика по каждому broadcaster'у
                for broadcaster in self.broadcasters:
                    broadcaster.print_stats()

                print(f"{'=' * 60}")

        except asyncio.CancelledError:
            print("\n📊 Статистика остановлена")
        except Exception as e:
            self.logger.error(f"Ошибка в задаче статистики: {e}")

async def main():
    """Главная функция"""
    app = SendMessageBotApp()
    
    try:
        await app.initialize()
        await app.start()
    except KeyboardInterrupt:
        print("\nПолучен сигнал прерывания...")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        await app.shutdown()

if __name__ == "__main__":
    # Настройка обработки исключений
    def exception_handler(loop, context):
        print(f"Необработанное исключение: {context}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_exception_handler(exception_handler)
    
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
