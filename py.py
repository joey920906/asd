import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 設定標的
STOCKS = {
    "台積電 (2330)": "2330.TW",
    "元大台灣50 (0050)": "0050.TW",
    "元大高股息 (0056)": "0056.TW",
    "國泰永續高股息 (00878)": "00878.TW",
    "群益台灣精選高息 (00919)": "00919.TW"
}

st.set_page_config(page_title="台股自動評估儀表板", layout="wide")
st.title("📊 專業投資評估儀表板")

selected_name = st.sidebar.selectbox("請選擇關注標的", list(STOCKS.keys()))
stock_id = STOCKS[selected_name]

# 抓取數據 (加入 auto_adjust=True 避免價格分裂問題)
@st.cache_data(ttl=3600)
def load_data(symbol):
    data = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
    # 修正 Multi-index 問題，只取 Close 欄位
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = load_data(stock_id)

if not df.empty:
    # 計算技術指標
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    # 確保抓到的是單一數值 (.item() 或 float)
    current_price = float(df['Close'].iloc[-1])
    ma20_val = float(df['MA20'].iloc[-1])
    ma60_val = float(df['MA60'].iloc[-1])

    # --- 進場評估邏輯 (針對 ETF 與權值股優化) ---
    def evaluate_status(price, m20, m60):
        # 邏輯 1：均線多頭排列
        if price > m20 > m60:
            return "🔥 強勢多頭", "股價在均線之上，適合順勢操作。", "green"
        # 邏輯 2：乖離率過大 (短線過熱)
        elif price > m20 * 1.08:
            return "⚠️ 短線過熱", "股價遠離月線，建議等拉回再買。", "orange"
        # 邏輯 3：跌深反彈機會 (適合 00878/00919 等收息股)
        elif price < m20 * 0.96:
            return "✅ 價值區間", "股價低於月線，對長期配息投資者來說是相對便宜點。", "blue"
        else:
            return "😴 橫盤整理", "目前無明顯趨勢，建議分批定期定額。", "grey"

    status, advice, color_code = evaluate_status(current_price, ma20_val, ma60_val)

    # 儀表板顯示
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label=f"{selected_name} 當前價格", value=f"{current_price:.2f} TWD")
        st.markdown(f"### 狀態：:{color_code}[{status}]")
        st.info(advice)
        
        # 額外小提示：如果是高股息 ETF
        if "00" in selected_name:
            st.caption("💡 提示：高股息 ETF 建議參考『殖利率』，除息後的貼息區間通常是好買點。")

    with col2:
        # K 線圖
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='K線'
        )])
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='月線(20MA)', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name='季線(60MA)', line=dict(color='blue')))
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("無法取得數據，請檢查網路或代碼是否正確。")
