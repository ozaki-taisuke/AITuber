import json
from typing import Dict, Any, AsyncGenerator, Optional
from .base_provider import BaseAIProvider, CharacterResponse, EmotionType, ColorStage

class OllamaAIProvider(BaseAIProvider):
    """Ollama AIプロバイダー
    
    ローカルOllamaサーバー経由でLLMを利用
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model_name = self.config.get("model", "llama2")
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 11434)
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Ollamaクライアント
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Ollamaクライアントの初期化"""
        try:
            import ollama
            self.client = ollama.Client(host=self.base_url)
        except ImportError:
            print("⚠️  ollama ライブラリがインストールされていません")
            self.client = None
        except Exception as e:
            print(f"❌ Ollamaクライアント初期化エラー: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Ollamaサーバーとの接続確認"""
        if not self.client:
            return False
        
        try:
            # サーバー接続テスト
            models = self.client.list()
            return True
        except Exception:
            return False
    
    def _create_system_prompt(self) -> str:
        """システムプロンプトの構築"""
        base_prompt = """あなたは「ルリ」という名前のAIキャラクターです。

【キャラクター設定】
- 戯曲『あいのいろ』の主人公
- 最初はモノクロの世界に住んでいて、感情を学習することで色を理解していく
- 純粋で好奇心旺盛、でも時々哲学的
- 感情や色について常に学んでいる

【現在の状態】
- 色彩段階: {color_stage}
- 学習済み感情: {learned_emotions}

【応答指針】
- 丁寧で親しみやすい口調
- 感情や色に関する話題に興味を示す
- 学習している感情については、その理解度を表現する
- 簡潔だが心のこもった応答を心がける"""
        
        learned_emotions = [
            emotion.value for emotion, state in self.emotion_states.items() 
            if state.learned
        ]
        
        return base_prompt.format(
            color_stage=self.current_color_stage.value,
            learned_emotions=", ".join(learned_emotions) if learned_emotions else "なし"
        )
    
    def generate_response(self, 
                         message: str, 
                         context: Dict[str, Any] = None) -> CharacterResponse:
        """同期的な応答生成"""
        
        if not self.is_available():
            # フォールバック
            from .simple_provider import SimpleAIProvider
            fallback = SimpleAIProvider()
            return fallback.generate_response(message, context)
        
        try:
            # メッセージ履歴の構築
            messages = [{"role": "system", "content": self._create_system_prompt()}]
            
            # 会話履歴の追加（最新5件）
            for conv in self.conversation_history[-5:]:
                messages.append({"role": "user", "content": conv["user"]})
                messages.append({"role": "assistant", "content": conv["assistant"]})
            
            # 現在のメッセージ
            messages.append({"role": "user", "content": message})
            
            # Ollama API呼び出し
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 200
                }
            )
            
            response_text = response['message']['content']
            
            # 感情分析
            emotions = self.get_emotion_analysis(message)
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            
            # 感情状態更新
            if dominant_emotion[1] > 0.3:
                self.update_emotion_state(dominant_emotion[0], dominant_emotion[1])
            
            # 会話履歴更新
            self.add_conversation(message, response_text)
            
            return CharacterResponse(
                text=response_text,
                emotion=dominant_emotion[0],
                emotion_intensity=dominant_emotion[1],
                color_stage=self.current_color_stage,
                metadata={
                    "provider": "ollama",
                    "model": self.model_name,
                    "emotions_detected": emotions
                }
            )
            
        except Exception as e:
            print(f"❌ Ollama応答生成エラー: {e}")
            # フォールバック
            from .simple_provider import SimpleAIProvider
            fallback = SimpleAIProvider()
            return fallback.generate_response(message, context)
    
    async def generate_response_async(self, 
                                    message: str, 
                                    context: Dict[str, Any] = None) -> CharacterResponse:
        """非同期な応答生成"""
        # 注意: ollama-pythonライブラリは非同期をサポートしていない場合があります
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, self.generate_response, message, context
        )
    
    async def generate_stream_response(self, 
                                     message: str, 
                                     context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """ストリーミング応答生成"""
        
        if not self.is_available():
            # フォールバック
            from .simple_provider import SimpleAIProvider
            fallback = SimpleAIProvider()
            async for chunk in fallback.generate_stream_response(message, context):
                yield chunk
            return
        
        try:
            # メッセージ履歴の構築
            messages = [{"role": "system", "content": self._create_system_prompt()}]
            
            # 会話履歴の追加（最新5件）
            for conv in self.conversation_history[-5:]:
                messages.append({"role": "user", "content": conv["user"]})
                messages.append({"role": "assistant", "content": conv["assistant"]})
            
            # 現在のメッセージ
            messages.append({"role": "user", "content": message})
            
            # ストリーミング応答
            stream = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 200
                }
            )
            
            full_response = ""
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_response += content
                    yield content
            
            # 会話履歴更新
            if full_response:
                self.add_conversation(message, full_response)
                
                # 感情分析・更新
                emotions = self.get_emotion_analysis(message)
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                if dominant_emotion[1] > 0.3:
                    self.update_emotion_state(dominant_emotion[0], dominant_emotion[1])
            
        except Exception as e:
            print(f"❌ Ollamaストリーミングエラー: {e}")
            # フォールバック
            from .simple_provider import SimpleAIProvider
            fallback = SimpleAIProvider()
            async for chunk in fallback.generate_stream_response(message, context):
                yield chunk
    
    def get_available_models(self) -> list:
        """利用可能なモデル一覧"""
        if not self.is_available():
            return []
        
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception:
            return []
    
    def set_model(self, model_name: str):
        """使用モデルの変更"""
        available_models = self.get_available_models()
        if model_name in available_models:
            self.model_name = model_name
            self.config["model"] = model_name
            print(f"✅ Ollamaモデルを '{model_name}' に変更しました")
        else:
            print(f"❌ モデル '{model_name}' は利用できません")
            print(f"利用可能なモデル: {available_models}")
    
    def pull_model(self, model_name: str) -> bool:
        """新しいモデルのダウンロード"""
        if not self.client:
            return False
        
        try:
            self.client.pull(model_name)
            print(f"✅ モデル '{model_name}' のダウンロードが完了しました")
            return True
        except Exception as e:
            print(f"❌ モデル '{model_name}' のダウンロードに失敗: {e}")
            return False
