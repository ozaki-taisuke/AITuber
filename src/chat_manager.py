"""
チャット機能のビジネスロジック管理

このモジュールは、UIレイヤーから分離されたチャット処理を提供します。
- メッセージ処理とAI応答生成
- 履歴管理と永続化
- ログ記録（将来の拡張用）
"""
from typing import List, Tuple, Optional, Dict, Any
import datetime
import random
import streamlit as st


class ChatMessage:
    """チャットメッセージの構造体"""
    
    def __init__(self, timestamp: str, user_message: str, ai_response: str, 
                 response_time: Optional[float] = None, model_info: Optional[str] = None):
        self.timestamp = timestamp
        self.user_message = user_message
        self.ai_response = ai_response
        self.response_time = response_time
        self.model_info = model_info
        
    def to_tuple(self) -> Tuple[str, str, str]:
        """後方互換性のためのタプル変換"""
        return (self.timestamp, self.user_message, self.ai_response)
    
    @classmethod
    def from_tuple(cls, data: Tuple[str, str, str]) -> 'ChatMessage':
        """既存のタプル形式からの変換"""
        return cls(data[0], data[1], data[2])


class ChatManager:
    """チャット機能の中央管理クラス"""
    
    def __init__(self, session_state_key: str = 'chat_history', max_history: int = 50):
        self.session_state_key = session_state_key
        self.max_history = max_history
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """セッション状態の初期化"""
        if self.session_state_key not in st.session_state:
            st.session_state[self.session_state_key] = []
        
        # 永続化用キー
        persistent_key = f'persistent_{self.session_state_key}'
        if persistent_key not in st.session_state:
            st.session_state[persistent_key] = []
    
    def get_history(self) -> List[ChatMessage]:
        """チャット履歴の取得"""
        history = st.session_state.get(self.session_state_key, [])
        messages = []
        
        for item in history:
            if isinstance(item, tuple) and len(item) >= 3:
                # 既存のタプル形式からの変換
                messages.append(ChatMessage.from_tuple(item))
            elif isinstance(item, ChatMessage):
                messages.append(item)
        
        return messages
    
    def add_message(self, user_message: str, ai_response: str, 
                   response_time: Optional[float] = None, model_info: Optional[str] = None) -> ChatMessage:
        """新しいメッセージを履歴に追加"""
        timestamp = datetime.datetime.now().strftime("%H:%M")
        message = ChatMessage(timestamp, user_message, ai_response, response_time, model_info)
        
        # セッション状態に追加（後方互換性のためタプル形式）
        history = st.session_state.get(self.session_state_key, [])
        history.append(message.to_tuple())
        
        # 履歴サイズ制限
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        st.session_state[self.session_state_key] = history
        self._save_to_persistent()
        
        return message
    
    def clear_history(self):
        """履歴をクリア"""
        st.session_state[self.session_state_key] = []
        self._save_to_persistent()
    
    def _save_to_persistent(self):
        """永続化ストレージに保存"""
        try:
            persistent_key = f'persistent_{self.session_state_key}'
            st.session_state[persistent_key] = st.session_state[self.session_state_key].copy()
        except Exception as e:
            print(f"⚠️ 履歴保存エラー: {e}")
    
    def _load_from_persistent(self):
        """永続化ストレージから読み込み"""
        try:
            persistent_key = f'persistent_{self.session_state_key}'
            if persistent_key in st.session_state:
                st.session_state[self.session_state_key] = st.session_state[persistent_key].copy()
        except Exception as e:
            print(f"⚠️ 履歴読み込みエラー: {e}")
    
    def export_history(self) -> str:
        """履歴をテキスト形式でエクスポート"""
        messages = self.get_history()
        if not messages:
            return "履歴がありません。"
        
        export_text = "=== ルリとの会話履歴 ===\n\n"
        for message in messages:
            export_text += f"[{message.timestamp}]\n"
            export_text += f"あなた: {message.user_message}\n"
            export_text += f"ルリ: {message.ai_response}\n\n"
        
        return export_text


class AIResponseGenerator:
    """AI応答生成の管理クラス"""
    
    def __init__(self):
        self._ruri_character = None
        
    def _get_ruri_character(self):
        """RuriCharacterインスタンスの取得（遅延ロード）"""
        if self._ruri_character is None:
            try:
                # 循環インポートを避けるために直接インポート
                import sys
                import os
                
                # パス追加（必要に応じて）
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                from src.character_ai import RuriCharacter
                self._ruri_character = RuriCharacter()
            except Exception as e:
                print(f"⚠️ RuriCharacter取得エラー: {e}")
                self._ruri_character = self._create_fallback_character()
        
        return self._ruri_character
    
    def _create_fallback_character(self):
        """フォールバック用のダミーキャラクター"""
        class FallbackCharacter:
            def generate_response(self, message, image=None):
                fallback_responses = [
                    "ありがとうございます！感情を学習中です...",
                    "そうですね...色々な感情があるんですね",
                    "まだ学習中ですが、あなたの言葉は覚えています",
                    "もっとお話ししたいです！",
                    "感情って...難しいですね"
                ]
                return random.choice(fallback_responses)
        
        return FallbackCharacter()
    
    def generate_response(self, message: str, user_level: Any = None, 
                         features: Dict[str, bool] = None, image: Any = None) -> Tuple[str, Optional[float], Optional[str]]:
        """AI応答を生成（レスポンス時間とモデル情報も返す）"""
        import time
        
        start_time = time.time()
        
        try:
            # AI機能が利用可能かチェック
            if features and not features.get("ai_conversation", True):
                response = "AI会話機能が無効になっています。"
                model_info = "disabled"
            else:
                ruri = self._get_ruri_character()
                response = ruri.generate_response(message, image)
                model_info = getattr(ruri, 'provider_name', 'unknown')
                
        except Exception as e:
            response = f"⚠️ AI応答エラー: {str(e)}"
            model_info = "error"
        
        response_time = time.time() - start_time
        
        return response, response_time, model_info


# グローバルインスタンス（シングルトンパターン）
_chat_manager_instance = None
_ai_generator_instance = None

def get_chat_manager() -> ChatManager:
    """ChatManagerのシングルトンインスタンスを取得"""
    global _chat_manager_instance
    if _chat_manager_instance is None:
        _chat_manager_instance = ChatManager()
    return _chat_manager_instance

def get_ai_generator() -> AIResponseGenerator:
    """AIResponseGeneratorのシングルトンインスタンスを取得"""
    global _ai_generator_instance
    if _ai_generator_instance is None:
        _ai_generator_instance = AIResponseGenerator()
    return _ai_generator_instance

def handle_chat_message(message: str, user_level: Any = None, 
                       features: Dict[str, bool] = None, image: Any = None) -> ChatMessage:
    """統一されたチャットメッセージ処理"""
    chat_manager = get_chat_manager()
    ai_generator = get_ai_generator()
    
    # AI応答生成
    ai_response, response_time, model_info = ai_generator.generate_response(
        message, user_level, features, image
    )
    
    # 履歴に追加
    chat_message = chat_manager.add_message(message, ai_response, response_time, model_info)
    
    return chat_message