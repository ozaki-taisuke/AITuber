# 統一WebUI - レスポンシブ対応版
import streamlit as st
import sys
import os
from typing import Dict

# プロジェクトパスの設定（本番環境対応強化）
import sys
import os
from typing import Dict

# より堅牢なパス設定
project_root = os.path.dirname(os.path.abspath(__file__))
webui_dir = os.path.basename(project_root)

# webuiフォルダ内にいる場合は親ディレクトリに移動
if webui_dir == 'webui':
    project_root = os.path.dirname(project_root)

src_path = os.path.join(project_root, 'src')

# パスの追加（重複チェック付き）
for path in [project_root, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 統一設定とセキュリティ（エラーハンドリング付き）
try:
    from src.unified_config import UnifiedConfig, UserLevel
    from src.unified_auth import UnifiedAuth
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 設定モジュールの読み込みに失敗: {e}")
    # フォールバック設定
    class UserLevel:
        PUBLIC = "public"
        OWNER = "owner"
    
    class UnifiedConfig:
        @staticmethod
        def get_user_level(session_state):
            return UserLevel.PUBLIC
        
        @staticmethod
        def get_ui_config(user_level):
            return {"title": "AITuber ルリ", "theme": "default"}
        
        @staticmethod
        def get_available_features(user_level):
            return {"ai_conversation": True, "character_status": True}
    
    class UnifiedAuth:
        @staticmethod
        def show_auth_interface():
            pass
    
    CONFIG_AVAILABLE = False

# 基本機能のインポート（エラーハンドリング付き）
AI_AVAILABLE = False
IMAGE_PROCESSING_AVAILABLE = False
PLOTTING_AVAILABLE = False

# 軽量インポート: 必要時のみ読み込み
def lazy_import_ai():
    """AI機能の遅延インポート"""
    global AI_AVAILABLE
    if not AI_AVAILABLE:
        try:
            from src.character_ai import RuriCharacter
            AI_AVAILABLE = True
            return True
        except ImportError as e:
            print(f"⚠️ AI機能の読み込みに失敗: {e}")
            return False
    return True

def get_ruri_character():
    """ルリキャラクターインスタンスの取得（フォールバック付き）"""
    if lazy_import_ai():
        try:
            from src.character_ai import RuriCharacter
            return RuriCharacter()
        except Exception as e:
            print(f"⚠️ ルリキャラクター初期化失敗: {e}")
    
    # フォールバック用ダミークラス
    class DummyRuriCharacter:
        def generate_response(self, message, image=None):
            return "AI機能が利用できません。システム管理者にお問い合わせください。"
    
    return DummyRuriCharacter()

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
    
    # 初期化プロセスの表示
    if 'initialization_complete' not in st.session_state:
        with st.spinner('Connecting pupa system...'):
            # ユーザーレベルの取得
            user_level = UnifiedConfig.get_user_level(st.session_state)
            ui_config = UnifiedConfig.get_ui_config(user_level)
            features = UnifiedConfig.get_available_features(user_level)
            
            # 初期化完了フラグを設定
            st.session_state.initialization_complete = True
            st.session_state.user_level = user_level
            st.session_state.ui_config = ui_config  
            st.session_state.features = features
        
        # 初期化後にページをリフレッシュ
        st.rerun()
    
    # セッションから設定を取得
    user_level = st.session_state.user_level
    ui_config = st.session_state.ui_config
    features = st.session_state.features
    
    # レスポンシブ対応の初期設定
    setup_responsive_design()
    
    # 認証状態の確認（改良版）
    auth_handler = UnifiedAuth()
    
    # サイドバーメニュー（レスポンシブ対応）
    setup_responsive_sidebar(user_level, features, ui_config)
    
    # 認証ダイアログの表示チェック（メインエリアに表示）
    if st.session_state.get('show_auth', False):
        show_auth_page()
        return
    
    # パブリックユーザー以外で認証が必要な場合の処理
    if user_level == UserLevel.PUBLIC:
        # パブリックモードでも動作を継続
        pass
    elif user_level == UserLevel.OWNER:
        # 所有者認証済みの場合は継続
        pass
    else:
        # 認証インターフェースをメインエリアに表示
        show_auth_page()
        return
    
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
    """レスポンシブデザインの設定（アクセシビリティ強化版）"""
    
    # アクセシビリティ重視のレスポンシブCSS
    st.markdown("""
    <style>
    /* 基本レスポンシブ設定 - 戯曲『あいのいろ』の世界観 */
    .main > div {
        padding-top: 2rem;
    }
    
    /* 会話関連スタイル - 明るく視認性重視 */
    .chat-container {
        max-width: 100%;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 1rem;
        margin: 1rem 0;
        border: 2px solid #cbd5e1;
    }
    
    .chat-message {
        background: #ffffff;
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 0.75rem;
        border-left: 5px solid #6366f1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
        transition: all 0.2s ease;
    }
    
    .chat-message:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25);
        transform: translateY(-1px);
    }
    
    .chat-input-section {
        background: transparent;
        padding: 1rem 0;
        border-radius: 0;
        margin-top: 0.5rem;
        border: none;
        box-shadow: none;
    }
    
    /* 画像レスポンシブ - 感情学習をイメージした枠（コンパクト版） */
    .ruri-image-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
        position: relative;
    }
    
    .ruri-image-container img {
        max-width: 100%;
        max-height: 300px;
        height: auto;
        border-radius: 1.5rem;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
        border: 3px solid #e2e8f0;
        transition: all 0.3s ease;
        object-fit: contain;
    }
    
    .ruri-image-container img:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 48px rgba(99, 102, 241, 0.3);
    }
    
    /* カラーパレット - 戯曲『あいのいろ』テーマ */
    :root {
        --primary-color: #6366f1;      /* 感情学習の青 */
        --secondary-color: #8b5cf6;    /* 成長の紫 */
        --accent-color: #06b6d4;       /* 変化の水色 */
        --success-color: #10b981;      /* 学習完了の緑 */
        --text-primary: #1e293b;       /* 高コントラスト黒 */
        --text-secondary: #475569;     /* 読みやすいグレー */
        --background-light: #f8fafc;   /* 明るい背景 */
        --border-light: #e2e8f0;       /* 優しいボーダー */
    }
    
    /* モバイル対応 */
    @media (max-width: 768px) {
        .chat-container {
            padding: 1rem;
            margin: 0.75rem 0;
            border-radius: 0.75rem;
        }
        
        .chat-message {
            padding: 0.75rem;
            font-size: 0.95rem;
            margin: 0.5rem 0;
        }
        
        .chat-input-section {
            padding: 0.5rem 0;
            border-radius: 0;
        }
        
        .ruri-image-container img {
            max-width: 80%;
            max-height: 200px;
            border-radius: 1rem;
        }
        
        .main > div {
            padding-top: 1rem;
        }
        
        /* モバイルでのボタン配置 */
        .stColumns > div {
            min-width: 0 !important;
            flex: 1 !important;
        }
        
        .stButton > button {
            width: 100% !important;
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
        }
        
        /* モバイルでのカラム幅調整 */
        div[data-testid="column"]:nth-child(1) {
            flex: 2 !important;
        }
        
        div[data-testid="column"]:nth-child(2),
        div[data-testid="column"]:nth-child(3) {
            flex: 1 !important;
        }
    }
    
    /* タブレット対応 */
    @media (min-width: 769px) and (max-width: 1024px) {
        .chat-container {
            padding: 1.25rem;
        }
        
        .ruri-image-container img {
            max-width: 85%;
        }
    }
    
    /* 高コントラストアクセシビリティ */
    @media (prefers-contrast: high) {
        .chat-message {
            border-left-width: 6px;
            border-color: #000000;
        }
        
        .chat-container {
            border-color: #475569;
            border-width: 3px;
        }
    }
    
    /* 視覚的な強調 */
    .highlight-text {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    .status-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-active {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #22c55e;
    }
    
    .status-limited {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #f59e0b;
    }
    </style>
    """, unsafe_allow_html=True)

def setup_responsive_sidebar(user_level: UserLevel, features: Dict[str, bool], ui_config: Dict):
    """レスポンシブ対応サイドバーの設定（シンプル版）"""
    
    with st.sidebar:
        
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
                if st.button(page_name, key=f"nav_{page_key}", width="stretch"):
                    st.session_state.current_page = page_key
                    st.rerun()
            else:
                st.button(page_name + " 🔒", disabled=True, width="stretch",
                         help="所有者認証が必要です")
        
        # 認証関連
        st.markdown("---")
        if user_level == UserLevel.PUBLIC:
            if st.button("🔐 所有者認証", width="stretch"):
                st.session_state.show_auth = True
                st.rerun()
        else:
            if st.button("🚪 ログアウト", width="stretch"):
                UnifiedAuth().logout(st.session_state)
                st.rerun()

def show_home_page(user_level: UserLevel, features: Dict[str, bool], ui_config: Dict):
    """ホームページ - レスポンシブ対応チャット機能付き"""
    
    # メイン画像とタイトル
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #4a90e2; margin-bottom: 0.5rem;">🌟 AITuber ルリ</h1>
        <p style="color: #666; font-size: 1.1rem;">戯曲『あいのいろ』から生まれた感情学習AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # レスポンシブ対応のルリ画像表示（コンパクト版）
    image_path = os.path.join(project_root, "assets", "ruri_imageboard.png")
    if os.path.exists(image_path):
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.image(image_path, width="stretch")
    else:
        st.info("🎭 ルリの画像を読み込み中...")
    
    # チャット初期化（履歴復元機能付き）
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # セッションから履歴を復元
        load_chat_history_from_session()
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    # 会話エリア（コンパクト設計）
    
    # 全ユーザーでAI会話機能を利用可能に変更
    st.markdown("### 💬 ルリと話す")
    
    # APIキー確認（非表示）
    has_api_key = False
    try:
        api_keys = UnifiedConfig.get_api_keys()
        has_api_key = bool(api_keys.get('OPENAI_API_KEY'))
    except Exception:
        pass
    
    if not has_api_key and user_level == UserLevel.PUBLIC:
        st.markdown('<span class="status-indicator status-limited">🤖 基本応答モードで動作中</span>', unsafe_allow_html=True)
    elif user_level == UserLevel.OWNER:
        st.markdown('<span class="status-indicator status-active">✅ フル機能モードで動作中</span>', unsafe_allow_html=True)
    
    # チャット履歴の表示（全ユーザー対応・新しいものが上）
    if st.session_state.chat_history:
        st.markdown("#### 📝 会話履歴")
        
        # 履歴表示数を固定（5件）- 新しいものから表示
        display_count = 5
        recent_history = st.session_state.chat_history[-display_count:]
        
        # 新しいものが上に来るように逆順で表示
        for i, (timestamp, user_msg, ruri_msg) in enumerate(reversed(recent_history)):
            st.markdown(f"""
            <div class="chat-message">
                <small style="color: var(--text-secondary); font-weight: 500;">{timestamp}</small><br>
                <strong class="highlight-text">ルリ:</strong> {ruri_msg}<br>
                <strong style="color: var(--text-primary);">あなた:</strong> {user_msg}
            </div>
            """, unsafe_allow_html=True)
    
    # チャット入力（全ユーザー対応）
    with st.form("chat_form", clear_on_submit=True):
        chat_input = st.text_input(
            "ルリにメッセージを送信:",
            placeholder="どうしたの。",
            key="chat_input_field"
        )
        
        # レスポンシブ対応：CSS Media Queryで自動判定
        st.markdown("""
        <style>
        .mobile-layout { display: none; }
        .desktop-layout { display: block; }
        
        @media (max-width: 768px) {
            .mobile-layout { display: block; }
            .desktop-layout { display: none; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # デスクトップ：横並び（常にこのレイアウトを使用、CSSで制御）
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submit_button = st.form_submit_button("▶ 送信", width="stretch")
        with col2:
            clear_history = st.form_submit_button("🗑️ 履歴削除")
        with col3:
            export_chat = st.form_submit_button("📄 エクスポート")
    
    # チャット処理（全ユーザー対応）
    if submit_button and chat_input.strip():
        handle_chat_message(chat_input.strip(), user_level, features)
    
    if clear_history:
        st.session_state.chat_history = []
        st.success("会話履歴を削除しました")
        st.rerun()
    
    if export_chat and st.session_state.chat_history:
        export_chat_history()
    
    # 最小限のフッター（権利表示のみ）
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2rem;'>"
        "原作・企画: ozaki-taisuke（戯曲『あいのいろ』） | アートワーク: まつはち | "
        "<a href='https://github.com/ozaki-taisuke/pupa-Ruri' target='_blank' style='color: #666;'>GitHub</a>"
        "</div>", 
        unsafe_allow_html=True
    )

def handle_chat_message(message: str, user_level: UserLevel, features: Dict[str, bool]):
    """チャットメッセージの処理（履歴管理機能付き）"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # チャット履歴の自動保存設定
    max_history = 50  # 最大保存履歴数
    
    if lazy_import_ai() and features.get("ai_conversation"):
        try:
            # AI応答の生成（遅延インポート）
            from ai_providers import get_configured_provider
            from character_ai import RuriCharacter
            
            provider = get_configured_provider()
            if provider:
                ruri = get_ruri_character()
                ai_response = ruri.generate_response(message)
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
    
    # 最新の会話として統一表示（一時的にハイライト）
    st.markdown(f"""
    <div class="chat-message" style="border-left: 3px solid #00ff9f; background: rgba(0, 255, 159, 0.1);">
        <small style="color: var(--text-secondary); font-weight: 500;">{timestamp} ✨ 最新</small><br>
        <strong class="highlight-text">ルリ:</strong> {ai_response}<br>
        <strong style="color: var(--text-primary);">あなた:</strong> {message}
    </div>
    """, unsafe_allow_html=True)
    
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

def show_auth_page():
    """所有者認証ページ（メインエリア表示）"""
    st.title("🔐 所有者認証")
    
    # 戻るボタン
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← ホームに戻る", width="stretch"):
            st.session_state.show_auth = False
            st.session_state.current_page = 'home'
            st.rerun()
    
    st.markdown("---")
    
    # 認証フォーム
    with st.container():
        st.markdown("### 🔑 認証情報を入力してください")
        
        with st.form("auth_form"):
            username = st.text_input("ユーザー名", placeholder="所有者ユーザー名を入力")
            password = st.text_input("パスワード", type="password", placeholder="パスワードを入力")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("🔐 認証", width="stretch")
            with col2:
                cancel_button = st.form_submit_button("キャンセル", width="stretch")
        
        # 認証処理
        if submit_button:
            if username and password:
                try:
                    auth_handler = UnifiedAuth()
                    success = auth_handler.authenticate(username, password, st.session_state)
                    
                    if success:
                        st.success("✅ 認証に成功しました！")
                        st.session_state.show_auth = False
                        st.session_state.current_page = 'home'
                        st.rerun()
                    else:
                        st.error("❌ 認証に失敗しました。ユーザー名とパスワードを確認してください。")
                except Exception as e:
                    st.error(f"❌ 認証エラー: {str(e)}")
            else:
                st.warning("⚠️ ユーザー名とパスワードを入力してください。")
        
        if cancel_button:
            st.session_state.show_auth = False
            st.session_state.current_page = 'home'
            st.rerun()
    
    # 認証についての説明
    st.markdown("---")
    with st.expander("📖 認証について"):
        st.markdown("""
        **所有者認証について:**
        
        - 所有者として認証されると、全ての機能にアクセスできます
        - AI会話、設定変更、分析機能などが利用可能になります
        - 認証情報は安全に管理されています
        
        **パブリックモードでも利用可能:**
        - 基本的な会話機能は認証なしでも利用できます
        - より高度な機能を使用したい場合は認証してください
        """)

if __name__ == "__main__":
    st.set_page_config(
        page_title="AITuber ルリ - 統一環境",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()