import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

# --- 1. 檔案讀寫邏輯 (包含成本數據) ---
SAVE_FILE = "my_stocks_v2.json"
# 預設清單格式：{"名稱": ["代號", 買入成本]}，0 代表未持有
DEFAULT_STOCKS = {
    "台積電": ["2330.TW", 0],
    "元大台灣50": ["0050.TW", 0],
    "微星科技": ["2377.TW", 114.0], # 這裡預設填入你的成本
    "群益台灣精選高息": ["00919.TW", 0]
}

def load_stocks():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return DEFAULT_STOCKS
    return DEFAULT_STOCKS

def save_stocks(stocks):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=4)

if 'stock_list' not in st.session_state:
    st.session_state.stock_list = load_stocks()

# --- 2. 介面設定 ---
st.set_page_config(page_title="投資與損益監控儀表板", layout="wide")
st.title("🚀 個人投資與損益監控")

# --- 3. 側邊欄：進階管理器 ---
st.sidebar.header("🛠️ 資產管理器")

with st.sidebar.expander("➕ 新增/更新持股"):
    new_name = st.text_input("股票名稱").strip()
    new_id = st.text_input("代號 (如: 2317.TW)").strip()
    new_cost = st.number_input("買入成本 (若未持有請填 0)", min_value=0.0, step=0.1)
    if st.button("儲存標的"):
        if new_name and new_id:
            st.session_state.stock_list[new_name] = [new_id, new_cost]
            save_stocks(st.session_state.stock_list)
            st.success(f"已更新 {new_name}")
            st.rerun()

with st.sidebar.expander("🗑️ 刪除標的"):
    del_name = st.selectbox("選擇要刪除的標的", list(st.session_state.stock_list.keys()))
    if st.button("確認刪除"):
        del st.session_state.stock_list[del_name]
        save_stocks(st.session_state.stock_list)
        st.rerun()

st.sidebar.divider()
selected_name = st.sidebar.selectbox("📈 選擇查看標的", list(st.session_state.stock_list.keys()))
stock_id, my_cost = st.session_state.stock_list[selected_name]

# --- 4. 數據處理與顯示 ---
@st.cache_data(ttl=3600)
def load_data(symbol):
    data = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = load_data(stock_id)

if not df.empty:
    current_price = float(df['Close'].iloc[-1])
    df['MA20'] = df['Close'].rolling(window=20).mean()
    ma20_val = float(df['MA20'].iloc[-1])

    # --- 核心邏輯：損益與賣出判斷 ---
    st.subheader(f"目前查看：{selected_name} ({stock_id})")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("當前市價", f"{current_price:.2f}")
    
    if my_cost > 0:
        profit_pct = (current_price - my_cost) / my_cost * 100
        m2.metric("我的成本", f"{my_cost:.2f}")
        m3.metric("目前損益", f"{profit_pct:.2f}%", delta=f"{profit_pct:.2f}%")
        
        # 賣出/持有評估
        st.write("---")
        st.markdown("### 🏹 持倉策略建議")
        
        if profit_pct > 20:
            st.warning(f"💰 獲利已達 {profit_pct:.1f}%！建議可先「分批入袋」落袋為安。")
        elif profit_pct < -10:
            st.error(f"🚨 虧損達 {profit_pct:.1f}%。請檢視基本面，若破線建議執行停損。")
        elif current_price > ma20_val:
            st.success("💪 股價仍高於月線且處於獲利狀態，建議「持續持有」享受波段。")
        else:
            st.info("🕒 目前股價震盪中，若未破關鍵支撐建議先行持有觀察。")
    else:
        m2.metric("我的成本", "未輸入")
        st.info("💡 你可以在左側選單輸入買入成本，程式將自動計算損益與賣出建議。")

    # K線圖
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線')])
    if my_cost > 0:
        fig.add_hline(y=my_cost, line_dash="dash", line_color="red", annotation_text="我的成本線")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("數據獲取失敗。")
