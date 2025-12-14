# Изоляция Auto Updater от Broadcaster

## Архитектура

### Независимые компоненты

1. **Broadcaster Service** - основной сервис рассылки сообщений
   - Работает независимо от auto_updater
   - Запускается при старте приложения
   - Продолжает работу даже если auto_updater упадет

2. **Auto Updater** - сервис обновления сообщений из Google Sheets
   - Работает как отдельная asyncio.Task
   - Запускается параллельно с broadcaster'ами
   - Не блокирует работу broadcaster'ов при падении

## Что происходит при падении Auto Updater?

### ✅ Сценарий 1: Auto Updater упал, но broadcaster'ы работают

**Результат:** ✅ Broadcaster'ы **продолжают работать**

- Broadcaster'ы используют сообщения, загруженные при старте
- Сообщения хранятся в файлах:
  - `broadcaster/config/messages_aaa.py`
  - `broadcaster/config/messages_gus.py`
  - `broadcaster/config/messages_aaa_ads.py`
  - `broadcaster/config/messages_gus_ads.py`
- Эти файлы не изменяются, если auto_updater не работает
- **Рассылка продолжается с последними загруженными сообщениями**

### ⚠️ Сценарий 2: Auto Updater упал во время обновления

**Результат:** ⚠️ Может быть проблема, если упал во время `_recreate_broadcasters()`

- Если auto_updater упал **до** вызова `_recreate_broadcasters()`:
  - ✅ Broadcaster'ы продолжают работать с текущими сообщениями
  - ❌ Новые сообщения не применятся до следующего успешного обновления

- Если auto_updater упал **во время** `_recreate_broadcasters()`:
  - ⚠️ Может быть частичное пересоздание broadcaster'ов
  - ⚠️ Может возникнуть "database is locked" (но это обрабатывается retry логикой)

### ✅ Сценарий 3: Ошибка в цикле обновления

**Результат:** ✅ Auto Updater продолжает работать

```python
except Exception as e:
    self.logger.error(f"❌ Ошибка в цикле обновления: {e}")
    await asyncio.sleep(60)  # Подождать минуту перед повтором
```

- Ошибка логируется, но цикл продолжается
- Через 60 секунд попытка повторится

## Текущая защита

### 1. Обработка ошибок в Auto Updater

```python
# В _update_loop
except Exception as e:
    self.logger.error(f"❌ Ошибка в цикле обновления: {e}")
    await asyncio.sleep(60)  # Подождать минуту перед повтором
```

- Ошибки не останавливают цикл
- Автоматический retry через 60 секунд

### 2. Обработка ошибок в Callback

```python
# В _on_auto_messages_updated
except Exception as e:
    self.logger.error(f"❌ Ошибка в callback автообновления: {e}")
    await notification_manager.send_error(...)
```

- Ошибки в callback не влияют на broadcaster'ы
- Отправляется уведомление об ошибке

### 3. Retry логика при пересоздании

```python
# В _recreate_broadcasters
max_retries = 3
retry_count = 0
while retry_count < max_retries:
    try:
        await self._create_broadcasters()
        break
    except Exception as create_err:
        if "database is locked" in error_msg:
            # Retry с задержкой
```

- До 3 попыток при "database is locked"
- Экспоненциальная задержка: 10, 20, 30 секунд

## Рекомендации по улучшению

### 1. Добавить Health Check для Auto Updater

```python
async def _health_check_task(self):
    # Проверка auto_updater
    if self.auto_updater:
        if self.auto_updater.task and self.auto_updater.task.done():
            self.logger.error("❌ Auto Updater упал, перезапускаем...")
            # Перезапуск auto_updater
```

### 2. Добавить изоляцию при пересоздании

```python
async def _recreate_broadcasters(self):
    try:
        # ... пересоздание ...
    except Exception as e:
        # Если пересоздание не удалось, broadcaster'ы продолжают работать
        self.logger.error(f"Ошибка пересоздания, broadcaster'ы продолжают работать: {e}")
        # НЕ останавливаем существующие broadcaster'ы
```

### 3. Добавить мониторинг

- Логировать статус auto_updater
- Отправлять уведомления при падении
- Отслеживать время последнего успешного обновления

## Вывод

✅ **Broadcaster'ы работают независимо от Auto Updater**

- Если auto_updater упадет, broadcaster'ы продолжат работу
- Они используют последние загруженные сообщения
- Новые сообщения не применятся до восстановления auto_updater
- Это безопасно - система не останавливается из-за проблем с обновлением

⚠️ **Риск:** Если auto_updater упадет во время `_recreate_broadcasters()`, может быть частичное пересоздание, но это обрабатывается retry логикой.

