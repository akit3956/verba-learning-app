import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.set_page_config(page_title="Admin - Verba", page_icon="👑", layout="wide")

# Initialize database
db.init_db()

st.title("👑 管理者ページ (Admin Dashboard)")
st.write("登録されたアカウントの情報を確認できます。")

# Simple password protection for admin page
# Note: In a production app, use st.secrets or environment variables for this!
admin_password = st.sidebar.text_input("管理者パスワード (Admin Password)", type="password")
ADMIN_SECRET = "admin123" # <<< Change this for real usage

if admin_password == ADMIN_SECRET:
    st.sidebar.success("✅ 認証成功 (Authenticated)")
    
    # Get user data
    users = db.get_all_users()
    
    if users:
        # KPI Metrics
        st.subheader("📊 統計情報 (Statistics)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="総登録ユーザー数 (Total Users)", value=len(users))
        
        with col2:
            # Count distinct nationalities
            nationalities_set = set(u["nationality"] for u in users)
            st.metric(label="登録国の数 (Target Countries)", value=len(nationalities_set))
        
        st.divider()
        
        # Display as DataFrame
        st.subheader("👥 ユーザー一覧 (User List)")
        df = pd.DataFrame(users)
        
        # Reorder and rename columns for display
        # We might not have 'created_at' in the returned rows if they couldn't be requested.
        columns_to_show = ["id", "username", "email", "nationality", "vrb_balance"]
        if "created_at" in df.columns:
            columns_to_show.append("created_at")
            df = df[columns_to_show]
            df.columns = ["ID", "Username", "Email", "Nationality", "VRB Balance", "Registration Date"]
        else:
            df = df[columns_to_show]
            df.columns = ["ID", "Username", "Email", "Nationality", "VRB Balance"]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # --- NEW SECTION: Token Issuance ---
        st.subheader("🪙 Token Issuance (VRB発行)")
        st.write("指定したアカウントに対して、VRB（バーチャル残高）を付与します。")
        
        # User Selection
        user_options = [f"{u['username']} ({u['email']})" for u in users]
        selected_user_str = st.selectbox("付与先のアカウント (Select User)", options=user_options)
        
        # Amount Selection
        amount_to_add = st.number_input(
            "付与する数量 (Amount to add)", 
            min_value=1, 
            max_value=100000000, 
            value=50000000, 
            step=10000,
            help="例: 5千万なら 50000000 と入力"
        )
        
        if st.button("VRBを付与 (Issue VRB)", type="primary"):
            # Extract email from the selected string "Username (email)"
            import re
            match = re.search(r'\((.*?)\)', selected_user_str)
            if match:
                selected_email = match.group(1)
                
                # Call DB function
                success, msg = db.add_vrb_to_user(selected_email, amount_to_add)
                
                if success:
                    st.success(msg)
                    st.balloons()
                    # Optionally tell them to refresh
                    st.info("💡 変更を反映するには、画面をリロードしてください。")
                else:
                    st.error(msg)
            else:
                st.error("Invalid user selection format.")
        
        st.divider()
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSVでダウンロード (Download CSV)",
            data=csv,
            file_name='verba_users.csv',
            mime='text/csv',
        )
    else:
        st.info("まだ登録されたアカウントはありません。(No users registered yet.)")
        
elif admin_password:
    st.sidebar.error("⚠️ パスワードが間違っています。")
else:
    st.warning("左側のサイドバーから管理者パスワードを入力してください。")
