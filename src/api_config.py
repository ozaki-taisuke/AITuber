# -*- coding: utf-8 -*-
"""
API設定統一管理

このモジュールはプロジェクト全体のAPI設定を統一管理します。
環境変数、.envファイル、Streamlitのsecretsから値を優先順位に従って取得します。
"""

import os
from typing import Dict, Optional, Any
from pathlib import Path

class APIConfig:
    """API設定統一管理クラス"""
    
    # プロジェクトルートディレクトリ
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # 環境変数名の定数
    OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY_ENV = "ANTHROPIC_API_KEY"
    GOOGLE_API_KEY_ENV = "GOOGLE_API_KEY"
    OLLAMA_BASE_URL_ENV = "OLLAMA_BASE_URL"
    HUGGINGFACE_API_TOKEN_ENV = "HUGGINGFACE_API_TOKEN"
    COHERE_API_KEY_ENV = "COHERE_API_KEY"
    AZURE_OPENAI_API_KEY_ENV = "AZURE_OPENAI_API_KEY"
    AZURE_OPENAI_ENDPOINT_ENV = "AZURE_OPENAI_ENDPOINT"
    
    # デフォルト値
    DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
    
    # プレースホルダー値（ハードコーディング回避）
    PLACEHOLDER_API_KEY = "YOUR_API_KEY_HERE"
    PLACEHOLDER_OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
    
    @classmethod
    def load_env_file(cls) -> None:
        """プロジェクトルートの.envファイルを読み込み"""
        env_file = cls.PROJECT_ROOT / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                # python-dotenvがない場合は手動で読み込み
                cls._load_env_manually(env_file)
    
    @classmethod
    def _load_env_manually(cls, env_file: Path) -> None:
        """手動で.envファイルを読み込み（python-dotenv無しの場合）"""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and not os.getenv(key):  # 既存の環境変数を上書きしない
                            os.environ[key] = value
        except Exception:
            pass  # エラーは無視
    
    @classmethod
    def get_openai_api_key(cls) -> str:
        """OpenAI APIキーを取得（優先順位: 環境変数 > .env > Streamlit secrets）"""
        cls.load_env_file()
        
        # 1. 環境変数から取得
        api_key = os.getenv(cls.OPENAI_API_KEY_ENV)
        if api_key and api_key != cls.PLACEHOLDER_OPENAI_API_KEY:
            return api_key
        
        # 2. Streamlit secretsから取得（利用可能な場合）
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and cls.OPENAI_API_KEY_ENV in st.secrets:
                secret_key = st.secrets[cls.OPENAI_API_KEY_ENV]
                if secret_key != cls.PLACEHOLDER_OPENAI_API_KEY:
                    return secret_key
        except (ImportError, Exception):
            pass
        
        return ""
    
    @classmethod
    def get_api_key(cls, provider: str) -> str:
        """指定されたプロバイダーのAPIキーを取得"""
        cls.load_env_file()
        
        env_map = {
            "openai": cls.OPENAI_API_KEY_ENV,
            "anthropic": cls.ANTHROPIC_API_KEY_ENV,
            "google": cls.GOOGLE_API_KEY_ENV,
            "huggingface": cls.HUGGINGFACE_API_TOKEN_ENV,
            "cohere": cls.COHERE_API_KEY_ENV,
            "azure": cls.AZURE_OPENAI_API_KEY_ENV,
        }
        
        env_name = env_map.get(provider.lower())
        if not env_name:
            return ""
        
        # 特別処理：OpenAIの場合は専用メソッドを使用
        if provider.lower() == "openai":
            return cls.get_openai_api_key()
        
        # 1. 環境変数から取得
        api_key = os.getenv(env_name)
        if api_key and api_key != cls.PLACEHOLDER_API_KEY:
            return api_key
        
        # 2. Streamlit secretsから取得（利用可能な場合）
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and env_name in st.secrets:
                secret_key = st.secrets[env_name]
                if secret_key != cls.PLACEHOLDER_API_KEY:
                    return secret_key
        except (ImportError, Exception):
            pass
        
        return ""
    
    @classmethod
    def get_ollama_base_url(cls) -> str:
        """Ollama Base URLを取得"""
        cls.load_env_file()
        return os.getenv(cls.OLLAMA_BASE_URL_ENV, cls.DEFAULT_OLLAMA_BASE_URL)
    
    @classmethod
    def get_azure_config(cls) -> Dict[str, str]:
        """Azure OpenAI設定を取得"""
        cls.load_env_file()
        return {
            "api_key": cls.get_api_key("azure"),
            "endpoint": os.getenv(cls.AZURE_OPENAI_ENDPOINT_ENV, ""),
        }
    
    @classmethod
    def get_all_api_keys(cls) -> Dict[str, str]:
        """全てのAPIキーを取得"""
        return {
            cls.OPENAI_API_KEY_ENV: cls.get_openai_api_key(),
            cls.ANTHROPIC_API_KEY_ENV: cls.get_api_key("anthropic"),
            cls.GOOGLE_API_KEY_ENV: cls.get_api_key("google"),
            cls.HUGGINGFACE_API_TOKEN_ENV: cls.get_api_key("huggingface"),
            cls.COHERE_API_KEY_ENV: cls.get_api_key("cohere"),
            cls.AZURE_OPENAI_API_KEY_ENV: cls.get_api_key("azure"),
        }
    
    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """指定されたプロバイダーが利用可能かチェック"""
        api_key = cls.get_api_key(provider)
        return bool(api_key)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """利用可能なプロバイダーのリストを取得"""
        providers = ["openai", "anthropic", "google", "huggingface", "cohere", "azure"]
        available = []
        
        for provider in providers:
            if cls.is_provider_available(provider):
                available.append(provider)
        
        # Ollamaは常に利用可能とみなす（ローカル実行のため）
        available.append("ollama")
        
        return available

# グローバル設定インスタンス（後方互換性のため）
config = APIConfig()