# 動的設定管理システム
import streamlit as st
import hashlib
import json
import os
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import bcrypt
from src.unified_config import UnifiedConfig, UserLevel

class SecureConfigManager:
    """セキュアな設定管理システム"""
    
    def __init__(self):
        self.config_file = "config/secure_settings.json"
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """暗号化キーの取得または生成"""
        key_file = "config/encryption.key"
        
        # 設定ディレクトリの作成
        os.makedirs("config", exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # 新しいキーを生成
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data: str) -> str:
        """データの暗号化"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """データの復号化"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str) -> str:
        """パスワードのハッシュ化（bcrypt使用）"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """パスワードの検証"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def save_secure_config(self, config_data: Dict[str, Any]) -> bool:
        """セキュアな設定の保存"""
        try:
            # パスワードをハッシュ化
            if 'passwords' in config_data:
                for level, password in config_data['passwords'].items():
                    if password:  # 空でない場合のみハッシュ化
                        config_data['passwords'][level] = self.hash_password(password)
            
            # API キーを暗号化
            if 'api_keys' in config_data:
                for key, value in config_data['api_keys'].items():
                    if value:  # 空でない場合のみ暗号化
                        config_data['api_keys'][key] = self.encrypt_data(value)
            
            # 設定ファイルに保存
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            st.error(f"設定保存エラー: {e}")
            return False
    
    def load_secure_config(self) -> Dict[str, Any]:
        """セキュアな設定の読み込み"""
        if not os.path.exists(self.config_file):
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # API キーを復号化（表示用には部分的にマスク）
            if 'api_keys' in config:
                for key, value in config['api_keys'].items():
                    if value:
                        try:
                            # 復号化してマスク表示用に変換
                            decrypted = self.decrypt_data(value)
                            config['api_keys'][key] = self._mask_api_key(decrypted)
                        except:
                            config['api_keys'][key] = "***復号エラー***"
            
            return config
        except Exception as e:
            st.error(f"設定読み込みエラー: {e}")
            return self._get_default_config()
    
    def _mask_api_key(self, api_key: str) -> str:
        """APIキーのマスク表示"""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定の取得"""
        return {
            "passwords": {
                "OWNER_PASSWORD": ""
            },
            "api_keys": {
                "OPENAI_API_KEY": "",
                "YOUTUBE_API_KEY": "",
                "TWITCH_CLIENT_SECRET": ""
            },
            "features": {
                "ENABLE_AI_FEATURES": True,
                "ENABLE_IMAGE_PROCESSING": True,
                "ENABLE_OBS_INTEGRATION": False,
                "ENABLE_STREAMING_FEATURES": False
            },
            "app_settings": {
                "DEFAULT_USER_LEVEL": "PUBLIC",
                "DEBUG_MODE": False,
                "SHOW_TECHNICAL_DETAILS": False
            }
        }
    
    def get_raw_password(self, level: str) -> str:
        """生パスワードの取得（認証用）"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('passwords', {}).get(level, '')
            return ''
        except:
            return ''
    
    def get_raw_api_key(self, key_name: str) -> str:
        """生APIキーの取得（実際の利用用）"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                encrypted_key = config.get('api_keys', {}).get(key_name, '')
                if encrypted_key:
                    return self.decrypt_data(encrypted_key)
            return ''
        except:
            return ''

def show_admin_settings_ui():
    """管理者用設定変更UI"""
    st.title("🔧 システム設定管理")
    st.markdown("---")
    
    # セキュリティ警告
    st.warning("⚠️ **管理者専用**: この画面では機密情報を変更できます。設定後は即座にシステム全体に反映されます。")
    
    config_manager = SecureConfigManager()
    current_config = config_manager.load_secure_config()
    
    # タブ分割
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 認証設定", "🔑 API設定", "⚙️ 機能設定", "📊 システム情報"])
    
    with tab1:
        st.header("所有者パスワード設定")
        st.info("💡 パスワードは暗号化されて保存されます。空欄の場合、所有者認証は無効になります。")
        
        col1, col2 = st.columns(2)
        
        with col1:
            owner_password = st.text_input(
                "� 所有者パスワード",
                type="password",
                help="全機能へのアクセス用パスワード",
                key="new_owner_password"
            )
        
        with col2:
            st.markdown("**現在の設定状況:**")
            passwords = current_config.get('passwords', {})
            owner_pass = passwords.get('OWNER_PASSWORD', '')
            status = "✅ 設定済み" if owner_pass else "❌ 未設定"
            st.write(f"- 所有者パスワード: {status}")
            
            if owner_pass:
                st.success("🔒 所有者認証が有効です")
            else:
                st.warning("⚠️ 所有者パスワードが未設定です")
    
    with tab2:
        st.header("API キー設定")
        st.info("💡 APIキーは暗号化されて保存されます。表示は一部マスクされます。")
        
        col1, col2 = st.columns(2)
        
        with col1:
            openai_api_key = st.text_input(
                "🤖 OpenAI API キー",
                type="password",
                help="AI機能で使用するOpenAI APIキー",
                key="new_openai_key"
            )
            
            youtube_api_key = st.text_input(
                "📺 YouTube API キー",
                type="password",
                help="YouTube連携で使用するAPIキー",
                key="new_youtube_key"
            )
            
            twitch_secret = st.text_input(
                "🎮 Twitch Client Secret",
                type="password",
                help="Twitch連携で使用するクライアントシークレット",
                key="new_twitch_secret"
            )
        
        with col2:
            st.markdown("**現在の設定状況:**")
            api_keys = current_config.get('api_keys', {})
            for key_name, masked_key in api_keys.items():
                status = "✅ 設定済み" if masked_key else "❌ 未設定"
                display_key = masked_key if masked_key else "未設定"
                st.write(f"- {key_name}: {status}")
                if masked_key:
                    st.code(display_key)
    
    with tab3:
        st.header("機能フラグ設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            features = current_config.get('features', {})
            
            enable_ai = st.checkbox(
                "🤖 AI機能を有効化",
                value=features.get('ENABLE_AI_FEATURES', True),
                help="OpenAI APIを使用したAI機能"
            )
            
            enable_image = st.checkbox(
                "🎨 画像処理機能を有効化",
                value=features.get('ENABLE_IMAGE_PROCESSING', True),
                help="OpenCVを使用した画像分析機能"
            )
        
        with col2:
            enable_obs = st.checkbox(
                "🎥 OBS連携機能を有効化",
                value=features.get('ENABLE_OBS_INTEGRATION', False),
                help="OBS Studio連携機能（高負荷）"
            )
            
            enable_streaming = st.checkbox(
                "📺 配信機能を有効化",
                value=features.get('ENABLE_STREAMING_FEATURES', False),
                help="YouTube/Twitch配信機能"
            )
        
        st.markdown("### アプリケーション設定")
        app_settings = current_config.get('app_settings', {})
        
        default_level = st.selectbox(
            "デフォルトユーザーレベル",
            options=["PUBLIC", "BETA", "DEVELOPER", "ADMIN"],
            index=["PUBLIC", "BETA", "DEVELOPER", "ADMIN"].index(
                app_settings.get('DEFAULT_USER_LEVEL', 'PUBLIC')
            ),
            help="認証なしでアクセスした場合のデフォルトレベル"
        )
        
        debug_mode = st.checkbox(
            "🐛 デバッグモード",
            value=app_settings.get('DEBUG_MODE', False),
            help="詳細なエラー情報を表示"
        )
    
    with tab4:
        st.header("システム情報")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("設定ファイル", "secure_settings.json")
            st.metric("暗号化", "✅ 有効")
            st.metric("設定ファイルサイズ", f"{os.path.getsize(config_manager.config_file) if os.path.exists(config_manager.config_file) else 0} bytes")
        
        with col2:
            if st.button("🔄 設定をリロード"):
                st.rerun()
            
            if st.button("⚠️ 設定を初期化", type="secondary"):
                if st.checkbox("本当に初期化しますか？"):
                    config_manager.save_secure_config(config_manager._get_default_config())
                    st.success("設定を初期化しました")
                    st.rerun()
    
    # 設定保存ボタン
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("💾 設定を保存", type="primary"):
            # 新しい設定を構築
            new_config = {
                "passwords": {
                    "OWNER_PASSWORD": owner_password if owner_password else current_config.get('passwords', {}).get('OWNER_PASSWORD', '')
                },
                "api_keys": {
                    "OPENAI_API_KEY": openai_api_key if openai_api_key else config_manager.get_raw_api_key('OPENAI_API_KEY'),
                    "YOUTUBE_API_KEY": youtube_api_key if youtube_api_key else config_manager.get_raw_api_key('YOUTUBE_API_KEY'),
                    "TWITCH_CLIENT_SECRET": twitch_secret if twitch_secret else config_manager.get_raw_api_key('TWITCH_CLIENT_SECRET')
                },
                "features": {
                    "ENABLE_AI_FEATURES": enable_ai,
                    "ENABLE_IMAGE_PROCESSING": enable_image,
                    "ENABLE_OBS_INTEGRATION": enable_obs,
                    "ENABLE_STREAMING_FEATURES": enable_streaming
                },
                "app_settings": {
                    "DEFAULT_USER_LEVEL": default_level,
                    "DEBUG_MODE": debug_mode,
                    "SHOW_TECHNICAL_DETAILS": debug_mode
                }
            }
            
            if config_manager.save_secure_config(new_config):
                st.success("✅ 設定が正常に保存されました")
                st.info("💡 変更は次回ページ更新時に反映されます")
                
                # セッション状態をクリア（設定変更の反映用）
                for key in list(st.session_state.keys()):
                    if key.startswith('new_'):
                        del st.session_state[key]
            else:
                st.error("❌ 設定の保存に失敗しました")

# グローバル設定管理インスタンス
_config_manager = None

def get_config_manager() -> SecureConfigManager:
    """設定管理インスタンスを取得"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager