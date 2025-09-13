# 画像解析とキャラクター発展システム

import cv2
import numpy as np
from PIL import Image, ImageStat
import colorsys
import openai
import os

class RuriImageAnalyzer:
    def __init__(self, imageboard_path):
        self.imageboard_path = imageboard_path
        self.dominant_colors = []
        self.color_emotions = {
            'red': '情熱・怒り・エネルギー',
            'orange': '活力・創造性・暖かさ',
            'yellow': '喜び・楽観・希望',
            'green': '自然・成長・安らぎ',
            'blue': '冷静・信頼・哀しみ',
            'purple': '神秘・高貴・想像力',
            'pink': '優しさ・愛情・可愛らしさ',
            'white': '純粋・清潔・無垢',
            'black': '力強さ・神秘・無',
            'gray': '中立・落ち着き・曖昧'
        }
    
    def analyze_colors(self):
        """イメージボードから主要な色を抽出"""
        image = Image.open(self.imageboard_path)
        image = image.convert('RGB')
        
        # 画像をリサイズして処理を軽くする
        image.thumbnail((150, 150))
        
        # 色の分析
        colors = image.getcolors(maxcolors=256*256*256)
        if colors:
            # 最も多く使われている色を取得
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            
            dominant_colors = []
            for count, color in sorted_colors[:5]:  # 上位5色
                r, g, b = color
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                
                color_name = self.get_color_name(h, s, v)
                dominant_colors.append({
                    'rgb': color,
                    'hex': f'#{r:02x}{g:02x}{b:02x}',
                    'hsv': (h, s, v),
                    'name': color_name,
                    'emotion': self.color_emotions.get(color_name, '未知の感情'),
                    'percentage': count / sum([c[0] for c in colors]) * 100
                })
            
            self.dominant_colors = dominant_colors
            return dominant_colors
    
    def get_color_name(self, h, s, v):
        """HSV値から色名を判定"""
        if v < 0.2:
            return 'black'
        elif s < 0.1:
            return 'gray' if v < 0.8 else 'white'
        elif h < 0.08 or h > 0.92:
            return 'red'
        elif h < 0.17:
            return 'orange'
        elif h < 0.25:
            return 'yellow'
        elif h < 0.42:
            return 'green'
        elif h < 0.67:
            return 'blue'
        elif h < 0.75:
            return 'purple'
        else:
            return 'pink'
    
    def generate_character_inspiration(self):
        """色分析結果からキャラクター要素を生成"""
        if not self.dominant_colors:
            self.analyze_colors()
        
        color_descriptions = []
        for color_data in self.dominant_colors[:3]:  # 上位3色
            color_descriptions.append(
                f"{color_data['name']}({color_data['hex']}) - {color_data['emotion']} "
                f"({color_data['percentage']:.1f}%)"
            )
        
        prompt = f"""
        ルリちゃんのイメージボードから以下の色彩分析結果が得られました：
        {'; '.join(color_descriptions)}
        
        この色彩情報を基に、以下の要素を提案してください：
        1. 新しい衣装デザインのアイデア
        2. 感情表現の新しいバリエーション
        3. 配信背景や演出のアイデア
        4. この色合いに合う新しい性格要素
        
        ルリちゃんの既存設定（感情を学んで色づく存在）に合わせて提案してください。
        """
        
        if os.getenv("OPENAI_API_KEY"):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはキャラクターデザインの専門家です。"},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message["content"]
        else:
            return f"色彩分析結果: {color_descriptions}"
    
    def create_color_palette_config(self):
        """Live2D/3D用のカラーパレット設定を生成"""
        if not self.dominant_colors:
            self.analyze_colors()
        
        config = {
            "character_name": "Ruri",
            "base_colors": {
                "monochrome": ["#000000", "#FFFFFF", "#808080"],
                "accent": ["#1E3A8A", "#FFD700"]  # 藍色と金色
            },
            "emotion_palettes": {}
        }
        
        # 主要色を感情段階に割り当て
        emotion_stages = ["joy", "anger", "sadness", "love"]
        for i, color_data in enumerate(self.dominant_colors[:4]):
            if i < len(emotion_stages):
                stage = emotion_stages[i]
                config["emotion_palettes"][stage] = {
                    "primary": color_data['hex'],
                    "emotion": color_data['emotion'],
                    "usage_percentage": color_data['percentage']
                }
        
        return config

def create_imageboard_integration():
    """イメージボード連携機能の実装例"""
    analyzer = RuriImageAnalyzer("assets/ruri_imageboard.png")
    
    print("=== ルリちゃんイメージボード分析 ===")
    colors = analyzer.analyze_colors()
    
    print("\n主要色分析:")
    for i, color in enumerate(colors, 1):
        print(f"{i}. {color['name']} ({color['hex']}) - {color['emotion']} ({color['percentage']:.1f}%)")
    
    print("\n=== キャラクター発展提案 ===")
    inspiration = analyzer.generate_character_inspiration()
    print(inspiration)
    
    print("\n=== Live2D/3D用カラー設定 ===")
    config = analyzer.create_color_palette_config()
    print(f"設定ファイル: {config}")
    
    return analyzer

if __name__ == "__main__":
    create_imageboard_integration()
