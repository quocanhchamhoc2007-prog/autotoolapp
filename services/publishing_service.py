import logging
import os
from publishers.binance_square import BinanceSquarePublisher
from publishers.facebook import FacebookPublisher
from publishers.telegram import TelegramPublisher

logger = logging.getLogger(__name__)

class PublishingService:
    @staticmethod
    def publish_post(post_id: int, platform: str, credentials: dict, content_data: dict = None) -> dict:
        """
        Xử lý điều phối xuất bản bài viết lên các nền tảng (Binance Square, Facebook, Telegram).
        """
        try:
            if content_data:
                title = content_data.get("title", "")
                content = content_data.get("content", "")
                hashtag = content_data.get("hashtag", "")
                cta = content_data.get("cta", "")
                image_path = content_data.get("image_path", "")
            else:
                try:
                    from database.connection import SessionLocal
                    from database.models import PostModel
                    db = SessionLocal()
                    post = db.query(PostModel).filter(PostModel.id == post_id).first()
                    if not post:
                        return {"success": False, "error": f"Không tìm thấy bài viết ID {post_id}"}
                    
                    title = getattr(post, 'title', '')
                    content = getattr(post, 'content', '')
                    hashtag = getattr(post, 'hashtag', '')
                    cta = getattr(post, 'cta', '')
                    image_path = getattr(post, 'image_url', '')
                except Exception as db_err:
                    return {"success": False, "error": f"Lỗi kết nối CSDL: {str(db_err)}"}

            # 1. Đăng lên Binance Square
            if platform == "Binance Square":
                openapi_key = credentials.get("openapi_key") or os.getenv("BINANCE_SQUARE_OPENAPI_KEY", "")
                publisher = BinanceSquarePublisher(openapi_key=openapi_key)
                tags = [tag.strip() for tag in hashtag.split()] if hashtag else []
                
                result = publisher.publish(title=title, content=content, tags=tags)
                
                if result.get("success") and image_path and os.path.exists(image_path):
                    result["image_notice"] = "Ảnh AI/Biểu đồ đã được tạo và lưu cục bộ. Định dạng bài đăng API Binance Square tập trung vào nội dung văn bản chuyên sâu."
                
                return result

            # 2. Giữ nguyên Facebook nếu cần tương thích ngược
            elif platform == "Facebook":
                page_id = credentials.get("page_id")
                access_token = credentials.get("access_token")
                full_text = f"{title}\n\n{content}\n\n{hashtag}\n\n{cta}".strip()
                
                if image_path and os.path.exists(image_path):
                    import requests
                    url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
                    with open(image_path, 'rb') as img_file:
                        files = {'source': img_file}
                        payload = {"message": full_text, "access_token": access_token}
                        response = requests.post(url, data=payload, files=files, timeout=30)
                    res_data = response.json()
                    if "id" in res_data:
                        return {"success": True, "post_id": res_data["id"], "url": f"https://facebook.com/{res_data['id']}"}
                    else:
                        return {"success": False, "error": f"FB Error: {res_data.get('error', {}).get('message', 'Lỗi không xác định')}"}
                else:
                    fb = FacebookPublisher(page_id=page_id, access_token=access_token)
                    return fb.publish(title=title, content=full_text)

            # 3. Giữ nguyên Telegram
            elif platform == "Telegram":
                bot_token = credentials.get("bot_token")
                chat_id = credentials.get("chat_id")
                full_text = f"{title}\n\n{content}\n\n{hashtag}\n\n{cta}".strip()
                tg = TelegramPublisher(bot_token=bot_token, chat_id=chat_id)
                return tg.publish(content=full_text)

            else:
                return {"success": False, "error": f"Nền tảng '{platform}' chưa được hỗ trợ."}

        except Exception as e:
            logger.exception("Lỗi trong PublishingService:")
            return {"success": False, "error": str(e)}