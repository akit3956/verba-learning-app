import streamlit as st
import google.generativeai as genai
import json
import time
import os
from prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# --- UI Configuration & Custom CSS ---
st.set_page_config(
    page_title="JLPT Original Question Generator",
    page_icon="🇯🇵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #003366;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00509d;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .question-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #003366;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .option-list {
        list-style-type: none;
        padding-left: 0;
    }
    .option-item {
        padding: 10px;
        margin: 5px 0;
        background-color: #f1f3f5;
        border-radius: 5px;
    }
    .answer-label {
        font-weight: bold;
        color: #2b8a3e;
    }
    .explanation-box {
        margin-top: 15px;
        padding: 15px;
        background-color: #e7f5ff;
        border-radius: 10px;
        font-size: 0.95em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ 設定")
    
    ai_provider = st.selectbox("AIプロバイダー", ["Google Gemini", "OpenAI"])
    
    if ai_provider == "OpenAI":
        api_key = st.text_input("OpenAI API Key", type="password", help="OpenAIのAPIキー（sk-...）を入力してください。")
        # 話題のGPT-5.5相当のモデルなども直接指定できるようにselectboxや直接入力を可能に
        model_name = st.selectbox("OpenAI モデル", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-5.5", "gpt-5.5-turbo"], index=0)
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studioで作成したAPIキーを入力してください。")
        model_name = "models/gemini-2.5-flash"
        
    level = st.selectbox("JLPTレベル", ["N1", "N2", "N3", "N4", "N5"], index=1)
    num_variations = st.slider("生成するバリエーション数", 1, 30, 24)
    
    st.markdown("---")
    st.info("💡 **使い方**\n1. 過去問のPDFをアップロード\n2. 「類似問題を生成」をクリック\n3. 生成された内容を確認し、PDF/Markdownで保存")

# --- PDF Generation Helper ---
def create_pdf(questions, level):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Macの日本語フォント候補を順番に試す
    font_candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/AppleGothic.ttf"
    ]
    
    font_loaded = False
    for path in font_candidates:
        if os.path.exists(path):
            try:
                pdf.add_font("JPFont", "", path)
                pdf.set_font("JPFont", size=14)
                font_loaded = True
                break
            except:
                continue

    pdf.cell(0, 10, txt=f"JLPT {level} 練習問題集 (オリジナル)", ln=True, align='C')
    pdf.ln(5)
    
    # --- 問題セクション ---
    for i, q in enumerate(questions):
        # 確実に左端から開始
        pdf.set_x(10)
        
        # 問題番号と本文
        pdf.set_font_size(12)
        pdf.multi_cell(0, 8, txt=f"問題 {i+1}: {q['question_text']}")
        pdf.ln(2)
        
        # 選択肢（少しインデントを入れる）
        for j, opt in enumerate(q['options']):
            pdf.set_x(15)
            pdf.multi_cell(0, 7, txt=f"{j+1}. {opt}")
        pdf.ln(8)
        
        # 改ページ判定
        if pdf.get_y() > 240:
            pdf.add_page()

    # --- 解答・解説セクション ---
    pdf.add_page()
    pdf.set_x(10)
    pdf.set_font_size(14)
    pdf.cell(0, 10, txt=f"解答と解説", ln=True, align='C')
    pdf.ln(5)

    for i, q in enumerate(questions):
        pdf.set_x(10)
        pdf.set_font_size(11)
        pdf.multi_cell(0, 8, txt=f"問題 {i+1}")
        
        pdf.set_x(10)
        pdf.set_font_size(10)
        pdf.set_text_color(43, 138, 62) # 正解を緑色に
        pdf.multi_cell(0, 7, txt=f"【正答】 {q['options'][q['answer_index']]}")
        
        # 解説
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(10)
        pdf.multi_cell(0, 7, txt=f"【解説】\n{q['explanation']}")
        pdf.ln(8)
        
        # 改ページ判定
        if pdf.get_y() > 240:
            pdf.add_page()
            
    return bytes(pdf.output())

# --- Main Area ---
header_path = "/Users/akiratakushi/.gemini/antigravity/brain/236b188b-919e-4011-9ceb-71424989fcba/jlpt_app_header_1777007139754.png"
if os.path.exists(header_path):
    st.image(header_path, use_container_width=True)
else:
    st.title("🇯🇵 JLPT Original Question Generator")
    st.subheader("過去問をベースに、高品質なオリジナル問題集を自動生成")

uploaded_file = st.file_uploader("過去問PDFをアップロードしてください", type="pdf")

if uploaded_file is not None:
    if st.button("✨ 類似問題を生成する"):
        if not api_key:
            st.error("API Keyを入力してください。")
        else:
            try:
                with st.status("🚀 解析 & 生成中...", expanded=True) as status:
                    temp_pdf_path = f"temp_{uploaded_file.name}"
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    if ai_provider == "Google Gemini":
                        genai.configure(api_key=api_key)
                        generation_config = {
                            "max_output_tokens": 8192,
                            "temperature": 0.7,
                        }
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config
                        )
                        
                        st.write("GeminiにPDFを送信中...")
                        pdf_file = genai.upload_file(path=temp_pdf_path, display_name=uploaded_file.name)
                        
                        while pdf_file.state.name == "PROCESSING":
                            time.sleep(1)
                            pdf_file = genai.get_file(pdf_file.name)
                        
                        st.write(f"過去問を分析し、{num_variations}問の類似問題を生成しています（1〜2分かかる場合があります）...")
                        response = model.generate_content([
                            SYSTEM_PROMPT.format(level=level),
                            pdf_file,
                            USER_PROMPT_TEMPLATE.format(level=level, num_variations=num_variations)
                        ])
                        raw_content = response.text
                        genai.delete_file(pdf_file.name)
                        
                    elif ai_provider == "OpenAI":
                        # OpenAIの場合はPDFからテキストを抽出して渡す
                        st.write("PDFデータを抽出中...")
                        from PyPDF2 import PdfReader
                        reader = PdfReader(temp_pdf_path)
                        pdf_text = ""
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                pdf_text += text + "\n"
                                
                        st.write(f"OpenAI ({model_name}) で分析と生成を行っています...")
                        from openai import OpenAI
                        client = OpenAI(api_key=api_key)
                        
                        user_content = USER_PROMPT_TEMPLATE.format(level=level, num_variations=num_variations)
                        user_content += f"\n\n--- 過去問 PDF抽出テキスト ---\n{pdf_text}"
                        
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT.format(level=level)},
                                {"role": "user", "content": user_content}
                            ],
                            temperature=0.7,
                            max_tokens=4096
                        )
                        raw_content = response.choices[0].message.content

                    os.remove(temp_pdf_path)
                    # --- パース処理 ---
                    import re
                    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_content)
                    if json_match:
                        output_text = json_match.group(1).strip()
                    else:
                        start_idx = raw_content.find('[')
                        end_idx = raw_content.rfind(']')
                        if start_idx != -1 and end_idx != -1:
                            output_text = raw_content[start_idx:end_idx+1]
                        else:
                            output_text = raw_content.strip()

                    try:
                        questions_data = json.loads(output_text)
                        st.session_state['generated_questions'] = questions_data
                        st.session_state.pop('parse_error', None) # 成功したらエラーを消す
                        status.update(label="✅ 生成完了！", state="complete", expanded=False)
                    except json.JSONDecodeError as e:
                        st.session_state['parse_error'] = raw_content
                        status.update(label="❌ 解析失敗", state="error", expanded=False)

            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")

