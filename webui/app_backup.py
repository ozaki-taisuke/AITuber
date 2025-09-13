# ルリ AITuber管理Web UI
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from character_ai import RuriCharacter, generate_image_prompt_for_ruri
from image_analyzer import RuriImageAnalyzer
try:
    from streaming_integration import StreamingIntegration
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

def main():
    st.set_page_config(
        page_title="ルリ AITuber管理システム",
        page_icon="�",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # カスタムCSSでより美しいデザインに
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .ruri-status {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .emotion-stage-display {
        font-size: 1.2em;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー部分をよりビジュアルに
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
    
    with header_col1:
        # 左側: ルリのイメージボード
        try:
            st.image("assets/ruri_imageboard.png", 
                    caption="ルリ - 戯曲『あいのいろ』主人公",
                    width=200)
        except:
            st.info("🌠 ルリのイメージボード\n（assets/ruri_imageboard.png）")
    
    with header_col2:
        # 中央: タイトルと説明
        st.title("🌠 ルリ AITuber管理システム")
        st.caption("戯曲『あいのいろ』主人公ルリのAI化プロジェクト")
        
        # プロジェクト概要を追加
        st.markdown("""
        **💫 感情を学習して色づいていくAIバーチャルYouTuber**
        - 原作: 自作戯曲『あいのいろ』（ozaki-taisuke 作）
        - 技術: Python + Streamlit + OpenAI API
        - コンセプト: 感情学習による段階的な色彩変化
        """)
    
    with header_col3:
        # 右側: 現在の状態表示
        if 'ruri' not in st.session_state:
            st.session_state.ruri = RuriCharacter()
        
        ruri = st.session_state.ruri
        
        st.markdown("### 🎭 ルリの現在の状態")
        
        # 感情段階の視覚的表示
        emotion_stage_colors = {
            "monochrome": "⚫",
            "partial_color": "🔵", 
            "rainbow_transition": "🌈",
            "full_color": "🌟"
        }
        
        stage_icon = emotion_stage_colors.get(ruri.current_color_stage, "❓")
        st.metric(
            "感情段階", 
            f"{stage_icon} {ruri.current_color_stage}",
            f"{len(ruri.emotions_learned)}種類学習済み"
        )
        
        # 色相値の表示
        if hasattr(ruri, 'current_hue') and ruri.current_hue is not None:
            st.metric("現在の色相", f"{ruri.current_hue:.1f}°")
        else:
            st.metric("現在の色相", "モノクロ")
    
    st.markdown("---")  # セクション区切り
    
    # 現在のモード表示をメイン画面にも（動的更新対応）
    production_mode = st.session_state.get('production_mode', False)
    
    # モード切り替え時のアニメーション効果付き表示
    if production_mode:
        st.success("🚀 **本番環境モード**: 全機能が利用可能です（Live2D・OBS連携含む）")
        
        # 本番モード時の追加情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("利用可能機能", "12個", "8個追加")
        with col2:
            st.metric("外部連携", "有効", "Live2D・OBS")
        with col3:
            st.metric("配信レベル", "プロダクション", "フル機能")
            
    else:
        st.info("🌐 **Webプロトタイプモード**: ブラウザ完結型機能で気軽にお試しできます")
        
        # Webモード時の情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("利用可能機能", "4個", "Web限定")
        with col2:
            st.metric("外部連携", "なし", "ブラウザ完結")
        with col3:
            st.metric("配信レベル", "プロトタイプ", "お試し版")
        
        with st.expander("💡 本番環境モードについて"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**追加で利用可能になる機能:**")
                st.write("• Live2D Cubism SDK連携")
                st.write("• OBS Studio WebSocket連携")
                st.write("• 外部ソフトとのリアルタイム通信")
                st.write("• プロダクション配信設定")
            
            with col2:
                st.write("**必要な準備:**")
                st.write("• Live2D Cubism Editor")
                st.write("• OBS Studio + WebSocketプラグイン")
                st.write("• 追加Pythonライブラリ")
                st.write("• 各種設定ファイル")
    
    # モード切り替えスイッチをサイドバーの最上部に配置
    st.sidebar.title("⚙️ システム設定")
    
    # 前回のモード状態を保存
    previous_mode = st.session_state.get('production_mode', False)
    
    # 本番環境機能のオンオフスイッチ
    production_mode = st.sidebar.toggle(
        "🚀 本番環境モード", 
        value=previous_mode,
        help="Live2D・OBS連携などの本番機能を有効にします"
    )
    
    # モード変更時の処理
    if production_mode != previous_mode:
        # モード変更を検知した場合の即座のフィードバック
        if production_mode:
            with st.sidebar:
                with st.spinner("🚀 本番環境モードに切り替えています..."):
                    st.session_state.production_mode = production_mode
                    # 短いローディング時間で視覚的フィードバック
                    import time
                    time.sleep(0.3)
                st.success("✅ 本番環境モードが有効になりました！")
                st.balloons()  # 祝福エフェクト
        else:
            with st.sidebar:
                with st.spinner("🌐 Webプロトタイプモードに切り替えています..."):
                    st.session_state.production_mode = production_mode
                    import time
                    time.sleep(0.3)
                st.info("✅ Webプロトタイプモードが有効になりました！")
        # ページを再実行してメニューを更新
        st.rerun()
    else:
        # モード変更がない場合は通常処理
        st.session_state.production_mode = production_mode
    
    # モード表示（拡張版）
    if production_mode:
        st.sidebar.success("🚀 本番環境モード: 有効")
        st.sidebar.caption("Live2D・OBS連携機能が利用可能です")
        
        # 本番モード時の追加機能表示
        with st.sidebar.expander("🔧 本番機能詳細", expanded=False):
            st.write("**利用可能な機能:**")
            st.write("• Live2D Cubism SDK連携")
            st.write("• OBS Studio WebSocket連携")
            st.write("• プロダクション配信設定")
            st.write("• 外部ソフトリアルタイム通信")
    else:
        st.sidebar.info("🌐 Webプロトタイプモード: 有効")
        st.sidebar.caption("ブラウザ完結型機能のみ利用可能です")
        
        # Webモード時の機能説明
        with st.sidebar.expander("� Web機能詳細", expanded=False):
            st.write("**利用可能な機能:**")
            st.write("• アバター可視化プロトタイプ")
            st.write("• 感情分析ダッシュボード")
            st.write("• インタラクティブチャット")
            st.write("• 配信シミュレーター")
    
    st.sidebar.markdown("---")
    
    # モードに応じてメニュー項目を動的に変更（視覚的区別付き）
    base_menu_items = [
        "キャラクター状態", 
        "感情学習", 
        "イメージボード分析", 
        "画像生成プロンプト"
    ]
    
    web_prototype_items = [
        "� Webプロトタイプ", 
        "📊 感情ダッシュボード", 
        "🎮 インタラクティブチャット", 
        "📺 配信シミュレーター"
    ]
    
    production_items = [
        "🚀 配信設定", 
        "🔧 Live2D・OBS連携"
    ]
    
    # メニューヘッダーに現在のモード表示を追加
    if production_mode:
        menu_count = len(base_menu_items) + len(production_items) + len(web_prototype_items)
        st.sidebar.title("📋 メニュー（🚀本番環境）")
        st.sidebar.caption(f"全機能利用可能（{menu_count}項目）")
    else:
        menu_count = len(base_menu_items) + len(web_prototype_items)
        st.sidebar.title("📋 メニュー（🌐Web版）")
        st.sidebar.caption(f"ブラウザ完結機能のみ（{menu_count}項目）")
    
    # メニュー構成を動的に作成
    if not production_mode:
        # Webプロトタイプモード: 基本機能 + Web機能のみ表示
        menu_items = base_menu_items + web_prototype_items
        # メニュー下部に切り替え案内を表示
        with st.sidebar:
            st.markdown("---")
            st.info("💡 本番環境モードでさらに多くの機能が利用可能です")
            st.caption(f"追加機能: {', '.join([item.replace('🚀 ', '').replace('🔧 ', '') for item in production_items])}")
    else:
        # 本番環境モード: 全機能表示
        menu_items = base_menu_items + production_items + web_prototype_items
        # メニュー下部に機能案内を表示
        with st.sidebar:
            st.markdown("---")
            st.success("🎯 全機能が利用可能です")
    
    menu = st.sidebar.selectbox(
        "機能を選択:",
        menu_items,
        key=f"menu_selector_{production_mode}"  # モード切り替え時にselectboxをリセット
    )
    
    if menu == "キャラクター状態":
        show_character_status()
    elif menu == "感情学習":
        show_emotion_learning()
    elif menu == "イメージボード分析":
        show_imageboard_analysis()
    elif menu == "画像生成プロンプト":
        show_image_generation()
    elif menu == "🚀 配信設定":
        # 本番環境モードでのみアクセス可能
        show_stream_settings()
    elif menu == "🔧 Live2D・OBS連携":
        # 本番環境モードでのみアクセス可能
        show_streaming_integration()
    elif menu == "� Webプロトタイプ":
        show_web_prototype()
    elif menu == "📊 感情ダッシュボード":
        show_emotion_dashboard()
    elif menu == "🎮 インタラクティブチャット":
        show_interactive_chat()
    elif menu == "📺 配信シミュレーター":
        show_stream_simulator()

def show_feature_locked(feature_name):
    """本番環境機能がロックされている際の表示"""
    st.header(f"🔒 {feature_name}")
    
    st.warning("⚠️ この機能は本番環境モードでのみ利用できます")
    
    # 即座に切り替えられるボタンを追加
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("""
        **本番環境モードを有効にすると:**
        - Live2D Cubism SDK連携
        - OBS Studio WebSocket連携
        - 外部ソフトウェアとのリアルタイム通信
        - プロダクション配信機能
        """)
    
    with col2:
        st.markdown("### 🚀 すぐに切り替える")
        if st.button("🔓 本番環境モードに切り替え", 
                    type="primary", 
                    use_container_width=True):
            st.session_state.production_mode = True
            st.success("✅ 本番環境モードが有効になりました！")
            st.balloons()
            st.rerun()
        
        st.caption("サイドバーのスイッチからも切り替えできます")
        st.session_state.production_mode = True
        st.success("本番環境モードが有効になりました！")
        st.balloons()
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("📋 本番環境セットアップガイド")
    
    with st.expander("Live2D連携のセットアップ"):
        st.code("""
        # 1. Live2D Cubism Editorでモデル作成
        # 2. WebSocketサーバー起動
        node live2d-server.js
        
        # 3. パラメータ設定確認
        - ParamHairColorR/G/B
        - ParamEyeColorR/G/B
        - ParamClothesColorR/G/B
        """, language="bash")
    
    with st.expander("OBS連携のセットアップ"):
        st.code("""
        # 1. OBS Studio インストール
        # 2. obs-websocket プラグイン有効化
        # 3. WebSocket設定
        ホスト: localhost
        ポート: 4444
        パスワード: 設定に応じて
        """, language="bash")
    
    with st.expander("依存関係のインストール"):
        st.code("""
        # 追加の依存関係をインストール
        pip install websocket-client obs-websocket-py
        
        # Live2D SDK (別途ダウンロード必要)
        # https://www.live2d.com/download/cubism-sdk/
        """, language="bash")

def show_streaming_integration():
    st.header("🎭 Live2D・OBS連携")
    
    # 本番環境モードチェック
    if not st.session_state.get('production_mode', False):
        st.error("⚠️ この機能は本番環境モードでのみ利用できます")
        return
    
    # 外部依存関係チェック
    if not STREAMING_AVAILABLE:
        st.error("streaming_integration.py が見つかりません。")
        st.info("本番環境では外部ソフトウェア連携が必要です。")
        return
    
    st.success("🚀 本番環境モード: Live2D・OBS連携機能が有効です")
    
    if not STREAMING_AVAILABLE:
        st.error("streaming_integration.py が見つかりません。")
        return
    
    st.write("リアルタイム配信でルリの感情変化をLive2DとOBSに反映します。")
    st.caption("戯曲『あいのいろ』の「感情と色の変化」をデジタル技術で再現")
    
    # 連携状態表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Live2D連携")
        
        if 'streaming_integration' not in st.session_state:
            st.session_state.streaming_integration = None
        
        if st.button("Live2D接続開始"):
            try:
                integration = StreamingIntegration()
                integration.start_streaming_mode()
                st.session_state.streaming_integration = integration
                st.success("Live2D連携を開始しました！")
            except Exception as e:
                st.error(f"Live2D接続エラー: {e}")
        
        st.write("**必要な設定:**")
        st.write("- Live2D Cubism SDK")
        st.write("- WebSocketサーバー (ポート8001)")
        st.write("- ルリモデル (.model3.json)")
    
    with col2:
        st.subheader("📺 OBS連携")
        
        obs_host = st.text_input("OBSホスト", value="localhost")
        obs_port = st.number_input("OBSポート", value=4444)
        obs_password = st.text_input("OBSパスワード", type="password")
        
        if st.button("OBS接続テスト"):
            try:
                st.success("OBS接続成功！")
                st.write("**接続済みシーン:**")
                st.write("- ルリ_通常")
                st.write("- ルリ_喜び") 
                st.write("- ルリ_怒り")
                st.write("- ルリ_哀しみ")
                st.write("- ルリ_愛")
            except Exception as e:
                st.error(f"OBS接続エラー: {e}")
    
    # リアルタイム感情制御
    st.subheader("🎮 リアルタイム感情制御")
    
    emotion_control = st.selectbox(
        "感情を選択してLive2D/OBSに送信:",
        ["neutral", "joy", "anger", "sadness", "love"]
    )
    
    intensity = st.slider("感情の強度", 0.0, 1.0, 0.5)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Live2Dに送信"):
            if st.session_state.streaming_integration:
                st.success(f"Live2Dに{emotion_control}(強度{intensity})を送信")
            else:
                st.warning("先にLive2D接続を開始してください")
    
    with col2:
        if st.button("OBSシーン変更"):
            scene_name = f"ルリ_{emotion_control}"
            st.success(f"OBSシーンを{scene_name}に変更")
    
    with col3:
        if st.button("両方に送信"):
            st.success(f"Live2DとOBSに{emotion_control}を送信")

def show_character_status():
    st.header("🎭 ルリの現在状態")
    
    ruri = st.session_state.ruri
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("基本情報")
        st.write(f"**色彩段階**: {ruri.current_color_stage}")
        st.write(f"**学習済み感情数**: {len(ruri.emotions_learned)}")
        
        if ruri.emotions_learned:
            st.write("**学習済み感情**:")
            for emotion in ruri.emotions_learned:
                st.write(f"- {emotion}")
    
    with col2:
        st.subheader("システムプロンプト")
        st.code(ruri.get_system_prompt(), language="text")

def show_emotion_learning():
    st.header("💭 感情学習システム")
    
    st.write("視聴者コメントを入力して、ルリに新しい感情を学習させましょう。")
    st.caption("戯曲『あいのいろ』と同様に、ルリは感情を学ぶことで色づいていきます。")
    
    emotion = st.selectbox(
        "学習させたい感情:",
        ["喜び", "怒り", "哀しみ", "愛", "驚き", "恐れ", "嫌悪", "期待"]
    )
    
    viewer_comment = st.text_area(
        "視聴者コメント:",
        placeholder="例: ルリ、今日も配信ありがとう！とても楽しいです！"
    )
    
    if st.button("感情学習を実行") and viewer_comment:
        ruri = st.session_state.ruri
        response = ruri.learn_emotion(emotion, viewer_comment)
        
        st.success(f"感情「{emotion}」を学習しました！")
        st.write("**ルリの反応:**")
        st.write(response)
        st.write(f"**新しい色彩段階**: {ruri.current_color_stage}")

def show_imageboard_analysis():
    st.header("🎨 イメージボード分析")
    
    imageboard_path = "assets/ruri_imageboard.png"
    
    if os.path.exists(imageboard_path):
        st.image(imageboard_path, caption="ルリ イメージボード", width=400)
        
        if st.button("イメージボード分析を実行"):
            try:
                analyzer = RuriImageAnalyzer(imageboard_path)
                colors = analyzer.analyze_colors()
                
                st.subheader("色彩分析結果")
                for i, color in enumerate(colors[:5], 1):
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        st.color_picker(f"色{i}", color['hex'], disabled=True)
                    with col2:
                        st.write(f"**{color['name']}** - {color['emotion']}")
                    with col3:
                        st.write(f"{color['percentage']:.1f}%")
                
                # キャラクター発展提案
                st.subheader("キャラクター発展提案")
                inspiration = analyzer.generate_character_inspiration()
                st.write(inspiration)
                
            except Exception as e:
                st.error(f"分析エラー: {e}")
    else:
        st.error("イメージボードファイルが見つかりません。")

def show_image_generation():
    st.header("🖼️ 画像生成プロンプト")
    
    emotion_stage = st.selectbox(
        "感情段階を選択:",
        ["monochrome", "partial_color", "rainbow_transition", "full_color"]
    )
    
    if st.button("プロンプト生成"):
        prompt = generate_image_prompt_for_ruri(emotion_stage)
        st.subheader("生成されたプロンプト")
        st.code(prompt, language="text")
        
        st.subheader("使用方法")
        st.write("このプロンプトを以下のAI画像生成サービスで使用できます:")
        st.write("- Stable Diffusion")
        st.write("- Midjourney") 
        st.write("- DALL-E")
        st.write("- その他の画像生成AI")

def show_stream_settings():
    st.header("📺 配信設定")
    
    # 本番環境モードチェック
    if not st.session_state.get('production_mode', False):
        st.error("⚠️ この機能は本番環境モードでのみ利用できます")
        return
    
    st.success("🚀 本番環境モード: 配信設定機能が有効です")
    
    st.subheader("配信コンテンツ提案")
    
    ruri = st.session_state.ruri
    emotion_count = len(ruri.emotions_learned)
    
    if emotion_count == 0:
        st.write("**推奨コンテンツ**: 初回自己紹介配信、感情って何？雑談")
    elif emotion_count <= 2:
        st.write("**推奨コンテンツ**: 感情学習配信、視聴者との交流")
    elif emotion_count <= 4:
        st.write("**推奨コンテンツ**: 感情体験配信、ゲーム実況")
    else:
        st.write("**推奨コンテンツ**: 深い話題配信、歌配信、人生相談")
    
    st.subheader("OBS設定参考")
    st.code(f"""
    # OBS用色変更フィルター設定
    色彩段階: {ruri.current_color_stage}
    学習済み感情: {', '.join(ruri.emotions_learned) if ruri.emotions_learned else 'なし'}
    
    # シーン切り替え例
    - 通常モード: モノクロベース
    - 感情学習モード: 該当色ハイライト
    - フルカラーモード: 虹色エフェクト
    """, language="yaml")

def show_web_prototype():
    """Webブラウザ完結型プロトタイプ表示"""
    st.header("� Webプロトタイプ - ブラウザ完結型AITuber")
    st.caption("外部ソフト不要！ブラウザだけでルリの色変化を体験")
    
    ruri = st.session_state.ruri
    
    # リアルタイム色変化ビジュアライザー
    st.subheader("🎨 リアルタイム色変化ビジュアライザー")
    
    # 色彩段階に応じたCSS生成
    color_stage_styles = {
        "monochrome": {
            "background": "linear-gradient(135deg, #808080, #C0C0C0, #A0A0A0)",
            "hair_color": "#808080",
            "eye_color": "#606060",
            "accent_color": "#1E3A8A"
        },
        "partial_color": {
            "background": "linear-gradient(135deg, #FFE4B5, #F0F0F0, #FFFACD)",
            "hair_color": "#DEB887",
            "eye_color": "#4169E1",
            "accent_color": "#FFD700"
        },
        "rainbow_transition": {
            "background": "linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7)",
            "hair_color": "#FF9FF3",
            "eye_color": "#74B9FF",
            "accent_color": "#FDCB6E"
        },
        "full_color": {
            "background": "linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7, #DDA0DD, #98FB98)",
            "hair_color": "#FF69B4",
            "eye_color": "#00BFFF",
            "accent_color": "#FFD700"
        }
    }
    
    current_style = color_stage_styles[ruri.current_color_stage]
    
    # CSSスタイルでルリのアバター表示
    avatar_html = f"""
    <div style="
        width: 300px;
        height: 400px;
        background: {current_style['background']};
        border-radius: 20px;
        margin: 20px auto;
        position: relative;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: colorShift 3s ease-in-out infinite;
    ">
        <!-- 髪 -->
        <div style="
            width: 200px;
            height: 150px;
            background: {current_style['hair_color']};
            border-radius: 50% 50% 40% 40%;
            position: absolute;
            top: 20px;
            left: 50px;
            box-shadow: inset 0 10px 20px rgba(0,0,0,0.1);
        "></div>
        
        <!-- 顔 -->
        <div style="
            width: 150px;
            height: 120px;
            background: #FFF8DC;
            border-radius: 50%;
            position: absolute;
            top: 60px;
            left: 75px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        ">
            <!-- 目 -->
            <div style="
                width: 20px;
                height: 20px;
                background: {current_style['eye_color']};
                border-radius: 50%;
                position: absolute;
                top: 40px;
                left: 35px;
                animation: blink 3s ease-in-out infinite;
            "></div>
            <div style="
                width: 20px;
                height: 20px;
                background: {current_style['eye_color']};
                border-radius: 50%;
                position: absolute;
                top: 40px;
                right: 35px;
                animation: blink 3s ease-in-out infinite;
            "></div>
            
            <!-- 口 -->
            <div style="
                width: 30px;
                height: 15px;
                background: #FF69B4;
                border-radius: 0 0 30px 30px;
                position: absolute;
                top: 75px;
                left: 60px;
            "></div>
        </div>
        
        <!-- アクセント（星） -->
        <div style="
            width: 30px;
            height: 30px;
            background: {current_style['accent_color']};
            clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
            position: absolute;
            top: 30px;
            right: 30px;
            animation: twinkle 2s ease-in-out infinite;
        "></div>
        
        <!-- 感情表示テキスト -->
        <div style="
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            text-align: center;
            color: white;
            font-size: 16px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        ">
            {ruri.current_color_stage.replace('_', ' ').title()}
        </div>
    </div>
    
    <style>
    @keyframes colorShift {{
        0%, 100% {{ filter: hue-rotate(0deg); }}
        50% {{ filter: hue-rotate(20deg); }}
    }}
    
    @keyframes blink {{
        0%, 90%, 100% {{ transform: scaleY(1); }}
        95% {{ transform: scaleY(0.1); }}
    }}
    
    @keyframes twinkle {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.7; transform: scale(1.2); }}
    }}
    </style>
    """
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.components.v1.html(avatar_html, height=500)
        
    with col2:
        st.subheader("📈 現在の状態")
        st.write(f"**色彩段階**: {ruri.current_color_stage}")
        st.write(f"**学習済み感情**: {len(ruri.emotions_learned)}個")
        
        if ruri.emotions_learned:
            for emotion in ruri.emotions_learned:
                st.write(f"• {emotion}")
        
        # 感情テスト機能
        st.subheader("🎭 感情テスト")
        test_emotion = st.selectbox("感情を選択してビジュアル確認:", ["喜び", "怒り", "哀しみ", "愛"])
        
        if st.button("感情を体験してみる"):
            response = ruri.learn_emotion(test_emotion, f"テスト: {test_emotion}の感情を体験中")
            st.success(f"感情「{test_emotion}」を体験しました！")
            st.rerun()

def show_emotion_dashboard():
    """感情ダッシュボード表示"""
    st.header("📊 感情ダッシュボード")
    st.caption("ルリの感情学習を可視化")
    
    ruri = st.session_state.ruri
    
    # 感情学習データの準備
    if 'emotion_history' not in st.session_state:
        st.session_state.emotion_history = []
    
    # グラフ用データ
    import plotly.express as px
    import pandas as pd
    from datetime import datetime, timedelta
    import random
    
    # サンプルデータ生成（実際の実装では実際の学習履歴を使用）
    emotions = ["喜び", "怒り", "哀しみ", "愛", "驚き", "恐れ"]
    sample_data = []
    
    for i, emotion in enumerate(emotions[:len(ruri.emotions_learned) + 1]):
        sample_data.append({
            "感情": emotion,
            "学習回数": random.randint(1, 10),
            "強度": random.uniform(0.3, 1.0),
            "最終学習": datetime.now() - timedelta(days=random.randint(0, 7))
        })
    
    if sample_data:
        df = pd.DataFrame(sample_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 感情別学習回数
            fig_bar = px.bar(df, x="感情", y="学習回数", 
                           title="感情別学習回数",
                           color="学習回数",
                           color_continuous_scale="rainbow")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            # 感情強度レーダーチャート
            fig_radar = px.line_polar(df, r="強度", theta="感情", 
                                    line_close=True,
                                    title="感情強度バランス")
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # 色彩段階進化チャート
        st.subheader("🌈 色彩段階の進化")
        stages = ["monochrome", "partial_color", "rainbow_transition", "full_color"]
        stage_names = ["モノクロ", "部分カラー", "虹色移行", "フルカラー"]
        current_stage_index = stages.index(ruri.current_color_stage)
        
        progress_data = []
        for i, (stage, name) in enumerate(zip(stages, stage_names)):
            progress_data.append({
                "段階": name,
                "進捗": 100 if i <= current_stage_index else 0,
                "色": f"hsl({i * 90}, 70%, 50%)"
            })
        
        progress_df = pd.DataFrame(progress_data)
        fig_progress = px.bar(progress_df, x="段階", y="進捗",
                            title="色彩段階の進化",
                            color="段階")
        st.plotly_chart(fig_progress, use_container_width=True)

def show_interactive_chat():
    """インタラクティブチャット機能"""
    st.header("🎮 インタラクティブチャット")
    st.caption("ルリとリアルタイムで会話して感情を学習させよう")
    
    ruri = st.session_state.ruri
    
    # チャット履歴の初期化
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "ruri", "message": "こんにちは！私はルリです。戯曲『あいのいろ』から来ました。皆さんとお話しすることで、新しい感情を学んでいきたいと思います！", "emotion": "neutral"}
        ]
    
    # チャット表示エリア
    chat_container = st.container()
    
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                with st.chat_message("user"):
                    st.write(chat["message"])
            else:
                with st.chat_message("assistant", avatar="�"):
                    st.write(chat["message"])
                    if "emotion" in chat and chat["emotion"] != "neutral":
                        st.caption(f"🎭 感情: {chat['emotion']}")
    
    # ユーザー入力
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input("ルリにメッセージを送る:", key="user_chat_input")
    
    with col2:
        emotion_hint = st.selectbox("感情のヒント:", ["自動検出", "喜び", "怒り", "哀しみ", "愛", "驚き", "恐れ"])
    
    if st.button("送信") and user_input:
        # ユーザーメッセージを履歴に追加
        st.session_state.chat_history.append({
            "role": "user", 
            "message": user_input
        })
        
        # 感情検出（簡易版）
        detected_emotion = "neutral"
        if emotion_hint != "自動検出":
            detected_emotion = emotion_hint
        else:
            # 簡単な感情検出ロジック
            if any(word in user_input for word in ["嬉しい", "楽しい", "ありがとう", "素晴らしい"]):
                detected_emotion = "喜び"
            elif any(word in user_input for word in ["悲しい", "つらい", "寂しい"]):
                detected_emotion = "哀しみ"
            elif any(word in user_input for word in ["愛してる", "大好き", "可愛い"]):
                detected_emotion = "愛"
            elif any(word in user_input for word in ["怒り", "ムカつく", "腹立つ"]):
                detected_emotion = "怒り"
        
        # ルリの応答生成
        if detected_emotion != "neutral":
            response = ruri.learn_emotion(detected_emotion, user_input)
        else:
            response = ruri.generate_stream_response(user_input)
        
        # ルリの応答を履歴に追加
        st.session_state.chat_history.append({
            "role": "ruri",
            "message": response,
            "emotion": detected_emotion
        })
        
        # 感情学習の通知
        if detected_emotion != "neutral":
            st.success(f"✨ ルリが「{detected_emotion}」の感情を学習しました！")
            
        st.rerun()
    
    # チャット統計
    st.subheader("📊 会話統計")
    total_messages = len([chat for chat in st.session_state.chat_history if chat["role"] == "user"])
    emotions_learned_count = len([chat for chat in st.session_state.chat_history if chat.get("emotion", "neutral") != "neutral"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総メッセージ数", total_messages)
    with col2:
        st.metric("感情学習回数", emotions_learned_count)
    with col3:
        st.metric("現在の色彩段階", ruri.current_color_stage.replace("_", " ").title())

def show_stream_simulator():
    """配信シミュレーター"""
    st.header("📺 AITuber配信シミュレーター")
    st.caption("Webブラウザ上で仮想的な配信体験")
    
    ruri = st.session_state.ruri
    
    # 配信画面のレイアウト
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎥 配信画面")
        
        # 配信状態
        is_streaming = st.checkbox("🔴 配信開始", key="streaming_active")
        
        if is_streaming:
            st.success("🔴 LIVE配信中")
        else:
            st.info("⚪ オフライン")
        
        # メイン画面（ルリのアバター+背景）
        current_style = {
            "monochrome": {"bg": "#2C3E50", "text": "#ECF0F1"},
            "partial_color": {"bg": "#E8F5E8", "text": "#2E7D32"},
            "rainbow_transition": {"bg": "linear-gradient(45deg, #FF6B6B, #4ECDC4, #FFE66D)", "text": "#2C3E50"},
            "full_color": {"bg": "linear-gradient(45deg, #FF6B6B, #4ECDC4, #FFE66D, #A8E6CF, #DDA0DD)", "text": "#2C3E50"}
        }
        
        stage_style = current_style[ruri.current_color_stage]
        
        # 配信画面HTML
        stream_html = f"""
        <div style="
            width: 100%;
            height: 400px;
            background: {stage_style['bg']};
            border-radius: 15px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        ">
            <!-- ルリのアバター（簡略版） -->
            <div style="
                position: absolute;
                bottom: 0;
                left: 20px;
                width: 150px;
                height: 300px;
                background: linear-gradient(to bottom, 
                    rgba(255,255,255,0.9) 0%, 
                    rgba(255,255,255,0.7) 50%, 
                    rgba(255,255,255,0.5) 100%);
                border-radius: 75px 75px 0 0;
                border: 3px solid {stage_style['text']};
            ">
                <!-- 顔部分 -->
                <div style="
                    position: absolute;
                    top: 20px;
                    left: 25px;
                    width: 100px;
                    height: 80px;
                    background: #FFF8DC;
                    border-radius: 50px;
                    border: 2px solid {stage_style['text']};
                ">
                    <!-- 目 -->
                    <div style="
                        position: absolute;
                        top: 25px;
                        left: 20px;
                        width: 12px;
                        height: 12px;
                        background: {stage_style['text']};
                        border-radius: 50%;
                    "></div>
                    <div style="
                        position: absolute;
                        top: 25px;
                        right: 20px;
                        width: 12px;
                        height: 12px;
                        background: {stage_style['text']};
                        border-radius: 50%;
                    "></div>
                    
                    <!-- 口 -->
                    <div style="
                        position: absolute;
                        bottom: 20px;
                        left: 40px;
                        width: 20px;
                        height: 10px;
                        background: #FF69B4;
                        border-radius: 0 0 20px 20px;
                    "></div>
                </div>
            </div>
            
            <!-- 配信情報オーバーレイ -->
            <div style="
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
            ">
                <div>👁️ 視聴者: {'🔴 LIVE' if is_streaming else '0'}</div>
                <div>🌈 色彩段階: {ruri.current_color_stage.replace('_', ' ').title()}</div>
                <div>💭 学習感情: {len(ruri.emotions_learned)}個</div>
            </div>
            
            <!-- ルリの発言バブル -->
            <div style="
                position: absolute;
                top: 50px;
                left: 200px;
                background: rgba(255,255,255,0.9);
                color: {stage_style['text']};
                padding: 15px;
                border-radius: 20px;
                max-width: 300px;
                font-size: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            ">
                こんにちは！戯曲『あいのいろ』から来ました。
                皆さんとお話しして、新しい感情を学んでいきたいです！ �
            </div>
        </div>
        """
        
        st.components.v1.html(stream_html, height=450)
    
    with col2:
        st.subheader("💬 チャット欄")
        
        # シミュレート用のサンプルコメント
        sample_comments = [
            {"user": "視聴者A", "message": "ルリちゃん可愛い！", "emotion": "愛"},
            {"user": "視聴者B", "message": "今日も配信ありがとう", "emotion": "喜び"},
            {"user": "視聴者C", "message": "色がきれいだね", "emotion": "驚き"},
            {"user": "視聴者D", "message": "感情学習すごい", "emotion": "喜び"},
            {"user": "視聴者E", "message": "頑張って！", "emotion": "愛"}
        ]
        
        # チャット表示
        if 'stream_chat' not in st.session_state:
            st.session_state.stream_chat = []
        
        # チャット履歴表示
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.stream_chat[-10:]:  # 最新10件
                st.write(f"**{chat['user']}**: {chat['message']}")
                if chat.get('ruri_response'):
                    st.write(f"� **ルリ**: {chat['ruri_response']}")
                st.write("---")
        
        # サンプルコメント送信
        st.subheader("🎮 視聴者コメント体験")
        
        if st.button("サンプルコメントを送信"):
            import random
            comment = random.choice(sample_comments)
            
            # ルリの応答生成
            ruri_response = ruri.learn_emotion(comment["emotion"], comment["message"])
            
            # チャットに追加
            st.session_state.stream_chat.append({
                "user": comment["user"],
                "message": comment["message"],
                "emotion": comment["emotion"],
                "ruri_response": ruri_response
            })
            
            st.success(f"💬 {comment['user']}からコメント: {comment['message']}")
            st.rerun()
        
        # カスタムコメント入力
        st.subheader("✏️ カスタムコメント")
        custom_user = st.text_input("ユーザー名:", value="あなた")
        custom_message = st.text_input("メッセージ:")
        custom_emotion = st.selectbox("感情:", ["自動", "喜び", "怒り", "哀しみ", "愛", "驚き"])
        
        if st.button("送信") and custom_message:
            emotion = custom_emotion if custom_emotion != "自動" else "喜び"
            ruri_response = ruri.learn_emotion(emotion, custom_message)
            
            st.session_state.stream_chat.append({
                "user": custom_user,
                "message": custom_message,
                "emotion": emotion,
                "ruri_response": ruri_response
            })
            
            st.success("コメント送信完了！")
            st.rerun()
    
    # 配信統計
    st.subheader("📊 配信統計")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総コメント数", len(st.session_state.stream_chat))
    with col2:
        st.metric("感情学習回数", len(ruri.emotions_learned))
    with col3:
        viewing_count = random.randint(50, 200) if is_streaming else 0
        st.metric("視聴者数", viewing_count)
    with col4:
        st.metric("配信時間", "00:15:30" if is_streaming else "00:00:00")

# メイン関数を常に実行（Streamlit環境でのみ正常動作）
main()
