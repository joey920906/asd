import streamlit as st
import openai

import requests
import re

def get_affiliate_id(short_url):
    try:
        # 模擬點擊連結，抓取跳轉後的最後一個網址
        response = requests.get(short_url, allow_redirects=True, timeout=5)
        final_url = response.url
        
        # 蝦皮通常會在網址參數中帶入分潤相關 ID (例如 sub_id 或 smtt)
        # 這裡我們用正則表達式來抓取可能是 ID 的部分
        # 註：具體參數名稱會隨蝦皮更新變動，建議先顯示 final_url 確認
        match = re.search(r'smtt=([^&]+)', final_url)
        if match:
            return match.group(1)
        else:
            return "無法解析 ID，請手動確認"
    except Exception as e:
        return f"解析失敗: {str(e)}"
        
# 頁面標題與設定
st.set_page_config(page_title="蝦皮 AI 分潤助手", layout="centered")
st.title("🛒 蝦皮分潤內容自動化產生器")

# 側邊欄設定
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("輸入 OpenAI API Key", type="password")
    affiliate_id = st.text_input("輸入你的分潤帳號 ID")

# 主要輸入區
input_link = st.text_input("1. 貼上你的蝦皮分潤連結", placeholder="https://s.shopee.tw/...")
raw_context = st.text_area("2. 補充商品資訊（若能貼上商品標題更好）", placeholder="例如：美式復古工裝褲 男生寬鬆直筒...")

# 模式選擇
mode = st.radio("3. 選擇推廣模式", ["分享好物 (推薦感強)", "使用者實際推薦 (真實心得感)"])

if st.button("✨ 開始生成文案與建議"):
    if not api_key or not affiliate_id:
        st.warning("請確保側邊欄的 API Key 和 分潤 ID 已填寫。")
    else:
        # 第一階段：AI 提取關鍵字與分析
        extract_prompt = f"請根據以下資訊，提取出該商品的 3 個核心風格關鍵字，並根據這些關鍵字列出 2 種『同類型但不同設計』的相關商品描述：\n資訊：{raw_context if raw_context else input_link}"
        
        # 這裡假設調用 AI (模擬結果)
        # 實際應用時請解除下方的 API 調用註釋
        # client = openai.OpenAI(api_key=api_key)
        # response = client.chat.completions.create(...)
        
        keywords = "美式復古、工裝寬鬆、垂墜感" # 模擬提取結果
        similar_items = "1. 重磅水洗帆布褲\n2. 側邊大口袋機能褲" # 模擬相關物品
        
        # 第二階段：根據模式生成文案
        if mode == "分享好物 (推薦感強)":
            style_desc = "語氣要充滿驚喜、推薦感，多用 Emoji，強調 CP 值。"
        else:
            style_desc = "語氣要誠懇、像真實開箱心得，強調穿上去的具體感受（如版型、修飾度）。"
            
        post_prompt = f"使用{style_desc}撰寫一段 Threads 文案。關鍵字：{keywords}。連結位置：{input_link}"
        
        # 顯示結果
        st.divider()
        st.subheader("💡 系統提取關鍵字")
        st.write(f"`{keywords}`")
        
        st.subheader("🔍 建議可尋找的類似物品")
        st.info(similar_items)
        
        st.subheader("📝 生成文案 (Threads 專用)")
        final_post = f"【AI 生成文案】\n這款真的必入！{keywords}風格完全是我的菜...\n(文案內容依據模式調整中...)\n\n🛒 傳送門：{input_link}"
        st.code(final_post, language="text")
        st.button("📋 點擊複製文案 (模擬)")
