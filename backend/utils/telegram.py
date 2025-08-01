import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_telegram_message(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Missing Telegram credentials")
        return

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(API_URL, data=payload)
        if res.status_code != 200:
            print(f"❌ Telegram Error: {res.status_code} - {res.text}")
        else:
            print("✅ Telegram notification sent.")
    except Exception as e:
        print(f"❌ Exception: {e}")
