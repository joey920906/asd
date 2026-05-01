import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 1. 頁面標題與佈局
st.set_page_config(page_title="Threads 穿搭分潤產生器", layout="wide")
st.title("🧵 Threads 穿搭分潤文案 + 財務試算助手")

# 2. 側邊欄：分潤帳號與財務設定
with st.sidebar:
    st.header("🔑 帳號與財務設定")
    aff_id = st.text_input("偵測到的分潤 ID", placeholder="自動提取中...")
    
    st.divider()
    st.subheader("📊 財務參數")
    # 預估比例設定
    est_commission = st.select_slider(
        "預估分潤比例 (%)",
        options=[1, 2, 4, 7, 10, 15, 20],
        value=7
    )
    est_conversion = st.number_input("預期轉單數 (件)", value=5)

# 3. 商品資訊提取函式
def get_shopee_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 抓取 Meta 標籤
        title = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else "抓取失敗，請手動輸入"
        image = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None
        return title, image
    except:
        return None, None

# 4. 主畫面輸入區
target_url = st.text_input("🔗 貼上你的蝦皮分潤連結", placeholder="https://s.shopee.tw/...")

if st.button("🚀 一鍵分析並產出矩陣文案"):
    if target_url:
        with st.spinner('正在破解商品內容與計算收益...'):
            title, img_url = get_shopee_info(target_url)
            
            # 佈局：左邊預覽與財務，右邊文案
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.subheader("🖼️ 商品內容預覽")
                if img_url:
                    st.image(img_url, use_column_width=True)
                else:
                    st.error("⚠️ 無法讀取圖片內容，請手動確認連結正確性")
                
                st.info(f"**偵測商品：** {title if title else '讀取中...'}")
                
                # 收益試算 (會計應用)
                st.subheader("💰 預期收益分析")
                price = 600  # 預設模擬單價
                revenue = price * est_conversion
                profit = revenue * (est_commission / 100)
                
                st.metric("預估總成交額", f"${revenue:,.0f}")
                st.metric("預估純利潤", f"${profit:,.0f}", delta=f"利潤率 {est_commission}%")

            with col2:
                st.subheader("📝 Threads 矩陣排版文案")
                # AI 風格聯想邏輯
                keywords = ["美式復古", "工裝寬鬆", "山系穿搭"]
                
                final_post = f"這就是我一直在找的那條「神褲」吧... 🛹\n最近真的被燒到不行，版型意外超顯腿長！\n\n"
                final_post += f"• 主推款式：{title[:20]}...\n🛒 {target_url}\n\n"
                final_post += "💡 相似風格建議同步搜尋：\n"
                for kw in keywords:
                    final_post += f"• {kw} 系列\n"
                
                st.code(final_post, language="text")
                st.success("✅ 文案已就緒，建議搭配商品實拍圖發布點擊率最高！")

    else:
        st.warning("請先輸入連結內容。")
