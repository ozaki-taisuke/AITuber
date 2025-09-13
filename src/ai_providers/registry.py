from typing import Dict, Type, List, Any, Optional
from .base_provider import BaseAIProvider

class AIProviderRegistry:
    """AIプロバイダーの動的レジストリ
    
    利用可能なAIライブラリを自動検出し、統一インターフェースで管理
    """
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseAIProvider]] = {}
        self._instances: Dict[str, BaseAIProvider] = {}
        self._default_provider = "simple"
    
    def register(self, name: str, provider_class: Type[BaseAIProvider]):
        """プロバイダーを登録"""
        self._providers[name] = provider_class
        print(f"✅ AIプロバイダー '{name}' を登録しました")
    
    def unregister(self, name: str):
        """プロバイダーの登録解除"""
        if name in self._providers:
            del self._providers[name]
            if name in self._instances:
                del self._instances[name]
            print(f"❌ AIプロバイダー '{name}' の登録を解除しました")
    
    def get_available_providers(self) -> List[str]:
        """利用可能なプロバイダー一覧"""
        available = []
        for name, provider_class in self._providers.items():
            try:
                # インスタンス化してテスト
                instance = provider_class()
                if instance.is_available():
                    available.append(name)
            except Exception:
                continue
        return available
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """プロバイダー詳細情報"""
        info = {}
        for name, provider_class in self._providers.items():
            try:
                instance = provider_class()
                info[name] = {
                    "class_name": provider_class.__name__,
                    "available": instance.is_available(),
                    "status": instance.get_status_info()
                }
            except Exception as e:
                info[name] = {
                    "class_name": provider_class.__name__,
                    "available": False,
                    "error": str(e)
                }
        return info
    
    def create_provider(self, 
                       name: str, 
                       config: Dict[str, Any] = None,
                       force_new: bool = False) -> Optional[BaseAIProvider]:
        """プロバイダーインスタンスの作成"""
        
        # キャッシュされたインスタンスを返す
        if not force_new and name in self._instances:
            return self._instances[name]
        
        # 新しいインスタンスを作成
        if name not in self._providers:
            print(f"❌ 未知のプロバイダー: {name}")
            return None
        
        try:
            provider_class = self._providers[name]
            instance = provider_class(config)
            
            if not instance.is_available():
                print(f"⚠️  プロバイダー '{name}' は現在利用できません")
                return None
            
            self._instances[name] = instance
            print(f"✅ プロバイダー '{name}' のインスタンスを作成しました")
            return instance
            
        except Exception as e:
            print(f"❌ プロバイダー '{name}' の作成に失敗: {e}")
            return None
    
    def get_best_available_provider(self, 
                                   preferences: List[str] = None) -> Optional[BaseAIProvider]:
        """最適な利用可能プロバイダーを取得"""
        
        # 優先順位リスト
        if preferences is None:
            preferences = ["gpt-oss", "ollama", "openai", "huggingface", "simple"]
        
        available_providers = self.get_available_providers()
        
        # 優先順位に従って選択
        for preferred in preferences:
            if preferred in available_providers:
                return self.create_provider(preferred)
        
        # フォールバック: 利用可能な最初のもの
        if available_providers:
            return self.create_provider(available_providers[0])
        
        print("❌ 利用可能なAIプロバイダーがありません")
        return None
    
    def set_default_provider(self, name: str):
        """デフォルトプロバイダーの設定"""
        if name in self._providers:
            self._default_provider = name
            print(f"✅ デフォルトプロバイダーを '{name}' に設定しました")
        else:
            print(f"❌ 未知のプロバイダー: {name}")
    
    def get_default_provider(self) -> Optional[BaseAIProvider]:
        """デフォルトプロバイダーの取得"""
        return self.create_provider(self._default_provider)
    
    def list_providers(self) -> Dict[str, str]:
        """登録済みプロバイダー一覧"""
        return {
            name: provider_class.__name__ 
            for name, provider_class in self._providers.items()
        }
    
    def test_all_providers(self) -> Dict[str, bool]:
        """全プロバイダーの動作テスト"""
        results = {}
        for name in self._providers.keys():
            try:
                provider = self.create_provider(name, force_new=True)
                if provider:
                    # 簡単なテスト
                    response = provider.generate_response("テスト")
                    results[name] = bool(response and response.text)
                else:
                    results[name] = False
            except Exception:
                results[name] = False
        
        return results
    
    def clear_cache(self):
        """インスタンスキャッシュのクリア"""
        self._instances.clear()
        print("🧹 プロバイダーキャッシュをクリアしました")
