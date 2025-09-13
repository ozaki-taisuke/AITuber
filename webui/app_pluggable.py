# ルリ AITuber管理Web UI - プラガブルAIアーキテクチャ版
import streamlit as st
import sys
import os
import json
import asyncio
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# プラガブルAIアーキテクチャのインポート
try:
    sys.path.append(os.path.join(project_root, 'src'))
    from ai_providers import registry, config_manager, get_configured_provider
    from ai_providers.base_provider import EmotionType, ColorStage
    from character_ai import RuriCharacter
    AI_SYSTEM_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️  AIシステムインポートエラー: {e}")
    AI_SYSTEM_AVAILABLE = False

# 従来のモジュール（フォールバック用）
try:
    from image_analyzer import RuriImageAnalyzer
    from streaming_integration import StreamingIntegration
    LEGACY_MODULES_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️  一部のモジュールが利用できません: {e}")
    LEGACY_MODULES_AVAILABLE = False

def initialize_ai_system():
    """AIシステムの初期化"""
    if not AI_SYSTEM_AVAILABLE:
        st.error("❌ AIシステムが利用できません")
        return None
    
    # セッション状態でのキャラクター管理
    if 'ruri_character' not in st.session_state:
        # 設定に基づいてプロバイダーを選択
        provider_name = st.session_state.get('selected_provider', None)
        provider_config = st.session_state.get('provider_config', {})
        
        st.session_state.ruri_character = RuriCharacter(
            ai_provider=provider_name,
            provider_config=provider_config
        )
        
        st.success(f"✅ ルリキャラクターを初期化しました (Provider: {st.session_state.ruri_character.provider_name})")
    
    return st.session_state.ruri_character

def main():
    """メインアプリケーション"""
    st.set_page_config(
        page_title="ルリ AITuber管理システム",
        page_icon="🌈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # タイトル
    st.title("🌈 ルリ AITuber管理システム")
    st.caption("戯曲『あいのいろ』主人公ルリのAI実装 - プラガブルAIアーキテクチャ版")
    
    # サイドバー: AIプロバイダー設定
    with st.sidebar:
        st.header("🤖 AI設定")
        
        if AI_SYSTEM_AVAILABLE:
            show_ai_provider_settings()
        else:
            st.error("AIシステムが利用できません")
            return
    
    # メインコンテンツ
    if AI_SYSTEM_AVAILABLE:
        ruri = initialize_ai_system()
        if ruri:
            show_main_interface(ruri)
    else:
        st.error("AIシステムの初期化に失敗しました")

def show_ai_provider_settings():
    """AIプロバイダー設定UI"""
    st.subheader("プロバイダー選択")
    
    # 利用可能なプロバイダー一覧
    available_providers = registry.get_available_providers()
    all_providers = registry.list_providers()
    
    # プロバイダー選択
    provider_options = ["自動選択"] + list(all_providers.keys())
    selected_provider = st.selectbox(
        "AIプロバイダー",
        options=provider_options,
        index=0,
        help="使用するAIライブラリを選択"
    )
    
    if selected_provider != "自動選択":
        st.session_state.selected_provider = selected_provider
    else:
        st.session_state.selected_provider = None
    
    # プロバイダー状態表示
    st.subheader("プロバイダー状態")
    
    for name, class_name in all_providers.items():
        available = name in available_providers
        status_icon = "🟢" if available else "🔴"
        st.text(f"{status_icon} {name} ({class_name})")
    
    # 設定管理
    st.subheader("設定管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("設定リロード"):
            config_manager.load_config()
            st.rerun()
    
    with col2:
        if st.button("デフォルトに戻す"):
            config_manager.reset_to_defaults()
            st.rerun()
    
    # 詳細設定
    with st.expander("詳細設定"):
        show_provider_config_editor()

def show_provider_config_editor():
    """プロバイダー詳細設定エディタ"""
    
    configs = config_manager.get_all_configs()
    
    for provider_name, config in configs.items():
        st.write(f"**{provider_name}**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            enabled = st.checkbox(
                "有効", 
                value=config['enabled'], 
                key=f"enabled_{provider_name}"
            )
            if enabled != config['enabled']:
                config_manager.set_provider_enabled(provider_name, enabled)
        
        with col2:
            priority = st.number_input(
                "優先度", 
                min_value=1, 
                max_value=10, 
                value=config['priority'],
                key=f"priority_{provider_name}"
            )
            if priority != config['priority']:
                config_manager.set_provider_priority(provider_name, priority)
        
        with col3:
            if st.button(f"設定編集", key=f"edit_{provider_name}"):
                show_provider_specific_config(provider_name, config['config'])

def show_provider_specific_config(provider_name: str, config: dict):
    """プロバイダー固有設定"""
    st.subheader(f"{provider_name} 詳細設定")
    
    # JSON編集エリア
    config_json = st.text_area(
        "設定JSON",
        value=json.dumps(config, indent=2, ensure_ascii=False),
        height=200,
        key=f"config_json_{provider_name}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("設定更新", key=f"save_config_{provider_name}"):
            try:
                new_config = json.loads(config_json)
                config_manager.set_provider_config(provider_name, new_config)
                st.success("設定を更新しました")
                st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"JSON形式エラー: {e}")
    
    with col2:
        if st.button("テスト", key=f"test_{provider_name}"):
            test_provider(provider_name)

def test_provider(provider_name: str):
    """プロバイダーのテスト"""
    try:
        provider_config = config_manager.get_provider_config(provider_name)
        test_character = RuriCharacter(provider_name, provider_config)
        
        response = test_character.generate_response("テストメッセージです")
        st.success(f"✅ テスト成功: {response[:100]}...")
        
    except Exception as e:
        st.error(f"❌ テスト失敗: {e}")

def show_main_interface(ruri: RuriCharacter):
    """メインインターフェース"""
    
    # タブメニュー
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 会話", 
        "🎨 感情・色彩", 
        "📊 分析", 
        "🔧 システム", 
        "📚 ドキュメント"
    ])
    
    with tab1:
        show_conversation_interface(ruri)
    
    with tab2:
        show_emotion_color_interface(ruri)
    
    with tab3:
        show_analysis_interface(ruri)
    
    with tab4:
        show_system_interface(ruri)
    
    with tab5:
        show_documentation()