# --- Parse Error Debug ---
if 'parse_error' in st.session_state:
    st.error("JSONの解析に失敗しました。AIの回答が途切れた可能性があります。")
    with st.expander("AIからの生の回答（デバッグ用）"):
        st.code(st.session_state['parse_error'])

# --- Display Results ---
if 'generated_questions' in st.session_state:
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(f"📝 生成された {level} 類似問題")
    with col2:
        pdf_bytes = create_pdf(st.session_state['generated_questions'], level)
        st.download_button(
            label="📄 PDF形式でダウンロード",
            data=pdf_bytes,
            file_name=f"JLPT_{level}_Questions.pdf",
            mime="application/pdf",
        )
    
    md_content = f"# JLPT {level} 類似問題集\n\n"
    
    for i, q in enumerate(st.session_state['generated_questions']):
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <h3>問題 {i+1}</h3>
                <p style="font-size: 1.2em; font-weight: 500;">{q['question_text']}</p>
                <div class="option-list">
                    <div class="option-item">1. {q['options'][0]}</div>
                    <div class="option-item">2. {q['options'][1]}</div>
                    <div class="option-item">3. {q['options'][2]}</div>
                    <div class="option-item">4. {q['options'][3]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("✅ 正解と解説を表示"):
                st.markdown(f"<p class='answer-label'>正解: {q['options'][q['answer_index']]}</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='explanation-box'><strong>解説:</strong><br>{q['explanation']}</div>", unsafe_allow_html=True)
                st.caption(f"分析ポイント: {q['analysis']}")

            md_content += f"## 問題 {i+1}\n\n{q['question_text']}\n\n"
            for j, opt in enumerate(q['options']):
                md_content += f"{j+1}. {opt}\n"
            md_content += f"\n**正解: {q['options'][q['answer_index']]}**\n\n"
            md_content += f"### 解説\n{q['explanation']}\n\n---\n\n"

    st.download_button(
        label="📥 Markdown形式でダウンロード",
        data=md_content,
        file_name=f"JLPT_{level}_Generated_Problems.md",
        mime="text/markdown"
    )

st.markdown("---")
st.caption("Powered by Gemini 1.5 Flash | Designed by Antigravity")
