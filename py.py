import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 頁面基本設定
st.set_page_config(page_title="蝦皮 Threads 自動化分潤助手", layout="wide")
st.title("🧵 Threads 穿搭分潤文案產生器")

# 側邊欄：分潤 ID 提取器
with st.sidebar:
    st.header("🔑 帳號設定")
    # 這裡實作你要求的自動提取 ID 功能
    affiliate_url = st.text_input("輸入任一你的分潤短連結（提取 ID 用）")
    if affiliate_url:
        try:
            res = requests.get(affiliate_url, allow_redirects=True, timeout=5)
            # 從跳轉後的網址抓取 smtt 或相關參數
            found_id = re.search(r'smtt=([^&]+)', res.url)
            if found_id:
                st.session_state.aff_id = found_id.group(1)
                st.success(f"偵測到分潤 ID: {st.session_state.aff_id}")
            else:
                st.session_state.aff_id = st.text_input("手動輸入分潤 ID")
        except:
            st.error("解析失敗，請手動輸入")

# 主介面
target_link = st.text_input("🔗 貼上你想推廣的原始商品連結")

if st.button("🚀 一鍵生成矩陣文案與圖片"):
    if target_link:
        with st.spinner('正在分析商品並搜尋相似單品...'):
            # 1. 抓取原始網頁內容 (簡化版模擬)
            # 注意：實際開發建議使用 Shopee Open API，直接爬蟲可能被擋
            st.info("系統正在根據關鍵字產出相似單品...")
            
            # 模擬 AI 產出的相似商品數據
            items = [
                {"name": "美式復古工裝", "link": target_link, "img": "https://via.placeholder.com/300", "desc": "刷色有質感，City Boy 必備。"},
                {"name": "寬鬆抽繩降落傘褲", "link": "https://s.shopee.tw/8ASaELasNe", "img": "https://via.placeholder.com/300", "desc": "褲腳抽繩設計，機能感拉滿。"},
                {"name": "水洗直筒寬褲", "link": "https://s.shopee.tw/2VoDTwwJsp", "img": "https://via.placeholder.com/300", "desc": "垂墜感極佳，視覺比例拉長。"}
            ]
            
            # 2. 顯示文案排版
            st.subheader("📝 Threads 文案預覽")
            post_content = f"這就是我一直在找的那條「神褲」吧... 🛹\n最近真的被燒到不行，版型意外超顯腿長！\n\n"
            for i, item in enumerate(items, 1):
                post_content += f"• {item['name']}\n{item['desc']}\n🛒 {item['link']}\n"
            
            st.code(post_content, language="text")
            
            # 3. 顯示圖片排版 (模擬 Threads 橫排顯示)
            st.subheader("🖼️ 推薦圖片 (可右鍵儲存)")
            cols = st.columns(3)
            for idx, col in enumerate(cols):
                col.image(items[idx]['img'], caption=items[idx]['name'], use_column_width=True)
                
    else:
        st.warning("請先輸入連結")
