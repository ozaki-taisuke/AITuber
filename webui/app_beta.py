# ベータ版 WebUI（機能制限版）
import streamlit as st
import sys
import os

# 本番環境設定の読み込み
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 設定とセキュリティ
from src.production_config import ProductionConfig
from src.beta_auth import check_beta_access, show_beta_header, show_beta_feedback

# 基本機能のインポート（エラーハンドリング強化）
AI_AVAILABLE = False
IMAGE_PROCESSING_AVAILABLE = False

try:
    from ai_providers import registry, config_manager, get_configured_provider
    from ai_providers.base_provider import EmotionType, ColorStage
    from character_ai import RuriCharacter
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI機能の読み込みに失敗: {e}")
    AI_AVAILABLE = False

try:
    import cv2
    import numpy as np
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 画像処理機能の読み込みに失敗: {e}")
    IMAGE_PROCESSING_AVAILABLE = False

# プロット機能の条件付き読み込み
PLOTTING_AVAILABLE = False
try:
    import plotly.graph_objects as go
    PLOTTING_AVAILABLE = True
except ImportError:
    print("⚠️ Plotly機能は無効です")

def main():
    """ベータ版メイン関数"""
    
    # ベータ版認証（環境変数で制御）
    if ProductionConfig.BETA_AUTH_REQUIRED:
        if not check_beta_access():
            return
    
    # ページ設定
    st.set_page_config(
        page_title="AITuber ルリ - ベータ版",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ベータ版ヘッダー（認証が有効な場合のみ表示）
    if ProductionConfig.BETA_AUTH_REQUIRED:
        show_beta_header()
    
    # 設定情報の取得
    config = ProductionConfig.get_config()
    
    # サイドバー
    with st.sidebar:
        st.title("🎭 ルリ ベータ版")
        st.markdown("---")
        
        # ベータ版で利用可能な機能
        beta_pages = {
            "🏠 ホーム": "home",
            "👤 キャラクター状態": "character",
            "💬 AI会話テスト": "chat" if config['features']['ai'] else None,
            "🎨 画像分析": "image",
            "📊 統計": "stats",
            "📝 フィードバック": "feedback"
        }
        
        # Noneの項目を除外
        available_pages = {k: v for k, v in beta_pages.items() if v is not None}
        
        selected_page = st.selectbox("📋 ページ選択", list(available_pages.keys()))
        current_page = available_pages[selected_page]
        
        st.markdown("---")
        st.markdown(f"**版本**: {config['app_version']}")
        
        # 機能制限の表示
        st.markdown("### 🚧 制限中の機能")
        st.markdown("""
        - 🎥 OBS連携
        - 📺 配信管理
        - 💾 データ永続化
        - 🔧 高度な設定
        """)
    
    # メインコンテンツ
    if current_page == "home":
        show_home_page(config)
    elif current_page == "character":
        show_character_page()
    elif current_page == "chat":
        show_chat_page()
    elif current_page == "image":
        show_image_page()
    elif current_page == "stats":
        show_stats_page()
    elif current_page == "feedback":
        show_feedback_page()

def show_home_page(config):
    """ホームページ"""
    st.title("🎭 AITuber ルリ - ベータ版へようこそ")
    
    st.markdown("""
    ## 🌟 ベータ版について
    
    戯曲『あいのいろ』の主人公「ルリ」のAITuberシステムをテスト版として公開しています。
    
    ### 📋 現在利用可能な機能
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### ✅ 動作確認済み
        - 👤 キャラクター基本設定の表示
        - 🎨 画像の色彩分析
        - 💬 簡易AI会話機能
        - 📊 基本統計の表示
        """)
    
    with col2:
        st.markdown("""
        #### 🚧 開発中・制限中
        - 🎥 OBS Studio連携
        - 📺 ライブ配信機能
        - 💾 学習データの永続化
        - 🎵 音声合成連携
        """)
    
    # システム状態
    st.markdown("### 🔧 システム状態")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("AI機能", "✅ 有効" if AI_AVAILABLE else "❌ 無効")
    with col2:
        st.metric("環境", "🧪 ベータ" if config['beta_mode'] else "🚀 本番")
    with col3:
        st.metric("デバッグ", "🔍 ON" if config['debug'] else "🔒 OFF")
    with col4:
        available_providers = ProductionConfig.get_available_ai_providers()
        st.metric("AIプロバイダー", len(available_providers))

def show_character_page():
    """キャラクター状態ページ"""
    st.title("👤 ルリの現在の状態")
    
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
            st.write("**最終学習**: ベータ版のため未保存")
        
        return
    
    # AI機能が有効な場合の実際の処理
    try:
        ruri = RuriCharacter()
        
        # キャラクター状態の表示
        st.markdown("### 🎭 現在の状態")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("感情学習段階", ruri.color_stage.value)
        with col2:
            st.metric("学習済み感情数", len(ruri.emotions_learned))
        with col3:
            st.metric("現在の色相", f"{ruri.current_color['h']:.0f}°")
        
        # 感情学習の進行状況
        st.markdown("### 📈 学習進行状況")
        emotions = ["喜び", "怒り", "哀しみ", "愛"]
        progress = len(ruri.emotions_learned) / len(emotions)
        st.progress(progress)
        st.write(f"進行率: {progress*100:.1f}%")
        
    except Exception as e:
        st.error(f"❌ データ読み込みエラー: {e}")

def show_chat_page():
    """AI会話テストページ"""
    st.title("💬 AI会話テスト")
    
    if not AI_AVAILABLE:
        st.warning("⚠️ AI機能が無効です")
        return
    
    st.markdown("### 🤖 ルリとの会話テスト")
    
    # 会話履歴の初期化
    if "beta_chat_history" not in st.session_state:
        st.session_state.beta_chat_history = []
    
    # メッセージ入力
    user_input = st.text_input("ルリに話しかけてみてください:", key="beta_chat_input")
    
    if st.button("💬 送信") and user_input:
        try:
            # 簡易応答（実際のAI連携は制限版では簡略化）
            ruri_response = f"こんにちは！「{user_input}」について、私も学んでみたいです。どんな感情が含まれているのでしょうか？"
            
            # 履歴に追加
            st.session_state.beta_chat_history.append({
                "user": user_input,
                "ruri": ruri_response
            })
            
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ 会話処理エラー: {e}")
    
    # 会話履歴の表示
    if st.session_state.beta_chat_history:
        st.markdown("### 💭 会話履歴")
        for i, chat in enumerate(reversed(st.session_state.beta_chat_history[-5:])):  # 最新5件
            with st.container():
                st.markdown(f"**あなた**: {chat['user']}")
                st.markdown(f"**ルリ**: {chat['ruri']}")
                st.markdown("---")

def show_image_page():
    """画像分析ページ"""
    st.title("🎨 画像の色彩分析")
    
    if not IMAGE_PROCESSING_AVAILABLE:
        st.warning("⚠️ 画像処理ライブラリ（OpenCV）が利用できません")
        st.info("基本的な画像表示機能のみ利用可能です")
    
    st.markdown("### 📸 画像をアップロードして色彩分析")
    
    uploaded_file = st.file_uploader(
        "画像ファイルを選択してください", 
        type=['png', 'jpg', 'jpeg'],
        key="beta_image_upload"
    )
    
    if uploaded_file is not None:
        # 画像表示
        st.image(uploaded_file, caption="アップロード画像", use_column_width=True)
        
        if IMAGE_PROCESSING_AVAILABLE:
            # 実際の画像分析（OpenCVが利用可能な場合）
            try:
                # 簡単な色彩分析
                import cv2
                import numpy as np
                from PIL import Image
                
                # PILで画像を読み込み
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                
                # HSVに変換
                if len(image_array.shape) == 3:
                    hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
                    
                    # 主要色の計算
                    h_mean = np.mean(hsv[:,:,0])
                    s_mean = np.mean(hsv[:,:,1]) / 255 * 100
                    v_mean = np.mean(hsv[:,:,2]) / 255 * 100
                    
                    st.markdown("### 🔍 分析結果")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("主要色相", f"{h_mean:.0f}°", help="画像の主な色相")
                    with col2:
                        st.metric("彩度", f"{s_mean:.1f}%", help="色の鮮やかさ")
                    with col3:
                        st.metric("明度", f"{v_mean:.1f}%", help="色の明るさ")
                else:
                    st.info("グレースケール画像です")
                    
            except Exception as e:
                st.error(f"画像分析エラー: {e}")
                # フォールバック: モック分析
                show_mock_analysis()
        else:
            # OpenCVが利用できない場合のモック分析
            show_mock_analysis()

def show_mock_analysis():
    """依存関係が利用できない場合のモック分析"""
    st.markdown("### 🔍 分析結果（簡易版）")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("主要色相", "180° (青系)", help="画像の主な色相")
    with col2:
        st.metric("彩度", "75%", help="色の鮮やかさ")
    with col3:
        st.metric("明度", "60%", help="色の明るさ")
    
    st.info("🚧 完全な画像分析には追加ライブラリが必要です")

def show_stats_page():
    """統計ページ"""
    st.title("📊 システム統計")
    
    st.markdown("### 📈 ベータ版統計情報")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総アクセス数", "---", help="ベータ版では非対応")
    with col2:
        st.metric("アクティブユーザー", "1", help="現在のセッション")
    with col3:
        st.metric("機能テスト回数", "---", help="ベータ版では非対応")
    with col4:
        st.metric("エラー数", "0", help="現在のセッション")
    
    # 利用可能機能の表示
    st.markdown("### 🔧 利用可能機能")
    
    feature_status = {
        "基本UI": "✅ 利用可能",
        "AI機能": "✅ 利用可能" if AI_AVAILABLE else "❌ 制限あり",
        "画像処理": "✅ 利用可能" if IMAGE_PROCESSING_AVAILABLE else "❌ 制限あり",
        "プロット機能": "✅ 利用可能" if PLOTTING_AVAILABLE else "❌ 制限あり",
    }
    
    for feature, status in feature_status.items():
        st.write(f"**{feature}**: {status}")
    
    st.markdown("### 🔧 技術情報")
    
    tech_info = ProductionConfig.get_config()
    st.json(tech_info)

def show_feedback_page():
    """フィードバックページ"""
    st.title("📝 ベータテストフィードバック")
    show_beta_feedback()

if __name__ == "__main__":
    main()
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2em;'>
        <p>🎭 原作：戯曲『あいのいろ』（ozaki-taisuke） | 🎨 原画：まつはち さん</p>
        <p>🚧 ベータ版 - テスト運用中 | 📧 フィードバックお待ちしています</p>
    </div>
    """, unsafe_allow_html=True)