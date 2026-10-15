import requests
from publishers.base import BasePublisher
from utils.logging_config import setup_logger

logger = setup_logger("TelegramPublisher")

class TelegramPublisher(BasePublisher):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def authenticate(self, credentials: dict = None) -> bool:
        try:
            res = requests.get(f"https://api.telegram.org/bot{self.bot_token}/getMe", timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Lỗi xác thực Telegram: {e}")
            return False

    def publish(self, title: str, content: str, **kwargs) -> dict:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        text = f"*{title}*\n\n{content}"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json().get("result", {})
                msg_id = str(data.get("message_id"))
                return {
                    "success": True,
                    "external_id": msg_id,
                    "url": f"https://t.me/c/{self.chat_id}/{msg_id}",
                    "error": None
                }
            else:
                return {"success": False, "external_id": None, "url": None, "error": f"Telegram Error: {res.text}"}
        except Exception as e:
            logger.error(f"Lỗi kết nối Telegram: {e}")
            return {"success": False, "external_id": None, "url": None, "error": str(e)}