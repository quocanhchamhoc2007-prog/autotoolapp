import os
import logging
import requests
import re
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ImageGenerationService:
    @staticmethod
    def generate_image_with_ai(topic: str) -> dict:
        """
        Tự động tạo hình ảnh minh họa thông minh:
        - Nếu là chủ đề chứng khoán / mã cổ phiếu / tài chính: Tự động tạo ảnh biểu đồ nến, phân tích kỹ thuật, trading chart.
        - Các chủ đề khác: Tạo ảnh minh họa kỹ thuật số hiện đại.
        """
        openai_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
        clean_topic = topic.strip()
        
        # 1. Kiểm tra xem chủ đề có phải về chứng khoán, cổ phiếu, tài chính hay không
        finance_keywords = ["cổ phiếu", "chứng khoán", "stock", "chart", "biểu đồ", "vn-index", "trading", "đầu tư", "thị trường tài chính", "mã cổ phiếu"]
        is_finance_topic = any(keyword in clean_topic.lower() for keyword in finance_keywords)
        
        # Nhận diện nếu có chứa mã viết hoa kiểu mã chứng khoán (VD: VCB, FPT, AAPL...)
        has_uppercase_code = bool(re.search(r'\b[A-Z]{3,5}\b', clean_topic))

        if is_finance_topic or has_uppercase_code:
            # Prompt chuyên biệt cho chứng khoán: Biểu đồ nến, màn hình giao dịch, phân tích kỹ thuật chuyên nghiệp
            image_prompt = (
                f"Professional financial stock market trading chart representing {clean_topic}, "
                f"candlestick chart showing green and red price action trends, technical analysis indicators, "
                f"modern financial dashboard, high tech data visualization, 4k resolution, ultra-realistic."
            )
            fallback_finance_query = f"stock market trading chart candlestick financial analysis {clean_topic}"
            logger.info(f"Phát hiện chủ đề chứng khoán/tài chính. Đang thiết lập prompt biểu đồ cho: {clean_topic}")
        else:
            # Prompt minh họa thông thường cho các chủ đề khác
            image_prompt = f"A professional, modern digital illustration representing: {clean_topic}. High quality, clean composition."
            fallback_finance_query = f"professional illustration of {clean_topic}"

        # 2. Thử gọi OpenAI DALL-E 3 trước (nếu có key)
        if openai_key and not openai_key.startswith("your_") and len(openai_key) > 20:
            try:
                headers = {
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "dall-e-3",
                    "prompt": image_prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
                res = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers, timeout=30)
                
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "success": True,
                        "image_url": data["data"][0]["url"],
                        "image_provider": "OpenAI DALL-E 3",
                        "image_license": "AI Generated"
                    }
            except Exception as e:
                logger.error(f"DALL-E 3 lỗi, chuyển sang nguồn ảnh động thông minh: {e}")

        # 3. Phương án sinh ảnh động qua Pollinations AI theo từ khóa chuyên biệt (Biểu đồ hoặc Minh họa)
        import urllib.parse
        encoded_prompt = urllib.parse.quote(fallback_finance_query)
        ai_generated_fallback_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"

        logger.info(f"Đã tạo URL ảnh biểu đồ/chủ đề động: {clean_topic}")
        return {
            "success": True,
            "image_url": ai_generated_fallback_url,
            "image_provider": "Dynamic Financial Chart Generator",
            "image_license": "Free Social Media License"
        }