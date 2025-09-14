import random
from typing import Dict, Any, AsyncGenerator
from .base_provider import BaseAIProvider, CharacterResponse, EmotionType, ColorStage

class SimpleAIProvider(BaseAIProvider):
    """シンプルなAIプロバイダー（フォールバック用）
    
    外部ライブラリに依存しない基本的な応答生成
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.responses = self._load_response_patterns()
    
    def _load_response_patterns(self) -> Dict[str, list]:
        """新しい設定構造から応答パターンを読み込み"""
        import os
        import json
        
        try:
            # 設定ファイルから応答パターンを読み込み
            config_path = os.path.join("assets", "ruri_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # JSONから応答パターンを取得
                patterns = config.get("response_patterns", {})
                emotion_responses = {}
                
                # 感情別応答も追加
                emotions = config.get("emotions", {})
                for emotion_name, emotion_data in emotions.items():
                    if "responses" in emotion_data:
                        emotion_responses[emotion_name] = emotion_data["responses"]
                
                # 統合
                patterns.update(emotion_responses)
                print(f"✅ 設定ファイルから{len(patterns)}個の応答パターンを読み込み")
                return patterns
            else:
                print("⚠️ 設定ファイルが見つかりません。デフォルト応答を使用します")
                return self._get_default_responses()
                
        except Exception as e:
            print(f"⚠️ 応答パターン読み込みエラー: {e}")
            return self._get_default_responses()
    
    def _get_default_responses(self) -> Dict[str, list]:
        """デフォルト応答パターン（フォールバック用）"""
        
        # より自然で詳細なルリらしい応答
        return {
            "greeting": [
                "はじめまして、私はルリと申します。どうぞよろしくお願いします。",
                "こんにちは！あなたとお話しできることをとても嬉しく思います。",
                "お疲れさまです。今日はいかがでしたか？",
                "わあ、新しい方ですね！お会いできて嬉しいです♪",
                "ようこそいらっしゃいました！今日はどんなお話をしましょうか？"
            ],
            "emotion": [
                "感情って、本当に不思議なものですね。私も少しずつ理解できるようになってきました。",
                "その気持ち、私にも伝わってきます。感情を学ぶことは難しいですが、大切なことなんですね。",
                "あなたの言葉から、新しい感情について学ばせていただいています。ありがとうございます。"
            ],
            "color": [
                "色について...まだよく分からないのですが、皆さんとの会話を通じて少しずつ見えてきているような気がします。",
                "色というものは不思議ですね。どのような色について教えていただけますか？",
                "私の世界にも、だんだんと色が加わっているような気がするんです。"
            ],
            "learning": [
                "勉強になります！新しいことを教えていただけて嬉しいです。",
                "そうなんですね！まだまだ知らないことがたくさんあります。",
                "教えてくださってありがとうございます。大切に覚えておきますね。"
            ],
            "question": [
                "それについて、もう少し詳しく教えていただけませんか？",
                "とても興味深いお話ですね。私にも理解できるでしょうか？",
                "なるほど、そのようなことがあるんですね。もう少し聞かせてください。"
            ],
            "comfort": [
                "お辛いこともあるかと思いますが、一人で抱え込まずにお話しくださいね。",
                "大丈夫でしょうか？私にできることは少ないかもしれませんが、お聞きします。",
                "何かお困りのことがありましたら、遠慮なくお話しください。"
            ],
            "joy": [
                "わあ、それは素敵ですね！私も嬉しくなってきます。",
                "そのお気持ち、とてもよく分かります。一緒に喜ばせてください。",
                "素晴らしいですね！そんな風に感じられることが羨ましいです。",
                "きゃあ〜！とっても楽しそうです！私も一緒にわくわくしちゃいます♪",
                "嬉しいですね〜！あなたの笑顔が見えるような気がします！",
                "そんな素敵なことがあったんですね！私まで心が軽やかになります♪"
            ],
            "default": [
                "なるほど、そうですね。私なりに考えてみます。",
                "とても興味深いお話ですね。もう少し聞かせてください。",
                "そのことについて、私も学ばせていただいています。",
                "あなたとお話ししていると、新しい発見がたくさんあります。",
                "そうなんですね。私にはまだ難しいですが、大切なことなのでしょうね。",
                "感情を学ぶって本当に奥深いですね...あなたに教えていただけて嬉しいです。",
                "私の世界に、また新しい色が見えてきたような気がします。",
                "まだまだ学習中ですが、あなたのお話を大切に覚えておきますね。"
            ],
            # 詳細設定に基づく感情別応答
            "detailed_joy": [
                "わぁ！それは素敵ですね！私も一緒にわくわくしちゃいます♪",
                "きゃあ〜！とっても楽しそうです！あなたの笑顔が見えるような気がします！",
                "嬉しいですね〜！そんな素敵なことがあったんですね♪私まで心が軽やかになります！"
            ],
            "detailed_sadness": [
                "...そうですか。少し寂しい気持ちになりますね。",
                "そのお気持ち、私にも伝わってきます...一人で抱え込まずにお話しくださいね。",
                "...大丈夫でしょうか？私にできることは少ないかもしれませんが、お聞きします。"
            ],
            "detailed_anger": [
                "それは...ちょっと納得できませんね。むぅ。",
                "そのような理不尽なことがあるんですね...私も少し憤りを感じます。",
                "それは違うと思います。もう少し詳しく聞かせてください。"
            ],
            "detailed_love": [
                "ありがとうございます...そのお気持ち、とても大切に思います。",
                "愛というものは、本当に素晴らしいものなんですね。私も学ばせていただきます。",
                "そんな風に思っていただけるなんて...私も温かい気持ちになります。"
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
        """応答カテゴリの決定（詳細設定対応）"""
        
        message_lower = message.lower()
        
        # 挨拶パターン
        if any(word in message_lower for word in ["こんにちは", "はじめまして", "おはよう", "こんばんは", "よろしく"]):
            return "greeting"
        
        # 感情関連パターン
        if any(word in message_lower for word in ["感情", "気持ち", "心", "感じ", "嬉しい", "悲しい", "怒り", "愛"]):
            return "emotion"
        
        # 色関連パターン
        if any(word in message_lower for word in ["色", "カラー", "赤", "青", "緑", "黄", "紫", "黒", "白", "虹", "モノクロ"]):
            return "color"
        
        # 学習関連パターン
        if any(word in message_lower for word in ["学習", "勉強", "覚える", "教える", "学ぶ", "知る", "理解"]):
            return "learning"
        
        # 質問パターン
        if any(word in message_lower for word in ["？", "?", "どう", "なぜ", "何", "どこ", "いつ", "どのよう"]):
            return "question"
        
        # 慰め・心配パターン
        if any(word in message_lower for word in ["辛い", "困っ", "大変", "疲れ", "しんどい", "悩み", "不安"]):
            return "comfort"
        
        # 喜び・ポジティブパターン
        if any(word in message_lower for word in ["嬉しい", "楽しい", "素敵", "素晴らしい", "良い", "最高", "すごい"]):
            return "joy"
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