def show_conversation_interface(ruri: RuriCharacter):
    """会話インターフェース"""
    st.header("💬 ルリとの会話")
    
    # 現在の状態表示
    status = ruri.get_character_status()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("プロバイダー", status['provider'])
    
    with col2:
        st.metric("会話回数", status['conversation_count'])
    
    with col3:
        # プロバイダー切り替えボタン
        if st.button("プロバイダー切り替え"):
            available = ruri.get_available_providers()
            if len(available) > 1:
                current_idx = available.index(ruri.provider_name) if ruri.provider_name in available else 0
                next_idx = (current_idx + 1) % len(available)
                next_provider = available[next_idx]
                
                if ruri.switch_ai_provider(next_provider):
                    st.success(f"プロバイダーを {next_provider} に切り替えました")
                    st.rerun()
    
    # 会話履歴表示
    st.subheader("会話履歴")
    
    if hasattr(ruri, 'conversation_history') and ruri.conversation_history:
        for i, conv in enumerate(reversed(ruri.conversation_history[-10:])):  # 最新10件
            with st.container():
                st.text(f"👤 ユーザー: {conv['user']}")
                st.text(f"🌈 ルリ: {conv['assistant']}")
                st.text(f"⏰ {conv.get('timestamp', '時刻不明')}")
                st.divider()
    else:
        st.info("まだ会話がありません。下のテキストボックスから話しかけてみてください！")
    
    # 新しいメッセージ入力
    st.subheader("新しいメッセージ")
    
    user_message = st.text_area(
        "ルリに話しかけてみてください",
        placeholder="こんにちは、ルリ！今日の気分はどう？",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("送信", type="primary"):
            if user_message.strip():
                with st.spinner("ルリが考えています..."):
                    try:
                        response = ruri.generate_response(user_message)
                        st.success("✅ 応答を生成しました")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ エラーが発生しました: {e}")
            else:
                st.warning("メッセージを入力してください")
    
    with col2:
        if st.button("ストリーミング送信"):
            if user_message.strip():
                show_streaming_response(ruri, user_message)

async def show_streaming_response(ruri: RuriCharacter, message: str):
    """ストリーミング応答表示"""
    response_container = st.empty()
    response_text = ""
    
    try:
        async for chunk in ruri.generate_stream_response(message):
            response_text += chunk
            response_container.text(f"🌈 ルリ: {response_text}")
    except Exception as e:
        st.error(f"ストリーミングエラー: {e}")

def show_emotion_color_interface(ruri: RuriCharacter):
    """感情・色彩インターフェース"""
    st.header("🎨 感情学習と色彩変化")
    
    # 感情状態の可視化
    if hasattr(ruri.ai_provider, 'emotion_states'):
        emotion_data = []
        for emotion, state in ruri.ai_provider.emotion_states.items():
            emotion_data.append({
                'emotion': emotion.value,
                'intensity': state.intensity,
                'learned': state.learned
            })
        
        df = pd.DataFrame(emotion_data)
        
        # 感情強度チャート
        fig = px.bar(
            df, 
            x='emotion', 
            y='intensity',
            color='learned',
            title="現在の感情状態",
            color_discrete_map={True: 'lightblue', False: 'lightgray'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 色彩段階表示
        color_info = ruri.ai_provider.get_color_info()
        st.subheader(f"現在の色彩段階: {color_info['stage']}")
        
        # 学習済み感情一覧
        learned_emotions = [emotion for emotion, state in ruri.ai_provider.emotion_states.items() if state.learned]
        if learned_emotions:
            st.write("**学習済み感情:**")
            for emotion in learned_emotions:
                st.write(f"- {emotion.value}")
        else:
            st.info("まだ感情を学習していません")
    
    else:
        st.info("現在のプロバイダーは感情学習をサポートしていません")

def show_analysis_interface(ruri: RuriCharacter):
    """分析インターフェース"""
    st.header("📊 分析とモニタリング")
    
    # システム状態
    status = ruri.get_character_status()
    
    st.subheader("システム状態")
    st.json(status)
    
    # プロバイダー詳細
    if hasattr(ruri, 'ai_provider') and ruri.ai_provider:
        st.subheader("プロバイダー詳細")
        try:
            provider_status = ruri.ai_provider.get_status_info()
            st.json(provider_status)
        except Exception as e:
            st.error(f"プロバイダー状態取得エラー: {e}")
    
    # 全プロバイダーテスト
    st.subheader("全プロバイダーテスト")
    if st.button("全プロバイダーテスト実行"):
        with st.spinner("テスト実行中..."):
            results = ruri.test_all_providers()
            
            for provider, success in results.items():
                status_icon = "✅" if success else "❌"
                st.write(f"{status_icon} {provider}")

def show_system_interface(ruri: RuriCharacter):
    """システム管理インターフェース"""
    st.header("🔧 システム管理")
    
    # 設定エクスポート/インポート
    st.subheader("設定管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("設定エクスポート"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"ai_config_backup_{timestamp}.json"
            config_manager.export_config(export_path)
            st.success(f"設定をエクスポートしました: {export_path}")
    
    with col2:
        uploaded_file = st.file_uploader("設定インポート", type=['json'])
        if uploaded_file and st.button("インポート実行"):
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(uploaded_file.getvalue().decode())
                    config_manager.import_config(f.name)
                st.success("設定をインポートしました")
                st.rerun()
            except Exception as e:
                st.error(f"インポートエラー: {e}")
    
    # 設定概要表示
    st.subheader("現在の設定")
    st.text(config_manager.get_config_summary())

def show_documentation():
    """ドキュメント表示"""
    st.header("📚 ドキュメント")
    
    st.markdown("""
    ## プラガブルAIアーキテクチャについて
    
    このシステムでは、様々なAIライブラリを統一インターフェースで利用できます。
    
    ### 対応プロバイダー
    
    - **Simple**: フォールバック用基本応答システム
    - **Ollama**: ローカルLLM（Llama2等）
    - **GPT-OSS**: OpenAIのオープンソースモデル
    - **OpenAI**: OpenAI API（GPT-3.5/4）
    - **HuggingFace**: HuggingFace Transformers
    
    ### 特徴
    
    1. **動的切り替え**: 実行中にAIプロバイダーを変更可能
    2. **設定管理**: 優先度やパラメーターをGUIで管理
    3. **フォールバック**: 障害時の自動切り替え
    4. **統一API**: プロバイダーに関係なく同じ方法で利用
    
    ### 設定ファイル
    
    `ai_provider_config.json` でプロバイダーの優先度や設定を管理します。
    
    ### 原作設定の継承
    
    戯曲『あいのいろ』の設定は全プロバイダーで共通して適用されます：
    
    - 感情学習による段階的な色彩変化
    - 純粋で好奇心旺盛な性格
    - 哲学的な問いかけへの興味
    """)

if __name__ == "__main__":
    main()
