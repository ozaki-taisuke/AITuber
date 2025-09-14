# ベータ版認証システム
import streamlit as st
import hashlib
import os
from src.production_config import ProductionConfig

def check_beta_access():
    """ベータ版アクセス認証"""
    
    def password_entered():
        """パスワード入力時の処理"""
        entered_password = st.session_state["beta_password"]
        correct_password = ProductionConfig.BETA_PASSWORD
        
        # パスワードのハッシュ化比較（セキュリティ強化）
        entered_hash = hashlib.sha256(entered_password.encode()).hexdigest()
        correct_hash = hashlib.sha256(correct_password.encode()).hexdigest()
        
        if entered_hash == correct_hash:
            st.session_state["beta_authenticated"] = True
            st.session_state["user_type"] = "beta_tester"
            del st.session_state["beta_password"]  # パスワードを削除
        else:
            st.session_state["beta_authenticated"] = False
            st.error("❌ パスワードが正しくありません")

    # 認証状態の確認
    if "beta_authenticated" not in st.session_state:
        st.session_state["beta_authenticated"] = False

    # 未認証の場合は認証画面を表示
    if not st.session_state["beta_authenticated"]:
        st.markdown("""
        # 🔒 AITuber ルリ - ベータ版
        
        このアプリケーションはベータテスト中です。  
        アクセスにはパスワードが必要です。
        
        ---
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input(
                "🔑 ベータテスト用パスワード", 
                type="password", 
                on_change=password_entered, 
                key="beta_password",
                placeholder="パスワードを入力してください"
            )
            
            if st.button("🚀 アクセス", use_container_width=True):
                if "beta_password" in st.session_state:
                    password_entered()
        
        # ベータ版についての情報
        st.markdown("""
        ---
        ## 📋 ベータ版について
        
        - **目的**: 基本機能の動作確認とフィードバック収集
        - **期間**: 限定期間のテスト運用
        - **対象**: 招待されたベータテスターのみ
        
        ## 🤝 フィードバックについて
        
        バグ報告や機能要望は以下までお願いします：
        - **GitHub Issues**: [リポジトリ](https://github.com/ozaki-taisuke/pupa-Ruri)
        - **Twitter**: [@ozaki-taisuke]
        - **メール**: [連絡先]
        
        ## ⚠️ 注意事項
        
        - ベータ版のため、予期しない動作や機能制限があります
        - データの永続化は保証されません
        - サービス停止や仕様変更が発生する可能性があります
        """)
        
        return False
    
    return True

def show_beta_header():
    """ベータ版用のヘッダー表示"""
    st.markdown("""
    <div style='
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        padding: 0.5rem;
        border-radius: 0.5rem;
        text-align: center;
        color: white;
        font-weight: bold;
        margin-bottom: 1rem;
    '>
        🚧 ベータ版 - テスト運用中 🚧
    </div>
    """, unsafe_allow_html=True)

def show_beta_feedback():
    """ベータ版フィードバック収集"""
    with st.expander("📝 ベータテストフィードバック"):
        st.markdown("""
        ### 🐛 見つけたバグや問題
        """)
        bug_report = st.text_area("バグの詳細を教えてください", height=100)
        
        st.markdown("""
        ### 💡 改善要望や新機能のアイデア
        """)
        feature_request = st.text_area("こんな機能があったらいいなというアイデア", height=100)
        
        st.markdown("""
        ### ⭐ 全体的な感想
        """)
        overall_rating = st.select_slider(
            "使いやすさ", 
            options=["😞 難しい", "😐 普通", "😊 使いやすい", "🤩 とても良い"]
        )
        
        if st.button("📨 フィードバック送信", use_container_width=True):
            # 実際の実装では、これらのデータを保存/送信する
            st.success("📧 フィードバックありがとうございます！開発の参考にさせていただきます。")

def get_beta_user_info():
    """ベータユーザーの情報を取得"""
    return {
        "user_type": st.session_state.get("user_type", "anonymous"),
        "authenticated": st.session_state.get("beta_authenticated", False),
        "session_id": st.session_state.get("session_id", "unknown")
    }