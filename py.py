import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

# --- 1. 檔案讀寫邏輯 (儲存你的清單) ---
SAVE_FILE = "my_stocks.json"
DEFAULT_STOCKS = {
    "台積電": "2330.TW",
    "元大台灣50": "0050.TW",
    "國泰永續高股息": "00878.TW",
    "群益台灣精選高息": "00919.TW"
}

def load_stocks():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_STOCKS

def save_stocks(stocks):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=4)

# 初始化 Session State
if 'stock_list' not in st.session_state:
    st.session_state.stock_list = load_stocks()

# --- 2. 介面設定 ---
st.set_page_config(page_title="自定義投資儀表板", layout="wide")

# --- 3. 側邊欄：標的管理器 ---
st.sidebar.title("🛠️ 標格管理器")

# 新增標的
with st.sidebar.expander("➕ 新增標的"):
    new_name = st.text_input("名稱 (如: 鴻海)", key="new_name")
    new_id = st.text_input("代號 (如: 2317.TW)", key="new_id")
    if st.button("確認新增"):
        if new_name and new_id:
            st.session_state.stock_list[new_name] = new_id
            save_stocks(st.session_state.stock_list)
            st.success(f"已新增 {new_name}")
            st.rerun()

# 刪除標的
with st.sidebar.expander("🗑️ 刪除標的"):
    del_name = st.selectbox("選擇要刪除的標的", list(st.session_state.stock_list.keys()))
    if st.button("確認刪除"):
        if len(st.session_state.stock_list) > 1:
            del st.session_state.stock_list[del_name]
            save_stocks(st.session_state.stock_list)
            st.warning(f"已刪除 {del_name}")
            st.rerun()
        else:
            st.error("至少需保留一個標的")

st.sidebar.divider()

# 選擇目前要查看的標的
selected_name = st.sidebar.selectbox("📈 選擇查看標的", list(st.session_state.stock_list.keys()))
stock_id = st.session_state.stock_list[selected_name]

# --- 4. 數據抓取與顯示 (維持之前的修正版邏輯) ---
@st.cache_data(ttl=3600)
def load_data(symbol):
    data = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

st.title(f"📊 {selected_name} ({stock_id}) 投資評估")

df = load_data(stock_id)

if not df.empty:
    # 指標計算
    df['MA20'] = df['Close'].rolling(window=20).mean()
    current_price = float(df['Close'].iloc[-1])
    ma20_val = float(df['MA20'].iloc[-1])

    # 顯示儀表板內容 (這部分可延用之前的評估邏輯)
    st.metric("目前股價", f"{current_price:.2f} TWD")
    
    # K線圖
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name='K線'
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='月線', line=dict(color='orange')))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("抓取失敗，請確認代號格式是否正確 (台股須加 .TW)")
