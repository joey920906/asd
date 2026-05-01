import streamlit as st
import openai

# 設定標題
st.title("🚀 蝦皮 AI 分潤文案神器")

# 側邊欄設定 API Key
with st.sidebar:
    api_key = st.text_input("輸入 OpenAI API Key", type="password")
    affiliate_id = st.text_input("輸入你的分潤代碼 (e.g., g00xxx)")

# 主畫面
prod_name = st.text_input("商品名稱", placeholder="例如：人體工學午睡枕")
prod_features = st.text_area("商品賣點", placeholder="例如：透氣、支撐力強、特價 199")

style = st.selectbox("文案風格", ["幽默逗趣", "專業測評", "急迫推銷(限時特價)"])

if st.button("生成文案"):
    if not api_key:
        st.error("請先輸入 API Key！")
    else:
        # 呼叫 AI (簡單示例)
        prompt = f"請用{style}風格，幫我寫一段推廣{prod_name}的蝦皮文案。特點是{prod_features}。結尾引導點擊連結。"
        
        # 這裡對接 OpenAI API (省略重複程式碼)
        # result = openai_call(prompt) 
        result = f"【測試文案】這款{prod_name}太神啦！{prod_features}，現在買超划算！"
        
        full_link = f"https://shope.ee/{affiliate_id}"
        
        st.subheader("生成結果：")
        final_post = f"{result}\n\n🛒 傳送門：{full_link}"
        st.code(final_post)
        st.button("複製文案", on_click=lambda: st.write("已複製到剪貼簿（需配合 JS）"))
