import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 設定標的清單 (台股代號需加 .TW)
STOCKS = {
    "台積電 (2330)": "2330.TW",
    "元大台灣50 (0050)": "0050.TW",
    "元大高股息 (0056)": "0056.TW",
    "國泰永續高股息 (00878)": "00878.TW",
    "群益台灣精選高息 (00919)": "00919.TW"
}

st.title("📊 專業投資評估儀表板")

# 側邊欄：選擇標的
selected_name = st.sidebar.selectbox("請選擇關注標的", list(STOCKS.keys()))
stock_id = STOCKS[selected_name]

# 獲取數據
df = yf.download(stock_id, period="1y")

# --- 技術指標計算 ---
df['MA20'] = df['Close'].rolling(window=20).mean() # 月線
df['MA60'] = df['Close'].rolling(window=60).mean() # 季線

# --- 進場評估邏輯 (範例：均線糾結或突破) ---
current_price = df['Close'].iloc[-1]
ma20_val = df['MA20'].iloc[-1]

def evaluate_status(price, ma):
    if price > ma * 1.05:
        return "⚠️ 目前股價過高", "建議觀望，等待拉回", "inverse"
    elif price < ma * 0.95:
        return "✅ 股價處於相對低點", "適合分批佈局", "normal"
    else:
        return "🔵 區間震盪", "目前股價貼近均線，適合中長線持有", "normal"

status, advice, color = evaluate_status(current_price, ma20_val)

# --- 展示區域 ---
st.metric(label=f"{selected_name} 當前股價", value=f"{current_price:.2f} TWD")
st.subheader(f"進場評估：{status}")
st.info(advice)

# --- 繪製 K 線圖 ---
fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'],
    name='K線'
)])
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='20MA', line=dict(color='orange')))
fig.add_update_layout(xaxis_rangeslider_visible=False, title=f"{selected_name} 歷史走勢")
st.plotly_chart(fig, use_container_width=True)
