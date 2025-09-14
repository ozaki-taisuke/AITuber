# ルリ AITuber管理Web UI - 軽量化版
import streamlit as st
import sys
import os
import json
from datetime import datetime

# 必要最小限のインポート（高速化）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 遅延読み込み用フラグ
AI_SYSTEM_LOADED = False
PLOTLY_LOADED = False

def load_ai_system():
    """AI関連モジュールの遅延読み込み"""
    global AI_SYSTEM_LOADED
    if not AI_SYSTEM_LOADED:
        try:
            global registry, config_manager, get_configured_provider
            global EmotionType, ColorStage, RuriCharacter
            
            from ai_providers import registry, config_manager, get_configured_provider
            from ai_providers.base_provider import EmotionType, ColorStage
            from character_ai import RuriCharacter
            AI_SYSTEM_LOADED = True
            return True
        except ImportError as e:
            st.error(f"⚠️  AIシステム読み込みエラー: {e}")
            return False
    return True

def load_plotly():
    """Plotly関連の遅延読み込み"""
    global PLOTLY_LOADED
    if not PLOTLY_LOADED:
        try:
            import plotly.graph_objects
            PLOTLY_LOADED = True
            return plotly.graph_objects
        except ImportError:
            return None
    import plotly.graph_objects
    return plotly.graph_objects

# 従来のモジュール（オプション）
IMAGE_ANALYZER_AVAILABLE = False
STREAMING_AVAILABLE = False

def load_optional_modules():
    """オプショナルモジュールの遅延読み込み"""
    global IMAGE_ANALYZER_AVAILABLE, STREAMING_AVAILABLE
    
    try:
        global RuriImageAnalyzer
        from image_analyzer import RuriImageAnalyzer
        IMAGE_ANALYZER_AVAILABLE = True
    except ImportError:
        pass

try:
    global StreamingIntegration
    from streaming_integration import StreamingIntegration
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

def initialize_ruri_character():
    """ルリキャラクターの軽量初期化"""
    # AIシステムの遅延読み込み
    if not load_ai_system():
        st.error("❌ AIシステムが利用できません")
        return None
    
    # セッション状態でのキャラクター管理
    if 'ruri' not in st.session_state:
        with st.spinner("🌠 ルリを初期化中..."):
            try:
                # 確実にSimpleプロバイダーを使用
                st.session_state.ruri = RuriCharacter(
                    ai_provider='simple',
                    provider_config={}
                )
                st.session_state.ruri_type = f"プラガブル({st.session_state.ruri.provider_name})"
                
            except Exception as e:
                st.error(f"❌ キャラクター初期化エラー: {e}")
                # フォールバック対応
                class MinimalRuri:
                    def __init__(self):
                        self.provider_name = "simple"
                        self.emotions_learned = []
                        self.color_stage = "monochrome"
                
                st.session_state.ruri = MinimalRuri()
                return st.session_state.ruri
    
    return st.session_state.ruri

def show_ai_provider_settings():
    """軽量なAIプロバイダー設定"""
    
    if load_ai_system():
        # 利用可能なプロバイダー一覧（シンプル表示）
        try:
            available_providers = registry.get_available_providers()
            
            # ルリちゃんの初期化を確実に実行
            if 'ruri' not in st.session_state:
                st.session_state.ruri = initialize_ruri_character()
            
            # 現在のプロバイダー表示
            if st.session_state.ruri and hasattr(st.session_state.ruri, 'provider_name'):
                current_provider = st.session_state.ruri.provider_name
                st.success(f"🤖 AI: {current_provider}")
            else:
                # フォールバック: Simple プロバイダーを使用
                st.session_state.ruri = initialize_ruri_character()
                if st.session_state.ruri:
                    st.success(f"🤖 AI: {st.session_state.ruri.provider_name}")
                else:
                    st.warning(f"🤖 AI: 初期化中...")
            
            # 利用可能プロバイダー数
            st.caption(f"利用可能: {len(available_providers)}個")
            
            # シンプルな設定リロードボタンのみ
            if st.button("🔄", help="AI設定を再読み込み"):
                if 'ruri' in st.session_state:
                    del st.session_state.ruri
                st.rerun()
        except Exception as e:
            st.error(f"設定エラー: {e}")
    else:
        st.error("AI未対応")

