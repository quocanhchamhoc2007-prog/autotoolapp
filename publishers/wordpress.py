import requests
from publishers.base import BasePublisher
from utils.logging_config import setup_logger

logger = setup_logger("WordPressPublisher")

class WordPressPublisher(BasePublisher):
    def __init__(self, site_url: str, username: str, app_password: str):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password

    def authenticate(self, credentials: dict = None) -> bool:
        try:
            res = requests.get(f"{self.site_url}/wp-json/wp/v2/users/me", auth=(self.username, self.app_password), timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Lỗi xác thực WordPress: {e}")
            return False

    def publish(self, title: str, content: str, **kwargs) -> dict:
        url = f"{self.site_url}/wp-json/wp/v2/posts"
        payload = {
            "title": title,
            "content": content,
            "status": kwargs.get("status", "draft") # publish hoặc draft
        }
        try:
            res = requests.post(url, json=payload, auth=(self.username, self.app_password), timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                return {
                    "success": True,
                    "external_id": str(data.get("id")),
                    "url": data.get("link"),
                    "error": None
                }
            else:
                return {"success": False, "external_id": None, "url": None, "error": f"WP Error: {res.text}"}
        except Exception as e:
            logger.error(f"Lỗi kết nối WordPress: {e}")
            return {"success": False, "external_id": None, "url": None, "error": str(e)}