# 統一環境設定ファイル
import os
from typing import Dict, Any, List
from enum import Enum

class UserLevel(Enum):
    """ユーザーアクセスレベル"""
    PUBLIC = "public"           # 一般公開（認証なし）
    BETA = "beta"              # ベータテスター（簡易認証）
    DEVELOPER = "developer"     # 開発者（フル機能）
    ADMIN = "admin"            # 管理者（全機能 + 管理機能）

class UnifiedConfig:
    """統一環境設定管理"""
    
    # 基本設定
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # 認証設定（環境変数・Streamlit Secrets対応）
    @classmethod
    def get_passwords(cls) -> Dict[str, str]:
        """認証パスワードを取得"""
        try:
            # Streamlit secrets から取得を試行
            import streamlit as st
            if hasattr(st, 'secrets'):
                return {
                    'BETA_PASSWORD': st.secrets.get('BETA_PASSWORD', 'ruri_beta_2024'),
                    'DEVELOPER_PASSWORD': st.secrets.get('DEVELOPER_PASSWORD', 'ruri_dev_2024'),
                    'ADMIN_PASSWORD': st.secrets.get('ADMIN_PASSWORD', 'ruri_admin_2024')
                }
        except Exception:
            pass
        
        # 環境変数から取得
        return {
            'BETA_PASSWORD': os.getenv('BETA_PASSWORD', 'ruri_beta_2024'),
            'DEVELOPER_PASSWORD': os.getenv('DEVELOPER_PASSWORD', 'ruri_dev_2024'),
            'ADMIN_PASSWORD': os.getenv('ADMIN_PASSWORD', 'ruri_admin_2024')
        }
    
    # 認証設定
    _passwords = get_passwords.__func__(None)
    BETA_PASSWORD = _passwords['BETA_PASSWORD']
    DEVELOPER_PASSWORD = _passwords['DEVELOPER_PASSWORD']
    ADMIN_PASSWORD = _passwords['ADMIN_PASSWORD']
    
    # API設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # アプリケーション設定
    APP_NAME = "AITuber ルリ"
    APP_VERSION = "1.0.0-unified"
    
    @classmethod
    def get_user_level(cls, session_state) -> UserLevel:
        """セッション状態からユーザーレベルを取得"""
        if session_state.get("admin_authenticated"):
            return UserLevel.ADMIN
        elif session_state.get("developer_authenticated"):
            return UserLevel.DEVELOPER
        elif session_state.get("beta_authenticated"):
            return UserLevel.BETA
        else:
            return UserLevel.PUBLIC
    
    @classmethod
    def get_available_features(cls, user_level: UserLevel) -> Dict[str, bool]:
        """ユーザーレベルに応じた利用可能機能"""
        features = {
            # 基本機能（全ユーザー）
            "character_display": True,
            "basic_ui": True,
            "image_upload": True,
            
            # ベータ機能
            "ai_chat": user_level.value in ["beta", "developer", "admin"],
            "emotion_learning": user_level.value in ["beta", "developer", "admin"],
            "advanced_image_analysis": user_level.value in ["beta", "developer", "admin"],
            
            # 開発者機能
            "obs_integration": user_level.value in ["developer", "admin"],
            "streaming_features": user_level.value in ["developer", "admin"],
            "api_access": user_level.value in ["developer", "admin"],
            "debug_info": user_level.value in ["developer", "admin"],
            
            # 管理者機能
            "user_management": user_level.value == "admin",
            "system_settings": user_level.value == "admin",
            "analytics": user_level.value == "admin",
            "log_viewer": user_level.value == "admin",
        }
        return features
    
    @classmethod
    def get_ui_config(cls, user_level: UserLevel) -> Dict[str, Any]:
        """ユーザーレベルに応じたUI設定"""
        configs = {
            UserLevel.PUBLIC: {
                "theme": "light",
                "sidebar_expanded": False,
                "show_advanced_options": False,
                "show_technical_details": False,
                "header_color": "#667eea",
                "title_suffix": "",
            },
            UserLevel.BETA: {
                "theme": "light",
                "sidebar_expanded": True,
                "show_advanced_options": True,
                "show_technical_details": False,
                "header_color": "#ff6b6b",
                "title_suffix": " - ベータ版",
            },
            UserLevel.DEVELOPER: {
                "theme": "dark",
                "sidebar_expanded": True,
                "show_advanced_options": True,
                "show_technical_details": True,
                "header_color": "#4ecdc4",
                "title_suffix": " - 開発者版",
            },
            UserLevel.ADMIN: {
                "theme": "dark",
                "sidebar_expanded": True,
                "show_advanced_options": True,
                "show_technical_details": True,
                "header_color": "#f39c12",
                "title_suffix": " - 管理者版",
            }
        }
        return configs.get(user_level, configs[UserLevel.PUBLIC])
    
    @classmethod
    def get_navigation_menu(cls, user_level: UserLevel) -> List[Dict[str, str]]:
        """ユーザーレベルに応じたナビゲーションメニュー"""
        base_menu = [
            {"icon": "🏠", "title": "ホーム", "page": "home"},
            {"icon": "👤", "title": "キャラクター", "page": "character"},
            {"icon": "🎨", "title": "画像分析", "page": "image"},
        ]
        
        if user_level.value in ["beta", "developer", "admin"]:
            base_menu.extend([
                {"icon": "💬", "title": "AI会話", "page": "chat"},
                {"icon": "📊", "title": "統計", "page": "stats"},
            ])
        
        if user_level.value in ["developer", "admin"]:
            base_menu.extend([
                {"icon": "🎥", "title": "OBS連携", "page": "obs"},
                {"icon": "📺", "title": "配信管理", "page": "streaming"},
                {"icon": "⚙️", "title": "設定", "page": "settings"},
            ])
        
        if user_level.value == "admin":
            base_menu.extend([
                {"icon": "👥", "title": "ユーザー管理", "page": "users"},
                {"icon": "📋", "title": "ログ", "page": "logs"},
            ])
        
        return base_menu
    
    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうかを判定"""
        return cls.ENVIRONMENT == 'production'