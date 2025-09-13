# AI Providers パッケージ
# 様々なAIライブラリを統一インターフェースで利用可能にする

from .base_provider import BaseAIProvider
from .registry import AIProviderRegistry
from .simple_provider import SimpleAIProvider
from .config_manager import AIProviderConfigManager, config_manager

# 動的インポート用
__all__ = [
    'BaseAIProvider',
    'AIProviderRegistry', 
    'SimpleAIProvider',
    'AIProviderConfigManager',
    'config_manager'
]

# グローバルレジストリインスタンス（設定管理統合）
registry = AIProviderRegistry()

# デフォルトプロバイダー登録
registry.register('simple', SimpleAIProvider)

# オプショナルプロバイダーの動的登録（Ollama削除で軽量化）
# try:
#     from .ollama_provider import OllamaAIProvider
#     registry.register('ollama', OllamaAIProvider)
# except ImportError:
#     pass

try:
    from .openai_provider import OpenAIProvider
    registry.register('openai', OpenAIProvider)
except ImportError:
    pass

try:
    from .gptoss_provider import GPTOSSProvider
    registry.register('gpt-oss', GPTOSSProvider)
except ImportError:
    pass

try:
    from .huggingface_provider import HuggingFaceProvider
    registry.register('huggingface', HuggingFaceProvider)
except ImportError:
    pass

# 設定管理との統合
def get_configured_provider(force_reload: bool = False):
    """設定ファイルに基づいて最適なプロバイダーを取得"""
    if force_reload:
        config_manager.load_config()
    
    preferences = config_manager.get_provider_preferences()
    
    for provider_name in preferences:
        provider_config = config_manager.get_provider_config(provider_name)
        provider = registry.create_provider(provider_name, provider_config)
        if provider:
            print(f"🎯 設定優先度に基づいて '{provider_name}' を選択しました")
            return provider
    
    print("⚠️  設定されたプロバイダーが見つかりません。フォールバックを使用します。")
    return registry.create_provider('simple')
