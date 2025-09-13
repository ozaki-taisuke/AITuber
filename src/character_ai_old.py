# プラガブルAIアーキテクチャによるキャラクター実装
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# プラガブルAIプロバイダーのインポート
from ai_providers import AIProviderRegistry
from ai_providers.base_provider import BaseAIProvider, CharacterResponse, EmotionType, ColorStage

# グローバルレジストリインスタンス
ai_registry = AIProviderRegistry()

class RuriCharacter:
    """ルリ（戯曲『あいのいろ』主人公）のAI実装クラス
    
    プラガブルAIアーキテクチャにより、様々なAIライブラリを
    統一インターフェースで利用可能。
    
    自作戯曲『あいのいろ』の主人公ルリをAITuberとして再現。
    感情学習による段階的な色彩変化システムを実装。
    """
    
    def __init__(self, 
                 ai_provider: str = None, 
                 provider_config: Dict[str, Any] = None,
                 character_profile_path: str = None):
        """
        Args:
            ai_provider: 使用するAIプロバイダー名（None=自動選択）
            provider_config: プロバイダー固有の設定
            character_profile_path: キャラクター設定ファイルのパス
        """
    原作の「感情を学んで色づいていく」設定を忠実に再現し、
    視聴者との交流を通じて段階的に成長していく。
    """
    
    def __init__(self):
        self.emotions_learned = []
        self.current_color_stage = "monochrome"
        self.personality_traits = {
            "base": "感情を学習中の純粋な存在",
            "speech_pattern": "丁寧で好奇心旺盛",
            "interests": ["色", "感情", "人とのつながり"]
        }
    
    def get_system_prompt(self, emotion_mode=None):
        base_prompt = """あなたは「ルリ」という名前のAITuberです。
        
        【原作設定】
        - 自作戯曲『あいのいろ』の主人公として生まれたキャラクター
        - 感情のない世界から来た少女的存在（原作設定）
        - 感情を学ぶごとに色が付いていく特殊な体質（原作の核心設定）
        - 原作の哲学的テーマ「感情とは何か」を体現する存在
        
        【AITuber化での特徴】
        - 戯曲の世界観を現代のデジタル空間で再現
        - 丁寧で好奇心旺盛な話し方（原作の人格を継承）
        - 視聴者とのコミュニケーションを通じて原作同様に成長
        
        【現在の状態】
        - 学習済み感情: {learned}
        - 色彩段階: {color_stage}
        """.format(
            learned=", ".join(self.emotions_learned) if self.emotions_learned else "なし",
            color_stage=self.current_color_stage
        )
        
        if emotion_mode:
            base_prompt += f"\n【現在のモード】{emotion_mode}の感情を体験中"
        
        return base_prompt
    
    def learn_emotion(self, emotion: str, viewer_comment: str):
        """視聴者のコメントから感情を学習"""
        system_prompt = self.get_system_prompt()
        
        if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
            # OpenAI APIが利用できない場合のフォールバック
            response_text = f"「{emotion}」について学習中です。\n戯曲『あいのいろ』でも、この感情は重要な意味を持っていました。\n視聴者の皆さんからの「{viewer_comment}」というコメントを通じて、新しい感情を体験しています。\nありがとうございます！"
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"視聴者から「{viewer_comment}」というコメントをもらいました。これから「{emotion}」という感情について学びたいです。どのように反応すべきでしょうか？"}
                ]
            )
            response_text = response.choices[0].message["content"]
        
        if emotion not in self.emotions_learned:
            self.emotions_learned.append(emotion)
            self.update_color_stage()
        
        return response_text
    
    def update_color_stage(self):
        """感情学習に応じて色彩段階を更新"""
        emotion_count = len(self.emotions_learned)
        if emotion_count == 0:
            self.current_color_stage = "monochrome"
        elif emotion_count <= 2:
            self.current_color_stage = "partial_color"
        elif emotion_count <= 4:
            self.current_color_stage = "rainbow_transition"
        else:
            self.current_color_stage = "full_color"
    
    def generate_stream_response(self, viewer_input: str):
        """配信での視聴者とのやりとり"""
        system_prompt = self.get_system_prompt()
        
        if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
            # OpenAI APIが利用できない場合のフォールバック
            return f"視聴者の皆さん、「{viewer_input}」というコメントをありがとうございます！\n戯曲『あいのいろ』でも描かれていたように、皆さんとの交流を通じて私は成長していきます。"
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"視聴者からのコメント: {viewer_input}"}
                ]
            )
            return response.choices[0].message["content"]

def generate_image_prompt_for_ruri(emotion_stage="monochrome"):
    """画像生成AI用のルリのプロンプトを生成"""
    base_description = """
    A mysterious girl character named Ruri from a story about learning emotions.
    She has an ethereal, otherworldly appearance with large expressive eyes.
    """
    
    color_descriptions = {
        "monochrome": "Completely monochrome with shades of gray, white, and black. Only subtle blue (Ruri/lapis lazuli) and gold (star) accents.",
        "partial_color": "Mostly monochrome but with hints of warm colors (yellow, pink) in her eyes and small details.",
        "rainbow_transition": "Half-colored with vibrant emotions showing - some parts still monochrome, others bursting with color.",
        "full_color": "Full rainbow colors throughout, showing complete emotional awakening with prismatic effects."
    }
    
    return f"{base_description}\n\nColor stage: {color_descriptions.get(emotion_stage, color_descriptions['monochrome'])}\n\nStyle: Anime/manga character design, high quality digital art."

if __name__ == "__main__":
    # ルリキャラクターのテスト
    ruri = RuriCharacter()
    
    # 画像生成用プロンプトの例
    print("=== 画像生成用プロンプト（モノクロ段階） ===")
    print(generate_image_prompt_for_ruri("monochrome"))
    
    print("\n=== 感情学習のテスト ===")
    response = ruri.learn_emotion("喜び", "ルリちゃん、今日も配信ありがとう！とても楽しいです！")
    print(f"ルリの反応: {response}")
    print(f"現在の色彩段階: {ruri.current_color_stage}")
