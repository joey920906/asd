import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

# --- 1. 檔案讀寫邏輯 ---
SAVE_FILE = "my_assets_v3.json"
DEFAULT_STOCKS = {
    "2377.TW": [114.0, 1000, "微星"],
    "00919.TW": [25.0, 5000, "群益台灣精選高息"]
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

if 'assets' not in st.session_state:
    st.session_state.assets = load_stocks()

# --- 2. 趨勢選股邏輯函數 ---
AI_STOCK_POOL = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2382.TW": "廣達", 
    "2308.TW": "台達電", "3231.TW": "緯創", "2376.TW": "技嘉",
    "6669.TW": "緯穎", "2454.TW": "聯發科", "2377.TW": "微星"
}

def scan_trending_stocks(stock_pool):
    recommendations = []
    for sid, name in stock_pool.items():
        try:
            df = yf.download(sid, period="60d", progress=False, auto_adjust=True)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            curr_p = float(df['Close'].iloc[-1])
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            ma60 = float(df['Close'].rolling(60).mean().iloc[-1])
            is_bullish = curr_p > ma20 > ma60
            is_not_overheated = (curr_p - ma20) / ma20 < 0.05
            if is_bullish:
                recommendations.append({
                    "代號": sid, "名稱": name, "目前價格": round(curr_p, 1),
                    "狀態": "🌟 剛起漲" if is_not_overheated else "🔥 已衝高",
                    "建議": "適合關注" if is_not_overheated else "等拉回再說"
                })
        except: continue
    return recommendations

# --- 3. 介面設定 ---
st.set_page_config(page_title="懶人投資助手", layout="wide")
st.title("💰 我的自動化資產儀表板")

# 使用 Tabs 區分功能
tab_stock, tab_radar = st.tabs(["📊 我的庫存管理", "🚀 AI 趨勢選股"])

# --- 側邊欄控制 (兩邊共用) ---
st.sidebar.header("📂 庫存管理")
with st.sidebar.expander("➕ 新增/更新持股"):
    symbol = st.text_input("輸入股票代號 (如: 2330.TW)").strip().upper()
    cost = st.number_input("買入單價", min_value=0.0, step=0.1)
    shares = st.number_input("持有股數", min_value=0, step=100)
    if st.button("確認加入"):
        if symbol:
            ticker = yf.Ticker(symbol)
            name = ticker.info.get('shortName', symbol)
            st.session_state.assets[symbol] = [cost, shares, name]
            save_stocks(st.session_state.assets)
            st.success(f"已加入 {name}")
            st.rerun()

with st.sidebar.expander("🗑️ 刪除標的"):
    del_id = st.selectbox("選擇要刪除", list(st.session_state.assets.keys()))
    if st.button("確認刪除"):
        del st.session_state.assets[del_id]
        save_stocks(st.session_state.assets)
        st.rerun()

# --- 分頁內容：我的庫存 ---
with tab_stock:
    if st.session_state.assets:
        selected_id = st.selectbox("📈 選擇查看標的", list(st.session_state.assets.keys()))
        my_cost, my_shares, my_name = st.session_state.assets[selected_id]
        
        d_df = yf.download(selected_id, period="1y", auto_adjust=True, progress=False)
        if isinstance(d_df.columns, pd.MultiIndex): d_df.columns = d_df.columns.get_level_values(0)
        
        if not d_df.empty:
            curr_p = float(d_df['Close'].iloc[-1])
            ma20 = float(d_df['Close'].rolling(20).mean().iloc[-1])
            
            # 計算損益
            total_cost = my_cost * my_shares
            profit_amt = (curr_p - my_cost) * my_shares
            profit_pct = (profit_amt / total_cost * 100) if total_cost > 0 else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("目前股價", f"{curr_p:.2f}")
            c2.metric("我的成本", f"{my_cost:.2f}")
            c3.metric("總損益 (NTD)", f"{profit_amt:,.0f}", delta=f"{profit_pct:.2f}%")

            st.divider()
            st.markdown("### 💡 AI 投資大白話建議")
            if my_cost > 0:
                if profit_pct < -10:
                    st.error(f"⚠️ 跌得有點痛了 (虧損 {profit_pct:.1f}%)！如果買入理由消失，別跟錢過不去，該撤就撤。")
                elif profit_pct > 20:
                    st.success(f"🎉 賺很大喔 (獲利 {profit_pct:.1f}%)！分批放口袋，剩下的讓它飛。")
                elif curr_p > ma20:
                    st.info("💪 目前穩穩站在月線上，建議繼續抱著不用急。")
                else:
                    st.warning("🧐 最近股價有點軟，先觀察就好，不要急著加碼。")

            fig = go.Figure(data=[go.Candlestick(x=d_df.index, open=d_df['Open'], high=d_df['High'], low=d_df['Low'], close=d_df['Close'], name='K線')])
            if my_cost > 0: fig.add_hline(y=my_cost, line_dash="dash", line_color="red", annotation_text="你的成本")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("目前庫存空空的，請從側邊欄新增股票！")

# --- 分頁內容：趨勢選股 ---
with tab_radar:
    st.header("🤖 AI 產業趨勢掃描器")
    st.write("自動篩選目前處於多頭排列（月線 > 季線）的熱門 AI 股。")
    if st.button("🔄 開始掃描最新趨勢"):
        with st.spinner('分析中...'):
            results = scan_trending_stocks(AI_STOCK_POOL)
            if results:
                st.table(pd.DataFrame(results))
                st.success("以上標的目前技術面較強，可挑選「剛起漲」的優先關注。")
            else:
                st.info("目前 AI 池中沒有標的符合起漲條件，建議再等等。")
