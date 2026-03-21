import streamlit.components.v1 as components

import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Verba - The Next Gen Language App",
    page_icon="🇯🇵",
    layout="wide"
)

# ------------------------------

# Main Title Area
st.title("🇯🇵 Japanese Teacher x Web3 x AI")
st.header("Next Gen Language App: 'Learn to Earn'")

# Notification Box
st.info("💡 We are currently accepting pre-orders for the Founder's Pack to raise development funds.")

# Introduction
st.subheader("👋 Hi, I'm Aki. I'm a former Japanese teacher.")
st.write("""
I have seen many students give up on their dream of learning Japanese because they 'didn't have money' or 'lost motivation'.

So, I decided to build a solution using the latest AI and blockchain technology.
**An app where the more you study, the more rewards (tokens) you earn.**

**Project Name: 'Verba (VRB)'**

Learning words (Verba) helps your life. Let's build this world together.
""")

st.divider()

# Problem Section
st.subheader("😤 Why do people fail at learning Japanese?")
st.markdown("##### 'No Money', 'No Motivation', 'Boring Textbooks'")
st.write("Traditional learning methods are expensive and quickly become boring. But Verba is different.")

# Solution Section
st.subheader("💡 Solution: Verba (Learn-to-Earn)")
st.info("The more you study, the more cryptocurrency ($VRB) you earn.")
st.write("Verba uses blockchain technology to record your learning history. Turn your efforts into assets.")

# Tokenomics
st.subheader("💎 Tokenomics (Verba Token)")
st.metric(label="Token Name", value="$VRB")

st.markdown("""
- **Earn**: Answer quizzes correctly, login daily, refer friends.
- **Burn**: Special AI characters, premium materials, JLPT mock exams.
""")

st.divider()

# Roadmap Section
st.subheader("🗺️ Roadmap: The Future We Build")
st.write("Your support ($30) will be the driving force of this journey.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### 🚩 Q1 2026")
    st.caption("Current Stage")
    st.success("✅ Project Start")
    st.success("✅ Founder Sale")

with col2:
    st.markdown("### 🛠️ Q2 2026")
    st.caption("Development")
    st.info("🚀 Public Beta & L2E Engine Launch")
    st.info("🏪 VRB Store Implementation")
    st.write("Release of the Verba Web App with 3 membership tiers (Standard / Pro / Founders). Earn and use tokens for premium JLPT mock exams.")

with col3:
    st.markdown("### 🌑 Q3 2026")
    st.caption("Token")
    st.info("💰 VRB Airdrop")
    st.info("🎁 10,000 VRB Bonus")
    st.write("Distribute tokens to early supporters and Founders.")

with col4:
    st.markdown("### 🚀 Q4 2026")
    st.caption("Global")
    st.warning("🌏 Official Release")
    st.warning("📈 DEX Listing")
    st.write("Public listing on Decentralized Exchanges and global expansion.")

st.divider()

# Pricing Plans (CTA)
st.header("⚡ Choose Your Plan")
st.write("Verbaで制限なく学習を進めるためのプランを選んでください。(Choose a plan to fully unlock Verba.)")

st.markdown("<br>", unsafe_allow_html=True)
st.info("💡 Please review the Terms of Service and Privacy Policy before proceeding.")
st.page_link("pages/2_📜_Terms_&_Privacy.py", label="Read the full Terms of Service and Privacy Policy", icon="📜")
agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")

if not agree:
    st.warning("⚠️ 決済を進めるには、上記の利用規約とプライバシーポリシーに同意してください。 (Agreement is required to proceed.)")

# Get PayPal Client ID
paypal_client_id = st.secrets.get("PAYPAL_CLIENT_ID", "test")
js_agreed = "true" if agree else "false"

col_std, col_pro, col_founder = st.columns(3)

def render_paypal_button(container_id, amount, plan_name, redirect_url):
    components.html(
        f"""
        <div style="text-align: center; margin-top: 10px;">
            <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD"></script>
            <div id="{container_id}"></div>
            <script>
              paypal.Buttons({{
                style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'pay' }},
                onClick: function(data, actions) {{
                  if (!{js_agreed}) {{
                    alert("⚠️ 決済に進むには、「利用規約とプライバシーポリシーに同意します」のチェックボックスにチェックを入れてください。");
                    return actions.reject();
                  }}
                  return actions.resolve();
                }},
                createOrder: function(data, actions) {{
                  return actions.order.create({{
                    purchase_units: [{{ amount: {{ value: '{amount}' }} }}]
                  }});
                }},
                onApprove: function(data, actions) {{
                  return actions.order.capture().then(function(details) {{
                    document.getElementById('{container_id}').style.display = 'none';
                    const successDiv = document.createElement('div');
                    successDiv.innerHTML = `
                      <h4 style="color: #2e7d32; font-family: sans-serif;">✅ 決済完了！</h4>
                      <a href="{redirect_url}" target="_blank" 
                         style="display: inline-block; background-color: #FFD140; color: #000; 
                                padding: 10px 20px; text-decoration: none; font-weight: bold; 
                                border-radius: 8px; font-family: sans-serif; font-size: 14px;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        登録画面へ 👉
                      </a>
                    `;
                    document.body.appendChild(successDiv);
                  }});
                }}
              }}).render('#{container_id}');
            </script>
        </div>
        """,
        height=200,
        scrolling=False
    )

with col_std:
    st.markdown("### 🥉 Standard")
    st.markdown("**( $4.99 / 月 )**")
    st.markdown("""
    - ✅ 基本機能のみ (Basic features)
    - ✅ 一問一答・小テスト
    - 🔒 全項目・模擬試験は利用不可
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    render_paypal_button("paypal-btn-std", "4.99", "standard", "Register?payment=success&plan=standard")

with col_pro:
    st.markdown("### 🥈 Pro")
    st.markdown("**( $12.99 / 月 )**")
    st.markdown("""
    - ✅ **全機能解放** (All features)
    - ✅ 模擬試験（AI画像認識）
    - ✅ 優先サポート
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    render_paypal_button("paypal-btn-pro", "12.99", "pro", "Register?payment=success&plan=pro")

with col_founder:
    st.markdown("### 🥇 Founder's Club")
    st.markdown("**( $30.00 / 買い切り )**")
    st.warning("限定100名 (Limited 100)")
    st.markdown("""
    - ✅ **一生涯全機能解放**
    - ✅ **10,000 VRB 初期ボーナス**
    - ✅ 限定Discord参加権
    """)
    render_paypal_button("paypal-btn-founder", "30.00", "founder", "Register?payment=success&plan=founder")

st.divider()

# FAQ Section
st.subheader("❓ FAQ")
with st.expander("Q: Can I really earn?"):
    st.write("A: Yes. You can earn tokens while learning. The earned tokens are planned to be tradable on exchanges in the future.")

with st.expander("Q: Who is Japanese Teacher Aki?"):
    st.write("A: I am a professional Japanese teacher. I started this project after seeing many students give up learning for financial reasons.")
