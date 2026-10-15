import logging
import os
import re
import json
import time
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class ContentGenerator:
    @staticmethod
    def generate_long_form_post(topic: str, target_words: int = 600) -> dict:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "Thiếu mã GEMINI_API_KEY trong file .env."
            }

        try:
            client = genai.Client(api_key=api_key)

            clean_user_topic = re.sub(r'(Live Market Data:|Mã:|Giá hiện tại:|Biến động:).*', '', topic).strip()
            if not clean_user_topic:
                clean_user_topic = "Bitcoin Market Trend and Price Action Analysis"

            prompt = (
                "You are an elite quantitative crypto market analyst writing an analytical report for Binance Square.\n\n"
                "RULES:\n"
                "1. LANGUAGE: 100% IN ENGLISH. NO VIETNAMESE.\n"
                "2. TITLE: Clean, concise, NO PUNCTUATION MARKS (letters, numbers, spaces, $ only).\n"
                "3. TAG: Embed $BTC properly.\n"
                "4. FORMAT: Return valid JSON ONLY with exact keys:\n"
                '{\n'
                '  "title": "Clean Title Without Punctuation",\n'
                '  "content": "Detailed professional technical analysis body strictly in English.",\n'
                '  "hashtag": "#BTC #Crypto #BinanceSquare #Trading",\n'
                '  "cta": "What are your price targets for $BTC? Share your analysis below!"\n'
                '}\n\n'
                f"Topic: {clean_user_topic}"
            )

            # Danh sách các model dự phòng theo thứ tự ưu tiên khi gặp lỗi quá tải 503
            candidate_models = ['gemini-3.8-flash', 'gemini-3.6-flash', 'gemini-3.5-flash-lite']
            response = None
            last_error = None

            for model_name in candidate_models:
                try:
                    logger.info(f"Đang thử gọi Gemini với model: {model_name}...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.7,
                        ),
                    )
                    if response and response.text:
                        logger.info(f"Gọi thành công với model {model_name}")
                        break
                except Exception as model_err:
                    last_error = model_err
                    logger.warning(f"Model {model_name} gặp lỗi, đang chuyển model dự phòng... Chi tiết: {model_err}")
                    time.sleep(1)

            if not response or not response.text:
                return {
                    "success": False,
                    "error": f"Hệ thống AI đang quá tải tạm thời (503). Vui lòng thử lại sau vài giây. Lỗi: {str(last_error)}"
                }

            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            data = json.loads(raw_text)

            title = data.get("title", "Bitcoin Market Analysis")
            clean_title = re.sub(r'[^A-Za-z0-9\s\$]', '', title).strip()

            return {
                "success": True,
                "title": clean_title,
                "content": data.get("content", ""),
                "hashtag": data.get("hashtag", "#BTC #BinanceSquare"),
                "cta": data.get("cta", "Share your thoughts below!")
            }

        except Exception as e:
            logger.exception("Lỗi khi gọi Google GenAI API:")
            return {
                "success": False,
                "error": f"Lỗi kết nối Gemini API: {str(e)}"
            }