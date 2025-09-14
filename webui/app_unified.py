# 統一WebUI - 全環境対応版
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
    
    # ページ設定
    st.set_page_config(
        page_title=f"{UnifiedConfig.APP_NAME}{ui_config['title_suffix']}",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded" if ui_config['sidebar_expanded'] else "collapsed"
    )
    
    # カスタムCSS（ユーザーレベルに応じたテーマ）
    apply_custom_theme(ui_config)
    
    # サイドバー
    with st.sidebar:
        st.title(f"🎭 {UnifiedConfig.APP_NAME}")
        st.markdown(f"**Version**: {UnifiedConfig.APP_VERSION}")
        
        # 認証インターフェース
        UnifiedAuth.show_auth_interface()
        
        # ナビゲーションメニュー
        st.markdown("---")
        st.markdown("### 📋 メニュー")
        
        nav_menu = UnifiedConfig.get_navigation_menu(user_level)
        menu_options = [f"{item['icon']} {item['title']}" for item in nav_menu]
        
        selected_index = st.selectbox(
            "ページ選択", 
            range(len(menu_options)),
            format_func=lambda x: menu_options[x],
            key="navigation"
        )
        
        current_page = nav_menu[selected_index]["page"]
        
        # 機能制限の表示
        show_feature_restrictions(user_level, features)
    
    # メインコンテンツ
    display_main_content(current_page, user_level, features, ui_config)

