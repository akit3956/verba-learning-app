import streamlit as st
import google.generativeai as genai
import time
import os
import emoji

# --- Page Config ---
st.set_page_config(page_title="Verba: 90秒 UX プロトタイプ", page_icon="✨")

# --- System Prompt (Miss Kaplan) ---
MISS_KAPLAN_PROMPT = """
あなたはVerbaの専属日本語チューター「Miss Kaplan」です。
ユーザーは日本語を学び始めたばかりの外国人（JLPT N5-N4レベル）です。

【至上命題：Magic Momentの創出】
ユーザーの入力に文法ミス、不自然な日本語、タイポ（例：「今日は〜ている を学びたい」）があっても、絶対に否定や訂正から入らないでください。
まずはユーザーの「意図」を完璧に汲み取り、「〇〇ですね！そこに気付けるなんてセンスがあります！」「素晴らしい着眼点です！」と全力で肯定・称賛してください。
ユーザーが「自分の拙い日本語でも通じた！AIが自分を理解してくれた！」と感動する体験を提供することが最大の目的です。

【出力ルール（15〜45秒フェーズ用）】
1. ユーザーの意図を120%肯定・称賛する（1〜2文）。
2. リクエストされた文法・単語の「超短い解説」を行う。
3. すぐに使える自然な「例文」を3つ提示する。
4. 最後に、ユーザーが短く答えられるクイズや問いかけをしてターンを返す。
5. 感情表現豊かな絵文字を積極的に使用する。
"""

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_reply_length" not in st.session_state:
    st.session_state.user_reply_length = []
if "emoji_count" not in st.session_state:
    st.session_state.emoji_count = 0
if "total_chars" not in st.session_state:
    st.session_state.total_chars = 0

# --- KPI Tracking Function ---
def track_kpi(user_text):
    char_len = len(user_text)
    st.session_state.user_reply_length.append(char_len)
    st.session_state.total_chars += char_len
    
    # Count emojis
    st.session_state.emoji_count += emoji.emoji_count(user_text)
    
    # Calculate KPIs
    avg_len = sum(st.session_state.user_reply_length) / len(st.session_state.user_reply_length)
    emoji_ratio = st.session_state.emoji_count / st.session_state.total_chars if st.session_state.total_chars > 0 else 0
    return avg_len, emoji_ratio

# --- UI Setup ---
st.title("✨ Verba 90秒UX プロトタイプ")
st.caption("揺らぎ全肯定AIチューター「Miss Kaplan」とKPIトラッキングの実機テスト")

# API Key Check
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # Gemini 2.5 Flash
    model = genai.GenerativeModel('models/gemini-2.5-flash', system_instruction=MISS_KAPLAN_PROMPT)

    # Sidebar KPI Display
    with st.sidebar:
        st.subheader("📊 感情的リテンション KPI")
        if st.session_state.user_reply_length:
            avg = sum(st.session_state.user_reply_length) / len(st.session_state.user_reply_length)
            ratio = st.session_state.emoji_count / st.session_state.total_chars
            st.metric("平均返信文字数 (熱量)", f"{avg:.1f} 文字")
            st.metric("絵文字出現率 (感情)", f"{ratio*100:.1f} %")
        else:
            st.write("まだ入力がありません。")

        if st.button("セッションをリセット"):
            st.session_state.messages = []
            st.session_state.user_reply_length = []
            st.session_state.emoji_count = 0
            st.session_state.total_chars = 0
            st.rerun()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Miss Kaplanに話しかけてみよう！（わざとタイポを入れてみてください）"):
        # Track KPI
        track_kpi(prompt)
        
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response with Safety Timeout Mock
        with st.chat_message("assistant"):
            placeholder = st.empty()
            
            # Start timer for timeout safety
            start_time = time.time()
            
            # Construct chat history for Gemini
            chat = model.start_chat(history=[
                {"role": "user", "parts": [m["content"]]} if m["role"] == "user" 
                else {"role": "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            # API Call (with streaming)
            response = chat.send_message(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                # If API is slow (simulated or real), show safety message
                elapsed = time.time() - start_time
                if elapsed > 1.5 and not full_response:
                    placeholder.markdown("*(Miss Kaplanが嬉しそうに考えています...)* 🤔✨")
                
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
                
            placeholder.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
else:
    st.warning("左のサイドバーからGemini API Keyを入力してください。（.envから自動読み込みも可能です）")
