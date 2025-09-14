# 統一WebUI - レスポンシブ対応版
import streamlit as st
import sys
import os
from typing import Dict

# プロジェクトパスの設定
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 統一設定とセキュリティ
from src.unified_config import UnifiedConfig, UserLevel
from src.unified_auth import UnifiedAuth

# 基本機能のインポート（エラーハンドリング付き）
AI_AVAILABLE = False
IMAGE_PROCESSING_AVAILABLE = False
PLOTTING_AVAILABLE = False

try:
    from ai_providers import registry, config_manager, get_configured_provider
    from ai_providers.base_provider import EmotionType, ColorStage
    from character_ai import RuriCharacter
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI機能の読み込みに失敗: {e}")

try:
    import cv2
    import numpy as np
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 画像処理機能の読み込みに失敗: {e}")

try:
    import plotly.graph_objects as go
    PLOTTING_AVAILABLE = True
except ImportError:
    print("⚠️ Plotly機能は無効です")

def main():
    """統一WebUIメイン関数"""
    
    # ユーザーレベルの取得
    user_level = UnifiedConfig.get_user_level(st.session_state)
    ui_config = UnifiedConfig.get_ui_config(user_level)
    features = UnifiedConfig.get_available_features(user_level)
    
    # レスポンシブ対応の初期設定
    setup_responsive_design()
    
    # 認証状態の確認（改良版）
    auth_handler = UnifiedAuth()
    
    # パブリックユーザー以外で認証が必要な場合の処理
    if user_level == UserLevel.PUBLIC:
        # パブリックモードでも動作を継続
        pass
    elif user_level == UserLevel.OWNER:
        # 所有者認証済みの場合は継続
        pass
    else:
        # 認証インターフェースを表示
        auth_handler.show_auth_interface()
        return
    
    # サイドバーメニュー（レスポンシブ対応）
    setup_responsive_sidebar(user_level, features, ui_config)
    
    # メインページの表示
    page = st.session_state.get('current_page', 'home')
    
    if page == 'home':
        show_home_page(user_level, features, ui_config)
    elif page == 'character' and features.get('character_status'):
        show_character_page(user_level, features)
    elif page == 'ai_conversation' and features.get('ai_conversation'):
        show_ai_conversation_page(user_level, features)
    elif page == 'image_analysis' and features.get('image_analysis'):
        show_image_analysis_page(user_level, features)
    elif page == 'streaming' and features.get('streaming_integration'):
        show_streaming_page(user_level, features)
    elif page == 'settings' and features.get('system_settings'):
        show_settings_page(user_level, features)
    elif page == 'analytics' and features.get('analytics'):
        show_analytics_page(user_level, features)
    else:
        st.error(f"ページ '{page}' は利用できません")

def setup_responsive_design():
    """レスポンシブデザインの設定"""
    
    # モバイル検出（簡易版）
    if 'mobile_view' not in st.session_state:
        st.session_state.mobile_view = False
    
    # レスポンシブ対応のCSS
    st.markdown("""
    <style>
    /* 基本レスポンシブ設定 */
    .main > div {
        padding-top: 2rem;
    }
    
    /* チャット関連スタイル */
    .chat-container {
        max-width: 100%;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .chat-message {
        background: #ffffff;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #4a90e2;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-input-section {
        background: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    
    /* 画像レスポンシブ */
    .ruri-image-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .ruri-image-container img {
        max-width: 100%;
        height: auto;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* モバイル対応 */
    @media (max-width: 768px) {
        .chat-container {
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        
        .chat-message {
            padding: 0.5rem;
            font-size: 0.9rem;
        }
        
        .chat-input-section {
            padding: 0.75rem;
        }
        
        .ruri-image-container img {
            max-width: 90%;
        }
        
        .main > div {
            padding-top: 1rem;
        }
    }
    
    /* ダークモード対応 */
    .dark-mode .chat-message {
        background: #2d3748;
        color: #e2e8f0;
    }
    
    .dark-mode .chat-container {
        background: #1a202c;
    }
    </style>
    """, unsafe_allow_html=True)

