import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

# --- 1. 檔案讀寫邏輯 (格式：{代號: [成本, 股數, 名稱]}) ---
SAVE_FILE = "my_assets_v3.json"
DEFAULT_STOCKS = {
    "2377.TW": [114.0, 1000, "微星"],
    "00919.TW": [25.0, 5000, "群益台灣精選高息"]
}

def load_stocks():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_STOCKS

def save_stocks(stocks):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=4)

if 'assets' not in st.session_state:
    st.session_state.assets = load_stocks()

# --- 2. 介面設定 ---
st.set_page_config(page_title="懶人投資助手", layout="wide")
st.title("💰 我的自動化資產儀表板")

# --- 在 app.py 的 title 下方加入這行 ---
tab1, tab2 = st.tabs(["📊 我的庫存", "🚀 AI 選股推薦"])

with tab1:
    # 這裡放原本 app.py 的庫存代碼
    # (即你截圖中看到的內容)

# --- 3. 側邊欄：簡化版管理 (只輸代號) ---
st.sidebar.header("📂 庫存管理")

with st.sidebar.expander("➕ 新增/更新持股"):
    symbol = st.text_input("輸入股票代號 (如: 2330.TW)").strip().upper()
    cost = st.number_input("買入單價", min_value=0.0, step=0.1)
    shares = st.number_input("持有股數 (1張=1000股)", min_value=0, step=100)
    
    if st.button("確認加入"):
        if symbol:
            with st.spinner('正在查詢名稱...'):
                ticker = yf.Ticker(symbol)
                # 抓取簡稱，抓不到就用代號代替
                name = ticker.info.get('shortName', symbol)
                st.session_state.assets[symbol] = [cost, shares, name]
                save_stocks(st.session_state.assets)
                st.success(f"已加入 {name}")
                st.rerun()

with st.sidebar.expander("🗑️ 刪除標的"):
    del_id = st.selectbox("選擇要刪除的標的", list(st.session_state.assets.keys()))
    if st.button("確認刪除"):
        del st.session_state.assets[del_id]
        save_stocks(st.session_state.assets)
        st.rerun()

st.sidebar.divider()
selected_id = st.sidebar.selectbox("📈 選擇查看標的", list(st.session_state.assets.keys()))
my_cost, my_shares, my_name = st.session_state.assets[selected_id]

# --- 4. 數據處理與顯示 ---
@st.cache_data(ttl=600)
def fetch_data(sid):
    d = yf.download(sid, period="1y", auto_adjust=True)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d

df = fetch_data(selected_id)

if not df.empty:
    curr_p = float(df['Close'].iloc[-1])
    ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
    
    st.subheader(f"{my_name} ({selected_id})")

    # 計算損益
    total_cost = my_cost * my_shares
    total_value = curr_p * my_shares
    profit_amt = total_value - total_cost
    profit_pct = (profit_amt / total_cost * 100) if total_cost > 0 else 0

    # 頂部指標
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("目前股價", f"{curr_p:.2f}")
    c2.metric("持倉成本", f"{my_cost:.2f}")
    c3.metric("總損益 (NTD)", f"{profit_amt:,.0f}", delta=f"{profit_pct:.2f}%")
    c4.metric("目前價值", f"{total_value:,.0f}")

    # --- 升級版白話建議 ---
    st.divider()
    st.markdown("### 💡 AI 投資大白話建議")
    
    if my_cost > 0:
        if profit_pct < -10:
            st.error(f"⚠️ 跌得有點痛了 (虧損 {profit_pct:.1f}%)！如果當初買入的理由不見了，建議考慮停損，別跟錢過不去。")
        elif profit_pct > 20:
            st.success(f"🎉 賺很大喔 (獲利 {profit_pct:.1f}%)！可以考慮先賣掉一點點放口袋，剩下的繼續讓它跑。")
        elif curr_p > ma20:
            st.info("💪 目前走勢還算強，股價穩穩站在月線上面，建議繼續抱著不用急。")
        else:
            st.warning("🧐 最近股價有點軟，雖然還沒大虧，但建議多觀察，先不要加碼。")
    else:
        st.info("你目前只是觀察這檔股票，還沒有輸入買入成本喔！")

    # K線圖加上成本線
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線')])
    if my_cost > 0:
        fig.add_hline(y=my_cost, line_dash="dash", line_color="red", annotation_text="你的買入價")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("代號輸入錯誤，請確認。")
with tab2:
    # 這裡放原本在選股頁面的代碼
    st.header("選股")
    # ...

