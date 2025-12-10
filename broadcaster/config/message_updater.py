"""
Модуль для обновления сообщений из Google Sheets
"""
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MessageConfigUpdater:
    """Класс для обновления конфигурации сообщений"""

    def __init__(self, messages_file_path: str = "config/messages.py"):
        self.messages_file_path = messages_file_path
        self.backup_dir = Path("backup/messages")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self):
        """Создание резервной копии файла сообщений"""
        if Path(self.messages_file_path).exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"messages_backup_{timestamp}.py"

            import shutil
            shutil.copy2(self.messages_file_path, backup_file)
            logger.info(f"Создана резервная копия: {backup_file}")
            return backup_file
        return None

    def update_messages_file(self, b2b_messages: List[str], b2c_messages: List[str]):
        """Обновление файла с сообщениями"""
        try:
            # Создаем резервную копию
            self.create_backup()

            # Генерируем новый контент файла
            content = self._generate_messages_file_content(b2b_messages, b2c_messages)

            # Записываем в файл
            with open(self.messages_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Файл сообщений обновлен: B2B={len(b2b_messages)}, B2C={len(b2c_messages)}")
            return True

        except Exception as e:
            logger.error(f"Ошибка обновления файла сообщений: {e}")
            return False

    def _generate_messages_file_content(self, b2b_messages: List[str], b2c_messages: List[str]) -> str:
        """Генерация содержимого файла сообщений"""
        content = '''"""
Конфигурация сообщений для рассылки
Обновлено: {timestamp}
"""
'''.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # B2B сообщения
        content += "\n# B2B сообщения (для оптовых клиентов)\n"
        content += "MESSAGES_B2B = [\n"

        for i, message in enumerate(b2b_messages):
            # Экранируем кавычки и переносы строк
            escaped_message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            content += f'    "{escaped_message}"'
            if i < len(b2b_messages) - 1:
                content += ","
            content += "\n"

        content += "]\n\n"

        # B2C сообщения
        content += "# B2C сообщения (для розничных клиентов)\n"
        content += "MESSAGES_B2C = [\n"

        for i, message in enumerate(b2c_messages):
            # Экранируем кавычки и переносы строк
            escaped_message = message.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            content += f'    "{escaped_message}"'
            if i < len(b2c_messages) - 1:
                content += ","
            content += "\n"

        content += "]\n"

        return content

    def reload_messages_module(self):
        """Перезагрузка модуля сообщений"""
        try:
            import sys
            import importlib

            # Удаляем модуль из кэша
            if 'config.messages' in sys.modules:
                del sys.modules['config.messages']

            # Перезагружаем модуль
            import config.messages
            importlib.reload(config.messages)

            logger.info("Модуль сообщений перезагружен")
            return True

        except Exception as e:
            logger.error(f"Ошибка перезагрузки модуля сообщений: {e}")
            return False

    def get_update_status(self) -> Dict[str, Any]:
        """Получение статуса обновлений"""
        backup_files = list(self.backup_dir.glob("messages_backup_*.py"))
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime) if backup_files else None

        return {
            'messages_file_exists': Path(self.messages_file_path).exists(),
            'backup_count': len(backup_files),
            'latest_backup': latest_backup.name if latest_backup else None,
            'latest_backup_time': datetime.fromtimestamp(
                latest_backup.stat().st_mtime).isoformat() if latest_backup else None
        }
