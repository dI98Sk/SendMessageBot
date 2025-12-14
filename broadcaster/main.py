"""
Улучшенная версия главного файла приложения
Главная точка входа в бот

"""
import asyncio
import signal
import sys
import traceback
from pathlib import Path
from typing import List
from datetime import datetime

# Добавляем корневую директорию проекта в путь для импорта shared компонентов
project_root = Path(__file__).parent.parent  # broadcaster -> корень проекта
sys.path.insert(0, str(project_root))

# Импорты из broadcaster (относительные импорты)
from broadcaster.config.settings import config_manager, AppConfig
from broadcaster.utils.logger import get_logger
from broadcaster.core.broadcaster import EnhancedBroadcaster
from shared.google_sheets.fetcher import GoogleSheetsFetcher
from broadcaster.config.message_updater import MessageConfigUpdater
from broadcaster.monitoring.reports import TelegramReporter
from broadcaster.core.queue import queue_manager, Priority, QueueItem
from broadcaster.monitoring.metrics import MetricsCollector, HealthChecker
from broadcaster.monitoring.notifications import (
    notification_manager, alert_manager,
    TelegramNotificationChannel, WebhookNotificationChannel
)
from broadcaster.utils.security import security_manager

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
        self.auto_updater = None  # Автоматический обновлятель всех сообщений

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
            self.logger = get_logger("main", self.config.logging)

            self.logger.info("Инициализация SendMessageBot...")

            # Валидация конфигурации
            await self._validate_config()

            # Настройка уведомлений
            await self._setup_notifications()

            # Инициализация очередей
            await self._setup_queues()

            # Инициализация Google Sheets и автообновления
            await self._setup_google_sheets()

            # Инициализация системы отчетов
            await self._setup_reports()

            # Создание broadcaster'ов (если еще не созданы)
            if not self.broadcasters:
                await self._create_broadcasters()
            else:
                self.logger.info(f"Broadcaster'ы уже созданы: {len(self.broadcasters)} шт.")

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
        self.logger.info("Настройка системы уведомлений...")
        
        # Telegram уведомления
        if self.config.notifications.enable_telegram_notifications:
            admin_id = self.config.notifications.admin_telegram_id
            
            if admin_id:
                try:
                    # Создаем отдельный Telegram клиент для уведомлений
                    from telethon import TelegramClient
                    
                    self.logger.info(f"Создание Telegram клиента для уведомлений...")
                    
                    notification_client = TelegramClient(
                        f"notification_session",
                        self.config.telegram.api_id,
                        self.config.telegram.api_hash
                    )
                    
                    # Запускаем клиент (без phone - используем существующую сессию)
                    # Если сессия не существует, Telethon запросит авторизацию автоматически
                    await notification_client.start()
                    
                    # Создаем канал уведомлений
                    telegram_channel = TelegramNotificationChannel(
                        client=notification_client,
                        admin_chat_id=admin_id
                    )
                    
                    # Добавляем канал в менеджер
                    notification_manager.add_channel(telegram_channel)
                    
                    # Сохраняем клиент для корректного закрытия
                    self.notification_client = notification_client
                    
                    self.logger.info(f"✅ Telegram уведомления включены для admin: {admin_id}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Ошибка настройки Telegram уведомлений: {e}")
                    self.logger.warning("Продолжаем работу без Telegram уведомлений")
            else:
                self.logger.warning("⚠️ ADMIN_TELEGRAM_ID не настроен - Telegram уведомления отключены")
                self.logger.info("Для включения уведомлений установите переменную окружения ADMIN_TELEGRAM_ID")
        else:
            self.logger.info("📱 Telegram уведомления отключены в конфигурации")

        # Webhook уведомления
        if self.config.notifications.enable_webhook_notifications:
            webhook_url = self.config.notifications.webhook_url
            if webhook_url and webhook_url != "https://your-webhook-url.com":
                try:
                    webhook_channel = WebhookNotificationChannel(webhook_url)
                    notification_manager.add_channel(webhook_channel)
                    self.logger.info(f"✅ Webhook уведомления включены: {webhook_url}")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка настройки Webhook уведомлений: {e}")
            else:
                self.logger.info("📡 Webhook уведомления отключены - не настроен WEBHOOK_URL")
        else:
            self.logger.info("📡 Webhook уведомления отключены в конфигурации")

        # Настройка алертов
        try:
            alert_manager.add_default_rules()
            self.logger.info("✅ Система алертов настроена")
        except Exception as e:
            self.logger.error(f"❌ Ошибка настройки алертов: {e}")
        
        # Проверяем общее состояние
        if notification_manager.channels:
            self.logger.info(f"📢 Система уведомлений готова: {len(notification_manager.channels)} каналов")
        else:
            self.logger.warning("⚠️ Система уведомлений не настроена - ни одного канала не добавлено")

    async def _setup_queues(self):
        """Настройка очередей"""
        # Создаем очереди для разных типов сообщений
        queue_manager.create_queue("b2b_messages", max_size=5000)
        queue_manager.create_queue("b2c_messages", max_size=5000)
        queue_manager.create_queue("priority_messages", max_size=1000)

    async def _create_broadcasters(self):
        """Создание broadcaster'ов"""
        before_count = len(self.broadcasters)
        print(f"📱 Создание broadcaster'ов... (текущее количество: {before_count})")
        
        if self.logger:
            self.logger.info(f"Создание broadcaster'ов... (текущее количество: {before_count})")

        # ========================================
        # ПРАЙСЫ (targets_prices) - цикл каждые 30 минут (оптимизировано)
        # Цель: ~48 циклов в сутки на broadcaster (всего ~96 циклов для 2 PRICE)
        # ========================================
        
        PRICE_CYCLE_DELAY = 30 * 60  # 30 минут = 1800 секунд (увеличено с 20 мин)
        PRICE_DELAY_BETWEEN_CHATS = 60.0  # 1 минута между чатами (оптимизировано)
        
        # AAA Прайсы - использует аккаунт acc2 (Анна Макарова) - ОПТОВЫЙ
        # УНИКАЛЬНЫЙ файл сессии чтобы избежать database locked!
        # ОПТИМИЗИРОВАНО: одно случайное сообщение на чат, цикл 30 минут
        aaa_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="AAA_PRICE_Broadcaster",
            targets=self.config.targets_prices,
            messages=self.config.aaa_messages,
            session_name="sessions/acc2_price",  # Анна Макарова
            cycle_delay=PRICE_CYCLE_DELAY,  # 30 минут между циклами
            delay_between_chats=PRICE_DELAY_BETWEEN_CHATS  # 1 минута между чатами
        )
        self.broadcasters.append(aaa_broadcaster)
        print(f"✅ AAA PRICE Broadcaster создан (acc2_price/Анна): {len(self.config.targets_prices)} чатов, {len(self.config.aaa_messages)} сообщений (случайное на чат), цикл: 30 мин, задержка: {PRICE_DELAY_BETWEEN_CHATS}с")

        # GUS Прайсы - использует аккаунт acc1 (Яблочный Гусь) - РОЗНИЧНЫЙ
        # УНИКАЛЬНЫЙ файл сессии чтобы избежать database locked!
        # ОПТИМИЗИРОВАНО: одно случайное сообщение на чат, цикл 30 минут
        gus_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="GUS_PRICE_Broadcaster",
            targets=self.config.targets_prices,
            messages=self.config.gus_messages,
            session_name="sessions/acc1_price",  # Яблочный Гусь
            cycle_delay=PRICE_CYCLE_DELAY,  # 30 минут между циклами
            delay_between_chats=PRICE_DELAY_BETWEEN_CHATS  # 1 минута между чатами
        )
        self.broadcasters.append(gus_broadcaster)
        print(f"✅ GUS PRICE Broadcaster создан (acc1_price/Яблочный Гусь): {len(self.config.targets_prices)} чатов, {len(self.config.gus_messages)} сообщений (случайное на чат), цикл: 30 мин, задержка: {PRICE_DELAY_BETWEEN_CHATS}с")
        
        # ========================================
        # РЕКЛАМА (targets_ads) - цикл каждые 50 минут (оптимизировано)
        # Цель: ~29 циклов в сутки на broadcaster (всего ~58 циклов для 2 ADS)
        # ========================================
        
        ADS_CYCLE_DELAY = 50 * 60  # 50 минут = 3000 секунд (уменьшено с 1 часа)
        ADS_DELAY_BETWEEN_CHATS = 60.0  # 1 минута между чатами (оптимизировано)
        
        # AAA Реклама - использует аккаунт acc2 (Анна Макарова) - ОПТОВЫЙ
        # УНИКАЛЬНЫЙ файл сессии чтобы избежать database locked!
        # ОПТИМИЗИРОВАНО: одно случайное сообщение на чат, цикл 50 минут
        aaa_ads_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="AAA_ADS_Broadcaster",
            targets=self.config.targets_ads,
            messages=self.config.aaa_ads_messages,
            session_name="sessions/acc2_ads",  # Анна Макарова
            cycle_delay=ADS_CYCLE_DELAY,  # 50 минут между циклами
            delay_between_chats=ADS_DELAY_BETWEEN_CHATS  # 1 минута между чатами
        )
        self.broadcasters.append(aaa_ads_broadcaster)
        print(f"✅ AAA ADS Broadcaster создан (acc2_ads/Анна): {len(self.config.targets_ads)} чатов, {len(self.config.aaa_ads_messages)} сообщений (случайное на чат), цикл: 50 мин, задержка: {ADS_DELAY_BETWEEN_CHATS}с")
        
        # GUS Реклама - использует аккаунт acc1 (Яблочный Гусь) - РОЗНИЧНЫЙ
        # УНИКАЛЬНЫЙ файл сессии чтобы избежать database locked!
        # ОПТИМИЗИРОВАНО: одно случайное сообщение на чат, цикл 50 минут
        gus_ads_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="GUS_ADS_Broadcaster",
            targets=self.config.targets_ads,
            messages=self.config.gus_ads_messages,
            session_name="sessions/acc1_ads",  # Яблочный Гусь
            cycle_delay=ADS_CYCLE_DELAY,  # 50 минут между циклами
            delay_between_chats=ADS_DELAY_BETWEEN_CHATS  # 1 минута между чатами
        )
        self.broadcasters.append(gus_ads_broadcaster)
        print(f"✅ GUS ADS Broadcaster создан (acc1_ads/Яблочный Гусь): {len(self.config.targets_ads)} чатов, {len(self.config.gus_ads_messages)} сообщений (случайное на чат), цикл: 50 мин, задержка: {ADS_DELAY_BETWEEN_CHATS}с")
        
        # ========================================
        # B2C РОЗНИЧНЫЙ (targets_b2c) - цикл каждые 1.5 часа (оптимизировано)
        # Цель: ~16 циклов в сутки (всего ~16 циклов для B2C)
        # ========================================
        
        B2C_CYCLE_DELAY = int(1.5 * 60 * 60)  # 1.5 часа = 5400 секунд (уменьшено с 2 часов)
        B2C_DELAY_BETWEEN_CHATS = 60.0  # 1 минута между чатами (оптимизировано)
        B2C_START_OFFSET = 300  # 5 минут смещение старта (чтобы не конфликтовать с другими)
        
        # GUS B2C - использует аккаунт acc1 (Яблочный Гусь) - РОЗНИЧНЫЙ
        # УНИКАЛЬНЫЙ файл сессии чтобы избежать database locked!
        # УВЕЛИЧЕННЫЕ задержки для избежания конфликтов с другими broadcaster'ами
        # Использует сообщения из ДВУХ таблиц: прайсы GUS + реклама GUS
        gus_b2c_messages = self.config.gus_messages + self.config.gus_ads_messages
        
        gus_b2c_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="GUS_B2C_Broadcaster",
            targets=self.config.targets_b2c,
            messages=gus_b2c_messages,  # Объединенные сообщения из прайсов и рекламы
            session_name="sessions/acc1_b2c",  # Яблочный Гусь
            cycle_delay=B2C_CYCLE_DELAY,  # 2 часа между циклами
            delay_between_chats=B2C_DELAY_BETWEEN_CHATS,  # 2 минуты между чатами
            start_offset_seconds=B2C_START_OFFSET  # 5 минут смещение старта
        )
        self.broadcasters.append(gus_b2c_broadcaster)
        print(
            f"✅ GUS B2C Broadcaster создан (acc1_b2c/Яблочный Гусь): "
            f"{len(self.config.targets_b2c)} чатов, "
            f"{len(gus_b2c_messages)} сообщений (случайное на чат) "
            f"(прайсы: {len(self.config.gus_messages)}, реклама: {len(self.config.gus_ads_messages)}), "
            f"цикл: 1.5 часа, задержка: {B2C_DELAY_BETWEEN_CHATS}с"
        )
        
        # ========================================
        # B2C MIDSLOW РОЗНИЧНЫЙ (targets_b2c_midslow) - цикл каждые 2.67 часа
        # Цель: ~9 циклов в сутки
        # ========================================
        
        # Расчет: 24 часа / 9 циклов = 2.67 часа = 160 минут
        B2C_MIDSLOW_CYCLE_DELAY = int(2.67 * 60 * 60)  # 2.67 часа = 9612 секунд (≈160 минут)
        B2C_MIDSLOW_DELAY_BETWEEN_CHATS = 60.0  # 1 минута между чатами
        B2C_MIDSLOW_START_OFFSET = 600  # 10 минут смещение старта (чтобы не конфликтовать с другими)
        
        # Проверяем, есть ли чаты для MIDSLOW
        if self.config.targets_b2c_midslow:
            # GUS B2C MIDSLOW - использует аккаунт acc1 (Яблочный Гусь) - РОЗНИЧНЫЙ
            # УНИКАЛЬНЫЙ файл сессии чтобы избежать database locked!
            # Использует сообщения из ДВУХ таблиц: прайсы GUS + реклама GUS
            gus_b2c_midslow_messages = self.config.gus_messages + self.config.gus_ads_messages
            
            gus_b2c_midslow_broadcaster = EnhancedBroadcaster(
                config=self.config,
                name="GUS_B2C_MIDSLOW_Broadcaster",
                targets=self.config.targets_b2c_midslow,
                messages=gus_b2c_midslow_messages,  # Объединенные сообщения из прайсов и рекламы
                session_name="sessions/acc1_b2c_midslow",  # Яблочный Гусь
                cycle_delay=B2C_MIDSLOW_CYCLE_DELAY,  # 2.67 часа между циклами
                delay_between_chats=B2C_MIDSLOW_DELAY_BETWEEN_CHATS,  # 1 минута между чатами
                start_offset_seconds=B2C_MIDSLOW_START_OFFSET  # 10 минут смещение старта
            )
            self.broadcasters.append(gus_b2c_midslow_broadcaster)
            print(
                f"✅ GUS B2C MIDSLOW Broadcaster создан (acc1_b2c_midslow/Яблочный Гусь): "
                f"{len(self.config.targets_b2c_midslow)} чатов, "
                f"{len(gus_b2c_midslow_messages)} сообщений (случайное на чат) "
                f"(прайсы: {len(self.config.gus_messages)}, реклама: {len(self.config.gus_ads_messages)}), "
                f"цикл: 2.67 часа (~9 циклов/день), задержка: {B2C_MIDSLOW_DELAY_BETWEEN_CHATS}с"
            )
        
        after_count = len(self.broadcasters)
        print(f"📊 Всего broadcaster'ов: {after_count}")
        
        if self.logger:
            self.logger.info(f"Всего broadcaster'ов после создания: {after_count}")

    async def _setup_google_sheets(self):
        """Настройка Google Sheets интеграции и автообновления"""
        try:
            from broadcaster.utils.auto_updater import AutoMessageUpdater
            
            # Инициализация автоматического обновлятеля
            self.auto_updater = AutoMessageUpdater(
                credentials_file=self.config.google_sheets.credentials_file,
                config=self.config
            )
            
            # Устанавливаем callback для обработки обновлений
            self.auto_updater.set_update_callback(self._on_auto_messages_updated)
            
            self.logger.info("✅ Автоматический обновлятель сообщений настроен")

        except Exception as e:
            self.logger.error(f"⚠️  Ошибка настройки Google Sheets: {e}")
            self.logger.info("ℹ️  Продолжаем работу без автообновления")

    async def _on_auto_messages_updated(self, results):
        """Callback для автоматического обновления всех сообщений"""
        try:
            self.logger.info("📊 Получены обновленные сообщения из Google Sheets")
            
            # Подсчитываем успешные обновления
            success_types = [k for k, v in results.items() if v['success']]
            
            if not success_types:
                self.logger.warning("⚠️ Ни один тип сообщений не был обновлен")
                return
            
            # Формируем отчет об обновлении
            update_info = []
            for msg_type, result in results.items():
                if result['success']:
                    update_info.append(f"{msg_type}={result['count']}")
            
            self.logger.info(f"✅ Обновлено типов: {', '.join(update_info)}")
            
            # Перезагружаем конфигурацию
            self.config = config_manager.load_config()
            
            # Пересоздаем broadcaster'ы с новыми сообщениями
            self.logger.info("🔄 Пересоздание broadcaster'ов с новыми сообщениями...")
            await self._recreate_broadcasters()
            
            # Отправляем уведомление
            await notification_manager.send_info(
                "🔄 Сообщения автоматически обновлены",
                f"Обновлено: {', '.join(update_info)}\n" +
                f"Broadcaster'ы перезапущены с новыми сообщениями"
            )
            
            self.logger.info("✅ Автообновление завершено успешно")

        except Exception as e:
            self.logger.error(f"❌ Ошибка в callback автообновления: {e}")
            await notification_manager.send_error(
                "Ошибка автообновления",
                f"Не удалось применить обновленные сообщения: {e}"
            )

    async def _recreate_broadcasters(self):
        """Пересоздание broadcaster'ов с новыми сообщениями"""
        try:
            old_count = len(self.broadcasters)
            self.logger.info(f"Пересоздание broadcaster'ов: было {old_count} шт.")
            
            # Останавливаем старые broadcaster'ы и их задачи
            for broadcaster in self.broadcasters:
                self.logger.info(f"Остановка broadcaster: {broadcaster.name}")
                await broadcaster.stop()

            # Очищаем список broadcaster'ов
            self.broadcasters.clear()
            self.logger.info("Список broadcaster'ов очищен")
            
            # ⚠️ ВАЖНО: Ждем дополнительное время после остановки, чтобы база данных освободилась
            self.logger.info("⏳ Ожидание освобождения базы данных после остановки broadcaster'ов (15 секунд)...")
            await asyncio.sleep(15)  # Увеличено с 0 до 15 секунд
            
            # Удаляем завершенные задачи из списка (кроме задачи отчетов!)
            # ⚠️ ВАЖНО: Сохраняем задачу telegram_reporter
            reporter_task = None
            if self.telegram_reporter and self.telegram_reporter.task:
                reporter_task = self.telegram_reporter.task
                self.logger.info("💾 Сохранена задача системы отчетов")
            
            # Фильтруем задачи
            new_tasks = []
            for task in self.tasks:
                if not task.done():
                    # Сохраняем задачу отчетов и системные задачи
                    if task == reporter_task or 'health_check' in str(task) or 'metrics' in str(task):
                        new_tasks.append(task)
                        
            self.tasks = new_tasks
            self.logger.info(f"Активных задач после очистки: {len(self.tasks)}")

            # Создаем новые broadcaster'ы с retry логикой для database is locked
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    await self._create_broadcasters()
                    self.logger.info(f"Broadcaster'ы пересозданы: теперь {len(self.broadcasters)} шт.")
                    break  # Успешно созданы
                except Exception as create_err:
                    error_msg = str(create_err).lower()
                    if "database is locked" in error_msg or "locked" in error_msg:
                        retry_count += 1
                        wait_time = 10 * retry_count  # Экспоненциальная задержка: 10, 20, 30 секунд
                        self.logger.warning(
                            f"⚠️ Database locked при создании broadcaster'ов, "
                            f"ожидание {wait_time}с перед повтором (попытка {retry_count}/{max_retries})..."
                        )
                        await asyncio.sleep(wait_time)
                        # Очищаем частично созданные broadcaster'ы перед повтором
                        for b in self.broadcasters:
                            try:
                                await b.stop()
                            except:
                                pass
                        self.broadcasters.clear()
                    else:
                        # Другие ошибки пробрасываем дальше
                        raise

            if retry_count >= max_retries:
                self.logger.error(f"❌ Не удалось создать broadcaster'ы после {max_retries} попыток из-за database is locked")
                raise Exception(f"Не удалось создать broadcaster'ы после {max_retries} попыток: database is locked")

            # ВАЖНО: Запускаем новые broadcaster'ы с задержкой между подключениями
            if self.running:
                self.logger.info("Запуск пересозданных broadcaster'ов...")
                for idx, broadcaster in enumerate(self.broadcasters, 1):
                    self.logger.info(f"Запуск broadcaster {idx}/{len(self.broadcasters)}: {broadcaster.name}")
                    
                    # Добавляем задержку между запусками (кроме первого)
                    if idx > 1:
                        await asyncio.sleep(15)  # Увеличено с 10 до 15 секунд между подключениями
                    
                    task = asyncio.create_task(broadcaster.start())
                    self.tasks.append(task)
                self.logger.info("✅ Все broadcaster'ы запущены после пересоздания")
                
                # ✅ Проверяем что система отчетов все еще работает
                if self.telegram_reporter and self.telegram_reporter.running:
                    self.logger.info("✅ Система отчетов продолжает работать")
                else:
                    self.logger.warning("⚠️ Система отчетов не активна!")

        except Exception as e:
            self.logger.error(f"Ошибка пересоздания broadcaster'ов: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")

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
            # Устанавливаем интервал из конфигурации
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
        """Задача проверки здоровья системы с мониторингом broadcaster'ов"""
        from datetime import datetime, timedelta
        
        while self.running:
            try:
                # Проверка "мертвых" broadcaster'ов
                dead_broadcasters = []
                for broadcaster in self.broadcasters:
                    # Проверяем, что broadcaster запущен
                    if not broadcaster._running:
                        dead_broadcasters.append(broadcaster)
                        continue
                    
                    # Проверяем последнюю активность (если есть)
                    if hasattr(broadcaster, '_cycle_start_time') and broadcaster._cycle_start_time:
                        time_since_cycle = datetime.now() - broadcaster._cycle_start_time
                        # Если прошло больше 2 циклов без активности - подозрительно
                        max_cycle_time = broadcaster.cycle_delay * 2.5
                        if time_since_cycle.total_seconds() > max_cycle_time:
                            self.logger.warning(
                                f"⚠️ [{broadcaster.name}] Нет активности {time_since_cycle.total_seconds()/60:.1f} минут "
                                f"(максимум: {max_cycle_time/60:.1f} минут)"
                            )
                    
                    # Проверяем соединение
                    if broadcaster._client:
                        try:
                            if not broadcaster._client.is_connected():
                                self.logger.warning(f"⚠️ [{broadcaster.name}] Клиент не подключен, пытаемся переподключить...")
                                await broadcaster._ensure_connection()
                        except Exception as e:
                            self.logger.error(f"❌ [{broadcaster.name}] Ошибка проверки соединения: {e}")
                            dead_broadcasters.append(broadcaster)
                
                # Перезапуск "мертвых" broadcaster'ов
                for broadcaster in dead_broadcasters:
                    self.logger.warning(f"🔄 [{broadcaster.name}] Обнаружен остановленный broadcaster, перезапускаем...")
                    try:
                        # Останавливаем старый
                        await broadcaster.stop()
                        # Небольшая пауза
                        await asyncio.sleep(5)
                        # Запускаем заново
                        task = asyncio.create_task(broadcaster.start())
                        # Обновляем задачу в списке
                        for i, t in enumerate(self.tasks):
                            if hasattr(t, '_broadcaster') and t._broadcaster == broadcaster:
                                self.tasks[i] = task
                                break
                        else:
                            self.tasks.append(task)
                        self.logger.info(f"✅ [{broadcaster.name}] Broadcaster перезапущен")
                    except Exception as e:
                        self.logger.error(f"❌ [{broadcaster.name}] Не удалось перезапустить: {e}")
                
                # Проверка здоровья системы отчетов
                if self.telegram_reporter:
                    try:
                        # Проверяем, что задача отчетов работает
                        if self.telegram_reporter.task and self.telegram_reporter.task.done():
                            self.logger.error("❌ [TelegramReporter] Задача отчетов завершена неожиданно!")
                            # Перезапускаем систему отчетов
                            try:
                                await self.telegram_reporter.stop()
                                await asyncio.sleep(2)
                                self.telegram_reporter.start(lambda: self.broadcasters)
                                self.logger.info("✅ [TelegramReporter] Система отчетов перезапущена")
                            except Exception as e:
                                self.logger.error(f"❌ [TelegramReporter] Не удалось перезапустить: {e}")
                        
                        # Проверяем, что система отчетов запущена
                        elif not self.telegram_reporter.running:
                            self.logger.warning("⚠️ [TelegramReporter] Система отчетов не запущена")
                            try:
                                self.telegram_reporter.start(lambda: self.broadcasters)
                                self.logger.info("✅ [TelegramReporter] Система отчетов запущена")
                            except Exception as e:
                                self.logger.error(f"❌ [TelegramReporter] Не удалось запустить: {e}")
                        
                        # Проверяем, отправлялись ли отчеты в последнее время
                        elif self.telegram_reporter.last_report_time:
                            time_since_last = datetime.now() - self.telegram_reporter.last_report_time
                            # Если прошло больше чем интервал + 50% запаса - подозрительно
                            max_time = timedelta(hours=self.telegram_reporter.report_interval_hours * 1.5)
                            if time_since_last > max_time:
                                self.logger.warning(
                                    f"⚠️ [TelegramReporter] Последний отчет был {time_since_last.total_seconds()/3600:.1f} часов назад "
                                    f"(максимум: {max_time.total_seconds()/3600:.1f} часов)"
                                )
                        # Если отчетов еще не было, но система работает - это нормально
                        elif self.telegram_reporter.running:
                            # Проверяем, что система работает достаточно долго для первого отчета
                            # Если система работает больше интервала, но отчетов нет - проблема
                            # Но это сложно проверить без времени запуска, пропускаем
                            pass
                            
                    except Exception as e:
                        self.logger.error(f"❌ Ошибка проверки здоровья системы отчетов: {e}")
                
                # Сбор метрик
                try:
                    health_status = self.health_checker.check_health()
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
                except Exception as e:
                    self.logger.debug(f"Ошибка сбора метрик в health check: {e}")

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
        self.logger.info(f"Количество broadcaster'ов для запуска: {len(self.broadcasters)}")

        try:
            # Запуск broadcaster'ов с задержкой между подключениями
            # Это предотвращает ошибки "database is locked" при одновременном подключении
            broadcaster_tasks = []
            for idx, broadcaster in enumerate(self.broadcasters, 1):
                self.logger.info(f"🚀 Запуск broadcaster {idx}/{len(self.broadcasters)}: {broadcaster.name}")
                print(f"🚀 Запуск broadcaster {idx}/{len(self.broadcasters)}: {broadcaster.name}")
                
                # Добавляем задержку между запусками (кроме первого)
                # Увеличено до 10 секунд для предотвращения "database is locked"
                # Это позволяет избежать конфликтов при подключении к базам данных сессий
                if idx > 1:
                    self.logger.info(f"⏳ Задержка 10 секунд перед запуском {broadcaster.name}...")
                    await asyncio.sleep(10)  # 10 секунд между подключениями (увеличено для избежания database locked)
                
                self.logger.info(f"📝 Создание задачи для {broadcaster.name}...")
                try:
                    task = asyncio.create_task(broadcaster.start())
                    broadcaster_tasks.append(task)
                    self.tasks.append(task)
                    self.logger.info(f"✅ Задача для {broadcaster.name} создана успешно (task={task})")
                except Exception as e:
                    self.logger.error(f"❌ Ошибка при создании задачи для {broadcaster.name}: {e}")
                    import traceback
                    self.logger.error(f"❌ Traceback: {traceback.format_exc()}")

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
            print(f"🎯 Используются тестовые чаты: {len(self.config.targets)}")
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

            # ✅ Запуск автоматического обновления ВСЕХ сообщений (прайсы + реклама)
            if self.auto_updater:
                # Интервал обновления в часах из конфигурации
                update_interval = self.config.google_sheets.update_interval / 3600.0  # секунды в часы
                
                await self.auto_updater.start(interval_hours=update_interval)
                
                self.logger.info(f"🔄 Автообновление сообщений запущено (интервал: {update_interval:.1f} часов)")
                print(f"🔄 Автообновление сообщений включено (каждые {update_interval:.1f} часов)")
                print("   • Прайсы AAA/GUS")
                print("   • Реклама AAA/GUS")

            # Запуск системы отчетов
            if self.telegram_reporter:
                # Передаем функцию для получения актуального списка broadcaster'ов
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

        self.logger.info("Завершение работы SendMessageBot...")
        self.running = False

        # Остановка broadcaster'ов
        for broadcaster in self.broadcasters:
            await broadcaster.stop()

        # Остановка автообновления
        if self.auto_updater:
            await self.auto_updater.stop()
            self.logger.info("Автообновление остановлено")

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

                print(f"🎯 Всего чатов: {len(self.config.targets)}")
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