def setup_responsive_sidebar(user_level: UserLevel, features: Dict[str, bool], ui_config: Dict):
    """レスポンシブ対応サイドバーの設定"""
    
    with st.sidebar:
        # ダークモード切り替え（セッション状態を適切に処理）
        dark_mode = st.checkbox("🌙 ダークモード", key="dark_mode")
        if 'dark_mode_active' not in st.session_state:
            st.session_state.dark_mode_active = False
        
        if dark_mode:
            st.session_state.dark_mode_active = True
            st.markdown('<div class="dark-mode">', unsafe_allow_html=True)
        else:
            st.session_state.dark_mode_active = False
        
        # モバイルビュー切り替え（デバッグ用）
        mobile_view = st.checkbox("📱 モバイルビュー", key="mobile_debug")
        if 'mobile_view_active' not in st.session_state:
            st.session_state.mobile_view_active = False
        
        if mobile_view:
            st.session_state.mobile_view_active = True
        else:
            st.session_state.mobile_view_active = False
        
        st.title("🌟 メニュー")
        
        # 認証状態表示
        if user_level == UserLevel.OWNER:
            st.success("🔓 所有者認証済み")
        else:
            st.info("🔒 パブリックモード")
        
        # ナビゲーションメニュー
        menu_items = [
            ("home", "🏠 ホーム", True),
            ("character", "👤 キャラクター状態", features.get('character_status', False)),
            ("ai_conversation", "💬 AI会話", features.get('ai_conversation', False)),
            ("image_analysis", "🖼️ 画像分析", features.get('image_analysis', False)),
            ("streaming", "📺 配信管理", features.get('streaming_integration', False)),
            ("settings", "⚙️ 設定", features.get('system_settings', False)),
            ("analytics", "📊 分析", features.get('analytics', False))
        ]
        
        for page_key, page_name, enabled in menu_items:
            if enabled:
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.experimental_rerun()
            else:
                st.button(page_name + " 🔒", disabled=True, use_container_width=True,
                         help="所有者認証が必要です")
        
        # 認証関連
        st.markdown("---")
        if user_level == UserLevel.PUBLIC:
            if st.button("🔐 所有者認証", use_container_width=True):
                st.session_state.show_auth = True
                st.experimental_rerun()
        else:
            if st.button("🚪 ログアウト", use_container_width=True):
                UnifiedAuth().logout(st.session_state)
                st.experimental_rerun()

