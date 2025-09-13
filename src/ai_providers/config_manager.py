# AIプロバイダー設定管理システム
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ProviderConfig:
    """AIプロバイダー設定"""
    name: str
    enabled: bool = True
    priority: int = 1  # 1=最高優先度
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}

class AIProviderConfigManager:
    """AIプロバイダー設定管理
    
    ユーザーが設定ファイルやUIから各種AIライブラリの
    優先度や設定を動的に変更できるシステム
    """
    
    def __init__(self, config_file: str = "ai_provider_config.json"):
        self.config_file = config_file
        self.providers: Dict[str, ProviderConfig] = {}
        self.load_config()
    
    def load_config(self):
        """設定ファイルから読み込み"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, config_data in data.items():
                        self.providers[name] = ProviderConfig(
                            name=name,
                            enabled=config_data.get('enabled', True),
                            priority=config_data.get('priority', 5),
                            config=config_data.get('config', {})
                        )
                print(f"✅ 設定を読み込みました: {self.config_file}")
            except Exception as e:
                print(f"⚠️  設定読み込みエラー: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def save_config(self):
        """設定ファイルに保存"""
        try:
            config_data = {}
            for name, provider in self.providers.items():
                config_data[name] = {
                    'enabled': provider.enabled,
                    'priority': provider.priority,
                    'config': provider.config
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 設定を保存しました: {self.config_file}")
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")
    
    def _create_default_config(self):
        """デフォルト設定の作成"""
        defaults = [
            ProviderConfig("gpt-oss", True, 1, {"model": "gpt-oss:20b"}),
            ProviderConfig("ollama", True, 2, {"model": "llama2", "host": "localhost", "port": 11434}),
            ProviderConfig("openai", False, 3, {"model": "gpt-3.5-turbo", "api_key": ""}),
            ProviderConfig("huggingface", False, 4, {"model": "microsoft/DialoGPT-medium"}),
            ProviderConfig("simple", True, 9, {})  # 最後のフォールバック
        ]
        
        for config in defaults:
            self.providers[config.name] = config
        
        self.save_config()
        print("📋 デフォルト設定を作成しました")
    
    def get_provider_preferences(self) -> List[str]:
        """優先度順のプロバイダーリスト"""
        enabled_providers = [
            (name, config.priority) 
            for name, config in self.providers.items() 
            if config.enabled
        ]
        # 優先度順（数値が小さい方が高優先度）
        enabled_providers.sort(key=lambda x: x[1])
        return [name for name, _ in enabled_providers]
    
    def set_provider_enabled(self, name: str, enabled: bool):
        """プロバイダーの有効/無効設定"""
        if name in self.providers:
            self.providers[name].enabled = enabled
            print(f"✅ {name}: {'有効' if enabled else '無効'}に設定しました")
            self.save_config()
        else:
            print(f"❌ 未知のプロバイダー: {name}")
    
    def set_provider_priority(self, name: str, priority: int):
        """プロバイダーの優先度設定"""
        if name in self.providers:
            self.providers[name].priority = priority
            print(f"✅ {name}: 優先度を{priority}に設定しました")
            self.save_config()
        else:
            print(f"❌ 未知のプロバイダー: {name}")
    
    def set_provider_config(self, name: str, config: Dict[str, Any]):
        """プロバイダー固有設定の更新"""
        if name in self.providers:
            self.providers[name].config.update(config)
            print(f"✅ {name}: 設定を更新しました")
            self.save_config()
        else:
            # 新しいプロバイダーとして追加
            self.providers[name] = ProviderConfig(name, True, 5, config)
            print(f"✅ 新しいプロバイダー {name} を追加しました")
            self.save_config()
    
    def get_provider_config(self, name: str) -> Optional[Dict[str, Any]]:
        """プロバイダー設定の取得"""
        if name in self.providers:
            return self.providers[name].config
        return None
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """全プロバイダー設定の取得"""
        return {
            name: {
                'enabled': config.enabled,
                'priority': config.priority,
                'config': config.config
            }
            for name, config in self.providers.items()
        }
    
    def add_provider(self, name: str, enabled: bool = True, priority: int = 5, config: Dict[str, Any] = None):
        """新しいプロバイダーの追加"""
        self.providers[name] = ProviderConfig(name, enabled, priority, config or {})
        print(f"✅ プロバイダー '{name}' を追加しました")
        self.save_config()
    
    def remove_provider(self, name: str):
        """プロバイダーの削除"""
        if name in self.providers:
            del self.providers[name]
            print(f"❌ プロバイダー '{name}' を削除しました")
            self.save_config()
        else:
            print(f"❌ プロバイダー '{name}' が見つかりません")
    
    def reset_to_defaults(self):
        """設定をデフォルトにリセット"""
        self.providers.clear()
        self._create_default_config()
        print("🔄 設定をデフォルトにリセットしました")
    
    def export_config(self, file_path: str):
        """設定のエクスポート"""
        try:
            import shutil
            shutil.copy2(self.config_file, file_path)
            print(f"📤 設定をエクスポートしました: {file_path}")
        except Exception as e:
            print(f"❌ エクスポートエラー: {e}")
    
    def import_config(self, file_path: str):
        """設定のインポート"""
        try:
            import shutil
            shutil.copy2(file_path, self.config_file)
            self.load_config()
            print(f"📥 設定をインポートしました: {file_path}")
        except Exception as e:
            print(f"❌ インポートエラー: {e}")
    
    def get_config_summary(self) -> str:
        """設定の概要テキスト"""
        summary = ["AIプロバイダー設定一覧:"]
        preferences = self.get_provider_preferences()
        
        for i, name in enumerate(preferences, 1):
            config = self.providers[name]
            status = "🟢" if config.enabled else "🔴"
            summary.append(f"{i}. {status} {name} (優先度: {config.priority})")
        
        return "\n".join(summary)

# グローバル設定マネージャーインスタンス
config_manager = AIProviderConfigManager()
