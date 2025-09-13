#!/usr/bin/env python3
# プラガブルAIアーキテクチャ動作テスト
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_basic_imports():
    """基本インポートテスト"""
    print("🧪 基本インポートテスト")
    
    try:
        from ai_providers.base_provider import BaseAIProvider, EmotionType, ColorStage
        print("✅ base_provider インポート成功")
    except ImportError as e:
        print(f"❌ base_provider インポートエラー: {e}")
        return False
    
    try:
        from ai_providers.registry import AIProviderRegistry
        print("✅ registry インポート成功")
    except ImportError as e:
        print(f"❌ registry インポートエラー: {e}")
        return False
    
    try:
        from ai_providers.simple_provider import SimpleAIProvider
        print("✅ simple_provider インポート成功")
    except ImportError as e:
        print(f"❌ simple_provider インポートエラー: {e}")
        return False
    
    try:
        from ai_providers.config_manager import AIProviderConfigManager
        print("✅ config_manager インポート成功")
    except ImportError as e:
        print(f"❌ config_manager インポートエラー: {e}")
        return False
    
    return True

def test_registry():
    """レジストリテスト"""
    print("\n🔧 レジストリテスト")
    
    try:
        from ai_providers import registry
        
        # 利用可能プロバイダーの確認
        available = registry.get_available_providers()
        print(f"✅ 利用可能プロバイダー: {available}")
        
        # プロバイダー情報
        info = registry.get_provider_info()
        for name, details in info.items():
            status = "✅" if details['available'] else "❌"
            print(f"{status} {name}: {details['class_name']}")
        
        return True
    except Exception as e:
        print(f"❌ レジストリテストエラー: {e}")
        return False

def test_simple_provider():
    """シンプルプロバイダーテスト"""
    print("\n🤖 シンプルプロバイダーテスト")
    
    try:
        from ai_providers.simple_provider import SimpleAIProvider
        
        provider = SimpleAIProvider()
        
        # 可用性チェック
        if not provider.is_available():
            print("❌ プロバイダーが利用できません")
            return False
        
        print("✅ プロバイダー初期化成功")
        
        # 基本応答テスト
        response = provider.generate_response("こんにちは")
        print(f"✅ 応答生成成功: {response.text[:50]}...")
        
        # 感情分析テスト
        emotions = provider.get_emotion_analysis("とても嬉しいです！")
        print(f"✅ 感情分析: {emotions}")
        
        # ステータス情報
        status = provider.get_status_info()
        print(f"✅ ステータス: {status['provider_name']}")
        
        return True
    except Exception as e:
        print(f"❌ シンプルプロバイダーテストエラー: {e}")
        return False

def test_config_manager():
    """設定マネージャーテスト"""
    print("\n⚙️  設定マネージャーテスト")
    
    try:
        from ai_providers.config_manager import AIProviderConfigManager
        
        config_mgr = AIProviderConfigManager("test_ai_config.json")
        
        # デフォルト設定作成
        config_mgr.reset_to_defaults()
        print("✅ デフォルト設定作成成功")
        
        # 優先度リスト取得
        preferences = config_mgr.get_provider_preferences()
        print(f"✅ プロバイダー優先度: {preferences}")
        
        # 設定変更テスト
        config_mgr.set_provider_priority("simple", 1)
        config_mgr.set_provider_config("simple", {"test_param": "test_value"})
        print("✅ 設定変更成功")
        
        # 概要表示
        summary = config_mgr.get_config_summary()
        print(f"✅ 設定概要:\n{summary}")
        
        return True
    except Exception as e:
        print(f"❌ 設定マネージャーテストエラー: {e}")
        return False

def test_character_ai():
    """キャラクターAIテスト"""
    print("\n🌈 キャラクターAIテスト")
    
    try:
        from character_ai import RuriCharacter
        
        # プラガブル版の初期化
        ruri = RuriCharacter()
        print(f"✅ ルリ初期化成功 (Provider: {ruri.provider_name})")
        
        # 基本応答テスト
        response = ruri.generate_response("はじめまして、ルリさん！")
        print(f"✅ 応答: {response[:100]}...")
        
        # 状態確認
        status = ruri.get_character_status()
        print(f"✅ キャラクター状態: {status['name']} (会話数: {status['conversation_count']})")
        
        # プロバイダー一覧
        providers = ruri.get_available_providers()
        print(f"✅ 利用可能プロバイダー: {providers}")
        
        return True
    except Exception as e:
        print(f"❌ キャラクターAIテストエラー: {e}")
        return False

def test_ollama_provider():
    """Ollamaプロバイダーテスト（オプション）"""
    print("\n🦙 Ollamaプロバイダーテスト")
    
    try:
        from ai_providers.ollama_provider import OllamaAIProvider
        
        provider = OllamaAIProvider()
        
        if provider.is_available():
            print("✅ Ollama接続成功")
            
            # モデル一覧
            models = provider.get_available_models()
            print(f"✅ 利用可能モデル: {models}")
            
            return True
        else:
            print("⚠️  Ollamaサーバーに接続できません")
            return False
    except ImportError:
        print("⚠️  Ollamaライブラリがインストールされていません")
        return False
    except Exception as e:
        print(f"⚠️  Ollamaテストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 プラガブルAIアーキテクチャ動作テスト")
    print("=" * 50)
    
    tests = [
        ("基本インポート", test_basic_imports),
        ("レジストリ", test_registry),
        ("シンプルプロバイダー", test_simple_provider),
        ("設定マネージャー", test_config_manager),
        ("キャラクターAI", test_character_ai),
        ("Ollama（オプション）", test_ollama_provider),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n▶️  {test_name}テスト開始")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}テスト成功")
            else:
                print(f"❌ {test_name}テスト失敗")
        except Exception as e:
            print(f"💥 {test_name}テストで例外発生: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！")
        print("\n💡 次のステップ:")
        print("1. WebUI起動: streamlit run webui/app_pluggable.py")
        print("2. 各種AIライブラリのインストール（オプション）")
        print("3. プロバイダー設定のカスタマイズ")
    else:
        print("⚠️  一部のテストが失敗しました。ログを確認してください。")
    
    print("\n📚 プラガブルアーキテクチャの利点:")
    print("- 任意のAIライブラリを統一インターフェースで利用")
    print("- 実行時の動的な切り替え")
    print("- 設定ファイルによる柔軟な管理")
    print("- フォールバック機能による信頼性")

if __name__ == "__main__":
    main()