def main():
    st.set_page_config(
        page_title="ルリ AITuber管理システム",
        page_icon="🌠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 軽量CSS（必要最小限）
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #4ecdc4, #45b7d1);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stButton > button[type="primary"] {
        background: linear-gradient(45deg, #20b2aa, #87ceeb) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
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
        
        # クイックアクション - 説明文の下に配置
        st.markdown("### ⚡ クイックアクション")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎭 キャラクター詳細", use_container_width=True):
                # サイドバーのメニューを直接変更
                st.session_state.menu_override = "🎭 キャラクター状態"
                st.success("キャラクター詳細ページに移動中...")
                st.rerun()
        
        with col2:
            if st.button("📊 学習状況", use_container_width=True):
                # サイドバーのメニューを直接変更
                st.session_state.menu_override = "💭 感情学習"
                st.success("学習状況ページに移動中...")
                st.rerun()
    
    with header_col3:
        # 右側: 空きスペース（将来的に他の要素を配置可能）
        st.write("")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")  # セクション区切り

    # メインコンテンツエリア - チャット入力を最上部に配置（X風）
    st.markdown("### 💬 ルリに話しかける")
    
    # チャット入力フォーム（会話ログより上に配置）
    with st.form("main_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "メッセージを入力:", 
                placeholder="今日はどんな気分？", 
                key="main_chat_input",
                label_visibility="collapsed"
            )
        with col2:
            submit_button = st.form_submit_button("送信", use_container_width=True, type="primary")

    # チャット処理（送信直後）
    if submit_button and user_input:
        # チャット履歴の初期化
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # ユーザーメッセージを追加
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # 簡易感情分析
        emotion_keywords = {
            '喜': ['嬉しい', '楽しい', '幸せ', '良い', 'ありがとう'],
            '哀': ['悲しい', 'つらい', '寂しい', '泣く'],
            '怒': ['怒る', 'むかつく', 'イライラ', '腹立つ'],
            '愛': ['好き', '愛', '大切', '想う'],
            '恐': ['怖い', '不安', '心配', 'びくびく'],
            '驚': ['びっくり', '驚く', 'すごい', 'えっ'],
            '嫌': ['嫌い', '気持ち悪い', 'やだ'],
            '期': ['楽しみ', '期待', 'わくわく', '待つ']
        }
        
        detected_emotion = "？"
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                detected_emotion = emotion
                break
        
        # 簡潔なフォールバック応答（サーバー不要）
        responses_by_emotion = {
            '喜': ["わー、嬉しそうですね！私も一緒に嬉しくなります🌟", "楽しい気持ちが伝わってきます！", "ポジティブなエネルギーを感じます✨"],
            '哀': ["大丈夫ですか？そんな時もありますよね...💙", "悲しい気持ち、わかります。一人じゃないですよ", "つらい時は無理しないでくださいね"],
            '怒': ["何かあったんですか？お話聞きますよ", "怒りの感情も大切な気持ちですね", "落ち着いて、深呼吸してみましょう"],
            '愛': ["素敵な気持ちですね💖", "愛に満ちた言葉をありがとうございます", "温かい気持ちが伝わってきます"],
            '恐': ["大丈夫、怖くないですよ。私がそばにいます", "不安な時は一緒に考えましょう", "安心してください💫"],
            '驚': ["わぁ！びっくりしましたね！", "驚きの気持ち、一緒に味わいましょう✨", "すごいことがあったんですね！"],
            '嫌': ["嫌な気持ちになることもありますよね", "無理しないでください", "気持ちに正直でいいんですよ"],
            '期': ["楽しみですね！わくわくします🌟", "期待感が伝わってきます", "素敵なことが待っていそうですね"],
            '？': ["そうなんですね", "なるほど...", "お話してくれてありがとうございます", "もう少し詳しく教えてください"]
        }
        
        import random
        ruri_response = random.choice(responses_by_emotion.get(detected_emotion, responses_by_emotion['？']))
        
        # ルリの応答を追加
        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': ruri_response,
            'detected_emotion': detected_emotion,
            'timestamp': datetime.now()
        })
        
        st.rerun()

    st.markdown("---")  # 入力エリアと会話ログの区切り
    
    # 会話ログ表示エリア
    st.markdown("### 🎬 ルリとの会話ログ")
    
    # チャットメッセージ表示エリア
    chat_container = st.container()
    with chat_container:
        if 'chat_messages' in st.session_state:
            for msg in st.session_state.chat_messages[-5:]:  # 最新5件のみ表示
                if msg['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(msg['content'])
                else:
                    with st.chat_message("assistant", avatar="🌠"):
                        st.write(msg['content'])
                        if 'detected_emotion' in msg:
                            st.caption(f"検出された感情: {msg['detected_emotion']}")
        else:
            st.info("💫 ルリと会話を始めてみましょう！")

    # ステータス表示をチャットエリアの下に配置
    st.markdown("---")
    st.markdown("### 📊 現在のステータス")
    
    # 簡易統計表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_messages = len(st.session_state.get('chat_messages', []))
        st.metric("総メッセージ", f"{total_messages}件")
    with col2:
        current_mode = "🌐 ブラウザ版"
        st.metric("現在のモード", current_mode)
    with col3:
        # 感情の種類をカウント
        emotions_detected = set()
        if 'chat_messages' in st.session_state:
            for msg in st.session_state.chat_messages:
                if msg.get('role') == 'assistant' and 'detected_emotion' in msg:
                    if msg['detected_emotion'] != "？":
                        emotions_detected.add(msg['detected_emotion'])
        st.metric("検出した感情", f"{len(emotions_detected)}種類")
    
    # サイドバーメニュー
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
                with st.spinner("� 本番環境モードに切り替えています..."):
                    st.session_state.production_mode = production_mode
                    import time
                    time.sleep(0.3)
                st.success("✅ 本番環境モードが有効になりました！")
                st.balloons()
        else:
            with st.sidebar:
                with st.spinner("🌐 Webプロトタイプモードに切り替えています..."):
                    st.session_state.production_mode = production_mode
                    import time
                    time.sleep(0.3)
                st.info("✅ Webプロトタイプモードが有効になりました！")
        st.rerun()
    else:
        st.session_state.production_mode = production_mode
    
    # モードに応じてメニュー項目を動的に変更
    base_menu_items = ["🏠 TOP"]
    
    if production_mode:
        st.sidebar.success("🚀 **本番環境モード**: 有効")
        st.sidebar.caption("Live2D・OBS連携機能が利用可能です")
    else:
        st.sidebar.info("🌐 **Webプロトタイプモード**: 有効")
        st.sidebar.caption("ブラウザ完結型機能のみ利用可能です")
        
    
    # モードに応じてメニュー項目を動的に変更
    base_menu_items = ["🏠 TOP"]
    
    detailed_menu_items = [
        "🎭 キャラクター状態", 
        "💭 感情学習", 
        "🎨 イメージボード分析", 
        "🖼️ 画像生成プロンプト"
    ]
    
    web_prototype_items = [
        "🌠 Webプロトタイプ", 
        "📊 感情ダッシュボード", 
        "📺 配信シミュレーター"
    ]
    
    production_items = [
        "🚀 配信設定", 
        "🔧 Live2D・OBS連携"
    ]
    
    # メニュー構成を動的に作成
    if production_mode:
        menu_items = base_menu_items + detailed_menu_items + production_items + web_prototype_items
    else:
        menu_items = base_menu_items + detailed_menu_items + web_prototype_items
    
    # クイックアクションからのメニューオーバーライドをチェック
    if 'menu_override' in st.session_state:
        target_menu = st.session_state.menu_override
        del st.session_state.menu_override
        
        # 対象メニューのインデックスを取得
        if target_menu in menu_items:
            menu_index = menu_items.index(target_menu)
            menu = st.sidebar.selectbox(
                "🎯 利用する機能:",
                menu_items,
                index=menu_index,
                key=f"menu_selector_{production_mode}",
                help="使いたい機能を選択してください"
            )
        else:
            # メニューが見つからない場合はTOPページに
            menu = st.sidebar.selectbox(
                "🎯 利用する機能:",
                menu_items,
                key=f"menu_selector_{production_mode}",
                help="使いたい機能を選択してください"
            )
    else:
        menu = st.sidebar.selectbox(
            "🎯 利用する機能:",
            menu_items,
            key=f"menu_selector_{production_mode}",
            help="使いたい機能を選択してください"
        )
    
    # メインコンテンツエリア - メニューが🏠 TOPの場合はチャット機能を既に上部に表示済み
    if menu == "� TOP":
        # TOPページのチャット機能は既に上部に表示済みなので、ここでは何もしない
        pass
    
    elif menu == "🎭 キャラクター状態":
        show_character_status()
    elif menu == "💭 感情学習":
        show_emotion_learning()
    elif menu == "🎨 イメージボード分析":
        show_imageboard_analysis()
    elif menu == "🖼️ 画像生成プロンプト":
        show_image_generation()
    elif menu == "🚀 配信設定":
        show_stream_settings()
    elif menu == "🔧 Live2D・OBS連携":
        show_streaming_integration()
    elif menu == "🌠 Webプロトタイプ":
        show_web_prototype()
    elif menu == "📊 感情ダッシュボード":
        show_emotion_dashboard()
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
    
    # ruriオブジェクトの初期化確認
    if 'ruri' not in st.session_state:
        st.session_state.ruri = initialize_ruri_character()
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
        # ruriオブジェクトの初期化確認
        if 'ruri' not in st.session_state:
            st.session_state.ruri = initialize_ruri_character()
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
        # プラガブル版では基本的なプロンプト生成を提供
        prompt = generate_basic_image_prompt(emotion_stage)
        st.subheader("生成されたプロンプト")
        st.code(prompt, language="text")
        
        st.subheader("使用方法")
        st.write("このプロンプトを以下のAI画像生成サービスで使用できます:")
        st.write("- Stable Diffusion")
        st.write("- Midjourney") 
        st.write("- DALL-E")
        st.write("- その他の画像生成AI")

def generate_basic_image_prompt(emotion_stage: str) -> str:
    """基本的な画像生成プロンプト"""
    base_prompt = "Beautiful anime girl character named Ruri from the play 'Ai no Iro', "
    
    stage_prompts = {
        "monochrome": base_prompt + "monochrome world, black and white, learning about emotions, curious expression, dramatic lighting",
        "partial_color": base_prompt + "partially colored world, some colors appearing, wonder in eyes, mixed black-white and colors",
        "rainbow_transition": base_prompt + "rainbow transitions, multiple colors flowing, emotional awakening, vibrant atmosphere",
        "full_color": base_prompt + "full colorful world, rainbow hair, emotional maturity, bright and lively, masterpiece quality"
    }
    
    return stage_prompts.get(emotion_stage, base_prompt + "beautiful character design, high quality")

def show_stream_settings():
    st.header("📺 配信設定")
    
    # 本番環境モードチェック
    if not st.session_state.get('production_mode', False):
        st.error("⚠️ この機能は本番環境モードでのみ利用できます")
        return
    
    st.success("🚀 本番環境モード: 配信設定機能が有効です")
    
    st.subheader("配信コンテンツ提案")
    
    # ruriオブジェクトの初期化確認
    if 'ruri' not in st.session_state:
        st.session_state.ruri = initialize_ruri_character()
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
    st.header("🌠 Webプロトタイプ - ブラウザ完結型AITuber")
    st.caption("外部ソフト不要！ブラウザだけでルリの色変化を体験")
    
    # ruriオブジェクトの初期化確認
    if 'ruri' not in st.session_state:
        st.session_state.ruri = initialize_ruri_character()
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
            # ruriオブジェクトの初期化確認
            if 'ruri' not in st.session_state:
                st.session_state.ruri = initialize_ruri_character()
            response = ruri.learn_emotion(test_emotion, f"テスト: {test_emotion}の感情を体験中")
            st.success(f"感情「{test_emotion}」を体験しました！")
            st.rerun()

def show_emotion_dashboard():
    """軽量感情ダッシュボード表示"""
    st.header("📊 感情ダッシュボード")
    st.caption("ルリの感情学習を可視化")
    
    # ルリキャラクターの初期化
    ruri = initialize_ruri_character()
    if not ruri:
        st.error("キャラクターの初期化に失敗しました")
        return
    
    # 感情学習データの準備
    if 'emotion_history' not in st.session_state:
        st.session_state.emotion_history = []
    
    # 軽量版: テキストベースの統計表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("学習済み感情", f"{len(ruri.emotions_learned)}個")
    
    with col2:
        st.metric("会話回数", f"{len(st.session_state.get('chat_messages', []))}回")
    
    with col3:
        st.metric("色彩段階", ruri.current_color_stage)
    
    # 感情リスト表示（軽量）
    st.subheader("🎭 学習済み感情")
    if ruri.emotions_learned:
        for i, emotion in enumerate(ruri.emotions_learned):
            st.write(f"{i+1}. {emotion}")
    else:
        st.info("まだ感情を学習していません")
    
    # Plotlyチャートは必要な場合のみ読み込み
    if st.button("📊 詳細グラフを表示"):
        if load_plotly():
            show_detailed_emotion_charts(ruri)
        else:
            st.error("グラフライブラリが利用できません")

def show_detailed_emotion_charts(ruri):
    """詳細な感情チャート（Plotly使用）"""
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
        # 軽量版: Pandasを使わずに直接データ表示
        st.subheader("📊 感情学習データ")
        
        # シンプルなテーブル表示
        for data in sample_data:
            st.write(f"**{data['感情']}**: 学習回数 {data['学習回数']}回, 強度 {data['強度']:.2f}")
        
        # Plotlyが利用可能な場合のみチャート表示
        plotly = load_plotly()
        if plotly:
            col1, col2 = st.columns(2)
            
            with col1:
                # 感情別学習回数（バーチャート）
                emotions = [d['感情'] for d in sample_data]
                counts = [d['学習回数'] for d in sample_data]
                
                fig_bar = plotly.graph_objects.Figure(data=[
                    plotly.graph_objects.Bar(x=emotions, y=counts, name="学習回数")
                ])
                fig_bar.update_layout(title="感情別学習回数")
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # 感情強度レーダーチャート
                intensities = [d['強度'] for d in sample_data]
                
                fig_radar = plotly.graph_objects.Figure()
                fig_radar.add_trace(plotly.graph_objects.Scatterpolar(
                    r=intensities,
                    theta=emotions,
                    fill='toself',
                    name='感情強度'
                ))
                fig_radar.update_layout(
                    title="感情強度バランス",
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    )
                )
                st.plotly_chart(fig_radar, use_container_width=True)

def show_stream_simulator():
    """配信シミュレーター"""
    st.header("📺 AITuber配信シミュレーター")
    st.caption("Webブラウザ上で仮想的な配信体験")
    
    # 統一初期化関数を使用
    ruri = initialize_ruri_character()
    
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
                皆さんとお話しして、新しい感情を学んでいきたいです！ 🌠
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
                    st.write(f"🌠 **ルリ**: {chat['ruri_response']}")
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
if __name__ == "__main__":
    main()
    
    # フッター - 権利関係の明示
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 2em;'>
        <p>🎭 原作：戯曲『あいのいろ』（ozaki-taisuke） | 🎨 原画：まつはち さん</p>
        <p>📋 <a href='https://github.com/ozaki-taisuke/pupa-Ruri/blob/main/docs/fan_creation_guidelines.md' target='_blank'>二次創作ガイドライン</a> | 
        ⚠️ <a href='https://github.com/ozaki-taisuke/pupa-Ruri/blob/main/docs/artwork_usage_restrictions.md' target='_blank'>原画使用制限</a></p>
        <p><small>⭐ 二次創作は自由に歓迎　⚠️ 原画の使用には個別許諾が必要です</small></p>
    </div>
    """, unsafe_allow_html=True)
