# update_configB2B.py
from google_sheet_fetch import fetch_messages_from_google_sheet
from dotenv import load_dotenv
import os

# =======================
# Загружаем переменные из .env
# =======================
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
telegram_session_name = os.getenv("SESSION_NAME")
sheet_url = os.getenv("SHEET_URL_B2B")

CONFIG_PATH = "config_mesВ2B.py"

def update_config():
    print("Обновление сообщений из Google Sheet...")
    messages = fetch_messages_from_google_sheet(sheet_url)

    # Формируем строку для config_mesВ2B.py
    config_content = "MESSAGESB2B = [\n"
    for msg in messages:
        config_content += f"    {repr(msg)},\n"
    config_content += "]\n"

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(config_content)