"""
Кастомные исключения для приложения
"""

class BroadcastingError(Exception):
    """Базовое исключение для ошибок рассылки"""
    pass

class ConfigurationError(Exception):
    """Исключение для ошибок конфигурации"""
    pass

class TelegramConnectionError(BroadcastingError):
    """Ошибка подключения к Telegram"""
    pass

class MessageSendError(BroadcastingError):
    """Ошибка отправки сообщения"""
    def __init__(self, message: str, chat_id: int, original_error: Exception = None):
        self.chat_id = chat_id
        self.original_error = original_error
        super().__init__(message)

class ConfigurationValidationError(ConfigurationError):
    """Ошибка валидации конфигурации"""
    pass

class GoogleSheetsError(Exception):
    """Ошибка работы с Google Sheets"""
    pass
