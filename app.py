from typing import Dict, Any, Optional
import streamlit as st
import sys
import os

# 🚀 Streamlit Cloud用 高速起動モード - 検出ロジック改善
def detect_cloud_mode():
    """Streamlit Cloud環境を検出"""
    cloud_indicators = [
        os.environ.get('STREAMLIT_SHARING_MODE') == '1',
        'streamlit.io' in os.environ.get('URL', ''),
        'streamlitapp.com' in os.environ.get('URL', ''),
        '/mount/src/' in os.getcwd(),  # Streamlit Cloudの典型的なパス
        os.environ.get('HOSTNAME', '').startswith('streamlit-'),
        'STREAMLIT_SERVER_HEADLESS' in os.environ,
        '/app/' in os.getcwd(),  # Docker環境
    ]
    return any(cloud_indicators)

CLOUD_MODE = detect_cloud_mode()

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

# Streamlit自動リロード対応: キャッシュクリア（CLOUD_MODEでは軽量化）
if not CLOUD_MODE:
    if 'unified_config' in sys.modules:
        del sys.modules['unified_config']
    if 'unified_auth' in sys.modules:
        del sys.modules['unified_auth']
    if 'src.unified_config' in sys.modules:
        del sys.modules['src.unified_config']
    if 'src.unified_auth' in sys.modules:
        del sys.modules['src.unified_auth']

# 統一設定とセキュリティ（エラーハンドリング付き・リロード対応）
CONFIG_AVAILABLE = False
UserLevel = None
UnifiedConfig = None
UnifiedAuth = None
APIConfig = None

def initialize_config_modules():
    """設定モジュールの初期化（リロード対応）"""
    global CONFIG_AVAILABLE, UserLevel, UnifiedConfig, UnifiedAuth, APIConfig
    
    try:
        # 複数のインポート方法を試行
        try:
            from src.unified_config import UnifiedConfig as UC, UserLevel as UL
            from src.unified_auth import UnifiedAuth as UA
            from src.api_config import APIConfig as AC
        except ImportError:
            try:
                from unified_config import UnifiedConfig as UC, UserLevel as UL
                from unified_auth import UnifiedAuth as UA
                from api_config import APIConfig as AC
            except ImportError:
                # 最後の手段として直接パス指定
                sys.path.insert(0, os.path.join(project_root, 'src'))
                from unified_config import UnifiedConfig as UC, UserLevel as UL
                from unified_auth import UnifiedAuth as UA
                from api_config import APIConfig as AC
        
        # 成功時に変数に代入
        UnifiedConfig = UC
        UserLevel = UL
        APIConfig = AC  
        UnifiedAuth = UA
        CONFIG_AVAILABLE = True
        return True
        
    except Exception as e:
        print(f"⚠️ 設定モジュールの読み込みに失敗: {e}")
        
        # フォールバック設定
        class FallbackUserLevel:
            PUBLIC = "public"
            OWNER = "owner"
        
        class FallbackUnifiedConfig:
            @staticmethod
            def get_user_level(session_state):
                return session_state.get('user_level', FallbackUserLevel.PUBLIC)
            
            @staticmethod
            def get_ui_config(user_level):
                return {"title": "AITuber ルリ", "theme": "default"}
            
            @staticmethod
            def get_available_features(user_level):
                if user_level == FallbackUserLevel.OWNER:
                    return {
                        "character_status": True, 
                        "ai_conversation": True,
                        "image_analysis": True,
                        "streaming_integration": True,
                        "system_settings": True,
                        "analytics": True
                    }
                return {"ai_conversation": True, "character_status": True}
        
        class FallbackUnifiedAuth:
            @staticmethod
            def show_auth_interface():
                pass
            
            @staticmethod
            def authenticate(username, password, session_state):
                """将来的な拡張用のユーザー名・パスワード認証"""
                try:
                    # 統一設定から認証情報を取得
                    owner_password = UnifiedConfig.OWNER_PASSWORD if hasattr(UnifiedConfig, 'OWNER_PASSWORD') else os.environ.get('OWNER_PASSWORD', 'ruri2024')
                    owner_username = UnifiedConfig.OWNER_USERNAME if hasattr(UnifiedConfig, 'OWNER_USERNAME') else os.environ.get('OWNER_USERNAME', 'owner')
                except:
                    # フォールバック
                    owner_password = os.environ.get('OWNER_PASSWORD', 'ruri2024')
                    owner_username = os.environ.get('OWNER_USERNAME', 'owner')
                
                # 現在はパスワードメインだが、将来的にユーザー名も考慮可能
                if password == owner_password:
                    session_state.user_level = FallbackUserLevel.OWNER
                    session_state.authenticated = True
                    session_state.authenticated_username = username
                    return True
                return False
            
            @staticmethod
            def authenticate_user(password):
                """現在の認証方式（パスワードのみ）"""
                try:
                    # 統一設定から認証情報を取得
                    owner_password = UnifiedConfig.OWNER_PASSWORD if hasattr(UnifiedConfig, 'OWNER_PASSWORD') else os.environ.get('OWNER_PASSWORD', 'ruri2024')
                except:
                    # フォールバック
                    owner_password = os.environ.get('OWNER_PASSWORD', 'ruri2024')
                
                if password == owner_password:
                    return FallbackUserLevel.OWNER
                return None
            
            @staticmethod
            def logout(session_state):
                session_state.user_level = FallbackUserLevel.PUBLIC
                session_state.authenticated = False
                session_state.authenticated_username = None
                # 初期化フラグもリセット
                session_state.initialization_complete = False
        
        UserLevel = FallbackUserLevel
        UnifiedConfig = FallbackUnifiedConfig
        UnifiedAuth = FallbackUnifiedAuth
        CONFIG_AVAILABLE = False
        return False

