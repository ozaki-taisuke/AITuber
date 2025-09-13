# Live2D・OBS連携システム

import json
import websocket
import threading
import time
from typing import Dict, Any, List
import requests
from src.character_ai import RuriCharacter
from src.image_analyzer import RuriImageAnalyzer

class Live2DController:
    """Live2D Cubism連携コントローラー"""
    
    def __init__(self, websocket_url="ws://localhost:8001"):
        self.websocket_url = websocket_url
        self.ws = None
        self.ruri = RuriCharacter()
        self.current_emotion = "neutral"
        self.color_data = {}
        
    def connect_live2d(self):
        """Live2D Cubism SDKへのWebSocket接続"""
        try:
            self.ws = websocket.WebSocketApp(
                self.websocket_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws.on_open = self.on_open
            self.ws.run_forever()
        except Exception as e:
            print(f"Live2D接続エラー: {e}")
    
    def on_open(self, ws):
        print("Live2D接続成功")
        
    def on_message(self, ws, message):
        print(f"Live2Dからのメッセージ: {message}")
        
    def on_error(self, ws, error):
        print(f"Live2Dエラー: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print("Live2D接続終了")
    
    def update_emotion_colors(self, emotion: str, intensity: float = 1.0):
        """感情に応じた色変更をLive2Dに送信"""
        color_mapping = {
            "joy": {"r": 255, "g": 255, "b": 0, "a": intensity},      # 黄色
            "anger": {"r": 255, "g": 0, "b": 0, "a": intensity},      # 赤色
            "sadness": {"r": 0, "g": 0, "b": 255, "a": intensity},    # 青色
            "love": {"r": 255, "g": 192, "b": 203, "a": intensity},   # ピンク
            "neutral": {"r": 128, "g": 128, "b": 128, "a": 0.5}       # グレー
        }
        
        if emotion in color_mapping:
            color = color_mapping[emotion]
            command = {
                "command": "setParameterValue",
                "parameterId": "ParamHairColorR",
                "value": color["r"] / 255.0
            }
            self.send_to_live2d(command)
            
            command = {
                "command": "setParameterValue", 
                "parameterId": "ParamHairColorG",
                "value": color["g"] / 255.0
            }
            self.send_to_live2d(command)
            
            command = {
                "command": "setParameterValue",
                "parameterId": "ParamHairColorB", 
                "value": color["b"] / 255.0
            }
            self.send_to_live2d(command)
    
    def send_to_live2d(self, command: Dict[str, Any]):
        """Live2Dにコマンド送信"""
        if self.ws:
            self.ws.send(json.dumps(command))

class OBSController:
    """OBS Studio WebSocket連携コントローラー"""
    
    def __init__(self, obs_host="localhost", obs_port=4444, obs_password=""):
        self.obs_host = obs_host
        self.obs_port = obs_port
        self.obs_password = obs_password
        self.ruri = RuriCharacter()
        
    def connect_obs(self):
        """OBS WebSocketに接続"""
        try:
            import obswebsocket
            from obswebsocket import obsws, requests as obs_requests
            
            self.ws = obsws(self.obs_host, self.obs_port, self.obs_password)
            self.ws.connect()
            print("OBS接続成功")
            return True
        except Exception as e:
            print(f"OBS接続エラー: {e}")
            return False
    
    def update_scene_by_emotion(self, emotion: str):
        """感情に応じてOBSシーンを切り替え"""
        scene_mapping = {
            "joy": "ルリ_喜び",
            "anger": "ルリ_怒り", 
            "sadness": "ルリ_哀しみ",
            "love": "ルリ_愛",
            "neutral": "ルリ_通常"
        }
        
        if emotion in scene_mapping:
            try:
                self.ws.call(obs_requests.SetCurrentScene(scene_mapping[emotion]))
                print(f"OBSシーンを{scene_mapping[emotion]}に変更")
            except Exception as e:
                print(f"OBSシーン変更エラー: {e}")
    
    def update_filter_colors(self, emotion: str):
        """感情に応じてカラーフィルターを調整"""
        filter_settings = {
            "joy": {"hue_shift": 60, "saturation": 1.5, "brightness": 1.2},
            "anger": {"hue_shift": 0, "saturation": 2.0, "brightness": 1.0},
            "sadness": {"hue_shift": 240, "saturation": 0.8, "brightness": 0.8},
            "love": {"hue_shift": 300, "saturation": 1.3, "brightness": 1.1},
            "neutral": {"hue_shift": 0, "saturation": 1.0, "brightness": 1.0}
        }
        
        if emotion in filter_settings:
            settings = filter_settings[emotion]
            try:
                # カラーフィルターの設定を更新
                filter_data = {
                    "sourceName": "ルリカメラ",
                    "filterName": "感情カラーフィルター",
                    "filterSettings": settings
                }
                self.ws.call(obs_requests.SetSourceFilterSettings(**filter_data))
                print(f"カラーフィルターを{emotion}用に設定")
            except Exception as e:
                print(f"フィルター設定エラー: {e}")

class StreamingIntegration:
    """配信統合システム"""
    
    def __init__(self):
        self.ruri = RuriCharacter()
        self.live2d = Live2DController()
        self.obs = OBSController()
        self.image_analyzer = RuriImageAnalyzer("assets/ruri_imageboard.png")
        self.is_streaming = False
        
    def start_streaming_mode(self):
        """配信モード開始"""
        print("ルリ配信モード開始")
        
        # Live2D接続
        live2d_thread = threading.Thread(target=self.live2d.connect_live2d)
        live2d_thread.daemon = True
        live2d_thread.start()
        
        # OBS接続
        if self.obs.connect_obs():
            print("OBS連携開始")
        
        # イメージボード分析
        colors = self.image_analyzer.analyze_colors()
        print(f"イメージボード分析完了: {len(colors)}色を検出")
        
        self.is_streaming = True
        
    def process_viewer_comment(self, comment: str, emotion: str):
        """視聴者コメントを処理して各システムに反映"""
        # ルリの感情学習
        response = self.ruri.learn_emotion(emotion, comment)
        
        # Live2Dに色変更を送信
        self.live2d.update_emotion_colors(emotion)
        
        # OBSのシーン・フィルター更新
        self.obs.update_scene_by_emotion(emotion)
        self.obs.update_filter_colors(emotion)
        
        return {
            "ruri_response": response,
            "emotion": emotion,
            "color_stage": self.ruri.current_color_stage,
            "systems_updated": ["Live2D", "OBS"]
        }
    
    def create_obs_scene_preset(self):
        """OBS用シーンプリセットを生成"""
        emotions = ["joy", "anger", "sadness", "love", "neutral"]
        
        scene_config = {
            "scenes": [],
            "sources": []
        }
        
        for emotion in emotions:
            scene_name = f"ルリ_{emotion}"
            scene_config["scenes"].append({
                "name": scene_name,
                "sources": [
                    {
                        "name": "ルリカメラ",
                        "type": "window_capture",
                        "settings": {
                            "window": "Live2D Cubism - ルリ"
                        }
                    },
                    {
                        "name": "感情カラーフィルター",
                        "type": "color_filter",
                        "emotion": emotion
                    },
                    {
                        "name": "背景",
                        "type": "image_source",
                        "settings": {
                            "file": f"assets/background_{emotion}.png"
                        }
                    }
                ]
            })
        
        return scene_config

def create_live2d_parameter_mapping():
    """Live2D用パラメータマッピングを生成"""
    return {
        "color_parameters": {
            "hair": ["ParamHairColorR", "ParamHairColorG", "ParamHairColorB"],
            "eyes": ["ParamEyeColorR", "ParamEyeColorG", "ParamEyeColorB"],
            "clothes": ["ParamClothesColorR", "ParamClothesColorG", "ParamClothesColorB"]
        },
        "emotion_parameters": {
            "joy": {"ParamMouthForm": 1.0, "ParamEyeForm": 1.0},
            "anger": {"ParamMouthForm": -0.5, "ParamEyeForm": -0.3},
            "sadness": {"ParamMouthForm": -1.0, "ParamEyeForm": -1.0},
            "love": {"ParamMouthForm": 0.8, "ParamEyeForm": 0.8}
        },
        "breathing": {
            "parameter": "ParamBreath",
            "cycle": 3.0,
            "amplitude": 0.5
        }
    }

if __name__ == "__main__":
    # 統合システムのテスト
    integration = StreamingIntegration()
    integration.start_streaming_mode()
    
    # サンプル視聴者コメント処理
    result = integration.process_viewer_comment("ルリちゃん、とても楽しいです！", "joy")
    print(f"処理結果: {result}")
