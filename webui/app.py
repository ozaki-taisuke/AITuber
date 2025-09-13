# ルリちゃんAITuber管理Web UI
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from character_ai import RuriCharacter, generate_image_prompt_for_ruri
from image_analyzer import RuriImageAnalyzer

def main():
    st.set_page_config(
        page_title="ルリちゃんAITuber管理システム",
        page_icon="🌈",
        layout="wide"
    )
    
    st.title("🌈 ルリちゃんAITuber管理システム")
    st.sidebar.title("メニュー")
    
    # セッション状態でルリちゃんを管理
    if 'ruri' not in st.session_state:
        st.session_state.ruri = RuriCharacter()
    
    menu = st.sidebar.selectbox(
        "機能を選択:",
        ["キャラクター状態", "感情学習", "イメージボード分析", "画像生成プロンプト", "配信設定"]
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

def show_character_status():
    st.header("🎭 ルリちゃんの現在状態")
    
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
    
    st.write("視聴者コメントを入力して、ルリちゃんに新しい感情を学習させましょう。")
    
    emotion = st.selectbox(
        "学習させたい感情:",
        ["喜び", "怒り", "哀しみ", "愛", "驚き", "恐れ", "嫌悪", "期待"]
    )
    
    viewer_comment = st.text_area(
        "視聴者コメント:",
        placeholder="例: ルリちゃん、今日も配信ありがとう！とても楽しいです！"
    )
    
    if st.button("感情学習を実行") and viewer_comment:
        if os.getenv("OPENAI_API_KEY"):
            ruri = st.session_state.ruri
            response = ruri.learn_emotion(emotion, viewer_comment)
            
            st.success(f"感情「{emotion}」を学習しました！")
            st.write("**ルリちゃんの反応:**")
            st.write(response)
            st.write(f"**新しい色彩段階**: {ruri.current_color_stage}")
        else:
            st.error("OpenAI APIキーが設定されていません。")

def show_imageboard_analysis():
    st.header("🎨 イメージボード分析")
    
    imageboard_path = "assets/ruri_imageboard.png"
    
    if os.path.exists(imageboard_path):
        st.image(imageboard_path, caption="ルリちゃんイメージボード", width=400)
        
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
