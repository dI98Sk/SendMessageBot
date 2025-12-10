"""
Базовый клиент для работы с Google Sheets
Общий компонент для всех микросервисов
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """
    Базовый клиент для работы с Google Sheets
    
    Используется обоими сервисами, но без обмена данными между ними
    """
    
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
            logger.info("✅ Успешная авторизация в Google Sheets")
        except Exception as e:
            logger.error(f"❌ Ошибка авторизации в Google Sheets: {e}")
            raise
    
    def open_sheet(self, sheet_url: str):
        """
        Открытие таблицы по URL
        
        Args:
            sheet_url: URL таблицы
            
        Returns:
            gspread.Spreadsheet: Объект таблицы
        """
        try:
            sheet = self.client.open_by_url(sheet_url)
            return sheet
        except Exception as e:
            logger.error(f"Ошибка открытия таблицы {sheet_url}: {e}")
            raise
    
    def read_column(self, sheet_url: str, column: int = 1, worksheet_name: Optional[str] = None) -> List[str]:
        """
        Чтение столбца из таблицы
        
        Args:
            sheet_url: URL таблицы
            column: Номер столбца (1-based)
            worksheet_name: Название листа (если None - первый лист)
            
        Returns:
            List[str]: Значения столбца
        """
        try:
            sheet = self.open_sheet(sheet_url)
            worksheet = sheet.worksheet(worksheet_name) if worksheet_name else sheet.sheet1
            values = worksheet.col_values(column)
            # Фильтруем пустые значения
            return [v.strip() for v in values if v.strip()]
        except Exception as e:
            logger.error(f"Ошибка чтения столбца {column} из таблицы: {e}")
            raise
    
    def write_data(self, sheet_url: str, data: List[List[Any]], 
                   worksheet_name: Optional[str] = None, 
                   start_cell: str = "A1"):
        """
        Запись данных в таблицу
        
        Args:
            sheet_url: URL таблицы
            data: Данные для записи (список списков)
            worksheet_name: Название листа (если None - первый лист)
            start_cell: Начальная ячейка (например, "A1")
        """
        try:
            sheet = self.open_sheet(sheet_url)
            worksheet = sheet.worksheet(worksheet_name) if worksheet_name else sheet.sheet1
            
            # Очистка существующих данных (опционально)
            # worksheet.clear()
            
            # Запись данных
            worksheet.update(start_cell, data)
            logger.info(f"✅ Записано {len(data)} строк в таблицу")
        except Exception as e:
            logger.error(f"Ошибка записи данных в таблицу: {e}")
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
            sheet = self.open_sheet(sheet_url)
            worksheet = sheet.sheet1
            # Пробуем получить первую ячейку
            worksheet.cell(1, 1).value
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к таблице: {e}")
            return False

