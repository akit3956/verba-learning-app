import streamlit as st

# ページ設定
st.set_page_config(
    page_title="Verba - 次世代の語学アプリ",
    page_icon="🇯🇵",
    layout="wide"
)

# タイトルエリア
st.title("🇯🇵 日本語教師 × Web3 × AI")
st.header("次世代の語学アプリ：「学んで稼ぐ」")

# お知らせボックス
st.info("💡 現在、開発資金を集めるためにファウンダーズパックの事前予約を受け付けています。")

# 自己紹介とプロジェクト概要
st.subheader("👋 こんにちは、アキです。元日本語教師です。")
st.write("""
「お金がない」や「やる気がなくなった」という理由で、日本語を学ぶ夢をあきらめてしまう学生を数多く見てきました。

そこで、最新のAIとブロックチェーン技術を活用したソリューションを構築することにしました。
**勉強すればするほど報酬（トークン）がもらえるアプリです。**

**プロジェクト名：「Verba（VRB）」**

言葉（Verba）を学ぶことはあなたの人生に役立ちます。一緒にこの世界を築きましょう。
""")

st.divider()

# ロードマップセクション
st.subheader("🗺️ ロードマップ: 私たちが築く未来")
st.write("あなたのサポート（30ドル）がこの旅の原動力になります。")

# 4つのカラムでロードマップを表示
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🚩 2026年第1四半期")
    st.caption("現在の段階")
    st.success("✅ プロジェクト開始")
    st.success("✅ 創業者セール")

with col2:
    st.markdown("### 🛠️ 2026年第2四半期")
    st.caption("発達")
    st.info("📱 ベータ版アプリのリリース")
    st.write("創設者のみを対象にプロトタイプアプリをリリース")

with col3:
    st.markdown("### 🌑 2026年第3四半期")
    st.caption("トークン")
    st.info("💰 VRB エアドロップ")
    st.write("早期支援者に 10,000 VRB トークンを配布")

with col4:
    st.markdown("### 🚀 2026年第4四半期")
    st.caption("グローバル")
    st.warning("🌏 公式リリース")
    st.write("DEX（分散型取引所）に公開・上場。")
