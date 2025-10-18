# 📝 История изменений (Changelog)

## [Версия 2024-10-17] - Исправление дублирования broadcaster'ов

### 🐛 Исправленные ошибки

#### 1. Дублирование broadcaster'ов (4 вместо 2)

**Проблема:**
- При запуске создавалось 4 broadcaster'а вместо 2
- B2B и B2C broadcaster'ы дублировались

**Причина:**
В методе `initialize()` broadcaster'ы создавались дважды:
1. При обновлении сообщений из Google Sheets: `_setup_google_sheets()` → `_initial_message_update()` → `_recreate_broadcasters()` (создает 2)
2. При основной инициализации: `_create_broadcasters()` (создает еще 2)

**Решение:**
```python
# Добавлена проверка перед созданием
if not self.broadcasters:
    await self._create_broadcasters()
else:
    self.logger.info(f"Broadcaster'ы уже созданы: {len(self.broadcasters)} шт.")
```

**Результат:** Теперь создается ровно 2 broadcaster'а (B2B и B2C)

---

#### 2. Неправильное распределение аккаунтов

**Проблема:**
- Оба broadcaster'а использовали один аккаунт (ID: 8108419249)
- Второй аккаунт (ID: 8497033180) не использовался

**Решение:**
- B2B broadcaster теперь использует `sessions/acc1` (ID: 8108419249)
- B2C broadcaster теперь использует `sessions/acc2` (ID: 8497033180)
- Добавлен параметр `session_name` в конструктор `EnhancedBroadcaster`

**Код:**

```python
# B2B Broadcaster
b2b_broadcaster = EnhancedBroadcaster(
    config=self.config,
    name="B2B_Broadcaster",
    targets=self.config.targets,
    messages=self.config.b2b_messages,
    session_name="sessions/acc1"  # ID: 8108419249
)

# B2C Broadcaster
b2c_broadcaster = EnhancedBroadcaster(
    config=self.config,
    name="B2C_Broadcaster",
    targets=self.config.targets,
    messages=self.config.b2c_messages,
    session_name="sessions/acc2"  # ID: 8497033180
)
```

---

#### 3. Ошибка "unable to open database file" на Windows

**Проблема:**
- Не могли открыться файлы сессий на Windows Server
- Директория `sessions/` не существовала

**Решение:**
- Добавлена автоматическая проверка и создание директории `sessions/`
- Улучшены сообщения об ошибках с инструкциями

**Код:**
```python
# Проверяем и создаем директорию для сессий
from pathlib import Path
session_path = Path(self.session_name)
session_dir = session_path.parent

if session_dir and str(session_dir) != '.':
    session_dir.mkdir(parents=True, exist_ok=True)
```

---

#### 4. Ошибка "Invalid JWT Signature" Google Sheets

**Проблема:**
- Ошибка аутентификации в Google Sheets на сервере
- Непонятные сообщения об ошибках

**Решение:**
- Добавлена детальная диагностика проблем с `credentials.json`
- Добавлены специфичные советы для JWT ошибок:
  - Проверка синхронизации времени на сервере
  - Инструкции по обновлению credentials.json
  - Проверка прав Service Account

---

### ✨ Новые возможности

#### 1. Скрипт диагностики окружения

**Файл:** `check_environment.py`

Автоматически проверяет:
- ✅ Версию Python
- ✅ Переменные окружения
- ✅ Директорию и файлы сессий
- ✅ Файл credentials.json
- ✅ Конфигурационные файлы
- ✅ Системное время
- ✅ Установленные зависимости

**Использование:**
```bash
python check_environment.py
```

---

#### 2. Улучшенное логирование

Добавлено детальное логирование:
- Количество broadcaster'ов при создании
- ID аккаунта при подключении
- Пересоздание broadcaster'ов при обновлении сообщений
- Запуск каждого broadcaster'а

**Пример лога:**
```
2024-10-17 12:00:00 [INFO] Создание broadcaster'ов... (текущее количество: 0)
2024-10-17 12:00:01 [INFO] Всего broadcaster'ов после создания: 2
2024-10-17 12:00:02 [INFO] Количество broadcaster'ов для запуска: 2
2024-10-17 12:00:03 [INFO] Запуск broadcaster 1/2: B2B_Broadcaster
2024-10-17 12:00:04 [INFO] ✅ B2B_Broadcaster подключен: ID=8108419249, Name=Владимир
2024-10-17 12:00:05 [INFO] Запуск broadcaster 2/2: B2C_Broadcaster
2024-10-17 12:00:06 [INFO] ✅ B2C_Broadcaster подключен: ID=8497033180, Name=Яблочный Гусь
```

---

### 📚 Новая документация

#### 1. TROUBLESHOOTING.md
Подробное руководство по устранению проблем:
- Типичные ошибки и их решения
- Команды для диагностики
- Контрольный список перед запуском

#### 2. WINDOWS_SETUP.md
Инструкция по настройке на Windows Server:
- Пошаговая установка
- Настройка автозапуска
- Мониторинг и обслуживание
- Полезные команды PowerShell

#### 3. CHANGELOG.md (этот файл)
История всех изменений в проекте

---

### 🔧 Технические улучшения

1. **Проверка существования broadcaster'ов**
   ```python
   if not self.broadcasters:
       await self._create_broadcasters()
   ```

2. **Автоматическое создание директорий**
   ```python
   session_dir.mkdir(parents=True, exist_ok=True)
   ```

3. **Улучшенная обработка ошибок Google Sheets**
   - Бот продолжает работу даже при ошибках Google Sheets
   - Используются сообщения из `config/messages.py` как fallback

4. **Детальная диагностика credentials.json**
   - Проверка существования файла
   - Проверка размера файла
   - Валидация JSON структуры
   - Проверка обязательных полей

---

## Миграция с предыдущих версий

### Для обновления до текущей версии:

1. **Подтяните изменения:**
   ```bash
   git pull
   ```

2. **Создайте директорию sessions:**
   ```bash
   mkdir sessions
   cp acc1.session sessions/
   cp acc2.session sessions/
   ```

3. **Запустите диагностику:**
   ```bash
   python check_environment.py
   ```

4. **Исправьте проблемы** (если есть)

5. **Запустите бота:**
   ```bash
   python main_improved.py
   ```

---

## Известные проблемы

Нет известных критических проблем.

---

## Планируемые улучшения

- [ ] Веб-интерфейс для мониторинга
- [ ] Dashboard с метриками в реальном времени
- [ ] Интеграция с Prometheus/Grafana
- [ ] Автоматическое резервное копирование
- [ ] Telegram бот для управления

---

## Обратная связь

Если вы нашли ошибку или у вас есть предложения:
1. Создайте issue в GitHub
2. Или свяжитесь с разработчиком

**ВАЖНО:** Не публикуйте в issues файлы `.env`, `credentials.json` или `.session`!

