from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    """感情タイプ"""
    JOY = "joy"           # 喜び
    ANGER = "anger"       # 怒り
    SADNESS = "sadness"   # 哀しみ
    LOVE = "love"         # 愛
    SURPRISE = "surprise" # 驚き
    FEAR = "fear"         # 恐れ
    DISGUST = "disgust"   # 嫌悪
    ANTICIPATION = "anticipation"  # 期待

class ColorStage(Enum):
    """色彩学習段階"""
    MONOCHROME = "monochrome"           # モノクロ段階
    PARTIAL_COLOR = "partial_color"     # 部分色彩段階
    RAINBOW_TRANSITION = "rainbow_transition"  # 虹変遷段階
    FULL_COLOR = "full_color"           # 完全色彩段階

@dataclass
class EmotionState:
    """感情状態"""
    emotion: EmotionType
    intensity: float  # 0.0-1.0
    color_hue: Optional[float] = None  # HSV色相値
    learned: bool = False

@dataclass
class CharacterResponse:
    """キャラクター応答"""
    text: str
    emotion: EmotionType
    emotion_intensity: float
    color_stage: ColorStage
    metadata: Dict[str, Any]

class BaseAIProvider(ABC):
    """AIプロバイダーの抽象基底クラス
    
    異なるAIライブラリ（OpenAI, Ollama, GPT-OSS, HuggingFace等）を
    統一インターフェースで利用可能にする
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Args:
            config: プロバイダー固有の設定
        """
        self.config = config or {}
        self.character_context = ""
        self.conversation_history: List[Dict[str, str]] = []
        self.emotion_states: Dict[EmotionType, EmotionState] = {}
        self.current_color_stage = ColorStage.MONOCHROME
        
        # 初期感情状態設定
        self._initialize_emotions()
    
    def _initialize_emotions(self):
        """感情状態の初期化"""
        for emotion in EmotionType:
            self.emotion_states[emotion] = EmotionState(
                emotion=emotion,
                intensity=0.0,
                learned=False
            )
    
    @abstractmethod
    def is_available(self) -> bool:
        """プロバイダーが利用可能かチェック"""
        pass
    
    @abstractmethod
    def generate_response(self, 
                         message: str, 
                         context: Dict[str, Any] = None) -> CharacterResponse:
        """同期的な応答生成"""
        pass
    
    @abstractmethod
    async def generate_response_async(self, 
                                    message: str, 
                                    context: Dict[str, Any] = None) -> CharacterResponse:
        """非同期な応答生成"""
        pass
    
    @abstractmethod
    def generate_stream_response(self, 
                               message: str, 
                               context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """ストリーミング応答生成"""
        pass
    
    def set_character_context(self, context: str):
        """キャラクター設定の読み込み"""
        self.character_context = context
    
    def add_conversation(self, user_message: str, assistant_message: str):
        """会話履歴の追加"""
        self.conversation_history.append({
            "user": user_message,
            "assistant": assistant_message
        })
        
        # 履歴制限（最新50件）
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def update_emotion_state(self, emotion: EmotionType, intensity: float):
        """感情状態の更新"""
        if emotion in self.emotion_states:
            self.emotion_states[emotion].intensity = max(0.0, min(1.0, intensity))
            self.emotion_states[emotion].learned = True
            
            # 色彩段階の更新
            self._update_color_stage()
    
    def _update_color_stage(self):
        """色彩段階の自動更新"""
        learned_count = sum(1 for state in self.emotion_states.values() if state.learned)
        
        if learned_count == 0:
            self.current_color_stage = ColorStage.MONOCHROME
        elif learned_count <= 2:
            self.current_color_stage = ColorStage.PARTIAL_COLOR
        elif learned_count <= 5:
            self.current_color_stage = ColorStage.RAINBOW_TRANSITION
        else:
            self.current_color_stage = ColorStage.FULL_COLOR
    
    def get_emotion_analysis(self, text: str) -> Dict[EmotionType, float]:
        """テキストの感情分析（基本実装）"""
        # 基本的なキーワードベース分析
        emotion_keywords = {
            EmotionType.JOY: ["嬉しい", "楽しい", "幸せ", "良い", "素晴らしい"],
            EmotionType.ANGER: ["怒り", "腹立たしい", "むかつく", "嫌い"],
            EmotionType.SADNESS: ["悲しい", "辛い", "寂しい", "落ち込む"],
            EmotionType.LOVE: ["愛", "好き", "大切", "愛している"],
            EmotionType.SURPRISE: ["驚き", "びっくり", "まさか", "信じられない"],
            EmotionType.FEAR: ["怖い", "恐れ", "不安", "心配"],
            EmotionType.DISGUST: ["気持ち悪い", "嫌", "うんざり"],
            EmotionType.ANTICIPATION: ["期待", "楽しみ", "待ち遠しい"]
        }
        
        results = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            results[emotion] = min(1.0, score * 0.3)
        
        return results
    
    def get_status_info(self) -> Dict[str, Any]:
        """プロバイダーの状態情報"""
        return {
            "provider_name": self.__class__.__name__,
            "available": self.is_available(),
            "color_stage": self.current_color_stage.value,
            "learned_emotions": [
                emotion.value for emotion, state in self.emotion_states.items() 
                if state.learned
            ],
            "conversation_count": len(self.conversation_history),
            "config": self.config
        }
    
    def get_color_info(self) -> Dict[str, Any]:
        """現在の色彩情報"""
        dominant_emotion = max(
            self.emotion_states.items(),
            key=lambda x: x[1].intensity,
            default=(EmotionType.JOY, EmotionState(EmotionType.JOY, 0.0))
        )
        
        return {
            "stage": self.current_color_stage.value,
            "dominant_emotion": dominant_emotion[0].value,
            "dominant_intensity": dominant_emotion[1].intensity,
            "emotion_colors": {
                emotion.value: state.color_hue 
                for emotion, state in self.emotion_states.items()
                if state.color_hue is not None
            }
        }
