import streamlit as st
import os
from dotenv import load_dotenv
from services.auto_orchestrator import AutoOrchestrator

# Nạp trực tiếp biến môi trường từ file .env ở thư mục gốc
load_dotenv()

def render_create_post():
    st.markdown("### 🚀 AutoPost AI - Tự động hóa nội dung Binance Square")
    
    # Lấy trực tiếp từ os.environ sau khi load_dotenv()
    api_key_configured = os.getenv("BINANCE_SQUARE_OPENAPI_KEY", "").strip()
    
    if not api_key_configured:
        try:
            api_key_configured = st.secrets.get("BINANCE_SQUARE_OPENAPI_KEY", "").strip()
        except Exception:
            api_key_configured = ""
    
    if not api_key_configured:
        st.warning("⚠️ Chưa cấu hình **BINANCE_SQUARE_OPENAPI_KEY**. Vui lòng kiểm tra lại file `.env` trong thư mục dự án.")
    else:
        st.success("✅ Đã nhận diện Binance Square OpenAPI Key thành công!")
    
    topic = st.text_input("Nhập chủ đề Crypto / Token cần phân tích:", placeholder="Ví dụ: Phân tích xu hướng giá BTC tuần tới, cơ hội tích lũy Altcoin...")
    target_words = st.slider("Độ dài mục tiêu (Từ):", min_value=600, max_value=1200, value=800, step=50)

    if st.button("🚀 TẠO BÀI VÀ ĐĂNG LÊN BINANCE SQUARE", type="primary", disabled=not api_key_configured):
        if not topic.strip():
            st.error("Vui lòng nhập chủ đề bài viết!")
            return

        status_box = st.status("Đang thực hiện quy trình tự động...", expanded=True)

        def progress_callback(msg):
            status_box.write(msg)

        credentials = {"openapi_key": api_key_configured}
        
        # Thực thi pipeline tự động hoàn toàn ở backend
        result = AutoOrchestrator.run_auto_post(
            topic=topic,
            platform="Binance Square",
            credentials=credentials,
            target_words=target_words,
            progress_callback=progress_callback
        )

        if result.get("success"):
            status_box.update(label="✅ Đăng bài thành công lên Binance Square!", state="complete", expanded=False)
            st.success("Bài viết đã được xuất bản thành công lên Binance Square!")
            if result.get("published_url"):
                st.markdown(f"**🔗 Liên kết bài đăng:** [{result.get('published_url')}]({result.get('published_url')})")
            
            with st.expander("📄 Xem trước nội dung bài viết"):
                st.subheader(result.get("title"))
                st.write(result.get("content"))
                if result.get("image_url"):
                    st.image(result.get("image_url"), caption="Biểu đồ / Hình ảnh minh họa kỹ thuật")
        else:
            status_box.update(label="❌ Đăng bài thất bại!", state="error", expanded=True)
            st.error(f"Chi tiết lỗi: {result.get('error')}")