# プラガブルAIアーキテクチャによるキャラクター実装
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# プラガブルAIプロバイダーのインポート
try:
    from ai_providers import registry  # グローバルレジストリを使用
    from ai_providers.base_provider import BaseAIProvider, CharacterResponse, EmotionType, ColorStage
    AI_PROVIDERS_AVAILABLE = True
except ImportError:
    AI_PROVIDERS_AVAILABLE = False
    print("⚠️  ai_providers モジュールが見つかりません。フォールバックモードで動作します。")

class RuriCharacter:
    """ルリ（戯曲『あいのいろ』主人公）のプラガブルAI実装クラス
    
    様々なAIライブラリ（OpenAI, Ollama, GPT-OSS, HuggingFace等）を
    統一インターフェースで利用可能な設計。
    
    原作戯曲の設定を忠実に継承し、感情学習による段階的な色彩変化を実現。
    """
    
    def __init__(self, 
                 ai_provider: str = None, 
                 provider_config: Dict[str, Any] = None,
                 character_profile_path: str = None):
        """
        Args:
            ai_provider: 使用するAIプロバイダー名（None=自動選択）
            provider_config: プロバイダー固有の設定
            character_profile_path: キャラクター設定ファイルのパス
        """
        
        # ステップ1: 基本属性の初期化
        self.name = "ルリ"
        self.conversation_history = []
        self.ai_provider = None
        self.provider_name = "fallback"
        
        # ステップ2: キャラクター設定の読み込み（AIプロバイダーより先）
        self.character_profile = self._load_character_profile(character_profile_path)
        
        # ステップ3: フォールバック応答の設定
        self.fallback_responses = [
            "そうですね...",
            "なるほど、面白いですね！",
            "もう少し詳しく教えていただけますか？",
            "私も同じように感じることがあります。",
            "とても興味深いお話ですね。"
        ]
        
        # ステップ4: AIプロバイダーの初期化（最後）
        if AI_PROVIDERS_AVAILABLE:
            self.registry = registry  # グローバルレジストリを使用
            self._initialize_ai_provider(ai_provider, provider_config)
        else:
            print("⚠️  AI Providersが利用できません。基本応答モードで動作します。")
    
    def _initialize_ai_provider(self, provider_name: str = None, config: Dict[str, Any] = None):
        """AIプロバイダーの安全な初期化"""
        try:
            # 事前条件チェック
            if not hasattr(self, 'registry') or not self.registry:
                print("❌ AI Providerレジストリが利用できません")
                return
            
            if not hasattr(self, 'character_profile'):
                print("❌ キャラクター設定が読み込まれていません")
                return
            
            # プロバイダーの選択と初期化
            if provider_name:
                # 指定されたプロバイダーを使用
                self.ai_provider = self.registry.create_provider(provider_name, config)
                if self.ai_provider:
                    self.provider_name = provider_name
                    print(f"✅ AIプロバイダー '{provider_name}' を初期化しました")
                else:
                    print(f"❌ プロバイダー '{provider_name}' の初期化に失敗しました")
                    self._fallback_to_default_provider()
            else:
                # 最適なプロバイダーを自動選択
                self._auto_select_provider()
            
            # キャラクター設定をプロバイダーに反映（利用可能な場合のみ）
            self._apply_character_context()
                
        except Exception as e:
            print(f"❌ AIプロバイダー初期化エラー: {e}")
            self.ai_provider = None
            self.provider_name = "fallback"
    
    def _auto_select_provider(self):
        """最適なプロバイダーの自動選択"""
        try:
            self.ai_provider = self.registry.get_best_available_provider()
            if self.ai_provider:
                self.provider_name = self.ai_provider.__class__.__name__
                print(f"🤖 自動選択: '{self.provider_name}' を使用します")
            else:
                print("⚠️ 利用可能なAIプロバイダーが見つかりません。フォールバックモードに切り替えます")
                self._fallback_to_default_provider()
        except Exception as e:
            print(f"❌ プロバイダー自動選択エラー: {e}")
            self._fallback_to_default_provider()
    
    def _fallback_to_default_provider(self):
        """デフォルトプロバイダーへのフォールバック"""
        self.ai_provider = None
        self.provider_name = "fallback"
        print("🔄 フォールバック応答モードに切り替えました")
    
    def _apply_character_context(self):
        """キャラクター設定をプロバイダーに適用"""
        if self.ai_provider and hasattr(self.ai_provider, 'set_character_context'):
            try:
                # 詳細設定を含む包括的なコンテキストを作成
                enhanced_context = {
                    "basic_info": {
                        "name": self.character_profile.get("name", "ルリ"),
                        "origin": self.character_profile.get("origin", "戯曲『あいのいろ』"),
                        "personality": self.character_profile.get("personality", "純粋で好奇心旺盛"),
                        "speaking_style": self.character_profile.get("speaking_style", "丁寧で親しみやすい")
                    },
                    "detailed_settings": self.character_profile.get("detailed_settings", ""),
                    "emotion_styles": self.character_profile.get("emotion_speaking_styles", {}),
                    "content_ideas": self.character_profile.get("content_ideas", []),
                    "current_state": {
                        "color_stage": self.character_profile.get("color_stage", "monochrome"),
                        "learned_emotions": self.character_profile.get("learned_emotions", [])
                    }
                }
                
                context_json = json.dumps(enhanced_context, ensure_ascii=False, indent=2)
                self.ai_provider.set_character_context(context_json)
                print("✅ 詳細キャラクター設定をAIプロバイダーに適用しました")
                print(f"📋 設定項目数: {len(enhanced_context)}")
            except Exception as e:
                print(f"⚠️ キャラクター設定の適用に失敗: {e}")
                # フォールバック: 基本設定のみ適用
                try:
                    basic_context = json.dumps(self.character_profile, ensure_ascii=False)
                    self.ai_provider.set_character_context(basic_context)
                    print("🔄 基本設定のみ適用しました")
                except Exception as fallback_error:
                    print(f"❌ 基本設定の適用も失敗: {fallback_error}")
    
    def _load_character_profile(self, profile_path: str = None) -> Dict[str, Any]:
        """新しい2ファイル構成での設定読み込み"""
        
        # 基本設定（JSON）の読み込み
        config_path = os.path.join("assets", "ruri_config.json")
        character_path = os.path.join("assets", "ruri_character.md")
        
        # デフォルト設定
        default_profile = {
            "name": "ルリ",
            "origin": "戯曲『あいのいろ』", 
            "personality": "純粋で好奇心旺盛、感情学習中",
            "speaking_style": "丁寧で親しみやすい",
            "color_stage": "monochrome",
            "learned_emotions": [],
            "background": "感情を学んで色づいていく特殊な体質を持つ"
        }
        
        profile = default_profile.copy()
        
        # 1. プログラム用設定（JSON）の読み込み
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    profile["config"] = config_data
                    profile["emotions"] = config_data.get("emotions", {})
                    profile["response_patterns"] = config_data.get("response_patterns", {})
                    print(f"✅ プログラム用設定を読み込み: {config_path}")
            except Exception as e:
                print(f"⚠️ プログラム用設定読み込みエラー: {e}")
        
        # 2. 自然言語設定（Markdown）の読み込み
        if os.path.exists(character_path):
            try:
                with open(character_path, 'r', encoding='utf-8') as f:
                    character_content = f.read()
                    profile["character_description"] = character_content
                    profile["natural_settings"] = character_content
                    print(f"✅ 自然言語設定を読み込み: {character_path}")
            except Exception as e:
                print(f"⚠️ 自然言語設定読み込みエラー: {e}")
        
        # カスタムパスが指定された場合の処理
        if profile_path and os.path.exists(profile_path):
            try:
                if profile_path.endswith('.json'):
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        custom_config = json.load(f)
                        profile["config"].update(custom_config)
                elif profile_path.endswith('.md'):
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        custom_content = f.read()
                        profile["character_description"] = custom_content
                print(f"✅ カスタム設定を適用: {profile_path}")
            except Exception as e:
                print(f"⚠️ カスタム設定エラー: {e}")
        
        print("✅ 新しい2ファイル構成での設定読み込み完了")
        return profile

    def generate_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """メッセージに対する応答を生成"""
        
        if self.ai_provider:
            try:
                response = self.ai_provider.generate_response(message, context)
                if response and hasattr(response, 'text'):
                    self._update_conversation_history(message, response.text)
                    return response.text
            except Exception as e:
                print(f"⚠️  AI応答生成エラー: {e}")
        
        # フォールバック応答
        return self._generate_fallback_response(message)
    
    async def generate_response_async(self, message: str, context: Dict[str, Any] = None) -> str:
        """非同期応答生成"""
        
        if self.ai_provider and hasattr(self.ai_provider, 'generate_response_async'):
            try:
                response = await self.ai_provider.generate_response_async(message, context)
                if response and hasattr(response, 'text'):
                    self._update_conversation_history(message, response.text)
                    return response.text
            except Exception as e:
                print(f"⚠️  非同期AI応答エラー: {e}")
        
        # フォールバック
        return self._generate_fallback_response(message)
    
    async def generate_stream_response(self, message: str, context: Dict[str, Any] = None):
        """ストリーミング応答生成"""
        
        if self.ai_provider and hasattr(self.ai_provider, 'generate_stream_response'):
            try:
                full_response = ""
                async for chunk in self.ai_provider.generate_stream_response(message, context):
                    full_response += chunk
                    yield chunk
                
                # 履歴更新
                if full_response:
                    self._update_conversation_history(message, full_response)
                return
            except Exception as e:
                print(f"⚠️  ストリーミング応答エラー: {e}")
        
        # フォールバック
        response = self._generate_fallback_response(message)
        for char in response:
            yield char
    
    def _generate_fallback_response(self, message: str) -> str:
        """フォールバック応答生成"""
        import random
        
        # 簡単なキーワード応答
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["こんにちは", "はじめまして", "おはよう"]):
            return f"こんにちは！私は{self.name}です。よろしくお願いします！"
        
        if any(word in message_lower for word in ["色", "カラー"]):
            return "色について、私はまだ学習中です。どんな色について教えていただけますか？"
        
        if any(word in message_lower for word in ["感情", "気持ち"]):
            return "感情って不思議ですね。私も少しずつ理解できるようになってきました。"
        
        # デフォルト応答
        response = random.choice(self.fallback_responses)
        self._update_conversation_history(message, response)
        return response
    
    def _update_conversation_history(self, user_message: str, assistant_response: str):
        """会話履歴の更新"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response
        })
        
        # 履歴制限（最新50件）
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_character_status(self) -> Dict[str, Any]:
        """キャラクターの現在状態を取得"""
        status = {
            "name": self.name,
            "provider": self.provider_name,
            "conversation_count": len(self.conversation_history),
            "profile": self.character_profile
        }
        
        # AIプロバイダーの詳細状態
        if self.ai_provider and hasattr(self.ai_provider, 'get_status_info'):
            try:
                status["ai_status"] = self.ai_provider.get_status_info()
            except Exception:
                pass
        
        return status
    
    def switch_ai_provider(self, provider_name: str, config: Dict[str, Any] = None) -> bool:
        """AIプロバイダーの動的切り替え"""
        if not AI_PROVIDERS_AVAILABLE:
            print("❌ AI Providersが利用できません")
            return False
        
        try:
            new_provider = self.registry.create_provider(provider_name, config, force_new=True)
            if new_provider:
                self.ai_provider = new_provider
                self.provider_name = provider_name
                
                # キャラクター設定を新プロバイダーに反映
                if hasattr(new_provider, 'set_character_context'):
                    context = json.dumps(self.character_profile, ensure_ascii=False)
                    new_provider.set_character_context(context)
                
                print(f"✅ AIプロバイダーを '{provider_name}' に切り替えました")
                return True
            else:
                print(f"❌ プロバイダー '{provider_name}' の初期化に失敗しました")
                return False
        except Exception as e:
            print(f"❌ プロバイダー切り替えエラー: {e}")
            return False
    
    def get_available_providers(self) -> List[str]:
        """利用可能なAIプロバイダー一覧"""
        if AI_PROVIDERS_AVAILABLE and self.registry:
            return self.registry.get_available_providers()
        return ["fallback"]
    
    def test_all_providers(self) -> Dict[str, bool]:
        """全プロバイダーの動作テスト"""
        if AI_PROVIDERS_AVAILABLE and self.registry:
            return self.registry.test_all_providers()
        return {"fallback": True}
    
    # 既存メソッドとの互換性維持
    def generate_stream_response_sync(self, message: str) -> str:
        """同期版ストリーミング応答（互換性用）"""
        return self.generate_response(message)
    
    def analyze_emotion_from_text(self, text: str) -> Dict[str, float]:
        """テキスト感情分析（互換性用）"""
        if self.ai_provider and hasattr(self.ai_provider, 'get_emotion_analysis'):
            return {emotion.value: score for emotion, score in self.ai_provider.get_emotion_analysis(text).items()}
        
        # フォールバック分析
        return {"neutral": 0.5}
    
    def get_color_stage_info(self) -> Dict[str, Any]:
        """色彩段階情報（互換性用）"""
        if self.ai_provider and hasattr(self.ai_provider, 'get_color_info'):
            return self.ai_provider.get_color_info()
        
        return {
            "stage": "monochrome",
            "dominant_emotion": "neutral",
            "dominant_intensity": 0.0
        }