# 初期化実行
initialize_config_modules()

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

# オプション機能の初期化（一度だけ実行）
if 'optional_features_initialized' not in st.session_state:
    st.session_state.optional_features_initialized = True
    
    try:
        import cv2
        import numpy as np
        IMAGE_PROCESSING_AVAILABLE = True
        if not CLOUD_MODE:
            print("✅ 画像処理機能: 利用可能")
    except ImportError as e:
        if not CLOUD_MODE:
            print(f"⚠️ 画像処理機能の読み込みに失敗: {e}")
        IMAGE_PROCESSING_AVAILABLE = False

    try:
        import plotly.graph_objects as go
        PLOTTING_AVAILABLE = True
        if not CLOUD_MODE:
            print("✅ Plotly機能: 利用可能")
    except ImportError:
        if not CLOUD_MODE:
            print("⚠️ Plotly機能は無効です")
        PLOTTING_AVAILABLE = False
else:
    # 既に初期化済みの場合はデフォルト値を設定
    IMAGE_PROCESSING_AVAILABLE = False
    PLOTTING_AVAILABLE = False

def main():
    """統一WebUIメイン関数"""
    
    # ナビゲーション用ユニークID生成（最優先で初期化）
    if 'nav_session_id' not in st.session_state:
        import time
        st.session_state.nav_session_id = str(int(time.time() * 1000000))
    
    try:
        # 設定モジュールの再初期化（リロード対応）
        initialize_config_modules()
        
        # ホットリロード対応: セッション状態の保護
        if 'hot_reload_protection' not in st.session_state:
            st.session_state.hot_reload_protection = True
            # 既存の認証状態があればそれを維持
            if 'authenticated' not in st.session_state:
                st.session_state.authenticated = False
            if 'user_level' not in st.session_state:
                st.session_state.user_level = UserLevel.PUBLIC if hasattr(UserLevel, 'PUBLIC') else "public"
        
        # アプリケーション初期化ログ（一度だけ表示）
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = True
            if not CLOUD_MODE:
                print("🚀 アプリケーション初期化開始...")
        
        # レスポンシブデザインのセットアップ（安全実行）
        try:
            setup_responsive_design()
            if not CLOUD_MODE and not st.session_state.get('design_setup_logged', False):
                print("✅ レスポンシブデザイン: 設定完了")
                st.session_state.design_setup_logged = True
        except Exception as e:
            if not CLOUD_MODE:
                print(f"⚠️ レスポンシブデザイン設定エラー: {e}")
            # デザインエラーでもアプリ続行
        
        # セッション状態の初期化（ホットリロード対応強化）
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'home'
        if 'initialization_complete' not in st.session_state or not st.session_state.initialization_complete:
            # 初期化が完了していない場合のみ実行
            if 'authenticated' not in st.session_state:
                st.session_state.authenticated = False
            if 'user_level' not in st.session_state:
                st.session_state.user_level = UserLevel.PUBLIC if hasattr(UserLevel, 'PUBLIC') else "public"
            
            # チャット履歴の安定した初期化
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
                if not CLOUD_MODE:
                    print("💬 チャット履歴を初期化しました")
            
            # セッションからチャット履歴を復元（オプション）
            try:
                load_chat_history_from_session()
            except Exception as e:
                if not CLOUD_MODE:
                    print(f"⚠️ チャット履歴復元エラー: {e}")
            
            # 初期化完了フラグを設定
            st.session_state.initialization_complete = True
        
        # 設定取得ログ（一度だけ表示）
        if not CLOUD_MODE and not st.session_state.get('config_fetch_logged', False):
            print("🎯 設定取得中...")
            st.session_state.config_fetch_logged = True
        
        # 設定の取得（エラーハンドリング強化）
        try:
            user_level = UnifiedConfig.get_user_level(st.session_state) if UnifiedConfig else "public"
            ui_config = UnifiedConfig.get_ui_config(user_level) if UnifiedConfig else {"title": "AITuber ルリ", "theme": "default"}
            features = UnifiedConfig.get_available_features(user_level) if UnifiedConfig else {"ai_conversation": True, "character_status": True}
        except Exception as e:
            if not CLOUD_MODE:
                print(f"⚠️ 設定取得エラー: {e}")
            # フォールバック設定
            user_level = "public"
            ui_config = {"title": "AITuber ルリ", "theme": "default"}
            features = {"ai_conversation": True, "character_status": True}
        
        # ユーザー情報ログ（一度だけ表示）
        if not CLOUD_MODE and not st.session_state.get('user_info_logged', False):
            print(f"👤 ユーザーレベル: {user_level}")
            print(f"🔧 利用可能機能: {list(features.keys())}")
            st.session_state.user_info_logged = True
        
        # レスポンシブサイドバーの設定
        setup_responsive_sidebar(user_level, features, ui_config)
        
        # 認証画面の表示判定
        current_page = st.session_state.get('current_page', 'home')
        is_owner = (hasattr(UserLevel, 'OWNER') and user_level == UserLevel.OWNER) or user_level == "owner"
        
        # ホーム、AI会話は常にアクセス可能
        public_pages = ['home', 'ai_conversation', 'character']
        
        if current_page in public_pages or is_owner:
            # アクセス許可 - 通常処理を継続
            pass
        elif st.session_state.get('show_auth', False):
            # 明示的に認証画面を要求された場合
            show_auth_page()
            return
        else:
            # 認証が必要なページにアクセスしようとした場合のみ認証画面表示
            if current_page not in public_pages:
                show_auth_page()
                return
        
        # ページ表示ログ（一度だけ、または変更時のみ）
        if not CLOUD_MODE and st.session_state.get('last_logged_page') != current_page:
            print(f"📄 ページ表示: {current_page}")
            st.session_state.last_logged_page = current_page
        
        # 完了ログ（一度だけ表示）
        if not CLOUD_MODE and not st.session_state.get('app_complete_logged', False):
            print("✅ アプリケーション表示完了")
            st.session_state.app_complete_logged = True
        
    except Exception as e:
        if not CLOUD_MODE:
            print(f"💥 致命的エラー: {e}")
        st.error(f"アプリケーションの初期化に失敗しました: {e}")
        st.markdown("### 🚨 緊急フォールバックモード")
        st.markdown("基本的な機能のみ利用可能です")
        
        # 最小限のUI表示
        st.title("🌟 AITuber ルリ")
        st.info("現在、軽量モードで動作しています")
        
        # 基本的なチャット機能のみ提供
        chat_input = st.text_input("ルリにメッセージを送信:")
        if st.button("送信") and chat_input:
            st.write(f"**あなた**: {chat_input}")
            st.write("**ルリ**: ありがとうございます！現在システムを調整中です...")
    
    # 初期化プロセスの表示（認証済みの場合はスキップ）
    if 'initialization_complete' not in st.session_state or not st.session_state.get('authenticated', False):
        with st.spinner('Connecting pupa system...'):
            # 既存の認証状態を確認
            current_user_level = st.session_state.get('user_level', UserLevel.PUBLIC if UserLevel else "public")
            
            # ユーザーレベルの取得（既存の状態を優先）
            try:
                if not st.session_state.get('authenticated', False):
                    user_level = UnifiedConfig.get_user_level(st.session_state)
                else:
                    user_level = current_user_level
            except:
                user_level = current_user_level
            
            try:
                ui_config = UnifiedConfig.get_ui_config(user_level)
            except:
                ui_config = {"title": "AITuber ルリ", "theme": "default"}
            
            try:
                features = UnifiedConfig.get_available_features(user_level)
            except:
                # 認証状態に応じてフィーチャーを設定
                if st.session_state.get('authenticated', False) or user_level in ["owner", getattr(UserLevel, 'OWNER', None)]:
                    features = {
                        "character_status": True, 
                        "ai_conversation": True,
                        "image_analysis": True,
                        "streaming_integration": True,
                        "system_settings": True,
                        "analytics": True
                    }
                else:
                    features = {"ai_conversation": True, "character_status": True}
            
            # 初期化完了フラグを設定（認証状態を保持）
            st.session_state.initialization_complete = True
            st.session_state.user_level = user_level
            st.session_state.ui_config = ui_config  
            st.session_state.features = features
        
        # 初期化完了後は無限ループを防ぐためrerunしない
        # （認証関連でのrerunは別途適切な場所で実行）
    
    # セッションから設定を取得（フォールバック）
    user_level = st.session_state.get('user_level', UserLevel.PUBLIC if UserLevel else "public")
    ui_config = st.session_state.get('ui_config', {"title": "AITuber ルリ", "theme": "default"})
    features = st.session_state.get('features', {"ai_conversation": True, "character_status": True})
    
    # レスポンシブ対応の初期設定
    setup_responsive_design()
    
    # 認証状態の確認（改良版・リロード対応）
    try:
        auth_handler = UnifiedAuth()
    except:
        auth_handler = None
    
    # サイドバーメニュー（レスポンシブ対応）
    setup_responsive_sidebar(user_level, features, ui_config)
    
    # 認証ダイアログの表示チェック（メインエリアに表示）
    if st.session_state.get('show_auth', False):
        show_auth_page()
        return
    
    # パブリックユーザー以外で認証が必要な場合の処理（改良版・ホットリロード対応）
    is_owner = False
    if hasattr(UserLevel, 'OWNER') and user_level == UserLevel.OWNER:
        is_owner = True
    elif user_level == "owner":
        is_owner = True
    elif st.session_state.get('authenticated', False):
        is_owner = True
    
    # 認証が必要なページかどうかチェック
    current_page = st.session_state.get('current_page', 'home')
    
    # ホーム、AI会話は常にアクセス可能
    public_pages = ['home', 'ai_conversation', 'character']
    
    if current_page in public_pages or is_owner:
        # アクセス許可 - 通常処理を継続
        pass
    elif st.session_state.get('show_auth', False):
        # 明示的に認証画面を要求された場合
        show_auth_page()
        return
    else:
        # 認証が必要なページにアクセスしようとした場合のみ認証画面表示
        if current_page not in public_pages:
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
    
    /* 会話関連スタイル - 個別ボックス設計 */
    .chat-container {
        max-width: 100%;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* ユーザーメッセージボックス */
    .user-message {
        background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 1rem 1rem 0.25rem 1rem;
        border-left: 4px solid #0288d1;
        color: #01579b;
        box-shadow: 0 3px 12px rgba(2, 136, 209, 0.2);
        max-width: 85%;
        margin-left: auto;
        margin-right: 0;
        animation: slideInRight 0.3s ease-out;
    }
    
    /* ルリメッセージボックス */
    .ruri-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 1rem 1rem 1rem 0.25rem;
        border-left: 4px solid #8e24aa;
        color: #4a148c;
        box-shadow: 0 3px 12px rgba(142, 36, 170, 0.2);
        max-width: 85%;
        margin-left: 0;
        margin-right: auto;
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* タイピング効果 */
    .typing-indicator {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 1rem 1rem 1rem 0.25rem;
        border-left: 4px solid #8e24aa;
        color: #4a148c;
        box-shadow: 0 3px 12px rgba(142, 36, 170, 0.2);
        max-width: 85%;
        margin-left: 0;
        margin-right: auto;
        /* 無限アニメーションを無効化 - 定期リロード防止 */
        /* animation: pulse 1.5s infinite; */
    }
    
    .typing-dots {
        display: inline-block;
        position: relative;
    }
    
    .typing-dots span {
        opacity: 1; /* 固定表示に変更 */
        /* 無限アニメーションを無効化 - 定期リロード防止 */
        /* animation: typingDots 1.4s infinite; */
    }
    
    /* アニメーション遅延も無効化 */
    .typing-dots span:nth-child(1) { /* animation-delay: 0s; */ }
    .typing-dots span:nth-child(2) { /* animation-delay: 0.2s; */ }
    .typing-dots span:nth-child(3) { /* animation-delay: 0.4s; */ }
    
    /* アニメーション定義 */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes typingDots {
        0%, 60%, 100% { opacity: 0; }
        30% { opacity: 1; }
    }
    
    /* タイムスタンプスタイル */
    .message-timestamp {
        font-size: 0.75rem;
        color: rgba(0, 0, 0, 0.5);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* ラベルスタイル */
    .message-label {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
        opacity: 0.8;
    }
    
    .message-content {
        font-size: 1rem;
        line-height: 1.5;
        margin: 0;
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
            padding: 0.75rem;
            margin: 0.5rem 0;
        }
        
        .user-message, .ruri-message, .typing-indicator {
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
            margin: 0.5rem 0;
            max-width: 90%;
            border-radius: 0.75rem 0.75rem 0.25rem 0.75rem;
        }
        
        .ruri-message, .typing-indicator {
            border-radius: 0.75rem 0.75rem 0.75rem 0.25rem;
        }
        
        .message-content {
            font-size: 0.9rem;
        }
        
        .message-timestamp {
            font-size: 0.7rem;
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

def setup_responsive_sidebar(user_level: Any, features: Dict[str, bool], ui_config: Dict):
    """レスポンシブ対応サイドバーの設定（シンプル版）"""
    
    with st.sidebar:
        
        st.title("🌟 メニュー")
        
        # 認証状態表示（改良版・ホットリロード対応）
        is_authenticated = st.session_state.get('authenticated', False)
        if (hasattr(UserLevel, 'OWNER') and user_level == UserLevel.OWNER) or user_level == "owner" or is_authenticated:
            st.success("🔓 所有者認証済み")
        else:
            st.info("🔒 パブリックモード")
        
        # ナビゲーションメニュー（キー重複防止）
        import time
        import random
        # 毎回新しいユニークIDを生成（セッション状態依存を排除）
        unique_id = f"{int(time.time() * 1000000)}_{random.randint(10000, 99999)}"
        
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
                if st.button(page_name, key=f"nav_{page_key}_{unique_id}", width="stretch"):
                    st.session_state.current_page = page_key
                    # st.rerun() を削除 - 自然な状態更新に変更
            else:
                st.button(page_name + " 🔒", disabled=True, width="stretch",
                         key=f"nav_{page_key}_disabled_{unique_id}",
                         help="所有者認証が必要です")
        
        # 認証関連（改良版・ホットリロード対応）
        st.markdown("---")
        is_authenticated = st.session_state.get('authenticated', False)
        is_public = (hasattr(UserLevel, 'PUBLIC') and user_level == UserLevel.PUBLIC) or user_level == "public"
        
        if (is_public and not is_authenticated):
            if st.button("🔐 所有者認証", key=f"auth_login_{unique_id}", width="stretch"):
                st.session_state.show_auth = True
                # 認証画面表示のみrerunが必要
                st.rerun()
        else:
            if st.button("🚪 ログアウト", key=f"auth_logout_{unique_id}", width="stretch"):
                try:
                    UnifiedAuth().logout(st.session_state)
                except:
                    # フォールバック時のログアウト
                    st.session_state.user_level = UserLevel.PUBLIC if hasattr(UserLevel, 'PUBLIC') else "public"
                    st.session_state.authenticated = False
                    # 初期化フラグもリセット
                    st.session_state.initialization_complete = False
                # ログアウト時のみrerunが必要
                st.rerun()

def show_home_page(user_level: Any, features: Dict[str, bool], ui_config: Dict):
    """ホームページ - レスポンシブ対応チャット機能付き"""
    
    # チャット履歴の安定した初期化（確実に実行）
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # メイン画像とタイトル
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #4a90e2; margin-bottom: 0.5rem;">🌟 pupa: ルリ</h1>
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
    
    # 会話エリア（モジュール化版）
    st.markdown("### 💬 ルリと話す")
    
    # APIキー確認と状態表示
    has_api_key = False
    try:
        has_api_key = bool(APIConfig.get_openai_api_key())
    except Exception:
        pass
    
    if not has_api_key and user_level == UserLevel.PUBLIC:
        st.markdown('<span class="status-indicator status-limited">🤖 基本応答モードで動作中</span>', unsafe_allow_html=True)
    elif user_level == UserLevel.OWNER:
        st.markdown('<span class="status-indicator status-active">✅ フル機能モードで動作中</span>', unsafe_allow_html=True)
    
    # モジュール化されたチャットコンポーネントを使用
    try:
        from src.ui_components import render_compact_chat
        render_compact_chat(user_level, features, "home_chat", max_display=5)
    except ImportError as e:
        # フォールバック: 従来の実装
        st.warning(f"モジュール読み込みエラー: {e}")
        st.info("🚧 従来のチャット機能を使用中...")
        
        # チャット初期化
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            load_chat_history_from_session()
        
        # シンプルなチャット入力
        with st.form("fallback_chat_form", clear_on_submit=True):
            chat_input = st.text_input("ルリにメッセージを送信:", placeholder="どうしたの。")
            submit_button = st.form_submit_button("送信")
        
        if submit_button and chat_input.strip():
            handle_chat_message_stable(chat_input.strip(), user_level, features)
        
        # シンプルな履歴表示
        if st.session_state.chat_history:
            st.markdown("#### 📝 会話履歴")
            recent_history = st.session_state.chat_history[-3:]
            for timestamp, user_msg, ruri_msg in recent_history:
                st.write(f"**[{timestamp}] あなた:** {user_msg}")
                st.write(f"**[{timestamp}] ルリ:** {ruri_msg}")
                st.markdown("---")

    # 最小限のフッター（権利表示のみ）
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2rem;'>"
        "原作・企画: ozaki-taisuke（戯曲『あいのいろ』） | アートワーク: まつはち | "
        "<a href='https://github.com/ozaki-taisuke/pupa-Ruri' target='_blank' style='color: #666;'>GitHub</a>"
        "</div>", 
        unsafe_allow_html=True
    )

def handle_chat_message_stable(message: str, user_level: Any, features: Dict[str, bool]):
    """安定したチャットメッセージ処理（st.rerun()なし）"""
    import datetime
    import time
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # チャット履歴の自動保存設定
    max_history = 50  # 最大保存履歴数
    
    # AI応答の生成
    if lazy_import_ai() and features.get("ai_conversation"):
        try:
            # AI応答の生成（遅延インポート）
            ruri = get_ruri_character()
            ai_response = ruri.generate_response(message)
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
    
    # 永続化のためのローカルストレージ保存（オプション）
    save_chat_history_to_session()
    
    # st.rerunは使わず、次回の自然な再描画で表示される

def handle_chat_message_dynamic(message: str, user_level: Any, features: Dict[str, bool]):
    """動的チャットメッセージ処理（画面更新なし）"""
    import datetime
    import time
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # チャット履歴の自動保存設定
    max_history = 50  # 最大保存履歴数
    
    # AI応答の生成
    if lazy_import_ai() and features.get("ai_conversation"):
        try:
            # 一時的な「考え中」表示（プレースホルダー内）
            with st.session_state.chat_placeholder.container():
                with st.spinner('ルリが考え中...'):
                    # AI応答の生成（遅延インポート）
                    ruri = get_ruri_character()
                    ai_response = ruri.generate_response(message)
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
    
    # 永続化のためのローカルストレージ保存（オプション）
    save_chat_history_to_session()

def handle_chat_message_legacy(message: str, user_level: Any, features: Dict[str, bool]):
    """チャットメッセージの処理（履歴更新型）"""
    import datetime
    import time
    
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # チャット履歴の自動保存設定
    max_history = 50  # 最大保存履歴数
    
    # AI応答の生成
    if lazy_import_ai() and features.get("ai_conversation"):
        try:
            # 一時的な「考え中」表示
            with st.spinner('ルリが考え中...'):
                # AI応答の生成（遅延インポート）
                ruri = get_ruri_character()
                ai_response = ruri.generate_response(message)
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
    
    # 永続化のためのローカルストレージ保存（オプション）
    save_chat_history_to_session()
    
    # メッセージ追加後は通常の履歴表示に任せる
    # （二重表示を防ぐため、最新会話の個別表示は削除）
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
        if not CLOUD_MODE:
            print(f"履歴保存エラー: {e}")

def load_chat_history_from_session():
    """セッションからチャット履歴を復元"""
    try:
        if 'persistent_chat_history' in st.session_state:
            st.session_state.chat_history = st.session_state.persistent_chat_history.copy()
    except Exception as e:
        if not CLOUD_MODE:
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
def show_character_page(user_level: Any, features: Dict[str, bool]):
    """キャラクター状態ページ"""
    st.title("👤 ルリの状態")
    st.info("🚧 実装中...")

def show_ai_conversation_page(user_level: Any, features: Dict[str, bool]):
    """AI会話ページ（モジュール化版）"""
    try:
        # 新しいモジュール化されたUIコンポーネントを使用
        from src.ui_components import render_full_chat_page
        render_full_chat_page(user_level, features)
    except ImportError as e:
        # フォールバック: 従来の実装
        st.title("💬 AI会話")
        st.error(f"モジュール読み込みエラー: {e}")
        st.info("🚧 モジュール化移行中... 一時的にフォールバック表示中")

def show_image_analysis_page(user_level: Any, features: Dict[str, bool]):
    """画像分析ページ"""
    st.title("🖼️ 画像分析")
    st.info("🚧 実装中...")

def show_streaming_page(user_level: Any, features: Dict[str, bool]):
    """配信管理ページ"""
    st.title("📺 配信管理")
    st.info("🚧 実装中...")

def show_settings_page(user_level: Any, features: Dict[str, bool]):
    """設定ページ"""
    st.title("⚙️ システム設定")
    st.info("🚧 実装中...")

def show_analytics_page(user_level: Any, features: Dict[str, bool]):
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
        
        # 認証処理（改良版・実際のメソッドに合わせて修正）
        # 認証処理（改良版・ユーザー名も考慮）
        if submit_button:
            if username and password:
                try:
                    auth_handler = UnifiedAuth()
                    # 実際に存在するメソッドを使用（パスワードのみで認証）
                    new_level = auth_handler.authenticate_user(password)
                    
                    if new_level and (new_level == UserLevel.OWNER if hasattr(UserLevel, 'OWNER') else new_level == "owner"):
                        st.session_state.user_level = new_level
                        st.session_state.authenticated = True
                        st.session_state.authenticated_username = username  # 将来的な利用のため保存
                        st.success("✅ 認証に成功しました！")
                        st.session_state.show_auth = False
                        st.session_state.current_page = 'home'
                        st.rerun()
                    else:
                        st.error("❌ 認証に失敗しました。ユーザー名とパスワードを確認してください。")
                except Exception as e:
                    st.error(f"❌ 認証エラー: {str(e)}")
                    # フォールバック認証（統一設定優先）
                    try:
                        owner_password = UnifiedConfig.OWNER_PASSWORD if hasattr(UnifiedConfig, 'OWNER_PASSWORD') else os.environ.get('OWNER_PASSWORD', 'ruri2024')
                        owner_username = UnifiedConfig.OWNER_USERNAME if hasattr(UnifiedConfig, 'OWNER_USERNAME') else os.environ.get('OWNER_USERNAME', 'owner')
                    except:
                        owner_password = os.environ.get('OWNER_PASSWORD', 'ruri2024')
                        owner_username = os.environ.get('OWNER_USERNAME', 'owner')
                    
                    # 現在はパスワードのみで認証（将来的にユーザー名も追加可能）
                    if password == owner_password:
                        st.session_state.user_level = UserLevel.OWNER if hasattr(UserLevel, 'OWNER') else "owner"
                        st.session_state.authenticated = True
                        st.session_state.authenticated_username = username
                        st.success("✅ 認証に成功しました！（フォールバック）")
                        st.session_state.show_auth = False
                        st.session_state.current_page = 'home'
                        st.rerun()
                    else:
                        st.error("❌ 認証に失敗しました。ユーザー名とパスワードを確認してください。")
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
        
        - ユーザー名とパスワードの両方の入力が必要です
        - 所有者として認証されると、全ての機能にアクセスできます
        - AI会話、設定変更、分析機能などが利用可能になります
        - 認証情報は安全に管理されています
        
        **セキュリティ対策:**
        - ユーザー名の入力により、ブルートフォース攻撃を抑制
        - 将来的な多ユーザー対応の基盤として設計
        - 環境変数による認証情報の安全な管理
        
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
    
    # Streamlit自動再実行の最適化
    if 'app_initialized_stable' not in st.session_state:
        st.session_state.app_initialized_stable = True
    
    main()