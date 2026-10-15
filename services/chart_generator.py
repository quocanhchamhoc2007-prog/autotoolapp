import logging
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

logger = logging.getLogger(__name__)

class ChartGenerator:
    @staticmethod
    def fetch_binance_klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100) -> pd.DataFrame:
        """
        Lấy dữ liệu nến thực tế theo thời gian thực từ Binance Public API.
        """
        # Chuẩn hóa tên symbol (VD: BTC -> BTCUSDT)
        formatted_symbol = symbol.upper().replace("$", "").strip()
        if not formatted_symbol.endswith("USDT"):
            formatted_symbol += "USDT"

        url = f"https://api.binance.com/api/v3/klines?symbol={formatted_symbol}&interval={interval}&limit={limit}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Chuyển đổi dữ liệu Binance sang Pandas DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['open'] = df['open'].astype(float)
            df['volume'] = df['volume'].astype(float)

            return df
        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu từ Binance API cho {formatted_symbol}: {e}")
            return pd.DataFrame()

    @staticmethod
    def generate_chart(symbol: str = "BTC", output_path: str = "latest_chart.png") -> dict:
        """
        Vẽ biểu đồ giá thực tế kèm MA20 và Volume, lưu thành file ảnh.
        """
        clean_symbol = symbol.upper().replace("$", "").strip()
        df = ChartGenerator.fetch_binance_klines(clean_symbol)

        if df.empty:
            return {"success": False, "error": f"Không lấy được dữ liệu nến cho {clean_symbol}"}

        try:
            # Tính chỉ số kỹ thuật cơ bản (MA20)
            df['MA20'] = df['close'].rolling(window=20).mean()

            # Khởi tạo khung vẽ Matplotlib
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            fig.patch.set_facecolor('#1e222d') # Màu nền tối chuẩn Binance
            
            # Style đường giá và MA20
            ax1.set_facecolor('#1e222d')
            ax1.plot(df['open_time'], df['close'], color='#26a69a', linewidth=1.8, label=f'{clean_symbol}/USDT Price')
            ax1.plot(df['open_time'], df['MA20'], color='#ff9800', linewidth=1.2, linestyle='--', label='MA (20)')
            
            latest_price = df['close'].iloc[-1]
            ax1.set_title(f"Binance Live Technical Chart - {clean_symbol}/USDT (${latest_price:,.2f})", color='#ffffff', fontsize=14, pad=12)
            ax1.tick_params(colors='#b2b5be')
            ax1.grid(True, color='#2a2e39', linestyle=':', alpha=0.6)
            ax1.legend(loc='upper left', facecolor='#2a2e39', edgecolor='none', labelcolor='#ffffff')

            # Style khối lượng giao dịch (Volume)
            ax2.set_facecolor('#1e222d')
            colors = ['#26a69a' if df['close'].iloc[i] >= df['open'].iloc[i] else '#ef5350' for i in range(len(df))]
            ax2.bar(df['open_time'], df['volume'], color=colors, alpha=0.7, width=0.03)
            ax2.set_ylabel("Volume", color='#b2b5be')
            ax2.tick_params(colors='#b2b5be')
            ax2.grid(True, color='#2a2e39', linestyle=':', alpha=0.6)

            # Định dạng trục thời gian
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            fig.autofmt_xdate()
            plt.tight_layout()

            # Lưu file ảnh biểu đồ
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close()

            return {
                "success": True,
                "chart_path": output_path,
                "latest_price": latest_price,
                "summary": f"Live Market Data: {clean_symbol}/USDT - Giá hiện tại: ${latest_price:,.2f}"
            }
        except Exception as e:
            logger.exception("Lỗi khi vẽ biểu đồ:")
            return {"success": False, "error": str(e)}