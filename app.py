import streamlit.components.v1 as components

import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Verba - The Next Gen Language App",
    page_icon="🇯🇵",
    layout="wide"
)

# ------------------------------

# 🧪 Aki Labs - Experimental Sandbox
# This environment is for testing new AI prompts and features.

# Simple Password Protection
PASSWORD = st.secrets.get("LABS_PASSWORD", "AkiLabs2026") # Default for safety

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🧪 Aki Labs")
    st.info("This is an experimental testing environment. If you are a student, please visit our official site.")
    st.link_button("Go to Official Verba Site 👉", "https://verba-learning-app.vercel.app/")
    
    st.divider()
    
    pwd = st.text_input("Enter Lab Access Password", type="password")
    if st.button("Unlock Lab"):
        if pwd == PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("😕 Incorrect password.")
    return False

if not check_password():
    st.stop() # Halt execution if not authorized

# --- Authorized Lab Content Below ---

# Main Title Area
st.title("🧪 Aki Labs (Sandbox)")
st.caption("Verba Experimental Environment - TEST ONLY")
st.header("Next Gen Language App: 'Learn to Earn'")

# ... rest of the content ...

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
st.write("Your support ($109.99) will be the driving force of this journey.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### 🚩 Q1 2026")
    st.caption("Current Stage")
    st.success("✅ Project Start")
    st.success("✅ Founder Sale")

with col2:
    st.markdown("### 🛠️ Q2 2026")
    st.caption("Development")
    st.success("✅ Public Beta & L2E Engine Launch")
    st.success("✅ VRB Store Implementation")
    st.write("Release of the Verba Web App with 3 membership tiers (Standard / Pro / Founders). Earn and use tokens for premium JLPT mock exams.")

with col3:
    st.markdown("### 🌑 Q3 2026")
    st.caption("Token")
    st.info("💰 VRB Airdrop")
    st.write("Distribute 10,000 VRB tokens to early supporters and Founders.")

with col4:
    st.markdown("### 🚀 Q4 2026")
    st.caption("Global")
    st.warning("🌏 Official Release")
    st.write("Public listing on Decentralized Exchanges (DEX) and global expansion.")

st.divider()

# Pricing Plans (CTA)
st.header("⚡ Choose Your Plan")
st.write("Select a plan to fully unlock Verba and start learning without limits.")

st.markdown("<br>", unsafe_allow_html=True)
st.info("💡 Please review the Terms of Service and Privacy Policy before proceeding.")
st.page_link("pages/2_📜_Terms_&_Privacy.py", label="Read the full Terms of Service and Privacy Policy", icon="📜")
agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")

if not agree:
    st.warning("⚠️ Please check the box above to agree to the Terms of Service and Privacy Policy to proceed with payment.")
else:
    st.success("✅ Agreement confirmed. Please choose your plan below.")

# Get PayPal Client ID
paypal_client_id = st.secrets.get("PAYPAL_CLIENT_ID", "test")
js_agreed = "true" if agree else "false"

col_std, col_pro, col_founder = st.columns(3)

def render_paypal_button(container_id, amount, plan_name, redirect_url):
    components.html(
        f"""
        <div style="text-align: center; margin-top: 10px;">
            <script src="https://www.paypal.com/sdk/js?client-id=AR0TveR8JR7AgvfPzsiYuQ0QYLVFSlzY8FIKnwM4r-apGra8xKaI1R7XstSoVxEtvlXzY2WUnCxWWPZP&currency=USD&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <div id="{container_id}"></div>
            <script>
              paypal.Buttons({{
                style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'pay' }},
                onClick: function(data, actions) {{
                  if (!{js_agreed}) {{
                    alert("⚠️ Please check the agreement checkbox before proceeding to payment.");
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
                      <h4 style="color: #2e7d32; font-family: sans-serif;">✅ Payment Successful!</h4>
                      <p style="font-size: 14px; font-family: sans-serif;">Thank you for your support. Please click the button below to complete your registration.</p>
                      <a href="{redirect_url}" target="_blank" 
                         style="display: inline-block; background-color: #FFD140; color: #000; 
                                padding: 10px 20px; text-decoration: none; font-weight: bold; 
                                border-radius: 8px; font-family: sans-serif; font-size: 14px;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        Go to Registration 👉
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
    st.markdown("**( Free )**")
    st.markdown("""
    - ✅ 10 High-Quality Quizzes / day
    - ✅ **Total 4 Rounds / day** across all features
    - 🔒 Mock Exams & Premium Content Locked
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("Start for Free 👉", "/auth" if "localhost" in st.query_params.get("host", [""])[0] else "https://verba-learning-app.vercel.app/auth")

with col_pro:
    st.markdown("### 🥈 Pro")
    st.markdown("**( $12.99 / Month )**")
    st.markdown("""
    - ✅ **All features unlocked**
    - ✅ AI-powered Mock Exams
    - ✅ Priority Support
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    if agree:
        render_paypal_button("paypal-btn-pro", "12.99", "pro", "Register?payment=success&plan=pro")
    else:
        st.button("Pay with PayPal", key="disabled-pro", disabled=True)

with col_founder:
    st.markdown("### 🥇 Founder's Club")
    st.markdown("**( $109.99 / Year )**")
    st.warning("Limited (100 spots only)")
    st.markdown("""
    - ✅ **Aki's Legacy Backer Status**
    - ✅ **10,000 VRB Early-bird Bonus**
    - ✅ Exclusive Discord Access
    """)
    if agree:
        render_paypal_button("paypal-btn-founder", "109.99", "founder", "Register?payment=success&plan=founder")
    else:
        st.button("Pay with PayPal", key="disabled-founder", disabled=True)

st.divider()

# FAQ Section
st.subheader("❓ FAQ")
with st.expander("Q: Can I really earn?"):
    st.write("A: Yes. You can earn tokens while learning. The earned tokens are planned to be tradable on exchanges in the future.")

with st.expander("Q: Who is Japanese Teacher Aki?"):
    st.write("A: I am a professional Japanese teacher. I started this project after seeing many students give up learning for financial reasons.")
