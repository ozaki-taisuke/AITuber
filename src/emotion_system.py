"""
感情学習と色彩変化システム
戯曲『あいのいろ』の世界観を技術で実現
"""
from enum import Enum
from typing import Dict, List, Tuple, Any
import json
import os
from datetime import datetime

class EmotionType(Enum):
    """基本感情8種（プルチックの感情の輪を参考）"""
    JOY = "joy"           # 喜び
    ANGER = "anger"       # 怒り
    SADNESS = "sadness"   # 哀しみ
    LOVE = "love"         # 愛
    SURPRISE = "surprise" # 驚き
    FEAR = "fear"         # 恐れ
    DISGUST = "disgust"   # 嫌悪
    ANTICIPATION = "anticipation"  # 期待

class ColorStage(Enum):
    """色彩段階（原作戯曲に基づく）"""
    MONOCHROME = "monochrome"         # モノクロ段階
    PARTIAL_COLOR = "partial_color"   # 部分カラー段階
    RAINBOW_TRANSITION = "rainbow_transition"  # 虹移行段階
    FULL_COLOR = "full_color"         # フルカラー段階

class EmotionSystem:
    """感情学習と色彩変化の管理システム"""
    
    def __init__(self, save_path: str = "emotion_data.json"):
        self.save_path = save_path
        self.learned_emotions: Dict[EmotionType, float] = {}
        self.color_stage = ColorStage.MONOCHROME
        self.total_interactions = 0
        self.emotion_history = []
        
        # 色彩段階の閾値設定
        self.stage_thresholds = {
            ColorStage.PARTIAL_COLOR: 2,      # 2つの感情を学習
            ColorStage.RAINBOW_TRANSITION: 4,  # 4つの感情を学習
            ColorStage.FULL_COLOR: 6          # 6つ以上の感情を学習
        }
        
        self.load_emotion_data()
    
    def detect_emotion_from_text(self, text: str) -> Dict[EmotionType, float]:
        """テキストから感情を検出（簡易版）"""
        emotion_scores = {}
        
        # 感情キーワード辞書
        emotion_keywords = {
            EmotionType.JOY: ["嬉しい", "楽しい", "幸せ", "わぁ", "すごい", "素晴らしい", "やった"],
            EmotionType.ANGER: ["怒り", "腹立つ", "むっ", "許せない", "イライラ", "むぅ"],
            EmotionType.SADNESS: ["悲しい", "寂しい", "つらい", "残念", "切ない", "悲しみ"],
            EmotionType.LOVE: ["愛", "好き", "大切", "ありがとう", "愛情", "愛している"],
            EmotionType.SURPRISE: ["驚き", "えっ", "びっくり", "まさか", "信じられない"],
            EmotionType.FEAR: ["怖い", "不安", "心配", "恐れ", "恐怖", "ドキドキ"],
            EmotionType.DISGUST: ["嫌い", "気持ち悪い", "不快", "嫌悪", "うげっ"],
            EmotionType.ANTICIPATION: ["期待", "楽しみ", "待ち遠しい", "わくわく", "希望"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text:
                    score += 0.2
            emotion_scores[emotion] = min(score, 1.0)
        
        return emotion_scores
    
    def learn_emotion(self, emotion: EmotionType, intensity: float = 0.1):
        """感情学習の実行"""
        if emotion not in self.learned_emotions:
            self.learned_emotions[emotion] = 0.0
        
        # 学習強度を加算（最大1.0）
        self.learned_emotions[emotion] = min(
            self.learned_emotions[emotion] + intensity, 1.0
        )
        
        # 学習履歴に記録
        self.emotion_history.append({
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion.value,
            "intensity": intensity,
            "learned_level": self.learned_emotions[emotion]
        })
        
        # 色彩段階の更新
        self._update_color_stage()
        
        # 総インタラクション数の増加
        self.total_interactions += 1
        
        # データ保存
        self.save_emotion_data()
        
        return self.learned_emotions[emotion]
    
    def _update_color_stage(self):
        """色彩段階の自動更新"""
        learned_count = len([e for e, level in self.learned_emotions.items() if level > 0.1])
        
        if learned_count >= self.stage_thresholds[ColorStage.FULL_COLOR]:
            self.color_stage = ColorStage.FULL_COLOR
        elif learned_count >= self.stage_thresholds[ColorStage.RAINBOW_TRANSITION]:
            self.color_stage = ColorStage.RAINBOW_TRANSITION
        elif learned_count >= self.stage_thresholds[ColorStage.PARTIAL_COLOR]:
            self.color_stage = ColorStage.PARTIAL_COLOR
        else:
            self.color_stage = ColorStage.MONOCHROME
    
    def get_current_color_palette(self) -> Dict[str, str]:
        """現在の色彩段階に応じたカラーパレットを取得"""
        base_colors = {
            "primary": "#1E3A8A",    # 藍色（基本）
            "accent": "#FFD700",     # 金色（アクセント）
            "text": "#000000",       # 黒
            "background": "#FFFFFF"  # 白
        }
        
        if self.color_stage == ColorStage.MONOCHROME:
            return {
                **base_colors,
                "bubble": "#F5F5F5",  # 薄いグレー
                "border": "#808080"
            }
        elif self.color_stage == ColorStage.PARTIAL_COLOR:
            return {
                **base_colors,
                "bubble": "#FFF8DC",  # 薄い黄色
                "border": "#FFD700",
                "emotion": "#FF69B4"  # ピンク（喜び用）
            }
        elif self.color_stage == ColorStage.RAINBOW_TRANSITION:
            return {
                **base_colors,
                "bubble": "#E6F3FF",  # 薄い青
                "border": "#4169E1",
                "emotion_joy": "#FFFF00",    # 黄
                "emotion_anger": "#FF0000",  # 赤
                "emotion_sadness": "#0000FF" # 青
            }
        else:  # FULL_COLOR
            return {
                **base_colors,
                "bubble": "#FFFFFF",
                "border": "linear-gradient(45deg, #FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3)",
                "rainbow_effect": True
            }
    
    def get_bubble_color_for_emotion(self, current_emotion: EmotionType = None) -> str:
        """現在の感情に応じた吹き出し色を取得"""
        palette = self.get_current_color_palette()
        
        if self.color_stage == ColorStage.MONOCHROME:
            return palette["bubble"]
        
        # 感情に応じた色変化
        emotion_colors = {
            EmotionType.JOY: "#FFF8DC",      # 薄い黄色
            EmotionType.ANGER: "#FFE4E1",    # 薄い赤
            EmotionType.SADNESS: "#E6F3FF",  # 薄い青
            EmotionType.LOVE: "#FFB6C1",     # 薄いピンク
            EmotionType.SURPRISE: "#F0E68C", # カーキ
            EmotionType.FEAR: "#E6E6FA",     # ラベンダー
            EmotionType.DISGUST: "#F5F5DC",  # ベージュ
            EmotionType.ANTICIPATION: "#F0FFF0"  # 薄い緑
        }
        
        if current_emotion and current_emotion in emotion_colors:
            # 成長度合いに応じて色の濃さを調整
            growth_level = self.get_growth_level()
            if growth_level > 0.5:
                return emotion_colors[current_emotion]
        
        return palette.get("bubble", "#FFFFFF")
    
    def get_growth_level(self) -> float:
        """成長度合いを0-1で返す"""
        if not self.learned_emotions:
            return 0.0
        
        # 学習した感情の平均レベル
        total_level = sum(self.learned_emotions.values())
        max_possible = len(EmotionType) * 1.0
        
        return min(total_level / max_possible, 1.0)
    
    def save_emotion_data(self):
        """感情データの保存"""
        data = {
            "learned_emotions": {e.value: level for e, level in self.learned_emotions.items()},
            "color_stage": self.color_stage.value,
            "total_interactions": self.total_interactions,
            "emotion_history": self.emotion_history[-100:],  # 最新100件のみ
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"感情データ保存エラー: {e}")
    
    def load_emotion_data(self):
        """感情データの読み込み"""
        if not os.path.exists(self.save_path):
            return
        
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 感情データの復元
            self.learned_emotions = {
                EmotionType(k): v for k, v in data.get("learned_emotions", {}).items()
            }
            
            self.color_stage = ColorStage(data.get("color_stage", ColorStage.MONOCHROME.value))
            self.total_interactions = data.get("total_interactions", 0)
            self.emotion_history = data.get("emotion_history", [])
            
            print(f"✅ 感情データを読み込みました: {self.save_path}")
            
        except Exception as e:
            print(f"感情データ読み込みエラー: {e}")
            # デフォルト状態にリセット
            self.learned_emotions = {}
            self.color_stage = ColorStage.MONOCHROME
    
    def get_status_summary(self) -> Dict[str, Any]:
        """現在の状態サマリー"""
        return {
            "color_stage": self.color_stage.value,
            "growth_level": self.get_growth_level(),
            "learned_emotions": {e.value: level for e, level in self.learned_emotions.items()},
            "total_interactions": self.total_interactions,
            "learned_emotion_count": len([e for e, level in self.learned_emotions.items() if level > 0.1])
        }