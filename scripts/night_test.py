#!/usr/bin/env python3
"""
Скрипт для тестирования в ночное время
Игнорирует тихий час и ограничения по времени
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, time
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import config_manager, AppConfig
from core.broadcaster import EnhancedBroadcaster
from utils.logger import get_logger

load_dotenv()

class NightTestRunner:
    """Класс для ночного тестирования"""
    
    def __init__(self):
        self.config: AppConfig = None
        self.logger = None
        self.broadcasters = []
        
    async def setup(self):
        """Настройка тестового окружения"""
        print("🌙 НАСТРОЙКА НОЧНОГО ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        # Загружаем конфигурацию
        self.config = config_manager.load_config()
        self.logger = get_logger("night_test", self.config.logging)
        
        # Переопределяем настройки для ночного тестирования
        self.config.message_delay = 0.5  # Быстрая отправка
        self.config.max_retries = 1      # Меньше попыток
        self.config.flood_wait_delay = 10  # Короткая задержка
        
        print(f"⏰ Время тестирования: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🎯 Тестовые чаты: {len(self.config.targets)}")
        print(f"💬 B2B сообщений: {len(self.config.b2b_messages)}")
        print(f"💬 B2C сообщений: {len(self.config.b2c_messages)}")
        print(f"💬 AAA сообщений: {len(self.config.aaa_messages)}")
        print(f"💬 GUS сообщений: {len(self.config.gus_messages)}")
        
    async def create_test_broadcasters(self):
        """Создание тестовых броудкастеров"""
        print("\n🚀 СОЗДАНИЕ ТЕСТОВЫХ БРОУДКАСТЕРОВ")
        print("=" * 40)
        
        # B2B Broadcaster
        b2b_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="NIGHT_TEST_B2B",
            targets=self.config.targets,
            messages=self.config.b2b_messages[:3],  # Только первые 3 сообщения
            session_name="sessions/acc1"
        )
        self.broadcasters.append(b2b_broadcaster)
        print("✅ B2B тестовый броудкастер создан")
        
        # B2C Broadcaster
        b2c_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="NIGHT_TEST_B2C",
            targets=self.config.targets,
            messages=self.config.b2c_messages[:3],  # Только первые 3 сообщения
            session_name="sessions/acc2"
        )
        self.broadcasters.append(b2c_broadcaster)
        print("✅ B2C тестовый броудкастер создан")
        
        # AAA Broadcaster
        aaa_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="NIGHT_TEST_AAA",
            targets=self.config.targets,
            messages=self.config.aaa_messages[:2],  # Только первые 2 сообщения
            session_name="sessions/acc1"
        )
        self.broadcasters.append(aaa_broadcaster)
        print("✅ AAA тестовый броудкастер создан")
        
        # GUS Broadcaster
        gus_broadcaster = EnhancedBroadcaster(
            config=self.config,
            name="NIGHT_TEST_GUS",
            targets=self.config.targets,
            messages=self.config.gus_messages[:2],  # Только первые 2 сообщения
            session_name="sessions/acc2"
        )
        self.broadcasters.append(gus_broadcaster)
        print("✅ GUS тестовый броудкастер создан")
        
        print(f"\n📊 Всего тестовых броудкастеров: {len(self.broadcasters)}")
        
    async def run_single_broadcaster_test(self, broadcaster_name: str):
        """Тестирование одного броудкастера"""
        print(f"\n🔥 ТЕСТИРОВАНИЕ {broadcaster_name}")
        print("=" * 40)
        
        broadcaster = None
        for b in self.broadcasters:
            if b.name == broadcaster_name:
                broadcaster = b
                break
        
        if not broadcaster:
            print(f"❌ Броудкастер {broadcaster_name} не найден")
            return
        
        try:
            print(f"📱 Запуск {broadcaster_name}...")
            await broadcaster.start()
            
            print(f"💬 Отправка {len(broadcaster.messages)} сообщений...")
            await broadcaster.send_messages()
            
            print(f"✅ {broadcaster_name} тест завершен успешно")
            
        except Exception as e:
            print(f"❌ Ошибка в {broadcaster_name}: {e}")
            self.logger.error(f"Ошибка в {broadcaster_name}: {e}")
        finally:
            await broadcaster.stop()
            print(f"🛑 {broadcaster_name} остановлен")
    
    async def run_all_broadcasters_test(self):
        """Тестирование всех броудкастеров"""
        print("\n🚀 ТЕСТИРОВАНИЕ ВСЕХ БРОУДКАСТЕРОВ")
        print("=" * 50)
        
        for broadcaster in self.broadcasters:
            try:
                print(f"\n📱 Запуск {broadcaster.name}...")
                await broadcaster.start()
                
                print(f"💬 Отправка {len(broadcaster.messages)} сообщений...")
                await broadcaster.send_messages()
                
                print(f"✅ {broadcaster.name} завершен")
                
            except Exception as e:
                print(f"❌ Ошибка в {broadcaster.name}: {e}")
                self.logger.error(f"Ошибка в {broadcaster.name}: {e}")
            finally:
                await broadcaster.stop()
                print(f"🛑 {broadcaster.name} остановлен")
                
            # Небольшая пауза между броудкастерами
            await asyncio.sleep(2)
    
    async def run_parallel_test(self):
        """Параллельное тестирование всех броудкастеров"""
        print("\n⚡ ПАРАЛЛЕЛЬНОЕ ТЕСТИРОВАНИЕ")
        print("=" * 40)
        
        try:
            # Запускаем все броудкастеры параллельно
            tasks = []
            for broadcaster in self.broadcasters:
                task = asyncio.create_task(self._run_broadcaster_task(broadcaster))
                tasks.append(task)
            
            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Анализируем результаты
            successful = 0
            failed = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"❌ {self.broadcasters[i].name}: {result}")
                    failed += 1
                else:
                    print(f"✅ {self.broadcasters[i].name}: Успешно")
                    successful += 1
            
            print(f"\n📊 Результаты: {successful} успешно, {failed} с ошибками")
            
        except Exception as e:
            print(f"❌ Критическая ошибка параллельного тестирования: {e}")
            self.logger.error(f"Критическая ошибка: {e}")
    
    async def _run_broadcaster_task(self, broadcaster):
        """Задача для одного броудкастера"""
        try:
            await broadcaster.start()
            await broadcaster.send_messages()
            return True
        except Exception as e:
            raise e
        finally:
            await broadcaster.stop()
    
    async def run_stress_test(self, duration_minutes: int = 5):
        """Стресс-тестирование в течение указанного времени"""
        print(f"\n💪 СТРЕСС-ТЕСТИРОВАНИЕ ({duration_minutes} минут)")
        print("=" * 50)
        
        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        iteration = 0
        
        while datetime.now().timestamp() < end_time:
            iteration += 1
            print(f"\n🔄 Итерация {iteration}")
            
            try:
                await self.run_all_broadcasters_test()
                
                # Пауза между итерациями
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"❌ Ошибка в итерации {iteration}: {e}")
                self.logger.error(f"Ошибка в итерации {iteration}: {e}")
        
        print(f"\n✅ Стресс-тестирование завершено. Выполнено {iteration} итераций")
    
    def show_menu(self):
        """Показать меню тестирования"""
        print("\n🌙 МЕНЮ НОЧНОГО ТЕСТИРОВАНИЯ")
        print("=" * 40)
        print("1. 🧪 Тест B2B броудкастера")
        print("2. 🧪 Тест B2C броудкастера")
        print("3. 🧪 Тест AAA броудкастера")
        print("4. 🧪 Тест GUS броудкастера")
        print("5. 🚀 Тест всех броудкастеров (последовательно)")
        print("6. ⚡ Тест всех броудкастеров (параллельно)")
        print("7. 💪 Стресс-тестирование")
        print("8. 📊 Информация о системе")
        print("0. ❌ Выход")
        print("=" * 40)
    
    async def show_system_info(self):
        """Показать информацию о системе"""
        print("\n📊 ИНФОРМАЦИЯ О СИСТЕМЕ")
        print("=" * 30)
        print(f"⏰ Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌙 Режим: Ночное тестирование")
        print(f"🎯 Тестовых чатов: {len(self.config.targets)}")
        print(f"📱 Броудкастеров: {len(self.broadcasters)}")
        
        for broadcaster in self.broadcasters:
            print(f"  - {broadcaster.name}: {len(broadcaster.messages)} сообщений")
        
        print(f"⚙️ Задержка между сообщениями: {self.config.message_delay}с")
        print(f"🔄 Максимум попыток: {self.config.max_retries}")
        print(f"⏳ Задержка FloodWait: {self.config.flood_wait_delay}с")

async def main():
    """Главная функция"""
    runner = NightTestRunner()
    
    try:
        await runner.setup()
        await runner.create_test_broadcasters()
        
        while True:
            runner.show_menu()
            choice = input("\nВыберите тест (0-8): ").strip()
            
            if choice == "0":
                print("👋 Завершение ночного тестирования")
                break
            elif choice == "1":
                await runner.run_single_broadcaster_test("NIGHT_TEST_B2B")
            elif choice == "2":
                await runner.run_single_broadcaster_test("NIGHT_TEST_B2C")
            elif choice == "3":
                await runner.run_single_broadcaster_test("NIGHT_TEST_AAA")
            elif choice == "4":
                await runner.run_single_broadcaster_test("NIGHT_TEST_GUS")
            elif choice == "5":
                await runner.run_all_broadcasters_test()
            elif choice == "6":
                await runner.run_parallel_test()
            elif choice == "7":
                duration = input("Введите длительность стресс-теста в минутах (по умолчанию 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                await runner.run_stress_test(duration)
            elif choice == "8":
                await runner.show_system_info()
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\nНажмите Enter для продолжения...")
    
    except KeyboardInterrupt:
        print("\n👋 Прерывание пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🌙 НОЧНОЕ ТЕСТИРОВАНИЕ SENDMESSAGEBOT")
    print("=" * 50)
    print("Этот скрипт предназначен для тестирования в ночное время")
    print("Игнорирует тихий час и ограничения по времени")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Прерывание пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