def show_home_page(user_level: UserLevel, features: Dict[str, bool], ui_config: Dict):
    """ホームページ - レスポンシブ対応チャット機能付き"""
    
    # メイン画像とタイトル
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #4a90e2; margin-bottom: 0.5rem;">🌟 AITuber ルリ</h1>
        <p style="color: #666; font-size: 1.1rem;">戯曲『あいのいろ』から生まれた感情学習AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # レスポンシブ対応のルリ画像表示
    image_path = os.path.join(project_root, "assets", "ruri_imageboard.png")
    if os.path.exists(image_path):
        col_left, col_center, col_right = st.columns([0.5, 3, 0.5])
        with col_center:
            st.image(image_path, caption="🎭 ルリちゃん", use_container_width=True)
    else:
        st.info("🎭 ルリの画像を読み込み中...")
    
    # チャット初期化（履歴復元機能付き）
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # セッションから履歴を復元
        load_chat_history_from_session()
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    # モバイル対応のチャット機能
    st.markdown("---")
    
    if user_level == UserLevel.PUBLIC:
        st.markdown("### 💬 ルリとチャット")
        st.info("🔒 フル機能を利用するには所有者認証が必要です")
        
        # パブリック用の簡易チャット（レスポンシブ対応）
        chat_input = st.text_input(
            "メッセージを入力してください...",
            placeholder="こんにちは、ルリちゃん！",
            disabled=True,
            help="所有者認証後にチャット機能が利用できます"
        )
        st.caption("👆 認証後にメッセージ送信が可能になります")
        
    else:
        st.markdown("### 💬 ルリとチャット")
        
        # チャット履歴の表示（レスポンシブ対応）
        if st.session_state.chat_history:
            st.markdown("#### 📝 会話履歴")
            
            # 履歴表示数をモバイルに最適化
            display_count = 3 if st.session_state.get('mobile_view_active', False) else 5
            
            for i, (timestamp, user_msg, ruri_msg) in enumerate(st.session_state.chat_history[-display_count:]):
                st.markdown(f"""
                <div class="chat-message">
                    <small style="color: #666;">{timestamp}</small><br>
                    <strong>あなた:</strong> {user_msg}<br>
                    <strong style="color: #4a90e2;">ルリ:</strong> {ruri_msg}
                </div>
                """, unsafe_allow_html=True)
        
        # チャット入力（レスポンシブ対応）
        st.markdown('<div class="chat-input-section">', unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            chat_input = st.text_input(
                "ルリにメッセージを送信:",
                placeholder="今日はどんな気分？感情を教えて！",
                key="chat_input_field"
            )
            
            # モバイル対応：ボタン配置を最適化
            if st.session_state.get('mobile_view_active', False):
                # モバイル：縦並び
                submit_button = st.form_submit_button("💌 送信", use_container_width=True)
                col1, col2 = st.columns(2)
                with col1:
                    clear_history = st.form_submit_button("🗑️ 履歴削除", use_container_width=True)
                with col2:
                    export_chat = st.form_submit_button("📄 エクスポート", use_container_width=True)
            else:
                # デスクトップ：横並び
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    submit_button = st.form_submit_button("💌 送信", use_container_width=True)
                with col2:
                    clear_history = st.form_submit_button("🗑️ 履歴削除")
                with col3:
                    export_chat = st.form_submit_button("📄 エクスポート")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # チャット処理
        if submit_button and chat_input.strip():
            handle_chat_message(chat_input.strip(), user_level, features)
        
        if clear_history:
            st.session_state.chat_history = []
            st.success("チャット履歴を削除しました")
            st.experimental_rerun()
        
        if export_chat and st.session_state.chat_history:
            export_chat_history()
    
    # ステータス情報（レスポンシブ対応）
    st.markdown("---")
    
    # モバイル対応：画面サイズに応じてカラム数を調整
    if st.session_state.get('mobile_view_active', False):
        # モバイル：縦並び
        st.markdown("### 📊 現在の状態")
        st.markdown(f"**アクセスレベル**: {user_level.value.title()}")
        if AI_AVAILABLE and user_level == UserLevel.OWNER:
            st.markdown("**AI状態**: 🟢 アクティブ")
            st.markdown("**学習段階**: 第1段階（感情学習中）")
        else:
            st.markdown("**AI状態**: 🔶 限定モード")
        
        st.markdown("### 🎯 利用可能機能")
        available_count = sum(features.values())
        total_count = len(features)
        
        progress = available_count / total_count if total_count > 0 else 0
        st.progress(progress)
        st.caption(f"{available_count}/{total_count} 機能が利用可能")
        
        if user_level == UserLevel.PUBLIC:
            st.info("🔓 所有者認証で全機能解放")
    else:
        # デスクトップ：横並び
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 現在の状態")
            st.markdown(f"**アクセスレベル**: {user_level.value.title()}")
            if AI_AVAILABLE and user_level == UserLevel.OWNER:
                st.markdown("**AI状態**: 🟢 アクティブ")
                st.markdown("**学習段階**: 第1段階（感情学習中）")
            else:
                st.markdown("**AI状態**: 🔶 限定モード")
            
        with col2:
            st.markdown("### 🎯 利用可能機能")
            available_count = sum(features.values())
            total_count = len(features)
            
            progress = available_count / total_count if total_count > 0 else 0
            st.progress(progress)
            st.caption(f"{available_count}/{total_count} 機能が利用可能")
            
            if user_level == UserLevel.PUBLIC:
                st.info("🔓 所有者認証で全機能解放")

def handle_chat_message(message: str, user_level: UserLevel, features: Dict[str, bool]):
    """チャットメッセージの処理（履歴管理機能付き）"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # チャット履歴の自動保存設定
    max_history = 50  # 最大保存履歴数
    
    if AI_AVAILABLE and features.get("ai_conversation"):
        try:
            # AI応答の生成
            provider = get_configured_provider()
            if provider:
                ruri = RuriCharacter()
                response = ruri.respond_to_message(message)
                ai_response = response.get("message", "申し訳ございません、今は応答できません...")
            else:
                ai_response = "🤖 AIプロバイダーが設定されていません"
        except Exception as e:
            ai_response = f"⚠️ AI応答エラー: {str(e)}"
    else:
        # AI機能が無効な場合のフォールバック
        fallback_responses = [
            "ありがとうございます！感情を学習中です...",
            "そうですね...色々な感情があるんですね",
            "まだ学習中ですが、あなたの言葉は覚えています",
            "もっとお話ししたいです！",
            "感情って...難しいですね"
        ]
        import random
        ai_response = random.choice(fallback_responses)
    
    # 履歴に追加（自動的に古い履歴を削除）
    st.session_state.chat_history.append((timestamp, message, ai_response))
    
    # 履歴のサイズ制限
    if len(st.session_state.chat_history) > max_history:
        st.session_state.chat_history = st.session_state.chat_history[-max_history:]
    
    # 成功メッセージ
    st.success(f"ルリ: {ai_response}")
    
    # 永続化のためのローカルストレージ保存（オプション）
    save_chat_history_to_session()

def save_chat_history_to_session():
    """チャット履歴をセッションに永続化"""
    try:
        import json
        
        # セッション状態に保存（Streamlitの標準機能）
        if 'persistent_chat_history' not in st.session_state:
            st.session_state.persistent_chat_history = []
        
        # 現在の履歴を永続化
        st.session_state.persistent_chat_history = st.session_state.chat_history.copy()
        
    except Exception as e:
        print(f"履歴保存エラー: {e}")

def load_chat_history_from_session():
    """セッションからチャット履歴を復元"""
    try:
        if 'persistent_chat_history' in st.session_state:
            st.session_state.chat_history = st.session_state.persistent_chat_history.copy()
    except Exception as e:
        print(f"履歴復元エラー: {e}")
        st.session_state.chat_history = []

def export_chat_history():
    """チャット履歴のエクスポート（改良版）"""
    if not st.session_state.chat_history:
        st.warning("エクスポートする履歴がありません")
        return
    
    import datetime
    import json
    
    current_time = datetime.datetime.now()
    
    # マークダウン形式でのエクスポート
    markdown_text = f"# ルリとの会話履歴\n\n"
    markdown_text += f"**エクスポート日時**: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    markdown_text += f"**会話数**: {len(st.session_state.chat_history)}件\n\n"
    markdown_text += "---\n\n"
    
    for i, (timestamp, user_msg, ruri_msg) in enumerate(st.session_state.chat_history, 1):
        markdown_text += f"## 会話 {i} ({timestamp})\n\n"
        markdown_text += f"**あなた**: {user_msg}\n\n"
        markdown_text += f"**ルリ**: {ruri_msg}\n\n"
        markdown_text += "---\n\n"
    
    # JSON形式でのエクスポートも提供
    json_data = {
        "export_time": current_time.isoformat(),
        "chat_count": len(st.session_state.chat_history),
        "conversations": [
            {
                "id": i,
                "timestamp": timestamp,
                "user_message": user_msg,
                "ruri_response": ruri_msg
            }
            for i, (timestamp, user_msg, ruri_msg) in enumerate(st.session_state.chat_history, 1)
        ]
    }
    
    # ダウンロードボタンを2つ用意
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Markdown形式でダウンロード",
            data=markdown_text,
            file_name=f"ruri_chat_{current_time.strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )
    
    with col2:
        st.download_button(
            label="📋 JSON形式でダウンロード",
            data=json.dumps(json_data, ensure_ascii=False, indent=2),
            file_name=f"ruri_chat_{current_time.strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

# 他のページ関数のプレースホルダー（必要に応じて実装）
def show_character_page(user_level: UserLevel, features: Dict[str, bool]):
    """キャラクター状態ページ"""
    st.title("👤 ルリの状態")
    st.info("🚧 実装中...")

def show_ai_conversation_page(user_level: UserLevel, features: Dict[str, bool]):
    """AI会話ページ"""
    st.title("💬 AI会話")
    st.info("🚧 実装中...")

def show_image_analysis_page(user_level: UserLevel, features: Dict[str, bool]):
    """画像分析ページ"""
    st.title("🖼️ 画像分析")
    st.info("🚧 実装中...")

def show_streaming_page(user_level: UserLevel, features: Dict[str, bool]):
    """配信管理ページ"""
    st.title("📺 配信管理")
    st.info("🚧 実装中...")

def show_settings_page(user_level: UserLevel, features: Dict[str, bool]):
    """設定ページ"""
    st.title("⚙️ システム設定")
    st.info("🚧 実装中...")

def show_analytics_page(user_level: UserLevel, features: Dict[str, bool]):
    """分析ページ"""
    st.title("📊 分析")
    st.info("🚧 実装中...")

if __name__ == "__main__":
    st.set_page_config(
        page_title="AITuber ルリ - 統一環境",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()