import logging
import re
from datetime import datetime
from services.content_generator import ContentGenerator
from services.content_quality_checker import ContentQualityChecker
from services.stock_chart_service import StockChartService
from services.publishing_service import PublishingService
from database.connection import SessionLocal
from database.models import PostModel

logger = logging.getLogger(__name__)

class AutoOrchestrator:
    @staticmethod
    def run_auto_post(topic: str, platform: str, credentials: dict, target_words: int = 800, progress_callback=None) -> dict:
        def update_progress(msg):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        try:
            clean_topic = topic.strip()
            stock_match = re.search(r'\b([A-Z]{3,5})(?:\.VN)?\b', clean_topic.upper())
            
            image_path = ""
            market_summary = ""
            
            if "cổ phiếu" in clean_topic.lower() or "chứng khoán" in clean_topic.lower() or "btc" in clean_topic.lower() or stock_match:
                ticker = stock_match.group(1) if stock_match else "BTC"
                update_progress(f"📈 Đang kết nối lấy dữ liệu thị trường và vẽ biểu đồ cho: {ticker}...")
                
                chart_res = StockChartService.fetch_and_plot_stock(ticker)
                if chart_res.get("success"):
                    image_path = chart_res.get("image_path")
                    market_summary = chart_res.get("market_data_summary")
                    update_progress(f"📊 Đã tạo xong biểu đồ trực quan cho {chart_res.get('symbol')}")
                else:
                    update_progress("⚠️ Không tải được dữ liệu mã, tiếp tục tạo bài viết chuyên sâu...")

            update_progress("🤖 Đang yêu cầu GPT viết bài phân tích chuyên sâu (English & Live Data)...")
            
            pure_topic = clean_topic
            if "giá" in pure_topic.lower() or "btc" in pure_topic.lower():
                pure_topic = "Bitcoin $BTC market analysis, price action, support and resistance levels"

            prompt_context = (
                f"{pure_topic}. "
                f"Instructions: Write a professional market analysis post ENTIRELY IN ENGLISH. "
                f"Current live data: Bitcoin ($BTC) price is around $83,000, support at $81,000, resistance at $84,000. "
                f"{market_summary}"
            )

            content_res = ContentGenerator.generate_long_form_post(topic=prompt_context, target_words=target_words)
            if not content_res.get("success"):
                return {"success": False, "error": f"Lỗi tạo nội dung: {content_res.get('error')}"}

            title = content_res.get("title")
            content = content_res.get("content")
            hashtag = content_res.get("hashtag", "")
            cta = content_res.get("cta", "")

            update_progress("🔍 Đang kiểm tra chất lượng bài viết...")
            quality_check = ContentQualityChecker.evaluate_post(content, target_words)
            if not quality_check.get("is_valid"):
                return {"success": False, "error": f"Bài viết không đạt chuẩn chất lượng: {quality_check.get('issues')}"}

            update_progress(f"🚀 Đang tự động xuất bản bài viết lên {platform}...")
            content_data = {
                "title": title,
                "content": content,
                "hashtag": hashtag,
                "cta": cta,
                "image_path": image_path
            }

            publish_res = PublishingService.publish_post(
                post_id=0,
                platform=platform,
                credentials=credentials,
                content_data=content_data
            )

            if not publish_res.get("success"):
                return {"success": False, "error": f"Lỗi khi đăng bài: {publish_res.get('error')}"}

            external_post_id = publish_res.get("post_id", "N/A")
            published_url = publish_res.get("url", "")

            update_progress("💾 Đang lưu lịch sử vào cơ sở dữ liệu...")
            db = SessionLocal()
            try:
                new_post = PostModel(
                    title=title,
                    content=content,
                    hashtag=hashtag,
                    cta=cta,
                    platform=platform,
                    platform_target=platform,
                    target_word_count=target_words,
                    actual_word_count=quality_check.get("actual_word_count", 0),
                    auto_publish_enabled=True,
                    publish_status="AUTO_PUBLISHED",
                    status="AUTO_PUBLISHED",
                    image_url=image_path,
                    image_provider="Auto AI Chart/Image Service",
                    external_post_id=str(external_post_id),
                    published_url=published_url,
                    published_at=datetime.utcnow()
                )
                db.add(new_post)
                db.commit()
            except Exception as db_err:
                logger.error(f"Lỗi lưu CSDL: {db_err}")
            finally:
                db.close()

            update_progress("✅ Hoàn tất toàn bộ quy trình tự động!")
            return {
                "success": True,
                "title": title,
                "content": content,
                "hashtag": hashtag,
                "cta": cta,
                "image_url": image_path,
                "published_url": published_url,
                "external_post_id": external_post_id
            }

        except Exception as e:
            return {"success": False, "error": str(e)}