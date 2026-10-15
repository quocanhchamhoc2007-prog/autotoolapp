import logging
import re
import requests

logger = logging.getLogger(__name__)

class BinanceSquarePublisher:
    def __init__(self, openapi_key: str):
        self.openapi_key = openapi_key.strip()
        self.api_endpoint = "https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add"

    def publish(self, title: str, content: str, tags: list = None) -> dict:
        """
        Publishes clean English market analysis to Binance Square, ensuring content length 
        does not exceed Binance API limits.
        """
        if not self.openapi_key:
            return {"success": False, "error": "Missing Binance Square OpenAPI Key. Please check your .env file."}

        try:
            # 1. Strict title cleaning: Letters, numbers, and spaces only (No punctuation marks)
            clean_title = re.sub(r'[^A-Za-z0-9\s]', '', title).strip()
            if not clean_title:
                clean_title = "Bitcoin Market Structure and Price Action Analysis"

            # 2. Auto-inject $BTC or $ETH symbol links safely (Max 2 symbols)
            common_symbols = ["BTC", "ETH", "BNB", "SOL", "XRP"]
            words = clean_title.split()
            final_title_words = []
            symbol_count = 0
            for w in words:
                upper_w = w.upper()
                if upper_w in common_symbols and symbol_count < 2:
                    final_title_words.append(f"${upper_w}")
                    symbol_count += 1
                else:
                    final_title_words.append(w)
            
            formatted_title = " ".join(final_title_words)
            
            # 3. Giới hạn độ dài nội dung (Content Length Limit) để tránh lỗi từ Binance API
            # Binance Square OpenAPI thường giới hạn khoảng dưới 1000-1200 ký tự cho mỗi post
            max_content_length = 900
            trimmed_content = content.strip()
            if len(trimmed_content) > max_content_length:
                trimmed_content = trimmed_content[:max_content_length].rsplit(' ', 1)[0] + "..."

            full_text = f"{formatted_title}\n\n{trimmed_content}".strip()
            
            if tags:
                valid_tags = [re.sub(r'[^A-Za-z0-9]', '', tag) for tag in tags if tag][:3]
                tag_str = " ".join([f"#{t}" for t in valid_tags if t])
                if tag_str:
                    # Kiểm tra tổng độ dài nếu gắn tag
                    if len(full_text) + len(tag_str) + 2 <= 1000:
                        full_text += f"\n\n{tag_str}"

            headers = {
                "Content-Type": "application/json",
                "X-Square-OpenAPI-Key": self.openapi_key,
                "clienttype": "binanceSkill"
            }

            payload = {
                "bodyTextOnly": full_text
            }

            logger.info("Publishing safe-length English analysis post to Binance Square...")
            response = requests.post(self.api_endpoint, json=payload, headers=headers, timeout=25)
            
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("code") == "000000" or res_data.get("success") is True:
                    data_result = res_data.get("data", {})
                    post_id = data_result.get("postId") or data_result.get("id") or "SUCCESS"
                    post_url = data_result.get("url") or (f"https://www.binance.com/en/square/post/{post_id}" if post_id != "SUCCESS" else "https://www.binance.com/square/creator-center/home")
                    return {
                        "success": True,
                        "post_id": str(post_id),
                        "url": post_url
                    }
                else:
                    error_msg = res_data.get("message", "Binance server error")
                    return {"success": False, "error": f"Binance API Error: {error_msg}"}
            elif response.status_code in [401, 403]:
                return {"success": False, "error": "Authentication failed: Invalid OpenAPI Key or KYC incomplete."}
            else:
                return {"success": False, "error": f"HTTP Error {response.status_code}: Cannot connect to Binance Square."}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "UNKNOWN_RESULT: Connection timeout to Binance Square."}
        except Exception as e:
            logger.exception("Exception during publishing to Binance Square:")
            return {"success": False, "error": str(e)}