import streamlit as st
import sys
import os

# Add parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.set_page_config(page_title="Register - Verba", page_icon="📝", layout="centered")

# Initialize database
db.init_db()

st.title("📝 会員登録 (Member Registration)")

# Handle post-payment celebration
is_success = st.query_params.get("payment") == "success" or st.query_params.get("status") == "success"
plan = st.query_params.get("plan", "standard")

if is_success:
    st.balloons()
    if plan == "founder":
        st.info("""
        🎉 **Founder's Packへのご参加ありがとうございます！ (Welcome to Founder's Club!)**  
        決済が完了しました。以下のステップに従って、10,000 VRBのボーナス獲得とアカウント作成を行ってください。
        """)
    elif plan == "pro":
        st.info("""
        🎉 **Proプランへのアップグレードありがとうございます！ (Welcome to Pro Plan!)**  
        決済が完了しました。無制限で全機能をご利用いただけます。アカウントを作成してください。
        """)
    else:
        st.info("""
        🎉 **Standardプランの決済が完了しました！ (Welcome to Standard!)**  
        アカウントを作成して、学習を始めましょう。
        """)
else:
    st.info("新規アカウントを作成してください。 (Please create a new account.)")

if is_success and plan == "founder":
    st.markdown("""
    Thank you for your support! As a Founder, please follow the steps below to claim your rewards:  
    サポートありがとうございます！以下のステップで、ファウンダー特典を受け取ってください。
    
    ---
    
    ### 1️⃣ Claim Your 10,000 VRB Tokens (トークンの受け取りについて)
    To receive your 10,000 VRB tokens, please join the Discord server and send a DM to "Aki" with your MetaMask wallet address.  
    10,000 VRBトークンを受け取るために、Discordに参加後、ファウンダーの「Aki」宛にあなたのMetaMaskウォレットアドレスをDMしてください。
    
    **🦊 スマホ版MetaMaskでのVRBトークンの追加方法:**
    1. MetaMaskアプリを開き、ネットワークが「**Amoy Testnet (Polygon)**」になっているか確認します。
    2. 「トークンをインポート」し、「カスタムトークン」タブを選択します。
    3. コントラクトアドレス: `0x5bE1bAD03Da337E576afb1BDbeE44d7546e6aed9`
    ---
    🌟 **Your Lifetime Premium Access is now active!**  
    """)

st.write("---")
st.subheader("ユーザー登録 (User Registration)")
st.write("アプリを利用するために、以下からアカウントを作成してください。(Please create an account below to use the app.)")

with st.form("register_form"):
    username = st.text_input("ユーザー名 (Username)*")
    email = st.text_input("メールアドレス (Email)*")
    password = st.text_input("パスワード (Password)*", type="password")
    
    # Detailed list of nationalities (in Japanese and English)
    nationalities = [
        "", # Default empty
        "日本 (Japan)",
        "アメリカ (United States)",
        "中国 (China)",
        "韓国 (South Korea)",
        "台湾 (Taiwan)",
        "ベトナム (Vietnam)",
        "フィリピン (Philippines)",
        "インドネシア (Indonesia)",
        "タイ (Thailand)",
        "インド (India)",
        "ブラジル (Brazil)",
        "イギリス (United Kingdom)",
        "フランス (France)",
        "ドイツ (Germany)",
        "その他 (Other)"
    ]
    
    nationality = st.selectbox("国籍 (Nationality)*", nationalities)
    
    submit_button = st.form_submit_button("登録 (Register)", use_container_width=True)
    
    if submit_button:
        if not username:
            st.warning("⚠️ ユーザー名を入力してください。(Please enter your username.)")
        elif not nationality:
            st.warning("⚠️ 国籍を選択してください。(Please select your nationality.)")
        elif email and password:
            success, message = db.create_user(email, username, password, nationality, plan_type=plan)
            if success:
                st.success(f"✅ {message} (Registration successful!)")
                st.balloons()
            else:
                st.error(f"⚠️ {message}")
        else:
            st.warning("⚠️ メールアドレスとパスワードを入力してください。(Please enter your email and password.)")

st.divider()
st.caption("※ご登録いただいた情報は、本サービスの提供以外の目的には使用いたしません。")
