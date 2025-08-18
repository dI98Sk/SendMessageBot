# google_sheet_fetch.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def fetch_messages_from_google_sheet(sheet_url):
    # Авторизация
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    # Открываем таблицу
    sheet = client.open_by_url(sheet_url).sheet1

    # Получаем все сообщения (предполагаем, что они в первом столбце)
    messages = sheet.col_values(1)
    return messages
