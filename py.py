import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import openai

# 1. 初始化頁面
st.set_page_config(page_title="Threads 穿搭分潤產生器", layout="wide")
st.title("🧵 Threads 穿搭分潤文案 + 收益計算助手")

# 2. 側邊欄設定
with st.sidebar:
    st.header("🔑 帳號設定")
    api_key = st.text_input("OpenAI API Key", type="password")
    # 分潤比例設定（會計/財管應用）
    commission_rate = st.slider("預估分潤比例 (%)", 1.0, 20.0, 7.0)
    
    affiliate_url = st.text_input("輸入任一你的分潤短連結 (提取 ID)")
    if affiliate_url:
        try:
            # 嘗試解析 ID
            res = requests.get(affiliate_url, allow_redirects=True, timeout=5)
            found_id = re.search(r'smtt=([^&]+)', res.url)
            if found_id:
                st.session_state.aff_id = found_id.group(1)
                st.success(f"已識別分潤 ID: {st.session_state.aff_id}")
        except:
            st.error("解析失敗，請手動輸入")

# 3. 核心功能：抓取蝦皮資料
def fetch_shopee_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://shopee.tw/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 抓取 OG 標籤（這是最容易抓到圖片跟標題的地方）
        title = soup.find("meta", property="og:title")["content"] if soup.find("meta", property="og:title") else "未知商品"
        image = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None
        return title, image
    except Exception as e:
        return f"錯誤: {str(e)}", None

# 4. 主畫面介面
target_link = st.text_input("🔗 貼上你想推廣的蝦皮商品連結")

if st.button("🚀 生成矩陣文案與財務預估"):
    if not target_link:
        st.warning("請先貼上連結")
    else:
        with st.spinner('正在分析商品資料...'):
            title, img_url = fetch_shopee_data(target_link)
            
            # 5. 顯示結果佈局
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🖼️ 商品預覽")
                if img_url:
                    st.image(img_url, width=300)
                else:
                    st.info("⚠️ 圖片受保護無法直接抓取，建議手動截圖。")
                st.write(f"**商品標題:** {title}")

            with col2:
                st.subheader("💰 財務與分潤預估")
                # 模擬商品單價
                est_price = st.number_input("商品單價 (TWD)", value=500)
                est_sales = st.number_input("預期轉單數 (件)", value=10)
                
                # 計算收益（結合會計觀念）
                total_revenue = est_price * est_sales
                estimated_profit = total_revenue * (commission_rate / 100)
                
                st.metric("預計總成交額", f"${total_revenue:,.0f}")
                st.metric("預計純收益", f"${estimated_profit:,.0f}", delta=f"{commission_rate}%")

            st.divider()
            
            # 6. 生成文案 (Threads 格式)
            st.subheader("📝 Threads 推薦文案預覽")
            
            # 這裡可以加入 AI 關鍵字處理
            keywords = title.split()[:3] # 簡單取前三個詞作為關鍵字
            
            post_content = f"這就是我一直在找的那條「神褲」吧... 🛹\n最近真的被燒到不行，版型意外超顯腿長！\n\n"
            post_content += f"• 主打單品：{title[:20]}...\n🛒 {target_link}\n\n"
            post_content += "💡 相似風格推薦：\n• 美式復古工裝系列\n• 垂墜感降落傘褲\n• 街頭水洗直筒褲"
            
            st.code(post_content, language="text")
            st.info("建議：點擊連結後，在蝦皮搜尋上方『相似風格』關鍵字，即可找到更多相似商品來豐富你的矩陣！")
