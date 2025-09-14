"""
チャット関連のStreamlit UIコンポーネント

このモジュールは、チャット機能のUI要素を再利用可能な形で提供します。
- チャット履歴表示
- メッセージ入力フォーム
- エクスポート機能
- レスポンシブデザイン対応
"""
from typing import Dict, Any, Optional, List
import streamlit as st
from src.chat_manager import get_chat_manager, get_ai_generator, handle_chat_message, ChatMessage


class ChatUI:
    """チャット用UIコンポーネントクラス"""
    
    def __init__(self, container_key: str = "default_chat"):
        self.container_key = container_key
        self.chat_manager = get_chat_manager()
    
    def render_chat_styles(self):
        """チャット用CSSスタイルを適用"""
        st.markdown("""
        <style>
        .chat-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .user-message {
            background: rgba(255, 255, 255, 0.9);
            padding: 0.8rem;
            border-radius: 18px 18px 4px 18px;
            margin: 0.5rem 0;
            margin-left: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .ruri-message {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            padding: 0.8rem;
            border-radius: 18px 18px 18px 4px;
            margin: 0.5rem 0;
            margin-right: 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            color: #333;
        }
        
        .message-timestamp {
            font-size: 0.75em;
            color: #666;
            margin: 0.2rem 0;
        }
        
        .message-label {
            font-weight: bold;
            margin-bottom: 0.3rem;
            display: block;
        }
        
        .message-content {
            line-height: 1.5;
        }
        
        .latest-message {
            border: 2px solid #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
        }
        
        /* レスポンシブ対応 */
        @media (max-width: 768px) {
            .chat-container {
                padding: 0.7rem;
                margin: 0.7rem 0;
            }
            
            .user-message, .ruri-message {
                margin-left: 0.5rem;
                margin-right: 0.5rem;
                padding: 0.6rem;
            }
        }
        
        /* 小画面対応 */
        @media (max-width: 480px) {
            .user-message, .ruri-message {
                margin-left: 0.2rem;
                margin-right: 0.2rem;
                padding: 0.5rem;
                font-size: 0.9rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_chat_history(self, max_display: int = 10, show_latest_highlight: bool = True):
        """チャット履歴を表示（最新の会話が上に来るよう逆順表示）"""
        messages = self.chat_manager.get_history()
        
        if not messages:
            st.info("💬 まだ会話履歴がありません。ルリにメッセージを送ってみてください！")
            return
        
        # 表示する履歴を制限
        display_messages = messages[-max_display:] if max_display > 0 else messages
        
        # 最新の会話が上に来るよう逆順で表示
        for i, message in enumerate(reversed(display_messages)):
            is_latest = (i == 0) and show_latest_highlight
            self._render_single_conversation_turn(message, is_latest)
    
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
                # メッセージ処理
                with st.spinner('ルリが考え中...'):
                    chat_message = handle_chat_message(message.strip(), user_level, features)
                
                # フォームのclear_on_submit=Trueにより自動的にクリアされる
                st.rerun()
        
        return None
    
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
        
        # チャットコンテナ（履歴表示）
        st.subheader("📜 会話履歴")
        with st.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # 履歴表示
            self.render_chat_history(max_display)
            
            st.markdown('</div>', unsafe_allow_html=True)

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
        
        # 区切り線
        st.markdown("---")
        
        # 履歴表示（下部）
        st.markdown("##### 📜 会話履歴")
        chat_ui.render_chat_history(max_display)
        
        # 管理ボタンは最下部
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("クリア", key=f"compact_clear_{container_key}"):
                chat_ui.chat_manager.clear_history()
                st.rerun()
        with col2:
            messages = chat_ui.chat_manager.get_history()
            st.caption(f"会話数: {len(messages)}")

def render_full_chat_page(user_level: Any, features: Dict[str, bool]):
    """専用チャットページの表示"""
    chat_ui = create_chat_ui("full_chat_page")
    chat_ui.render_full_chat_interface(
        user_level, 
        features, 
        title="💬 ルリとのAI会話",
        max_display=20
    )