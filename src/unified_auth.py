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
        """パスワードによるユーザーレベル判定（セキュア設定対応）"""
        try:
            # セキュア設定管理システムから認証を試行
            from src.secure_config import get_config_manager
            config_manager = get_config_manager()
            
            # 各レベルのパスワードをチェック
            admin_pass = config_manager.get_raw_password('ADMIN_PASSWORD')
            if admin_pass and config_manager.verify_password(password, admin_pass):
                return UserLevel.ADMIN
                
            dev_pass = config_manager.get_raw_password('DEVELOPER_PASSWORD')
            if dev_pass and config_manager.verify_password(password, dev_pass):
                return UserLevel.DEVELOPER
                
            beta_pass = config_manager.get_raw_password('BETA_PASSWORD')
            if beta_pass and config_manager.verify_password(password, beta_pass):
                return UserLevel.BETA
        except Exception:
            # セキュア設定が利用できない場合はフォールバック
            pass
        
        # フォールバック: 従来の設定ファイル認証
        if UnifiedAuth.check_password(password, UnifiedConfig.ADMIN_PASSWORD):
            return UserLevel.ADMIN
        elif UnifiedAuth.check_password(password, UnifiedConfig.DEVELOPER_PASSWORD):
            return UserLevel.DEVELOPER
        elif UnifiedAuth.check_password(password, UnifiedConfig.BETA_PASSWORD):
            return UserLevel.BETA
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
                UserLevel.BETA: {"color": "🧪", "name": "ベータテスター"},
                UserLevel.DEVELOPER: {"color": "👨‍💻", "name": "開発者"},
                UserLevel.ADMIN: {"color": "👑", "name": "管理者"},
            }
            
            current_info = level_info[current_level]
            st.write(f"{current_info['color']} **{current_info['name']}**")
            
            # アップグレードオプション
            if current_level != UserLevel.ADMIN:
                st.markdown("#### 🆙 アクセスレベル向上")
                
                upgrade_password = st.text_input(
                    "認証パスワード", 
                    type="password", 
                    key="upgrade_password",
                    placeholder="上位レベルのパスワードを入力"
                )
                
                if st.button("🚀 レベルアップ", use_container_width=True):
                    if upgrade_password:
                        new_level = UnifiedAuth.authenticate_user(upgrade_password)
                        if new_level and new_level.value != current_level.value:
                            # セッション状態を更新
                            UnifiedAuth.set_authentication_level(new_level)
                            st.success(f"✅ {level_info[new_level]['name']}にアップグレードしました！")
                            st.rerun()
                        else:
                            st.error("❌ 無効なパスワードです")
            
            # ダウングレード（ログアウト）オプション
            if current_level != UserLevel.PUBLIC:
                if st.button("📤 ログアウト", use_container_width=True):
                    UnifiedAuth.logout()
                    st.success("✅ ログアウトしました")
                    st.rerun()
    
    @staticmethod
    def set_authentication_level(level: UserLevel):
        """認証レベルの設定"""
        # すべての認証状態をリセット
        st.session_state["admin_authenticated"] = False
        st.session_state["developer_authenticated"] = False
        st.session_state["beta_authenticated"] = False
        
        # 指定されたレベルに応じて認証状態を設定
        if level == UserLevel.ADMIN:
            st.session_state["admin_authenticated"] = True
            st.session_state["developer_authenticated"] = True
            st.session_state["beta_authenticated"] = True
        elif level == UserLevel.DEVELOPER:
            st.session_state["developer_authenticated"] = True
            st.session_state["beta_authenticated"] = True
        elif level == UserLevel.BETA:
            st.session_state["beta_authenticated"] = True
    
    @staticmethod
    def logout():
        """すべての認証状態をクリア"""
        for key in ["admin_authenticated", "developer_authenticated", "beta_authenticated"]:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def require_level(required_level: UserLevel, show_error=True) -> bool:
        """指定されたレベル以上の認証を要求"""
        current_level = UnifiedConfig.get_user_level(st.session_state)
        
        # レベルの数値比較（PUBLIC=0, BETA=1, DEVELOPER=2, ADMIN=3）
        level_values = {
            UserLevel.PUBLIC: 0,
            UserLevel.BETA: 1,
            UserLevel.DEVELOPER: 2,
            UserLevel.ADMIN: 3
        }
        
        if level_values[current_level] >= level_values[required_level]:
            return True
        
        if show_error:
            level_names = {
                UserLevel.BETA: "ベータテスター",
                UserLevel.DEVELOPER: "開発者",
                UserLevel.ADMIN: "管理者"
            }
            st.error(f"🔒 この機能は{level_names[required_level]}以上のアクセスが必要です")
            st.info("サイドバーの認証セクションからレベルアップしてください")
        
        return False