# 統一環境設定ファイル
import os
from typing import Dict, Any, List
from enum import Enum

try:
    from .api_config import APIConfig
except ImportError:
    from api_config import APIConfig

class UserLevel(Enum):
    """ユーザーアクセスレベル"""
    PUBLIC = "public"          # 一般公開（認証なし）
    OWNER = "owner"           # 所有者（全機能アクセス）

class UnifiedConfig:
    """統一環境設定管理"""
    
    # 基本設定
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # 認証設定（環境変数・Streamlit Secrets対応）
    @classmethod
    def get_passwords(cls) -> Dict[str, str]:
        """認証パスワードとユーザー名を取得（デフォルトは空文字）"""
        try:
            # Streamlit secrets から取得を試行
            import streamlit as st
            if hasattr(st, 'secrets'):
                return {
                    'OWNER_PASSWORD': st.secrets.get('OWNER_PASSWORD', ''),
                    'OWNER_USERNAME': st.secrets.get('OWNER_USERNAME', '')
                }
        except Exception:
            pass
        
        # 環境変数から取得（デフォルトは空文字）
        return {
            'OWNER_PASSWORD': os.getenv('OWNER_PASSWORD', ''),
            'OWNER_USERNAME': os.getenv('OWNER_USERNAME', '')
        }
    
    # 認証設定
    _passwords = get_passwords.__func__(None)
    OWNER_PASSWORD = _passwords['OWNER_PASSWORD']
    OWNER_USERNAME = _passwords['OWNER_USERNAME']
    
    # API設定（新しいAPIConfig使用）
    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """APIキーを取得（統一設定管理）"""
        return APIConfig.get_all_api_keys()
    
    # API設定
    _api_keys = get_api_keys.__func__(None)
    OPENAI_API_KEY = APIConfig.get_openai_api_key()
    
    # アプリケーション設定
    APP_NAME = "AITuber ルリ"
    APP_VERSION = "1.0.0-unified"
    
    @classmethod
    def get_user_level(cls, session_state) -> UserLevel:
        """セッション状態からユーザーレベルを取得"""
        if session_state.get("owner_authenticated"):
            return UserLevel.OWNER
        else:
            return UserLevel.PUBLIC
    
    @classmethod
    def get_available_features(cls, user_level: UserLevel) -> Dict[str, bool]:
        """ユーザーレベルに応じた利用可能機能"""
        # 所有者認証時は全機能有効、未認証時は基本機能のみ
        is_owner = (user_level == UserLevel.OWNER)
        
        features = {
            # 基本機能（全ユーザー）
            "character_display": True,
            "basic_ui": True,
            "image_upload": True,
            "ai_conversation": False,    # 一時的に無効化
            "character_status": False,   # 未実装のため無効化
            
            # 限定開放機能（パブリックでも利用可能）
            "ai_chat": True,            # AIチャット機能を全ユーザーに開放
            "emotion_learning": True,   # 感情学習の表示
            "basic_image_analysis": False, # 未実装のため無効化
            
            # 所有者専用機能（未実装のため全て無効化）
            "advanced_image_analysis": False,
            "obs_integration": False,
            "streaming_integration": False,
            "api_access": False,
            "debug_info": False,
            "user_management": False,
            "system_settings": False,
            "analytics": False,
            "log_viewer": False,
        }
        return features
    
    @classmethod
    def get_ui_config(cls, user_level: UserLevel) -> Dict[str, Any]:
        """ユーザーレベルに応じたUI設定"""
        if user_level == UserLevel.OWNER:
            return {
                "theme": "dark",
                "sidebar_expanded": True,
                "show_advanced_options": True,
                "show_technical_details": True,
                "header_color": "#6366f1",
                "title_suffix": " - 所有者モード",
            }
        else:
            return {
                "theme": "light",
                "sidebar_expanded": False,
                "show_advanced_options": False,
                "show_technical_details": False,
                "header_color": "#667eea",
                "title_suffix": "",
            }
    
    @classmethod
    def get_navigation_menu(cls, user_level: UserLevel) -> List[Dict[str, str]]:
        """ユーザーレベルに応じたナビゲーションメニュー"""
        base_menu = [
            {"icon": "🏠", "title": "ホーム", "page": "home"},
            {"icon": "👤", "title": "キャラクター", "page": "character"},
            {"icon": "🎨", "title": "画像分析", "page": "image"},
        ]
        
        if user_level == UserLevel.OWNER:
            # 所有者は全機能にアクセス可能
            owner_menu = [
                {"icon": "💬", "title": "AI会話", "page": "chat"},
                {"icon": "📊", "title": "統計", "page": "stats"},
                {"icon": "🎥", "title": "OBS連携", "page": "obs"},
                {"icon": "📺", "title": "配信管理", "page": "streaming"},
                {"icon": "⚙️", "title": "システム設定", "page": "settings"},
                {"icon": "👥", "title": "ユーザー管理", "page": "users"},
                {"icon": "📋", "title": "ログ", "page": "logs"},
            ]
            base_menu.extend(owner_menu)
        
        return base_menu
    
    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうかを判定"""
        return cls.ENVIRONMENT == 'production'