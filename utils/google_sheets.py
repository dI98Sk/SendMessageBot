"""
Модуль для работы с Google Sheets
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsFetcher:
    """Класс для получения данных из Google Sheets"""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        """
        Инициализация клиента Google Sheets
        
        Args:
            credentials_path: Путь к файлу с учетными данными
        """
        self.credentials_path = credentials_path
        self.client = None
        self._authorize()
    
    def _authorize(self):
        """Авторизация в Google Sheets API"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )
            self.client = gspread.authorize(creds)
            logger.info("Успешная авторизация в Google Sheets")
        except Exception as e:
            logger.error(f"Ошибка авторизации в Google Sheets: {e}")
            raise
    
    def fetch_messages(self, sheet_url: str) -> List[str]:
        """
        Получение сообщений из Google Sheets
        
        Args:
            sheet_url: URL таблицы
            
        Returns:
            List[str]: Список сообщений
        """
        try:
            # Открываем таблицу
            sheet = self.client.open_by_url(sheet_url).sheet1
            
            # Получаем все сообщения (предполагаем, что они в первом столбце)
            messages = sheet.col_values(1)
            
            # Фильтруем пустые сообщения
            messages = [msg.strip() for msg in messages if msg.strip()]
            
            logger.info(f"Получено {len(messages)} сообщений из таблицы")
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка получения сообщений из таблицы: {e}")
            raise
    
    def test_connection(self, sheet_url: str) -> bool:
        """
        Тестирование подключения к таблице
        
        Args:
            sheet_url: URL таблицы
            
        Returns:
            bool: True если подключение успешно
        """
        try:
            sheet = self.client.open_by_url(sheet_url).sheet1
            # Пробуем получить первую ячейку
            sheet.cell(1, 1).value
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к таблице: {e}")
            return False

# Функция для обратной совместимости
def fetch_messages_from_google_sheet(sheet_url: str) -> List[str]:
    """
    Функция для обратной совместимости
    
    Args:
        sheet_url: URL таблицы
        
    Returns:
        List[str]: Список сообщений
    """
    fetcher = GoogleSheetsFetcher()
    return fetcher.fetch_messages(sheet_url)
