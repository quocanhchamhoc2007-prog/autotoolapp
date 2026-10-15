import os
import logging
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class StockChartService:
    @staticmethod
    def fetch_and_plot_stock(ticker_symbol: str) -> dict:
        """
        Lấy dữ liệu chứng khoán thực tế và vẽ biểu đồ kỹ thuật, trả về đường dẫn file ảnh.
        """
        try:
            # Chuẩn hóa mã cổ phiếu (Nếu người dùng nhập fpt, vic... tự động thêm .VN cho cổ phiếu Việt Nam nếu cần)
            symbol = ticker_symbol.strip().upper()
            if not symbol.endswith(".VN") and len(symbol) <= 4 and symbol.isalpha() and symbol not in ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA"]:
                # Mặc định thử thêm .VN nếu là mã ngắn viết hoa của Việt Nam
                symbol_vn = f"{symbol}.VN"
            else:
                symbol_vn = symbol

            logger.info(f"Đang tải dữ liệu tài chính cho mã: {symbol_vn}")
            
            # Lấy dữ liệu 3 tháng gần nhất để vẽ biểu đồ trực quan
            stock = yf.Ticker(symbol_vn)
            df = stock.history(period="3mo")
            
            if df.empty:
                # Thử lại với mã gốc nếu mã .VN không trả về dữ liệu
                stock = yf.Ticker(symbol)
                df = stock.history(period="3mo")
                symbol_vn = symbol
                if df.empty:
                    return {"success": False, "error": f"Không tìm thấy dữ liệu giao dịch cho mã '{ticker_symbol}'."}

            # Lấy thông tin giá mới nhất
            latest_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else latest_row
            current_price = latest_row['Close']
            price_change = current_price - prev_row['Close']
            percent_change = (price_change / prev_row['Close']) * 100

            # Vẽ biểu đồ kỹ thuật bằng Matplotlib
            plt.figure(figsize=(10, 5), dpi=100)
            plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
            
            plt.plot(df.index, df['Close'], label=f'Giá đóng cửa ({symbol_vn})', color='#1f77b4', linewidth=2)
            plt.title(f'Biểu đồ kỹ thuật thực tế - Mã: {symbol_vn} (Cập nhật: {datetime.now().strftime("%d/%m/%Y")})', fontsize=12, fontweight='bold')
            plt.xlabel('Thời gian', fontsize=10)
            plt.ylabel('Giá (VND/USD)', fontsize=10)
            plt.legend(loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.5)
            
            # Lưu file ảnh tạm thời
            os.makedirs("temp_images", exist_ok=True)
            img_path = f"temp_images/{symbol_vn}_chart.png"
            plt.savefig(img_path, bbox_inches='tight')
            plt.close()

            return {
                "success": True,
                "symbol": symbol_vn,
                "current_price": round(current_price, 2),
                "price_change": round(price_change, 2),
                "percent_change": round(percent_change, 2),
                "image_path": img_path,
                "market_data_summary": f"Mã: {symbol_vn}, Giá hiện tại: {round(current_price, 2)}, Biến động: {round(percent_change, 2)}%"
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu hoặc vẽ biểu đồ chứng khoán: {e}")
            return {"success": False, "error": str(e)}