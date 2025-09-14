// 画像ウォーターマーク挿入スクリプト
// 権利保護のため、重要な画像ファイルにウォーターマークを挿入

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

class WatermarkManager:
    """画像の権利保護用ウォーターマーク管理"""
    
    def __init__(self):
        self.copyright_text = "© ozaki-taisuke / まつはち"
        self.project_text = "AITuber ルリ プロジェクト"
        
    def add_watermark(self, image_path, output_path=None, opacity=0.3):
        """
        画像にウォーターマークを追加
        
        Args:
            image_path: 元画像のパス
            output_path: 出力パス（Noneの場合は元画像を上書き）
            opacity: 透明度（0.0-1.0）
        """
        try:
            # 画像を読み込み
            image = Image.open(image_path).convert("RGBA")
            
            # ウォーターマーク用の透明レイヤーを作成
            watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # フォントサイズを画像サイズに応じて調整
            font_size = max(12, min(image.size) // 40)
            
            try:
                # システムフォントを使用（日本語対応）
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # ウォーターマーク位置を計算（右下）
            text_bbox = draw.textbbox((0, 0), self.copyright_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = image.size[0] - text_width - 10
            y = image.size[1] - text_height - 10
            
            # 著作権表示を描画
            draw.text((x, y), self.copyright_text, 
                     fill=(255, 255, 255, int(255 * opacity)), font=font)
            
            # プロジェクト名を描画（上の行）
            project_y = y - text_height - 5
            draw.text((x, project_y), self.project_text, 
                     fill=(200, 200, 200, int(255 * opacity * 0.8)), font=font)
            
            # 元画像とウォーターマークを合成
            watermarked = Image.alpha_composite(image, watermark)
            
            # 出力パスが指定されていない場合は元画像を更新
            if output_path is None:
                output_path = image_path
                
            # RGBに変換して保存（透明度情報を除去）
            watermarked_rgb = watermarked.convert("RGB")
            watermarked_rgb.save(output_path, "PNG", quality=95)
            
            print(f"✅ ウォーターマーク追加完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ ウォーターマーク追加エラー: {e}")
            return False
    
    def protect_project_images(self, base_dir="assets"):
        """
        プロジェクト内の重要な画像ファイルにウォーターマークを追加
        """
        image_files = [
            "image.png",
            "ruri_imageboard.png"
        ]
        
        protected_dir = os.path.join(base_dir, "protected")
        os.makedirs(protected_dir, exist_ok=True)
        
        for filename in image_files:
            input_path = os.path.join(base_dir, filename)
            output_path = os.path.join(protected_dir, f"watermarked_{filename}")
            
            if os.path.exists(input_path):
                self.add_watermark(input_path, output_path)
            else:
                print(f"⚠️  ファイルが見つかりません: {input_path}")

if __name__ == "__main__":
    # 使用例
    watermark_manager = WatermarkManager()
    watermark_manager.protect_project_images()