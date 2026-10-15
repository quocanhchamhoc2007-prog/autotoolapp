import requests
from publishers.base import BasePublisher
from utils.logging_config import setup_logger

logger = setup_logger("FacebookPublisher")

class FacebookPublisher(BasePublisher):
    def __init__(self, page_id: str, access_token: str):
        self.page_id = page_id
        self.access_token = access_token

    def authenticate(self, credentials: dict = None) -> bool:
        try:
            res = requests.get(f"https://graph.facebook.com/v18.0/{self.page_id}?access_token={self.access_token}", timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Lỗi xác thực Facebook: {e}")
            return False

    def publish(self, title: str, content: str, **kwargs) -> dict:
        url = f"https://graph.facebook.com/v18.0/{self.page_id}/feed"
        message = f"{title}\n\n{content}"
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        try:
            res = requests.post(url, data=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                post_id = data.get("id")
                return {
                    "success": True,
                    "external_id": post_id,
                    "url": f"https://facebook.com/{post_id}",
                    "error": None
                }
            else:
                return {"success": False, "external_id": None, "url": None, "error": f"FB Error: {res.text}"}
        except Exception as e:
            logger.error(f"Lỗi kết nối Facebook: {e}")
            return {"success": False, "external_id": None, "url": None, "error": str(e)}