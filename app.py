import os
import logging
from dotenv import load_dotenv

# Nạp file .env ngay từ đầu chương trình
load_dotenv()

import streamlit as st
from services.chart_generator import ChartGenerator
from services.content_generator import ContentGenerator
from services.binance_publisher import BinancePublisher  # Module đăng bài cũ của bạn

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình giao diện trang Streamlit
st.set_page_config(
    page_title="AutoPost AI - Binance Square",
    page_icon="🚀",
    layout="centered"
)

def main():
    st.title("🚀 AutoPost AI - Tự động hóa nội dung Binance Square")
    st.markdown("Hệ thống tự động lấy dữ liệu thị trường thực tế từ Binance, vẽ biểu đồ kỹ thuật, tạo bài viết phân tích chuyên sâu bằng AI và xuất bản trực tiếp lên Binance Square.")
    
    st.divider()

    # Nhập thông tin cấu hình và chủ đề từ người dùng
    col1, col2 = st.columns([2, 1])
    with col1:
        symbol = st.text_input("Nhập mã Token / Crypto cần phân tích:", value="BTC", placeholder="Ví dụ: BTC, ETH, SOL...")
    with col2:
        target_words = st.selectbox("Độ dài mục tiêu (Từ):", [600, 800, 1200], index=0)

    st.markdown("### ⚙️ Thao tác vận hành")
    
    # Khởi tạo Session State để lưu kết quả bài viết và biểu đồ
    if "post_result" not in st.session_state:
        st.session_state.post_result = None
    if "chart_result" not in st.session_state:
        st.session_state.chart_result = None

    if st.button("📈 Tạo Biểu Đồ & Bài Viết Phân Tích", type="primary", use_container_width=True):
        if not symbol.strip():
            st.error("Vui lòng nhập mã Token hợp lệ!")
            return

        clean_symbol = symbol.upper().replace("$", "").strip()

        # Bước 1: Kết nối Binance lấy dữ liệu nến thực tế và vẽ biểu đồ kỹ thuật
        chart_result = None
        market_data_summary = ""

        with st.status(f"📊 Đang kết nối lấy dữ liệu thời gian thực từ Binance cho {clean_symbol}...", expanded=True) as status:
            st.write("Đang gọi Public API của Binance lấy dữ liệu giá & khối lượng...")
            chart_result = ChartGenerator.generate_chart(symbol=clean_symbol, output_path="temp_chart.png")

            if chart_result and chart_result.get("success"):
                market_data_summary = chart_result.get("summary", "")
                status.update(label=f"Đã vẽ xong biểu đồ cho {clean_symbol}! Giá hiện tại: ${chart_result.get('latest_price', 0):,.2f}", state="complete", expanded=False)
            else:
                error_msg = chart_result.get("error") if chart_result else "Không xác định"
                status.update(label=f"Cảnh báo: Không thể vẽ biểu đồ ({error_msg}). Tiếp tục tạo bài viết dạng văn bản.", state="error", expanded=False)

        st.session_state.chart_result = chart_result

        # Bước 2: Gọi AI tạo nội dung bài viết chuyên sâu kết hợp số liệu thực tế
        with st.spinner(f"🤖 Đang yêu cầu AI phân tích và viết bài dài (Mục tiêu: {target_words} từ)..."):
            full_topic_input = f"${clean_symbol} - {market_data_summary}" if market_data_summary else f"${clean_symbol}"
            
            post_result = ContentGenerator.generate_long_form_post(
                topic=full_topic_input, 
                target_words=target_words
            )
            st.session_state.post_result = post_result

    # Hiển thị biểu đồ nếu vẽ thành công
    if st.session_state.chart_result and st.session_state.chart_result.get("success"):
        st.markdown("### 📉 Biểu đồ kỹ thuật thời gian thực (Binance Data)")
        st.image(
            st.session_state.chart_result["chart_path"], 
            caption=f"Biểu đồ kỹ thuật thực tế từ Binance", 
            use_container_width=True
        )

    # Hiển thị kết quả bài viết hoàn chỉnh và nút đăng bài tự động
    if st.session_state.post_result:
        post_result = st.session_state.post_result
        if post_result.get("success"):
            st.success("🎉 Đã tạo nội dung bài viết phân tích thành công!")
            
            st.markdown("### 📝 Nội dung bài viết xuất bản")
            
            with st.container(border=True):
                st.markdown(f"**📌 Title:** {post_result.get('title', '')}")
                st.markdown("---")
                st.markdown(post_result.get('content', ''))
                st.markdown("---")
                st.markdown(f"**🏷️ Hashtag:** `{post_result.get('hashtag', '')}`")
                st.markdown(f"**💬 Call To Action (CTA):** {post_result.get('cta', '')}")

            st.divider()

            # --- NÚT ĐĂNG BÀI TỰ ĐỘNG LÊN BINANCE SQUARE ---
            st.markdown("### 🚀 Xuất bản tự động")
            if st.button("📤 Tự động đăng bài lên Binance Square", type="secondary", use_container_width=True):
                with st.spinner("Đang kết nối API và đẩy bài viết lên Binance Square..."):
                    # Gọi trực tiếp module đăng bài tự động
                    publish_res = BinancePublisher.publish_post(
                        title=post_result.get('title', ''),
                        content=post_result.get('content', ''),
                        hashtag=post_result.get('hashtag', ''),
                        cta=post_result.get('cta', '')
                    )

                    if publish_res.get("success"):
                        st.success(f"✅ {publish_res.get('message', 'Đăng bài thành công!')}")
                        st.balloons()
                    else:
                        st.error(f"❌ Đăng bài thất bại: {publish_res.get('error')}")

            if st.session_state.chart_result and st.session_state.chart_result.get("success"):
                st.info("💡 **Mẹo:** Bạn có thể nhấn chuột phải vào ảnh biểu đồ phía trên chọn **Lưu ảnh (Save image as)** nếu muốn tải về lưu trữ hoặc dùng kèm thủ công.")
        else:
            error_detail = post_result.get("error", "Lỗi không xác định") if post_result else "Lỗi kết nối AI"
            st.error(f"❌ Lỗi tạo nội dung: {error_detail}")

if __name__ == "__main__":
    main()