def apply_custom_theme(ui_config):
    """ユーザーレベルに応じたカスタムテーマ"""
    theme_css = f"""
    <style>
    .stApp > header {{
        background-color: {ui_config['header_color']};
    }}
    
    .main-header {{
        background: linear-gradient(90deg, {ui_config['header_color']}, {ui_config['header_color']}99);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
    }}
    
    .level-badge {{
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background: rgba(255,255,255,0.2);
        border-radius: 1rem;
        font-size: 0.8rem;
        margin-left: 1rem;
    }}
    
    .feature-locked {{
        opacity: 0.5;
        pointer-events: none;
    }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

def show_feature_restrictions(user_level: UserLevel, features: Dict[str, bool]):
    """機能制限の表示"""
    st.markdown("### 🔓 利用可能機能")
    
    feature_categories = {
        "基本機能": ["character_display", "basic_ui", "image_upload"],
        "ベータ機能": ["ai_chat", "emotion_learning", "advanced_image_analysis"],
        "開発者機能": ["obs_integration", "streaming_features", "api_access"],
        "管理者機能": ["user_management", "system_settings", "analytics"]
    }
    
    for category, feature_list in feature_categories.items():
        if any(features.get(f, False) for f in feature_list):
            st.markdown(f"**{category}**")
            for feature in feature_list:
                if feature in features:
                    status = "✅" if features[feature] else "🔒"
                    st.markdown(f"  {status} {feature.replace('_', ' ').title()}")

def display_main_content(page: str, user_level: UserLevel, features: Dict[str, bool], ui_config: Dict):
    """メインコンテンツの表示"""
    
    # ヘッダー
    level_names = {
        UserLevel.PUBLIC: "一般公開版",
        UserLevel.BETA: "ベータ版",
        UserLevel.DEVELOPER: "開発者版",
        UserLevel.ADMIN: "管理者版"
    }
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🎭 AITuber ルリ</h1>
        <span class="level-badge">{level_names[user_level]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ページ別コンテンツ
    if page == "home":
        show_home_page(user_level, features, ui_config)
    elif page == "character":
        show_character_page(user_level, features)
    elif page == "image":
        show_image_page(user_level, features)
    elif page == "chat":
        if UnifiedAuth.require_level(UserLevel.BETA):
            show_chat_page(user_level, features)
    elif page == "stats":
        if UnifiedAuth.require_level(UserLevel.BETA):
            show_stats_page(user_level, features)
    elif page == "obs":
        if UnifiedAuth.require_level(UserLevel.DEVELOPER):
            show_obs_page(user_level, features)
    elif page == "streaming":
        if UnifiedAuth.require_level(UserLevel.DEVELOPER):
            show_streaming_page(user_level, features)
    elif page == "settings":
        if UnifiedAuth.require_level(UserLevel.DEVELOPER):
            show_settings_page(user_level, features)
    elif page == "users":
        if UnifiedAuth.require_level(UserLevel.ADMIN):
            show_user_management_page(user_level, features)
    elif page == "logs":
        if UnifiedAuth.require_level(UserLevel.ADMIN):
            show_logs_page(user_level, features)

def show_home_page(user_level: UserLevel, features: Dict[str, bool], ui_config: Dict):
    """ホームページ"""
    st.title("🌟 ようこそ")
    
    st.markdown(f"""
    ## 🎭 AITuber ルリ について
    
    戯曲『あいのいろ』の主人公「ルリ」のAITuberシステムです。
    
    **現在のアクセスレベル**: {user_level.value.title()}
    """)
    
    # 利用可能機能の概要
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ 利用可能機能")
        available_features = [k.replace('_', ' ').title() for k, v in features.items() if v]
        for feature in available_features[:5]:  # 最初の5個を表示
            st.write(f"• {feature}")
    
    with col2:
        st.markdown("### 🎯 次のレベルで解放される機能")
        if user_level == UserLevel.PUBLIC:
            st.write("• AI会話機能")
            st.write("• 感情学習システム")
            st.write("• 高度な画像分析")
        elif user_level == UserLevel.BETA:
            st.write("• OBS Studio連携")
            st.write("• 配信管理機能")
            st.write("• API アクセス")
        elif user_level == UserLevel.DEVELOPER:
            st.write("• ユーザー管理")
            st.write("• システム設定")
            st.write("• 分析レポート")
    
    # システム状態
    if ui_config['show_technical_details']:
        st.markdown("### 🔧 システム状態")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("AI機能", "✅ 有効" if AI_AVAILABLE else "❌ 無効")
        with col2:
            st.metric("画像処理", "✅ 有効" if IMAGE_PROCESSING_AVAILABLE else "❌ 無効")
        with col3:
            st.metric("プロット機能", "✅ 有効" if PLOTTING_AVAILABLE else "❌ 無効")
        with col4:
            st.metric("環境", UnifiedConfig.ENVIRONMENT.title())

def show_character_page(user_level: UserLevel, features: Dict[str, bool]):
    """キャラクター状態ページ"""
    st.title("👤 ルリの状態")
    
    if not AI_AVAILABLE:
        st.warning("⚠️ AI機能が無効のため、基本情報のみ表示されます")
        
        # モックデータでの表示
        st.markdown("### 🎭 基本情報")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**名前**: ルリ")
            st.write("**状態**: 感情学習中")
            st.write("**段階**: 第1段階（喜び学習中）")
        with col2:
            st.write("**色彩段階**: モノクロ → 部分カラー")
            st.write("**学習済み感情**: 1/4")
            st.write("**最終学習**: 統合版テスト中")
        
        return
    
    # 実際のキャラクター情報（AI機能が有効な場合）
    try:
        if features.get("emotion_learning"):
            ruri = RuriCharacter()
            
            st.markdown("### 🎭 現在の状態")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("感情学習段階", ruri.color_stage.value)
            with col2:
                st.metric("学習済み感情数", len(ruri.emotions_learned))
            with col3:
                st.metric("現在の色相", f"{ruri.current_color['h']:.0f}°")
        else:
            st.info("🔒 詳細な感情学習情報にはベータレベル以上が必要です")
            
    except Exception as e:
        st.error(f"❌ データ読み込みエラー: {e}")

def show_image_page(user_level: UserLevel, features: Dict[str, bool]):
    """画像分析ページ"""
    st.title("🎨 画像分析")
    
    uploaded_file = st.file_uploader(
        "画像ファイルを選択してください", 
        type=['png', 'jpg', 'jpeg'],
        key="unified_image_upload"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="アップロード画像", use_column_width=True)
        
        if features.get("advanced_image_analysis") and IMAGE_PROCESSING_AVAILABLE:
            # 高度な画像分析
            try:
                import cv2
                import numpy as np
                from PIL import Image
                
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                
                if len(image_array.shape) == 3:
                    hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
                    
                    h_mean = np.mean(hsv[:,:,0])
                    s_mean = np.mean(hsv[:,:,1]) / 255 * 100
                    v_mean = np.mean(hsv[:,:,2]) / 255 * 100
                    
                    st.markdown("### 🔍 詳細分析結果")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("主要色相", f"{h_mean:.0f}°")
                    with col2:
                        st.metric("彩度", f"{s_mean:.1f}%")
                    with col3:
                        st.metric("明度", f"{v_mean:.1f}%")
                        
            except Exception as e:
                st.error(f"画像分析エラー: {e}")
        else:
            # 基本分析
            st.markdown("### 🔍 基本分析結果")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("主要色相", "推定値")
            with col2:
                st.metric("彩度", "推定値")
            with col3:
                st.metric("明度", "推定値")
            
            if not features.get("advanced_image_analysis"):
                st.info("🔒 詳細な画像分析にはベータレベル以上が必要です")

def show_chat_page(user_level: UserLevel, features: Dict[str, bool]):
    """AI会話ページ"""
    st.title("💬 AI会話")
    st.write("🤖 ルリとの会話機能（ベータ版）")
    
    # 簡易実装
    user_input = st.text_input("メッセージを入力してください:")
    if st.button("送信") and user_input:
        st.write(f"**ルリ**: こんにちは！「{user_input}」について、もっと教えてくださいね。")

def show_stats_page(user_level: UserLevel, features: Dict[str, bool]):
    """統計ページ"""
    st.title("📊 統計情報")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総セッション数", "12")
    with col2:
        st.metric("平均利用時間", "15分")
    with col3:
        st.metric("機能利用率", "85%")

def show_obs_page(user_level: UserLevel, features: Dict[str, bool]):
    """OBS連携ページ"""
    st.title("🎥 OBS Studio連携")
    st.info("🚧 開発者機能 - OBS連携設定")

def show_streaming_page(user_level: UserLevel, features: Dict[str, bool]):
    """配信管理ページ"""
    st.title("📺 配信管理")
    st.info("🚧 開発者機能 - 配信管理システム")

def show_settings_page(user_level: UserLevel, features: Dict[str, bool]):
    """設定ページ"""
    st.title("⚙️ システム設定")
    st.info("🚧 開発者機能 - システム設定")

def show_user_management_page(user_level: UserLevel, features: Dict[str, bool]):
    """ユーザー管理ページ"""
    st.title("👥 ユーザー管理")
    st.info("🚧 管理者機能 - ユーザー管理システム")

def show_logs_page(user_level: UserLevel, features: Dict[str, bool]):
    """ログページ"""
    st.title("📋 システムログ")
    st.info("🚧 管理者機能 - ログビューア")

if __name__ == "__main__":
    main()
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2em;'>
        <p>🎭 原作：戯曲『あいのいろ』（ozaki-taisuke） | 🎨 原画：まつはち さん</p>
        <p>📋 <a href='https://github.com/ozaki-taisuke/pupa-Ruri/blob/main/docs/fan_creation_guidelines.md' target='_blank'>二次創作ガイドライン</a> | 
        ⚠️ <a href='https://github.com/ozaki-taisuke/pupa-Ruri/blob/main/docs/artwork_usage_restrictions.md' target='_blank'>原画使用制限</a></p>
        <p><small>⭐ 統合環境版 - 認証レベルに応じて機能が動的に変化します</small></p>
    </div>
    """, unsafe_allow_html=True)