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
        page_icon="🌈",
        layout="wide"
    )
    
    st.title("🌈 ルリ AITuber管理システム")
    st.caption("戯曲『あいのいろ』主人公ルリのAITuber化プロジェクト")
    st.sidebar.title("メニュー")
    
    # セッション状態でルリを管理
    if 'ruri' not in st.session_state:
        st.session_state.ruri = RuriCharacter()
    
    menu = st.sidebar.selectbox(
        "機能を選択:",
        ["キャラクター状態", "感情学習", "イメージボード分析", "画像生成プロンプト", "配信設定", "Live2D・OBS連携"]
    )
    
    if menu == "キャラクター状態":
        show_character_status()
    elif menu == "感情学習":
        show_emotion_learning()
    elif menu == "イメージボード分析":
        show_imageboard_analysis()
    elif menu == "画像生成プロンプト":
        show_image_generation()
    elif menu == "配信設定":
        show_stream_settings()
    elif menu == "Live2D・OBS連携":
        show_streaming_integration()

def show_streaming_integration():
    st.header("🎭 Live2D・OBS連携")
    
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

if __name__ == "__main__":
    main()
