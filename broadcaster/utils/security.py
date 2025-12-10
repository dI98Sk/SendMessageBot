"""
Утилиты безопасности
"""
import os
import hashlib
import secrets
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityManager:
    """Менеджер безопасности для защиты конфигурации"""
    
    def __init__(self, master_password: Optional[str] = None):
        self.master_password = master_password or os.getenv("MASTER_PASSWORD")
        self._key: Optional[bytes] = None
    
    def _get_encryption_key(self) -> bytes:
        """Получение ключа шифрования"""
        if self._key is not None:
            return self._key
        
        if not self.master_password:
            # Если нет мастер-пароля, генерируем случайный ключ
            self._key = Fernet.generate_key()
            return self._key
        
        # Генерируем ключ из мастер-пароля
        salt = b'sendmessagebot_salt'  # В продакшене должен быть случайным
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        self._key = key
        return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Шифрование чувствительных данных"""
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Расшифровка чувствительных данных"""
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def mask_sensitive_value(self, value: str, show_chars: int = 4) -> str:
        """Маскировка чувствительных значений для логирования"""
        if len(value) <= show_chars:
            return "*" * len(value)
        
        return value[:show_chars] + "*" * (len(value) - show_chars)
    
    def validate_environment_variables(self, required_vars: list) -> Dict[str, bool]:
        """Валидация переменных окружения"""
        validation_results = {}
        
        for var in required_vars:
            value = os.getenv(var)
            validation_results[var] = value is not None and value.strip() != ""
        
        return validation_results
    
    def sanitize_config_for_logging(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка конфигурации от чувствительных данных для логирования"""
        sensitive_keys = {
            'api_hash', 'secret', 'password', 'token', 'key',
            'proxy_secret', 'credentials'
        }
        
        sanitized = {}
        for key, value in config.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(value, str):
                    sanitized[key] = self.mask_sensitive_value(value)
                else:
                    sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized

class ConfigValidator:
    """Валидатор конфигурации"""
    
    @staticmethod
    def validate_telegram_config(config: Dict[str, Any]) -> Dict[str, str]:
        """Валидация конфигурации Telegram"""
        errors = {}
        
        # Проверка API ID
        api_id = config.get('api_id')
        if not api_id:
            errors['api_id'] = "API ID обязателен"
        elif not isinstance(api_id, int) or api_id <= 0:
            errors['api_id'] = "API ID должен быть положительным числом"
        
        # Проверка API Hash
        api_hash = config.get('api_hash')
        if not api_hash:
            errors['api_hash'] = "API Hash обязателен"
        elif not isinstance(api_hash, str) or len(api_hash) < 20:
            errors['api_hash'] = "API Hash должен быть строкой длиной не менее 20 символов"
        
        # Проверка session_name
        session_name = config.get('session_name')
        if not session_name:
            errors['session_name'] = "Имя сессии обязательно"
        
        return errors
    
    @staticmethod
    def validate_proxy_config(config: Dict[str, Any]) -> Dict[str, str]:
        """Валидация конфигурации прокси"""
        errors = {}
        
        if not config.get('enabled', False):
            return errors
        
        # Проверка адреса
        addr = config.get('addr')
        if not addr:
            errors['addr'] = "Адрес прокси обязателен"
        
        # Проверка порта
        port = config.get('port')
        if not port:
            errors['port'] = "Порт прокси обязателен"
        elif not isinstance(port, int) or not (1 <= port <= 65535):
            errors['port'] = "Порт должен быть числом от 1 до 65535"
        
        # Проверка секрета для MTProto
        if config.get('protocol') == 'mtproto':
            secret = config.get('secret')
            if not secret:
                errors['secret'] = "Секрет прокси обязателен для MTProto"
        
        return errors
    
    @staticmethod
    def validate_broadcasting_config(config: Dict[str, Any]) -> Dict[str, str]:
        """Валидация конфигурации рассылки"""
        errors = {}
        
        # Проверка задержки между чатами
        delay = config.get('delay_between_chats')
        if delay is not None:
            if not isinstance(delay, int) or delay < 0:
                errors['delay_between_chats'] = "Задержка должна быть неотрицательным числом"
        
        # Проверка задержки цикла
        cycle_delay = config.get('cycle_delay')
        if cycle_delay is not None:
            if not isinstance(cycle_delay, int) or cycle_delay < 60:
                errors['cycle_delay'] = "Задержка цикла должна быть не менее 60 секунд"
        
        return errors

# Глобальный экземпляр менеджера безопасности
security_manager = SecurityManager()
