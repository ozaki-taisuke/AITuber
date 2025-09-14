"""
環境変数・設定管理ユーティリティ
複数プラットフォーム対応（ローカル、Streamlit Cloud、Docker等）
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path


class ConfigManager:
    """統一設定管理クラス"""
    
    def __init__(self):
        self.config_cache = {}
        self._load_environment()
    
    def _load_environment(self):
        """環境変数の読み込み（複数ソース対応）"""
        # 1. .env ファイルの読み込み
        self._load_dotenv()
        
        # 2. Streamlit secrets の読み込み（存在する場合）
        self._load_streamlit_secrets()
    
    def _load_dotenv(self):
        """Python-dotenv風の.envファイル読み込み"""
        try:
            # python-dotenvがあれば使用
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .env ファイルを読み込みました (python-dotenv)")
        except ImportError:
            # 手動で.envファイルを読み込み
            env_path = Path(".env")
            if env_path.exists():
                self._manual_load_env(env_path)
                print("✅ .env ファイルを読み込みました (手動)")
    
    def _manual_load_env(self, env_path: Path):
        """手動での.env ファイル読み込み"""
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
        except Exception as e:
            print(f"⚠️ .env ファイル読み込みエラー: {e}")
    
    def _load_streamlit_secrets(self):
        """Streamlit secrets の読み込み"""
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                # Streamlit秘密情報を環境変数として設定
                for key, value in st.secrets.items():
                    if key not in os.environ:  # 既存の環境変数を優先
                        os.environ[key] = str(value)
                print("✅ Streamlit secrets を読み込みました")
        except:
            pass
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """プロバイダー用APIキーの取得"""
        provider_keys = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'gemini': 'GOOGLE_API_KEY',
            'huggingface': 'HUGGINGFACE_API_KEY',
            'cohere': 'COHERE_API_KEY',
            'azure_openai': 'AZURE_OPENAI_API_KEY',
        }
        
        env_key = provider_keys.get(provider.lower())
        if env_key:
            return os.getenv(env_key)
        return None
    
    def get_model_name(self, provider: str) -> str:
        """プロバイダー用モデル名の取得"""
        provider_models = {
            'openai': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'anthropic': os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307'),
            'google': os.getenv('GEMINI_MODEL', 'gemini-pro'),
            'gemini': os.getenv('GEMINI_MODEL', 'gemini-pro'),
            'huggingface': os.getenv('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-medium'),
            'cohere': os.getenv('COHERE_MODEL', 'command'),
            'ollama': os.getenv('OLLAMA_MODEL', 'llama2'),
        }
        return provider_models.get(provider.lower(), 'default')
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """プロバイダー固有設定の取得"""
        api_key = self.get_api_key(provider)
        if not api_key:
            return {}
        
        base_config = {
            'api_key': api_key,
            'model': self.get_model_name(provider),
            'timeout': int(os.getenv('AI_REQUEST_TIMEOUT', '30')),
            'max_tokens': int(os.getenv('AI_MAX_TOKENS', '500')),
            'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
        }
        
        # プロバイダー固有の設定
        if provider.lower() == 'azure_openai':
            base_config.update({
                'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
                'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                'deployment_name': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            })
        elif provider.lower() == 'ollama':
            base_config.update({
                'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            })
        elif provider.lower() == 'openai':
            base_config.update({
                'organization': os.getenv('OPENAI_ORGANIZATION'),
                'project': os.getenv('OPENAI_PROJECT'),
            })
        
        return base_config
    
    def get_provider_priority(self) -> List[str]:
        """プロバイダー優先順位の取得"""
        priority_str = os.getenv('AI_PROVIDER_PRIORITY', 'openai,simple')
        return [p.strip() for p in priority_str.split(',')]
    
    def get_default_provider(self) -> str:
        """デフォルトプロバイダーの取得"""
        return os.getenv('DEFAULT_AI_PROVIDER', 'openai')
    
    def is_provider_available(self, provider: str) -> bool:
        """プロバイダーが利用可能かチェック"""
        # SimpleプロバイダーはAPIキー不要
        if provider.lower() == 'simple':
            return True
        
        # 他のプロバイダーはAPIキーが必要
        api_key = self.get_api_key(provider)
        return bool(api_key and api_key != 'your_api_key_here')
    
    def get_debug_info(self) -> Dict[str, Any]:
        """デバッグ情報の取得"""
        return {
            'debug_mode': os.getenv('AI_DEBUG_MODE', 'false').lower() == 'true',
            'verbose_logging': os.getenv('AI_VERBOSE_LOGGING', 'false').lower() == 'true',
            'available_providers': [p for p in self.get_provider_priority() if self.is_provider_available(p)],
            'environment': os.getenv('APP_ENVIRONMENT', 'development'),
            'config_sources': ['environment_variables', '.env_file', 'streamlit_secrets']
        }


# グローバルインスタンス
config_manager = ConfigManager()