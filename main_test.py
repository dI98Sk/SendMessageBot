"""
Тестовая версия главного файла приложения
ПОЛНЫЙ ДУБЛИКАТ main.py, но с ТЕСТОВЫМИ чатами:
- Прайсы → TEST_TARGETS (2 чата)
- Реклама → TEST_TARGETS_ADS (2 чата)
"""
import asyncio
import signal
import sys
import os
from pathlib import Path
from typing import List
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

# ⚠️ ОТКЛЮЧАЕМ scheduling и тихий час для тестирования
os.environ["ENABLE_SCHEDULING"] = "false"
os.environ["ENABLE_QUIET_HOURS"] = "false"

from config.settings import config_manager, AppConfig
from utils.logger import get_logger
from core.broadcaster import EnhancedBroadcaster
from utils.google_sheets import GoogleSheetsFetcher
from config.message_updater import MessageConfigUpdater
from monitoring.reports import TelegramReporter
from core.queue import queue_manager, Priority, QueueItem
from monitoring.metrics import MetricsCollector, HealthChecker
from monitoring.notifications import (
    notification_manager, alert_manager,
    TelegramNotificationChannel, WebhookNotificationChannel
)
from utils.security import security_manager

class SendMessageBotTestApp:
    """Тестовая версия приложения (полный дубликат, но с TEST чатами)"""

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
        
        # Система уведомлений
        self.notification_client = None

    async def initialize(self):
        """Инициализация приложения"""
        try:
            # Загрузка конфигурации
            self.config = config_manager.load_config()

            # Инициализация логгера
            self.logger = get_logger("main_test", self.config.logging)

            self.logger.info("🧪 Инициализация ТЕСТОВОЙ версии SendMessageBot...")

            # Валидация конфигурации
            await self._validate_config()

            # Настройка уведомлений
            await self._setup_notifications()

            # Инициализация очередей
            await self._setup_queues()

            # Инициализация системы отчетов
            await self._setup_reports()

            # Создание broadcaster'ов (если еще не созданы)
            if not self.broadcasters:
                await self._create_broadcasters()
            else:
                self.logger.info(f"Broadcaster'ы уже созданы: {len(self.broadcasters)} шт.")

            # Настройка обработчиков сигналов
            self._setup_signal_handlers()

            self.logger.info("✅ Инициализация завершена успешно")

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

    async def _setup_notifications(self):
        """Настройка системы уведомлений"""
        self.logger.info("Настройка системы уведомлений...")
        
        # Telegram уведомления
        if self.config.notifications.enable_telegram_notifications:
            admin_id = self.config.notifications.admin_telegram_id
            
            if admin_id:
                try:
                    from telethon import TelegramClient
                    
                    self.logger.info(f"Создание Telegram клиента для уведомлений...")
                    
                    notification_client = TelegramClient(
                        f"notification_session",
                        self.config.telegram.api_id,
                        self.config.telegram.api_hash
                    )
                    
                    await notification_client.start(phone=self.config.telegram.phone)
                    
                    telegram_channel = TelegramNotificationChannel(
                        client=notification_client,
                        admin_chat_id=admin_id
                    )
                    
                    notification_manager.add_channel(telegram_channel)
                    self.notification_client = notification_client
                    
                    self.logger.info(f"✅ Telegram уведомления включены для admin: {admin_id}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Ошибка настройки Telegram уведомлений: {e}")
                    self.logger.warning("Продолжаем работу без Telegram уведомлений")
            else:
                self.logger.warning("⚠️ ADMIN_TELEGRAM_ID не настроен - Telegram уведомления отключены")
        else:
            self.logger.info("📱 Telegram уведомления отключены в конфигурации")

        # Настройка алертов
        try:
            alert_manager.add_default_rules()
            self.logger.info("✅ Система алертов настроена")
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки алертов: {e}")

    async def _setup_queues(self):
        """Настройка очередей"""
        queue_manager.create_queue("test_messages", max_size=5000)
        queue_manager.create_queue("test_ads_messages", max_size=5000)
        queue_manager.create_queue("priority_messages", max_size=1000)

    async def _create_broadcasters(self):
        """Создание broadcaster'ов С ТЕСТОВЫМИ ЧАТАМИ"""
        before_count = len(self.broadcasters)
        print(f"🧪 Создание ТЕСТОВЫХ broadcaster'ов... (текущее количество: {before_count})")
        
        if self.logger:
            self.logger.info(f"🧪 Создание ТЕСТОВЫХ broadcaster'ов... (текущее количество: {before_count})")

        # ========================================
        # ПРАЙСЫ → TEST_TARGETS (2 чата)
        # ========================================
        
        print(f"\n📊 ПРАЙСЫ → TEST_TARGETS ({len(self.config.targets)} чатов)")
        
        # AAA Прайсы - использует аккаунт acc1 (ID: ОПТОВЫЙ)
        aaa_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="AAA_PRICE_TEST_Broadcaster",
            targets=self.config.targets,  # ⚠️ TEST_TARGETS вместо targets_prices
            messages=self.config.aaa_messages,
            session_name="sessions/acc1"
        )
        self.broadcasters.append(aaa_broadcaster)
        print(f"✅ AAA PRICE TEST Broadcaster создан (acc1): {len(self.config.targets)} чатов, {len(self.config.aaa_messages)} сообщений")

        # GUS Прайсы - использует аккаунт acc2 (ID: РОЗНИЧНЫЙ)
        gus_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="GUS_PRICE_TEST_Broadcaster",
            targets=self.config.targets,  # ⚠️ TEST_TARGETS вместо targets_prices
            messages=self.config.gus_messages,
            session_name="sessions/acc2"
        )
        self.broadcasters.append(gus_broadcaster)
        print(f"✅ GUS PRICE TEST Broadcaster создан (acc2): {len(self.config.targets)} чатов, {len(self.config.gus_messages)} сообщений")
        
        # ========================================
        # РЕКЛАМА → TEST_TARGETS_ADS (2 чата)
        # ========================================
        
        print(f"\n📢 РЕКЛАМА → TEST_TARGETS_ADS ({len(self.config.targets_ads_test)} чатов)")
        
        # AAA Реклама - использует аккаунт acc2 (Анна Макарова)
        aaa_ads_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="AAA_ADS_TEST_Broadcaster",
            targets=self.config.targets_ads_test,  # ⚠️ TEST_TARGETS_ADS вместо targets_ads
            messages=self.config.aaa_ads_messages,
            session_name="sessions/acc2"
        )
        self.broadcasters.append(aaa_ads_broadcaster)
        print(f"✅ AAA ADS TEST Broadcaster создан (acc2): {len(self.config.targets_ads_test)} чатов, {len(self.config.aaa_ads_messages)} сообщений")
        
        # GUS Реклама - использует аккаунт acc1 (Яблочный Гусь Менеджер)
        gus_ads_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="GUS_ADS_TEST_Broadcaster",
            targets=self.config.targets_ads_test,  # ⚠️ TEST_TARGETS_ADS вместо targets_ads
            messages=self.config.gus_ads_messages,
            session_name="sessions/acc1"
        )
        self.broadcasters.append(gus_ads_broadcaster)
        print(f"✅ GUS ADS TEST Broadcaster создан (acc1): {len(self.config.targets_ads_test)} чатов, {len(self.config.gus_ads_messages)} сообщений")
        
        after_count = len(self.broadcasters)
        print(f"\n📊 Всего ТЕСТОВЫХ broadcaster'ов: {after_count}")
        print("=" * 70)
        
        if self.logger:
            self.logger.info(f"Всего broadcaster'ов после создания: {after_count}")

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
            self.telegram_reporter.report_interval_hours = self.config.reports.report_interval_hours

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
                health_status = self.health_checker.check_health()

                stats = self.metrics_collector.get_summary_stats()
                await alert_manager.check_alerts(stats['general'])

                if health_status['status'] != 'healthy':
                    await notification_manager.send_warning(
                        "Проблемы с системой",
                        f"Статус: {health_status['status']}",
                        rate_limit_key="health_check",
                        rate_limit_seconds=1800
                    )

                await asyncio.sleep(300)

            except Exception as e:
                self.logger.exception(f"Ошибка в health check: {e}")
                await asyncio.sleep(60)

    async def _metrics_collection_task(self):
        """Задача сбора метрик"""
        while self.running:
            try:
                for broadcaster in self.broadcasters:
                    stats = broadcaster.get_stats()

                await asyncio.sleep(60)

            except Exception as e:
                self.logger.exception(f"Ошибка сбора метрик: {e}")
                await asyncio.sleep(60)

    async def start(self):
        """Запуск приложения"""
        if self.running:
            self.logger.warning("Приложение уже запущено")
            return

        self.running = True
        self.logger.info("🧪 Запуск ТЕСТОВОЙ версии SendMessageBot...")
        self.logger.info(f"Количество broadcaster'ов для запуска: {len(self.broadcasters)}")

        try:
            # Запуск broadcaster'ов
            broadcaster_tasks = []
            for idx, broadcaster in enumerate(self.broadcasters, 1):
                self.logger.info(f"Запуск broadcaster {idx}/{len(self.broadcasters)}: {broadcaster.name}")
                task = asyncio.create_task(broadcaster.start())
                broadcaster_tasks.append(task)
                self.tasks.append(task)

            # Запуск фоновых задач
            health_task = asyncio.create_task(self._health_check_task())
            metrics_task = asyncio.create_task(self._metrics_collection_task())

            self.tasks.extend([health_task, metrics_task])

            # Отправка уведомления о запуске
            await notification_manager.send_info(
                "🧪 ТЕСТОВЫЙ SendMessageBot запущен",
                "Система рассылки в ТЕСТОВОМ режиме успешно запущена"
            )

            self.logger.info("🧪 ТЕСТОВЫЙ SendMessageBot запущен успешно")
            print("🧪 ТЕСТОВЫЙ SendMessageBot запущен успешно!")
            print(f"📊 Запущено broadcaster'ов: {len(self.broadcasters)}")
            print(f"🎯 Прайсы → TEST_TARGETS: {len(self.config.targets)} чатов")
            print(f"📢 Реклама → TEST_TARGETS_ADS: {len(self.config.targets_ads_test)} чатов")
            print("💬 Начинаем рассылку...")

            print("\n💡 Для просмотра статистики в реальном времени запустите:")
            print("   python watch_stats.py")
            print("   или python show_stats.py")

            # Запуск задачи для периодического вывода статистики
            stats_task = asyncio.create_task(self._stats_display_task())
            self.tasks.append(stats_task)

            # Запуск системы отчетов
            if self.telegram_reporter:
                report_task = asyncio.create_task(
                    self.telegram_reporter.start(lambda: self.broadcasters)
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

        self.logger.info("Завершение работы ТЕСТОВОГО SendMessageBot...")
        self.running = False

        # Остановка broadcaster'ов
        for broadcaster in self.broadcasters:
            await broadcaster.stop()

        # Остановка системы отчетов
        if self.telegram_reporter:
            await self.telegram_reporter.stop()

        # Закрытие клиента уведомлений
        if self.notification_client:
            try:
                await self.notification_client.disconnect()
                self.logger.info("Telegram клиент уведомлений отключен")
            except Exception as e:
                self.logger.error(f"Ошибка отключения клиента уведомлений: {e}")

        # Отмена всех задач
        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)

        # Отправка уведомления о завершении
        await notification_manager.send_info(
            "🧪 ТЕСТОВЫЙ SendMessageBot остановлен",
            "Система рассылки корректно остановлена"
        )

        self.logger.info("ТЕСТОВЫЙ SendMessageBot завершен")

    async def _stats_display_task(self):
        """Задача для периодического отображения статистики"""
        try:
            while self.running:
                await asyncio.sleep(30)

                if not self.running:
                    break

                print(f"\n{'=' * 60}")
                print(f"📊 ТЕСТОВАЯ СТАТИСТИКА ({datetime.now().strftime('%H:%M:%S')})")
                print(f"{'=' * 60}")

                total_sent = sum(b.stats.total_sent for b in self.broadcasters)
                total_failed = sum(b.stats.total_failed for b in self.broadcasters)
                total_flood_waits = sum(b.stats.flood_waits for b in self.broadcasters)

                print(f"🎯 Тестовых чатов прайсы: {len(self.config.targets)}")
                print(f"📢 Тестовых чатов реклама: {len(self.config.targets_ads_test)}")
                print(f"✅ Отправлено: {total_sent}")
                print(f"❌ Ошибок: {total_failed}")
                print(f"⏳ FloodWait: {total_flood_waits}")

                if total_sent + total_failed > 0:
                    success_rate = (total_sent / (total_sent + total_failed)) * 100
                    print(f"📈 Успешность: {success_rate:.1f}%")

                for broadcaster in self.broadcasters:
                    broadcaster.print_stats()

                print(f"{'=' * 60}")

        except asyncio.CancelledError:
            print("\n📊 Статистика остановлена")
        except Exception as e:
            self.logger.error(f"Ошибка в задаче статистики: {e}")

async def main():
    """Главная функция"""
    print("=" * 80)
    print("🧪 ТЕСТОВАЯ ВЕРСИЯ SENDMESSAGEBOT")
    print("=" * 80)
    print("⚠️  Используются ТЕСТОВЫЕ чаты:")
    print("   • Прайсы → TEST_TARGETS (2 чата)")
    print("   • Реклама → TEST_TARGETS_ADS (2 чата)")
    print("=" * 80)
    print()
    
    app = SendMessageBotTestApp()
    
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

