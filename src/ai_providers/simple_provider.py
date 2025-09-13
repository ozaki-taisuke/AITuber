import random
from typing import Dict, Any, AsyncGenerator
from .base_provider import BaseAIProvider, CharacterResponse, EmotionType, ColorStage

class SimpleAIProvider(BaseAIProvider):
    """シンプルなAIプロバイダー（フォールバック用）
    
    外部ライブラリに依存しない基本的な応答生成
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.responses = self._load_default_responses()
    
    def _load_default_responses(self) -> Dict[str, list]:
        """デフォルト応答パターンの読み込み"""
        return {
            "greeting": [
                "こんにちは！私はルリです。",
                "はじめまして、ルリと申します。",
                "お疲れさまです！"
            ],
            "emotion": [
                "その気持ち、よくわかります。",
                "感情って、複雑ですね。",
                "私も同じようなことを感じたことがあります。"
            ],
            "color": [
                "色って不思議ですね。私にはまだよくわからないのですが...",
                "もしかしたら、これが色というものでしょうか？",
                "少しずつ、色というものが見えてきているような気がします。"
            ],
            "learning": [
                "勉強になります！",
                "新しいことを学べました。",
                "教えてくださってありがとうございます。"
            ],
            "default": [
                "なるほど、そうですね。",
                "興味深いお話ですね。",
                "そのことについて、もう少し詳しく教えていただけますか？",
                "私なりに考えてみますね。",
                "とても面白いですね！"
            ]
        }
    
    def is_available(self) -> bool:
        """常に利用可能"""
        return True
    
    def generate_response(self, 
                         message: str, 
                         context: Dict[str, Any] = None) -> CharacterResponse:
        """同期的な応答生成"""
        
        # 感情分析
        emotions = self.get_emotion_analysis(message)
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        
        # 応答カテゴリの決定
        category = self._determine_response_category(message, context)
        
        # 応答選択
        response_text = random.choice(self.responses[category])
        
        # 感情状態更新
        if dominant_emotion[1] > 0.3:
            self.update_emotion_state(dominant_emotion[0], dominant_emotion[1])
        
        # キャラクター応答作成
        return CharacterResponse(
            text=response_text,
            emotion=dominant_emotion[0],
            emotion_intensity=dominant_emotion[1],
            color_stage=self.current_color_stage,
            metadata={
                "provider": "simple",
                "category": category,
                "emotions_detected": emotions
            }
        )
    
    async def generate_response_async(self, 
                                    message: str, 
                                    context: Dict[str, Any] = None) -> CharacterResponse:
        """非同期な応答生成（同期版をラップ）"""
        return self.generate_response(message, context)
    
    async def generate_stream_response(self, 
                                     message: str, 
                                     context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """ストリーミング応答生成"""
        response = self.generate_response(message, context)
        
        # 文字ごとに遅延してストリーミング風に
        import asyncio
        for char in response.text:
            yield char
            await asyncio.sleep(0.05)  # 50ms遅延
    
    def _determine_response_category(self, 
                                   message: str, 
                                   context: Dict[str, Any] = None) -> str:
        """応答カテゴリの決定"""
        
        message_lower = message.lower()
        
        # 挨拶パターン
        if any(word in message_lower for word in ["こんにちは", "はじめまして", "おはよう", "こんばんは"]):
            return "greeting"
        
        # 感情関連パターン
        if any(word in message_lower for word in ["感情", "気持ち", "心", "感じ"]):
            return "emotion"
        
        # 色関連パターン
        if any(word in message_lower for word in ["色", "カラー", "赤", "青", "緑", "黄", "紫", "黒", "白"]):
            return "color"
        
        # 学習関連パターン
        if any(word in message_lower for word in ["学習", "勉強", "覚える", "教える", "学ぶ"]):
            return "learning"
        
        return "default"
    
    def set_custom_responses(self, responses: Dict[str, list]):
        """カスタム応答の設定"""
        self.responses.update(responses)
    
    def add_response_pattern(self, category: str, responses: list):
        """応答パターンの追加"""
        if category not in self.responses:
            self.responses[category] = []
        self.responses[category].extend(responses)
    
    def get_response_stats(self) -> Dict[str, Any]:
        """応答統計情報"""
        return {
            "total_patterns": sum(len(patterns) for patterns in self.responses.values()),
            "categories": list(self.responses.keys()),
            "category_counts": {
                category: len(patterns) 
                for category, patterns in self.responses.items()
            }
        }
