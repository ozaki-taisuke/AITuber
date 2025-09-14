# 統一認証システム
import streamlit as st
import hashlib
from src.unified_config import UnifiedConfig, UserLevel

class UnifiedAuth:
    """統一認証システム"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """パスワードのハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def check_password(entered_password: str, correct_password: str) -> bool:
        """パスワード照合"""
        entered_hash = UnifiedAuth.hash_password(entered_password)
        correct_hash = UnifiedAuth.hash_password(correct_password)
        return entered_hash == correct_hash
    
    @staticmethod
    def authenticate_user(password: str) -> UserLevel:
        """パスワードによるユーザーレベル判定（シンプル認証）"""
        try:
            # セキュア設定管理システムから認証を試行
            from src.secure_config import get_config_manager
            config_manager = get_config_manager()
            
            # 所有者パスワードをチェック
            owner_pass = config_manager.get_raw_password('OWNER_PASSWORD')
            if owner_pass and config_manager.verify_password(password, owner_pass):
                return UserLevel.OWNER
        except Exception:
            # セキュア設定が利用できない場合はフォールバック
            pass
        
        # フォールバック: 従来の設定ファイル認証
        if UnifiedAuth.check_password(password, UnifiedConfig.OWNER_PASSWORD):
            return UserLevel.OWNER
        else:
            return None
    
    @staticmethod
    def show_auth_interface():
        """認証インターフェースの表示"""
        current_level = UnifiedConfig.get_user_level(st.session_state)
        
        # サイドバーに認証状態とアップグレードオプションを表示
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🔐 アクセスレベル")
            
            # 現在のレベル表示
            level_info = {
                UserLevel.PUBLIC: {"color": "🌐", "name": "一般公開"},
                UserLevel.OWNER: {"color": "👑", "name": "所有者"},
            }
            
            current_info = level_info[current_level]
            st.write(f"{current_info['color']} **{current_info['name']}**")
            
            # アップグレードオプション
            if current_level != UserLevel.OWNER:
                st.markdown("#### 🆙 所有者認証")
                
                upgrade_password = st.text_input(
                    "所有者パスワード", 
                    type="password", 
                    key="upgrade_password",
                    placeholder="所有者パスワードを入力"
                )
                
                if st.button("🚀 認証"):
                    if upgrade_password:
                        new_level = UnifiedAuth.authenticate_user(upgrade_password)
                        if new_level and new_level == UserLevel.OWNER:
                            # セッション状態を更新
                            UnifiedAuth.set_authentication_level(new_level)
                            st.success(f"✅ {level_info[new_level]['name']}にアップグレードしました！")
                            st.success("✅ 認証成功！所有者モードに切り替えました")
                            st.rerun()
                        else:
                            st.error("❌ パスワードが正しくありません")
                    else:
                        st.warning("⚠️ パスワードを入力してください")
            else:
                # ログアウトオプション
                if st.button("🚪 ログアウト"):
                    UnifiedAuth.logout()
                    st.success("✅ ログアウトしました")
                    st.rerun()
    
    @staticmethod
    def set_authentication_level(level: UserLevel):
        """認証レベルの設定"""
        # すべての認証状態をリセット
        st.session_state["owner_authenticated"] = False
        
        # 所有者レベルの設定
        if level == UserLevel.OWNER:
            st.session_state["owner_authenticated"] = True
    
    @staticmethod
    def logout():
        """すべての認証状態をクリア"""
        for key in ["owner_authenticated"]:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def require_level(required_level: UserLevel, show_error=True) -> bool:
        """指定されたレベル以上の認証を要求"""
        current_level = UnifiedConfig.get_user_level(st.session_state)
        
        if current_level == required_level or current_level == UserLevel.OWNER:
            return True
        
        if show_error:
            if required_level == UserLevel.OWNER:
                st.error("🔒 この機能は所有者のみアクセス可能です")
                st.info("サイドバーの認証セクションから所有者パスワードを入力してください")
        
        return False