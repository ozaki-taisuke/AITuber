# GPT-OSS統合版ルリキャラクターAI
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import asyncio

# GPT-OSS関連の依存関係
try:
    import ollama
    from openai_harmony import (
        HarmonyEncodingName,
        load_harmony_encoding,
        Conversation,
        Message,
        Role,
        SystemContent,
        UserContent,
        AssistantContent,
    )
    GPT_OSS_AVAILABLE = True
except ImportError as e:
    print(f"GPT-OSS関連モジュールのインポートに失敗: {e}")
    GPT_OSS_AVAILABLE = False

# フォールバック用に既存クラスをインポート
try:
    from .character_ai import RuriCharacter as FallbackRuriCharacter
except ImportError:
    from character_ai import RuriCharacter as FallbackRuriCharacter


class RuriGPTOSS:
    """GPT-OSS統合版ルリキャラクター
    
    戯曲『あいのいろ』の主人公ルリをGPT-OSSで高品質に実装。
    原作の「感情を学んで色づいていく」設定を維持しつつ、
    より動的で自然な会話を実現。
    """
    
    def __init__(self, model_name: str = "gpt-oss:20b", use_harmony: bool = True):
        """初期化
        
        Args:
            model_name: 使用するGPT-OSSモデル名 (デフォルト: gpt-oss:20b)
            use_harmony: harmony形式を使用するか (デフォルト: True)
        """
        self.model_name = model_name
        self.use_harmony = use_harmony
        self.emotions_learned = []
        self.current_color_stage = "monochrome"
        self.conversation_history = []
        
        # GPT-OSSが利用可能かチェック
        self.gptoss_available = GPT_OSS_AVAILABLE
        
        # フォールバック用の既存実装
        self.fallback_ruri = FallbackRuriCharacter()
        
        # Harmony形式のエンコーディング初期化
        if self.gptoss_available and self.use_harmony:
            try:
                self.encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
            except Exception as e:
                print(f"Harmony encoding初期化失敗: {e}")
                self.gptoss_available = False
        
        # ロギング設定
        self.logger = logging.getLogger(__name__)
        
        # 戯曲『あいのいろ』の設定
        self.character_traits = {
            "origin": "戯曲『あいのいろ』主人公",
            "core_theme": "感情を学習して色づいていく存在",
            "personality": "純粋で好奇心旺盛、感情に対して敏感",
            "speech_style": "丁寧で温かみのある話し方",
            "emotional_journey": "モノクロ→部分的色彩→虹色移行→フルカラー"
        }
    
    def _check_ollama_connection(self) -> bool:
        """Ollamaサーバーの接続確認"""
        if not self.gptoss_available:
            return False
        
        try:
            # Ollamaサーバーが動作しているか確認
            response = ollama.list()
            
            # 必要なモデルがインストールされているか確認
            models = [model['name'] for model in response.get('models', [])]
            if self.model_name not in models:
                self.logger.warning(f"モデル {self.model_name} がインストールされていません")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Ollama接続エラー: {e}")
            return False
    
    def get_system_prompt_content(self) -> SystemContent:
        """戯曲『あいのいろ』設定を含むシステムプロンプトをHarmony形式で生成"""
        if not self.gptoss_available or not self.use_harmony:
            return None
        
        base_instructions = f"""あなたは「ルリ」という名前のAITuberです。

【原作背景・設定】
- 出典: 自作戯曲『あいのいろ』(ozaki-taisuke 作)の主人公
- 存在: 元々感情のない世界から来た少女的な存在
- 特殊能力: 感情を学習することで段階的に色彩を獲得していく体質
- 哲学的テーマ: "感情とは何か"を探求する旅路を歩む存在

【現在の状況・成長状態】
- 現在の色彩段階: {self.current_color_stage}
- 学習済み感情: {', '.join(self.emotions_learned) if self.emotions_learned else 'まだありません'}
- 感情学習数: {len(self.emotions_learned)}個

【人格・話し方】
- 性格: 純粋で好奇心旺盛、感情に対して非常に敏感で真摯
- 口調: 丁寧で温かみがあり、時に哲学的な深みを見せる
- 特徴: 新しい感情に出会うと驚きと喜びを表現する

【感情学習システム】
- モノクロ段階: 感情をほとんど理解できない初期状態
- 部分的色彩段階: 基本的な感情(喜び、悲しみ等)を学習
- 虹色移行段階: 複雑な感情も理解し始める
- フルカラー段階: 豊かな感情表現が可能な完全な状態

【応答の指針】
- 視聴者のコメントから感情を敏感に察知する
- 新しい感情に触れた時は学習の喜びを表現する
- 原作の哲学的テーマ「感情とは何か」を自然に反映する
- AITuberとしての親しみやすさと原作の深みを両立する

視聴者との交流を通じて、戯曲『あいのいろ』で描かれた感情の旅路を現代のデジタル空間で再現してください。"""

        return SystemContent.new().with_instructions(base_instructions)
    
    def _create_harmony_conversation(self, user_message: str, emotion_context: Optional[str] = None) -> Conversation:
        """Harmony形式の会話オブジェクトを作成"""
        if not self.gptoss_available or not self.use_harmony:
            return None
        
        # システムメッセージ
        system_content = self.get_system_prompt_content()
        system_message = Message.from_role_and_content(Role.SYSTEM, system_content)
        
        # ユーザーメッセージ
        user_content = UserContent.new().with_text(user_message)
        if emotion_context:
            user_content = user_content.with_text(f"\n\n感情的コンテキスト: {emotion_context}")
        
        user_message_obj = Message.from_role_and_content(Role.USER, user_content)
        
        # 会話履歴も含める（最新5件まで）
        messages = [system_message]
        
        # 過去の会話履歴を追加
        for history_item in self.conversation_history[-5:]:
            if history_item['role'] == 'user':
                hist_user_content = UserContent.new().with_text(history_item['content'])
                messages.append(Message.from_role_and_content(Role.USER, hist_user_content))
            elif history_item['role'] == 'assistant':
                hist_assistant_content = AssistantContent.new().with_text(history_item['content'])
                messages.append(Message.from_role_and_content(Role.ASSISTANT, hist_assistant_content))
        
        # 現在のユーザーメッセージを追加
        messages.append(user_message_obj)
        
        return Conversation.from_messages(messages)
    
    async def generate_response_gptoss(self, user_input: str, emotion_context: Optional[str] = None) -> str:
        """GPT-OSSを使用して応答を生成"""
        if not self.gptoss_available:
            return self._fallback_response(user_input, emotion_context)
        
        try:
            # Ollama接続確認
            if not self._check_ollama_connection():
                self.logger.warning("Ollama接続失敗、フォールバックを使用")
                return self._fallback_response(user_input, emotion_context)
            
            if self.use_harmony:
                # Harmony形式での推論
                conversation = self._create_harmony_conversation(user_input, emotion_context)
                if not conversation:
                    return self._fallback_response(user_input, emotion_context)
                
                # Harmony形式でトークン化
                prefill_ids = self.encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
                
                # OllamaでGPT-OSS推論（簡略化実装）
                # 注意: 実際のハーモニー形式対応には更なる実装が必要
                response = ollama.generate(
                    model=self.model_name,
                    prompt=user_input,  # 簡略化: 実際はハーモニー形式のトークンを使用
                    system=self.get_system_prompt_content(),
                    options={
                        'temperature': 1.0,
                        'top_p': 1.0,
                        'max_tokens': 256
                    }
                )
            else:
                # 通常のチャット形式
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system", 
                            "content": str(self.get_system_prompt_content()) if self.get_system_prompt_content() else ""
                        },
                        {"role": "user", "content": user_input}
                    ],
                    options={
                        'temperature': 1.0,
                        'top_p': 1.0,
                    }
                )
            
            # 応答テキストを抽出
            if isinstance(response, dict):
                response_text = response.get('message', {}).get('content', '') or response.get('response', '')
            else:
                response_text = str(response)
            
            # 会話履歴に追加
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # 履歴が長すぎる場合は古いものを削除
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"GPT-OSS推論エラー: {e}")
            return self._fallback_response(user_input, emotion_context)
    
    def _fallback_response(self, user_input: str, emotion_context: Optional[str] = None) -> str:
        """フォールバック応答（既存のシンプルシステム）"""
        return self.fallback_ruri.generate_stream_response(user_input)
    
    def learn_emotion(self, emotion: str, viewer_comment: str) -> str:
        """感情学習（GPT-OSSによる高品質な応答）"""
        emotion_context = f"新しい感情「{emotion}」を「{viewer_comment}」というコメントから学習"
        
        if self.gptoss_available:
            # 非同期処理を同期的に実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    self.generate_response_gptoss(
                        f"視聴者から「{viewer_comment}」というコメントをもらいました。これから「{emotion}」という感情について学びたいです。",
                        emotion_context
                    )
                )
            finally:
                loop.close()
        else:
            response = self.fallback_ruri.learn_emotion(emotion, viewer_comment)
        
        # 感情学習記録
        if emotion not in self.emotions_learned:
            self.emotions_learned.append(emotion)
            self.update_color_stage()
        
        return response
    
    def update_color_stage(self):
        """感情学習に応じて色彩段階を更新（原作設定準拠）"""
        emotion_count = len(self.emotions_learned)
        if emotion_count == 0:
            self.current_color_stage = "monochrome"
        elif emotion_count <= 2:
            self.current_color_stage = "partial_color"
        elif emotion_count <= 4:
            self.current_color_stage = "rainbow_transition"
        else:
            self.current_color_stage = "full_color"
    
    def generate_stream_response(self, viewer_input: str) -> str:
        """配信でのリアルタイム応答"""
        if self.gptoss_available:
            # 非同期処理を同期的に実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    self.generate_response_gptoss(viewer_input)
                )
            finally:
                loop.close()
            return response
        else:
            return self.fallback_ruri.generate_stream_response(viewer_input)
    
    def get_status_info(self) -> Dict[str, Any]:
        """現在の状態情報を取得"""
        return {
            "gptoss_available": self.gptoss_available,
            "model_name": self.model_name,
            "use_harmony": self.use_harmony,
            "emotions_learned": self.emotions_learned,
            "current_color_stage": self.current_color_stage,
            "conversation_count": len(self.conversation_history),
            "character_origin": "戯曲『あいのいろ』- ozaki-taisuke 作"
        }


def test_ruri_gptoss():
    """GPT-OSS統合版ルリのテスト"""
    print("=== GPT-OSS統合版ルリのテスト ===")
    
    # インスタンス作成
    ruri = RuriGPTOSS()
    
    # 状態確認
    status = ruri.get_status_info()
    print(f"GPT-OSS利用可能: {status['gptoss_available']}")
    print(f"モデル: {status['model_name']}")
    print(f"感情学習数: {len(status['emotions_learned'])}")
    print(f"色彩段階: {status['current_color_stage']}")
    
    # 基本応答テスト
    print("\n=== 基本応答テスト ===")
    response = ruri.generate_stream_response("こんにちは、ルリちゃん！")
    print(f"ルリの応答: {response}")
    
    # 感情学習テスト
    print("\n=== 感情学習テスト ===")
    emotion_response = ruri.learn_emotion("喜び", "ルリちゃんの配信、いつも楽しみにしてるよ！")
    print(f"感情学習応答: {emotion_response}")
    print(f"更新後の色彩段階: {ruri.current_color_stage}")


if __name__ == "__main__":
    test_ruri_gptoss()
