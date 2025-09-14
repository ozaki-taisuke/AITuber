# 本番環境用設定ファイル
import os
from typing import Dict, Any

class ProductionConfig:
    """本番環境用の設定管理"""
    
    # デバッグモード（本番では False）
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # セキュリティ設定
    BETA_PASSWORD = os.getenv('BETA_PASSWORD', 'ruri_beta_2024')
    
    # AI API設定（環境変数から取得）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # データベース設定（将来用）
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    # アプリケーション設定
    APP_NAME = "AITuber ルリ - ベータ版"
    APP_VERSION = "0.1.0-beta"
    
    # 機能フラグ（本番で無効化したい機能）
    ENABLE_DEBUG_FEATURES = DEBUG
    ENABLE_AI_FEATURES = os.getenv('ENABLE_AI_FEATURES', 'True').lower() == 'true'
    ENABLE_OBS_INTEGRATION = os.getenv('ENABLE_OBS_INTEGRATION', 'False').lower() == 'true'
    ENABLE_STREAMING_FEATURES = os.getenv('ENABLE_STREAMING_FEATURES', 'False').lower() == 'true'
    BETA_AUTH_REQUIRED = os.getenv('BETA_AUTH_REQUIRED', 'False').lower() == 'true'
    
    # UI設定
    SHOW_TECHNICAL_DETAILS = DEBUG
    BETA_MODE = True
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """設定をdict形式で取得"""
        return {
            'debug': cls.DEBUG,
            'app_name': cls.APP_NAME,
            'app_version': cls.APP_VERSION,
            'beta_mode': cls.BETA_MODE,
            'features': {
                'ai': cls.ENABLE_AI_FEATURES,
                'obs': cls.ENABLE_OBS_INTEGRATION,
                'streaming': cls.ENABLE_STREAMING_FEATURES,
                'debug': cls.ENABLE_DEBUG_FEATURES
            }
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうかを判定"""
        return not cls.DEBUG and os.getenv('ENVIRONMENT') == 'production'
    
    @classmethod
    def get_available_ai_providers(cls) -> list:
        """利用可能なAIプロバイダーを返す"""
        providers = ['simple']  # 基本プロバイダーは常に利用可能
        
        if cls.OPENAI_API_KEY:
            providers.append('openai')
        
        if cls.ENABLE_AI_FEATURES:
            providers.extend(['ollama', 'gpt-oss'])
            
        return providers