"""
OpenAI API Provider for AITuber Ruri
OpenAI GPT models integration
"""

from typing import Dict, Any, Optional
import os
from .base_provider import BaseAIProvider, CharacterResponse, EmotionType

try:
    from ..api_config import APIConfig
except ImportError:
    import sys
    sys.path.append('..')
    from api_config import APIConfig

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(BaseAIProvider):
    """OpenAI API Provider"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.client = None
        self.model = "gpt-4o-mini"
        
    def is_available(self) -> bool:
        """OpenAI利用可能性チェック"""
        if not OPENAI_AVAILABLE:
            return False
        
        return APIConfig.is_provider_available('openai')
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """OpenAI初期化"""
        try:
            if not OPENAI_AVAILABLE:
                print("❌ OpenAI library not installed")
                return False
            
            # APIConfigから設定を取得
            api_key = APIConfig.get_openai_api_key()
            if not api_key:
                print("❌ OpenAI API key not configured")
                return False
            
            # クライアント初期化
            self.client = openai.OpenAI(
                api_key=api_key,
                organization=config.get('organization') if config else None,
                project=config.get('project') if config else None
            )
            self.model = config.get('model', 'gpt-4o-mini') if config else 'gpt-4o-mini'
            
            # 接続テスト
            try:
                response = self.client.models.list()
                print(f"✅ OpenAI API接続成功: {self.model}")
                return True
            except Exception as e:
                print(f"❌ OpenAI API接続失敗: {e}")
                return False
                
        except Exception as e:
            print(f"❌ OpenAI初期化エラー: {e}")
            return False
            try:
                response = self.client.models.list()
                print(f"✅ OpenAI API接続成功: {self.model}")
                return True
            except Exception as e:
                print(f"❌ OpenAI API接続失敗: {e}")
                return False
                
        except Exception as e:
            print(f"❌ OpenAI初期化エラー: {e}")
            return False
    
    def generate_response(self, 
                         message: str, 
                         context: Dict[str, Any] = None) -> CharacterResponse:
        """OpenAI応答生成"""
        try:
            if not self.client:
                # クライアントが初期化されていない場合、APIキーで初期化を試行
                api_key = None
                
                # 1. 環境変数
                api_key = os.getenv('OPENAI_API_KEY')
                
                # 2. Streamlit secrets
                if not api_key:
                    try:
                        import streamlit as st
                        api_key = st.secrets.get('OPENAI_API_KEY')
                    except:
                        pass
                
                # 3. 設定ファイル
                if not api_key and hasattr(self, 'config') and self.config:
                    api_key = self.config.get('api_key')
                
                if api_key and api_key != "YOUR_OPENAI_API_KEY_HERE":
                    self.client = openai.OpenAI(api_key=api_key)
                else:
                    return CharacterResponse(
                        text="OpenAI APIキーが設定されていません",
                        emotion=self.emotion_states[list(self.emotion_states.keys())[0]].emotion,
                        emotion_intensity=0.0,
                        color_stage=self.current_color_stage,
                        metadata={"error": "no_api_key"}
                    )
                
            # メッセージ構築
                
            # メッセージ構築
            messages = []
            
            # システムメッセージ（キャラクター設定）
            if context and context.get('character_context'):
                messages.append({
                    "role": "system", 
                    "content": context['character_context']
                })
            
            # 会話履歴
            if context and context.get('conversation_history'):
                for entry in context['conversation_history'][-10:]:  # 最新10件のみ
                    if entry.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": entry['role'],
                            "content": entry['content']
                        })
            
            # 現在のプロンプト
            messages.append({
                "role": "user",
                "content": message
            })
            
            # API呼び出し
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            return CharacterResponse(
                text=response_text,
                emotion=self.emotion_states[list(self.emotion_states.keys())[0]].emotion,
                emotion_intensity=0.7,
                color_stage=self.current_color_stage,
                metadata={"model": self.model, "tokens": response.usage.total_tokens if response.usage else 0}
            )
            
        except Exception as e:
            return CharacterResponse(
                text=f"OpenAI APIエラー: {str(e)}",
                emotion=self.emotion_states[list(self.emotion_states.keys())[0]].emotion,
                emotion_intensity=0.0,
                color_stage=self.current_color_stage,
                metadata={"error": str(e)}
            )
    
    async def generate_response_async(self, 
                                    message: str, 
                                    context: Dict[str, Any] = None) -> CharacterResponse:
        """非同期応答生成（未実装）"""
        # 同期版を使用
        return self.generate_response(message, context)
    
    def generate_stream_response(self, 
                               message: str, 
                               context: Dict[str, Any] = None):
        """ストリーミング応答生成（未実装）"""
        # 通常応答を返す
        response = self.generate_response(message, context)
        yield response
    
    def get_provider_info(self) -> Dict[str, Any]:
        """プロバイダー情報取得"""
        return {
            "name": "OpenAI",
            "model": self.model,
            "available": self.is_available(),
            "library_installed": OPENAI_AVAILABLE,
            "api_configured": bool(os.getenv('OPENAI_API_KEY'))
        }