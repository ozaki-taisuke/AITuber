"""
チャット関連のStreamlit UIコンポーネント

このモジュールは、チャット機能のUI要素を再利用可能な形で提供します。
- チャット履歴表示
- メッセージ入力フォーム
- エクスポート機能
- レスポンシブデザイン対応
- 感情学習による色彩変化システム
"""
from typing import Dict, Any, Optional, List
import streamlit as st
import time

try:
    from src.chat_manager import get_chat_manager, get_ai_generator, handle_chat_message, ChatMessage
    from src.emotion_system import EmotionSystem, EmotionType, ColorStage
    EMOTION_SYSTEM_AVAILABLE = True
except ImportError:
    EMOTION_SYSTEM_AVAILABLE = False
    print("⚠️ 感情システムまたはチャットマネージャーが利用できません")


class ChatUI:
    """チャット用UIコンポーネントクラス（感情学習対応）"""
    
    def __init__(self, container_key: str = "default_chat"):
        self.container_key = container_key
        self.chat_manager = get_chat_manager() if 'get_chat_manager' in globals() else None
        
        # 感情システムの初期化
        if EMOTION_SYSTEM_AVAILABLE:
            self.emotion_system = EmotionSystem()
        else:
            self.emotion_system = None
    
    def render_chat_styles(self):
        """チャット用CSSスタイルを適用（感情対応色彩変化）"""
        
        # 感情システムから色情報を取得
        bubble_color = "#ff9a9e"  # デフォルト色
        border_color = "#fecfef"
        
        if self.emotion_system:
            color_palette = self.emotion_system.get_current_color_palette()
            bubble_color = color_palette.get("bubble", bubble_color)
            
            # 虹色エフェクトの場合
            if color_palette.get("rainbow_effect"):
                bubble_style = f"background: {color_palette['border']};"
            else:
                bubble_style = f"background: linear-gradient(135deg, {bubble_color} 0%, {border_color} 50%, {border_color} 100%);"
        else:
            bubble_style = f"background: linear-gradient(135deg, {bubble_color} 0%, {border_color} 50%, {border_color} 100%);"
        
        st.markdown(f"""
        <style>
        .chat-container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .user-message {{
            background: rgba(255, 255, 255, 0.9);
            padding: 0.8rem;
            border-radius: 18px 18px 4px 18px;
            margin: 0.5rem 0;
            margin-left: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .ruri-message {{
            {bubble_style}
            padding: 0.8rem;
            border-radius: 18px 18px 18px 4px;
            margin: 0.5rem 0;
            margin-right: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            color: #333;
            transition: all 0.3s ease;
        }}
        
        /* 感情状態による追加スタイル（白系背景+アニメーションボーダー） */
        .ruri-message.emotion-joy {{
            background: linear-gradient(135deg, #fefefe 0%, #fffef8 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-joy::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #FFD700, #FFF8DC, #FFFF88, #FFD700);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: joy-glow 2s ease-in-out infinite alternate;
        }}
        
        .ruri-message.emotion-anger {{
            background: linear-gradient(135deg, #fefefe 0%, #fffafa 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-anger::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #FF6B6B, #FFE4E1, #FF9999, #FF6B6B);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: anger-pulse 1.5s ease-in-out infinite;
        }}
        
        .ruri-message.emotion-sadness {{
            background: linear-gradient(135deg, #fefefe 0%, #f8feff 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-sadness::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #87CEEB, #E6F3FF, #B3D9FF, #87CEEB);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: sadness-wave 3s ease-in-out infinite;
        }}
        
        .ruri-message.emotion-love {{
            background: linear-gradient(135deg, #fefefe 0%, #fffafc 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-love::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #FF69B4, #FFB6C1, #FF91A4, #FF69B4);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: love-heartbeat 1.8s ease-in-out infinite;
        }}
        
        .ruri-message.emotion-surprise {{
            background: linear-gradient(135deg, #fefefe 0%, #fffcf8 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-surprise::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #FFA500, #FFE5CC, #FFCC99, #FFA500);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: surprise-flash 0.8s ease-out infinite alternate;
        }}
        
        .ruri-message.emotion-fear {{
            background: linear-gradient(135deg, #fefefe 0%, #fafafa 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-fear::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #696969, #F0F0F0, #D3D3D3, #696969);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: fear-shake 2.5s ease-in-out infinite;
        }}
        
        .ruri-message.emotion-disgust {{
            background: linear-gradient(135deg, #fefefe 0%, #f8fff8 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-disgust::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #90EE90, #E6FFE6, #CCFFCC, #90EE90);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: disgust-ripple 2s ease-in-out infinite;
        }}
        
        .ruri-message.emotion-anticipation {{
            background: linear-gradient(135deg, #fefefe 0%, #fafcff 50%, #fefefe 100%);
            border-radius: 18px 18px 18px 4px;
            position: relative;
            border: 3px solid transparent;
        }}
        
        .ruri-message.emotion-anticipation::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            background: linear-gradient(45deg, #9370DB, #E6E6FA, #DDA0DD, #9370DB);
            border-radius: 18px 18px 18px 4px;
            z-index: -1;
            animation: anticipation-rotate 3s linear infinite;
        }}
        
        /* 感情別アニメーション定義 */
        @keyframes joy-glow {{
            0% {{ 
                background: linear-gradient(45deg, #FFD700, #FFF8DC, #FFFF88, #FFD700);
                opacity: 0.8;
            }}
            100% {{ 
                background: linear-gradient(45deg, #FFFF88, #FFD700, #FFF8DC, #FFFF88);
                opacity: 1;
            }}
        }}
        
        @keyframes anger-pulse {{
            0%, 100% {{ 
                background: linear-gradient(45deg, #FF6B6B, #FFE4E1, #FF9999, #FF6B6B);
                transform: scale(1);
            }}
            50% {{ 
                background: linear-gradient(45deg, #FF9999, #FF6B6B, #FFE4E1, #FF9999);
                transform: scale(1.02);
            }}
        }}
        
        @keyframes sadness-wave {{
            0%, 100% {{ 
                background: linear-gradient(45deg, #87CEEB, #E6F3FF, #B3D9FF, #87CEEB);
            }}
            33% {{ 
                background: linear-gradient(45deg, #E6F3FF, #B3D9FF, #87CEEB, #E6F3FF);
            }}
            66% {{ 
                background: linear-gradient(45deg, #B3D9FF, #87CEEB, #E6F3FF, #B3D9FF);
            }}
        }}
        
        @keyframes love-heartbeat {{
            0%, 100% {{ 
                background: linear-gradient(45deg, #FF69B4, #FFB6C1, #FF91A4, #FF69B4);
                transform: scale(1);
            }}
            25% {{ 
                transform: scale(1.03);
            }}
            50% {{ 
                background: linear-gradient(45deg, #FFB6C1, #FF91A4, #FF69B4, #FFB6C1);
                transform: scale(1);
            }}
            75% {{ 
                transform: scale(1.02);
            }}
        }}
        
        @keyframes surprise-flash {{
            0% {{ 
                background: linear-gradient(45deg, #FFA500, #FFE5CC, #FFCC99, #FFA500);
                opacity: 1;
            }}
            100% {{ 
                background: linear-gradient(45deg, #FFCC99, #FFA500, #FFE5CC, #FFCC99);
                opacity: 0.7;
            }}
        }}
        
        @keyframes fear-shake {{
            0%, 100% {{ 
                background: linear-gradient(45deg, #696969, #F0F0F0, #D3D3D3, #696969);
                transform: translateX(0);
            }}
            25% {{ transform: translateX(-1px); }}
            75% {{ transform: translateX(1px); }}
        }}
        
        @keyframes disgust-ripple {{
            0% {{ 
                background: linear-gradient(45deg, #90EE90, #E6FFE6, #CCFFCC, #90EE90);
                opacity: 0.8;
            }}
            50% {{ 
                opacity: 1;
            }}
            100% {{ 
                background: linear-gradient(45deg, #CCFFCC, #90EE90, #E6FFE6, #CCFFCC);
                opacity: 0.8;
            }}
        }}
        
        @keyframes anticipation-rotate {{
            0% {{ 
                background: linear-gradient(45deg, #9370DB, #E6E6FA, #DDA0DD, #9370DB);
            }}
            25% {{ 
                background: linear-gradient(135deg, #9370DB, #E6E6FA, #DDA0DD, #9370DB);
            }}
            50% {{ 
                background: linear-gradient(225deg, #9370DB, #E6E6FA, #DDA0DD, #9370DB);
            }}
            75% {{ 
                background: linear-gradient(315deg, #9370DB, #E6E6FA, #DDA0DD, #9370DB);
            }}
            100% {{ 
                background: linear-gradient(45deg, #9370DB, #E6E6FA, #DDA0DD, #9370DB);
            }}
        }}
        
        /* アニメーション効果 */
        .ruri-message.thinking {{
            opacity: 0.9;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        
        .thinking-dots {{
            animation: thinking 1.5s infinite;
        }}
        
        @keyframes thinking {{
            0%, 20% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        .typing-cursor {{
            animation: blink 1s infinite;
            font-weight: bold;
            color: #333;
        }}
        
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0; }}
        }}
        
        .message-timestamp {{
            font-size: 0.75em;
            color: #666;
            margin: 0.2rem 0;
        }}
        
        .message-label {{
            font-weight: bold;
            margin-bottom: 0.3rem;
            display: block;
        }}
        
        .message-content {{
            line-height: 1.5;
        }}
        
        .latest-message {{
            border: 2px solid #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
        }}
        
        /* 成長度表示 */
        .growth-indicator {{
            font-size: 0.8em;
            opacity: 0.7;
            text-align: right;
            margin-top: 0.5rem;
        }}
        
        /* レスポンシブ対応 */
        @media (max-width: 768px) {{
            .chat-container {{
                padding: 0.7rem;
                margin: 0.7rem 0;
            }}
            
            .user-message, .ruri-message {{
                margin-left: 0.5rem;
                margin-right: 0.5rem;
                padding: 0.6rem;
            }}
        }}
        
        /* 小画面対応 */
        @media (max-width: 480px) {{
            .user-message, .ruri-message {{
                margin-left: 0.2rem;
                margin-right: 0.2rem;
                padding: 0.5rem;
                font-size: 0.9rem;
            }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def render_chat_history(self, max_display: int = 10, show_latest_highlight: bool = True):
        """チャット履歴を表示（将来の拡張ポイント）"""
        # TODO: LocalStorage / リモートサーバー対応時に有効化
        # messages = self.chat_manager.get_history()
        # 
        # if not messages:
        #     st.info("💬 まだ会話履歴がありません。ルリにメッセージを送ってみてください！")
        #     return
        # 
        # # 表示する履歴を制限
        # display_messages = messages[-max_display:] if max_display > 0 else messages
        # 
        # # 最新の会話が上に来るよう逆順で表示
        # for i, message in enumerate(reversed(display_messages)):
        #     is_latest = (i == 0) and show_latest_highlight
        #     self._render_single_conversation_turn(message, is_latest)
        
        # 履歴表示を完全に無効化（Streamlit Cloud対応）
        pass
    
    def _render_single_conversation_turn(self, message: ChatMessage, is_latest: bool = False):
        """
        1つの会話ターンを表示（視覚的な流れ：ルリ応答→ユーザー発言の順）
        
        視覚的な流れ：
        1. ルリの応答（上に表示、考えて追加された印象）
        2. ユーザーのメッセージ（下に表示、即時発言の印象）
        
        これにより「ユーザーが発言→ルリが考えて上に応答を追加」という自然な流れを表現
        """
        latest_class = " latest-message" if is_latest else ""
        
        # 1. ルリの応答を上に表示（考えて追加された印象）
        st.markdown(f"""
        <div class="ruri-message{latest_class}">
            <span class="message-label">🎭 ルリ</span>
            <div class="message-timestamp">{message.timestamp}</div>
            <div class="message-content">{message.ai_response}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. ユーザーメッセージを下に表示（即時発言の印象）
        st.markdown(f"""
        <div class="user-message{latest_class}">
            <span class="message-label">👤 あなた</span>
            <div class="message-timestamp">{message.timestamp}</div>
            <div class="message-content">{message.user_message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_message_input(self, user_level: Any, features: Dict[str, bool], 
                           placeholder: str = "ルリにメッセージを送信...") -> Optional[str]:
        """メッセージ入力フォームを表示し、送信されたメッセージを返す"""
        
        # フォームを使用してメッセージ送信を処理
        with st.form(key=f"chat_form_{self.container_key}", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                message = st.text_input(
                    "メッセージ", 
                    placeholder=placeholder,
                    label_visibility="collapsed"
                )
            
            with col2:
                send_button = st.form_submit_button("送信")
            
            if send_button and message.strip():
                # リアルタイム応答表示でユーザー体験を向上
                self._handle_message_with_live_feedback(message.strip(), user_level, features)
                # st.rerun()を削除して、発言後の消失を防止
                # 履歴は次回のページ更新時に反映される
        
        return None

    def _handle_message_with_live_feedback(self, message: str, user_level: Any, features: Dict[str, bool]):
        """ライブフィードバック付きメッセージ処理（感情学習対応）"""
        # 会話処理中フラグを設定（ナビゲーション保護）
        st.session_state.chat_processing = True
        
        try:
            # 1. タイムスタンプを統一
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 2. 感情検出（ユーザーメッセージから）
            detected_emotion = None
            if self.emotion_system:
                emotions = self.emotion_system.detect_emotion_from_text(message)
                # 最も強い感情を特定
                if emotions:
                    detected_emotion = max(emotions.items(), key=lambda x: x[1])
                    if detected_emotion[1] > 0.1:  # 閾値以上の場合のみ学習
                        self.emotion_system.learn_emotion(detected_emotion[0], detected_emotion[1])
            
            # 3. 専用コンテナを作成（履歴とは別管理）
            live_container = st.container()
            
            with live_container:
                # 現在の色彩情報を取得
                bubble_color = "#ff9a9e"  # デフォルト
                emotion_class = ""
                
                if self.emotion_system and detected_emotion:
                    bubble_color = self.emotion_system.get_bubble_color_for_emotion(detected_emotion[0])
                    emotion_class = f" emotion-{detected_emotion[0].value}"
                
                # ルリの吹き出し（上部・感情対応色）
                ruri_placeholder = st.empty()
                ruri_placeholder.markdown(f"""
                <div class="ruri-message{emotion_class}">
                    <span class="message-label">🎭 ルリ</span>
                    <div class="message-timestamp">{timestamp}</div>
                    <div class="message-content">💭 考え中...</div>
                </div>
                """, unsafe_allow_html=True)
                
                # ユーザーメッセージ（下部）
                st.markdown(f"""
                <div class="user-message">
                    <span class="message-label">👤 あなた</span>
                    <div class="message-timestamp">{timestamp}</div>
                    <div class="message-content">{message}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 4. AI応答生成
            try:
                if 'get_ai_generator' in globals():
                    ai_generator = get_ai_generator()
                    if ai_generator:
                        # generate_response はタプル (応答文, 処理時間, プロバイダー名) を返すので、最初の要素のみ取得
                        response_tuple = ai_generator.generate_response(message)
                        if isinstance(response_tuple, tuple) and len(response_tuple) >= 1:
                            ai_response = response_tuple[0]  # 応答文のみ取得
                        else:
                            ai_response = str(response_tuple)
                    else:
                        ai_response = "すみません、AIが応答できません。"
                else:
                    # フォールバック応答（ルリらしく）
                    fallback_responses = [
                        "そうですね...とても興味深いお話ですね。",
                        "なるほど！私もそう思います。",
                        "それについて、もう少し教えていただけますか？",
                        "わぁ、新しいことを教えていただけて嬉しいです！",
                        "そのお気持ち、少し分かるような気がします。"
                    ]
                    import random
                    ai_response = random.choice(fallback_responses)
                
                # 5. AI応答の感情分析と学習
                ai_detected_emotion = None
                if self.emotion_system and isinstance(ai_response, str):
                    ai_emotions = self.emotion_system.detect_emotion_from_text(ai_response)
                    
                    # AI応答から最も強い感情を特定
                    if ai_emotions:
                        ai_detected_emotion = max(ai_emotions.items(), key=lambda x: x[1])
                        # デバッグ情報
                        if ai_detected_emotion[1] > 0.1:
                            print(f"🎭 AI応答感情検出: {ai_detected_emotion[0].value} (強度: {ai_detected_emotion[1]:.2f})")
                        
                        # AI応答の感情学習（少し弱めに）
                        for emotion, intensity in ai_emotions.items():
                            if intensity > 0.1:
                                self.emotion_system.learn_emotion(emotion, intensity * 0.5)
                
                # 6. 最終応答の表示（AI応答の感情に応じた色）
                final_emotion_class = ""
                if ai_detected_emotion and ai_detected_emotion[1] > 0.15:  # 閾値を設定
                    final_emotion_class = f" emotion-{ai_detected_emotion[0].value}"
                
                ruri_placeholder.markdown(f"""
                <div class="ruri-message{final_emotion_class}">
                    <span class="message-label">🎭 ルリ</span>
                    <div class="message-timestamp">{timestamp}</div>
                    <div class="message-content">{ai_response}</div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"AI応答エラー: {e}")
            
        except Exception as e:
            st.error(f"メッセージ処理エラー: {e}")
        
        finally:
            # 会話処理中フラグをクリア
            st.session_state.chat_processing = False
    
    def render_chat_controls(self):
        """チャット管理用コントロールを表示"""
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("履歴クリア", key=f"clear_btn_{self.container_key}"):
                self.chat_manager.clear_history()
                st.success("履歴をクリアしました")
                st.rerun()
        
        with col2:
            if st.button("履歴エクスポート", key=f"export_btn_{self.container_key}"):
                export_text = self.chat_manager.export_history()
                st.download_button(
                    label="💾 履歴をダウンロード",
                    data=export_text,
                    file_name="ruri_chat_history.txt",
                    mime="text/plain",
                    key=f"download_btn_{self.container_key}"
                )
        
        with col3:
            messages = self.chat_manager.get_history()
            st.metric("会話数", len(messages))
    
    def render_full_chat_interface(self, user_level: Any, features: Dict[str, bool],
                                 title: str = "💬 ルリとの会話", max_display: int = 10):
        """完全なチャットインターフェースを表示"""
        st.title(title)
        
        # スタイル適用
        self.render_chat_styles()
        
        # メッセージ入力を上部に固定
        st.subheader("📝 メッセージを送信")
        self.render_message_input(user_level, features)
        
        # 区切り線
        st.markdown("---")
        
        # チャットコンテナ（将来の拡張ポイント）
        # st.subheader("📜 会話履歴")
        # with st.container():
        #     st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        #     
        #     # 履歴表示
        #     self.render_chat_history(max_display)
        #     
        #     st.markdown('</div>', unsafe_allow_html=True)

        # コントロール
        st.subheader("🔧 チャット管理")
        self.render_chat_controls()


# ファクトリ関数
def create_chat_ui(container_key: str = "default_chat") -> ChatUI:
    """ChatUIインスタンスを作成"""
    return ChatUI(container_key)

def render_compact_chat(user_level: Any, features: Dict[str, bool], 
                      container_key: str = "compact_chat", max_display: int = 5):
    """コンパクトなチャット表示（ホームページ用）"""
    chat_ui = create_chat_ui(container_key)
    
    # スタイル適用
    chat_ui.render_chat_styles()
    
    # コンパクト表示 - レイアウト改善
    with st.expander("💬 ルリとの会話", expanded=True):
        # 入力フォームを上部に固定
        st.markdown("##### 📝 メッセージ送信")
        chat_ui.render_message_input(user_level, features, "ルリに話しかけてみてください...")
        
        # 履歴表示（将来の拡張ポイント）
        # st.markdown("##### 📜 会話履歴")
        # chat_ui.render_chat_history(max_display)

def render_full_chat_page(user_level: Any, features: Dict[str, bool]):
    """専用チャットページの表示"""
    chat_ui = create_chat_ui("full_chat_page")
    chat_ui.render_full_chat_interface(
        user_level, 
        features, 
        title="💬 ルリとのAI会話",
        max_display=20
    )