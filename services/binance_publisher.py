import logging
import os
import requests

logger = logging.getLogger(__name__)

class BinancePublisher:
    @staticmethod
    def publish_post(title: str, content: str, hashtag: str, cta: str, chart_image_path: str = None) -> dict:
        """
        Đăng bài viết kèm theo file ảnh biểu đồ thực tế trực tiếp lên Binance Square API.
        """
        api_key = os.getenv("BINANCE_SQUARE_OPENAPI_KEY")
        if not api_key:
            logger.error("Missing BINANCE_SQUARE_OPENAPI_KEY environment variable.")
            return {
                "success": False,
                "error": "Thiếu mã BINANCE_SQUARE_OPENAPI_KEY trong file .env."
            }

        # URL chuẩn của Binance Square dành cho việc đăng bài viết và media
        url = "https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add"

        headers = {
            "X-Square-OpenAPI-Key": api_key
        }

        # Giới hạn độ dài nội dung an toàn để tránh lỗi từ Binance API
        if len(content) > 1200:
            content = content[:1200] + "..."

        # Ghép nối nội dung bài viết hoàn chỉnh
        full_body = f"{title}\n\n{content}\n\n{hashtag}\n\n{cta}"

        # Dữ liệu văn bản gửi đi
        data = {
            "bodyTextOnly": full_body
        }

        files = {}
        file_handle = None

        try:
            # Nếu có tệp ảnh biểu đồ thực tế, tiến hành đính kèm trực tiếp vào yêu cầu
            if chart_image_path and os.path.exists(chart_image_path):
                logger.info(f"Đang đính kèm file ảnh thực tế từ đường dẫn: {chart_image_path}")
                file_handle = open(chart_image_path, "rb")
                # Đóng gói file theo định dạng multipart/form-data
                files = {"file": ("chart.png", file_handle, "image/png")}

            logger.info("Đang gửi yêu cầu đăng bài kèm file ảnh trực tiếp lên Binance Square...")
            
            if files:
                response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, json=data, headers=headers, timeout=20)
            
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("code") == "000000" or res_data.get("success") == True:
                    return {"success": True, "message": "Đăng bài kèm ảnh biểu đồ thực tế thành công!"}
                else:
                    return {"success": False, "error": f"Binance API từ chối: {res_data.get('message', res_data)}"}
            else:
                return {"success": False, "error": f"Lỗi HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            logger.exception("Lỗi ngoại lệ khi gọi API đăng bài Binance kèm ảnh:")
            return {"success": False, "error": f"Lỗi kết nối: {str(e)}"}
            
        finally:
            if file_handle:
                file_handle.close()