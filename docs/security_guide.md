# セキュリティ強化ガイド

## 🔒 機密情報の完全保護

### ✅ 実装済みセキュリティ対策

#### 1. **ハードコーディング撤廃**
- 全ての認証パスワードとAPIキーをデフォルト空文字に変更
- 環境変数・Streamlit Secrets経由でのみ設定可能

#### 2. **Git除外強化**
- `.gitignore`に機密情報関連パターンを追加:
  ```
  .env*
  .streamlit/secrets.toml
  config/secrets.json
  src/secrets.py
  secrets/
  *.secret
  *.key
  api_keys.txt
  passwords.txt
  credentials.json
  ```

#### 3. **動的設定管理システム**
- `src/secure_config.py`: 暗号化ベースの設定管理
- **機能**:
  - パスワード: bcryptハッシュ化
  - APIキー: Fernet暗号化
  - リアルタイム設定変更UI
  - 設定ファイル暗号化

### 🛡️ セキュリティレベル

#### **レベル1: 基本保護**（現在実装済み）
- ハードコーディング除去
- 環境変数・Secrets利用
- Git除外設定

#### **レベル2: 暗号化保護**（要パッケージインストール）
```bash
pip install cryptography bcrypt
```
- パスワードハッシュ化（bcrypt）
- APIキー暗号化（Fernet）
- 動的設定変更UI

#### **レベル3: 高度な保護**（将来拡張）
- 2FA認証
- ログ監査
- アクセス制御

### 🎯 デプロイメント手順（セキュア版）

#### **Streamlit Cloud**
1. アプリ作成時に `webui/app_unified.py` を指定
2. **Settings → Secrets** で設定:
   ```toml
   # 強力なパスワードに変更してください
   BETA_PASSWORD = "your-strong-beta-password-here"
   DEVELOPER_PASSWORD = "your-strong-dev-password-here"  
   ADMIN_PASSWORD = "your-strong-admin-password-here"
   
   # APIキー（必要な場合のみ）
   OPENAI_API_KEY = "your-openai-api-key-here"
   ```

#### **ローカル開発**
1. `.env`ファイル作成（Gitには含まれません）:
   ```
   BETA_PASSWORD=local-beta-password
   DEVELOPER_PASSWORD=local-dev-password
   ADMIN_PASSWORD=local-admin-password
   OPENAI_API_KEY=your-openai-key
   ```

### 🔧 動的設定変更の使い方

#### **管理者UIアクセス**
1. 統一WebUIにアクセス
2. 管理者パスワードで認証
3. 「システム設定」ページを選択
4. 各種パスワード・APIキーを変更
5. 「設定を保存」で即座に反映

#### **設定変更の影響範囲**
- **即座反映**: 新規ユーザー認証
- **次回反映**: UI表示、機能制限
- **再起動必要**: 一部システム設定

### ⚡ パフォーマンス最適化

#### **軽量デプロイメント**
- cryptography/bcryptは`requirements.txt`でオプション扱い
- パッケージ未インストールでも基本機能は動作
- 暗号化機能のみ無効化（graceful degradation）

#### **ファイルサイズ**
- 設定ファイル: ~2KB（暗号化後）
- 暗号化キー: 32bytes
- ログファイル: 設定により制御

### 🚨 セキュリティ注意事項

#### **DO（すべきこと）**
- 強力なパスワード使用（12文字以上、複合文字）
- 定期的なパスワード変更
- APIキーの定期ローテーション
- アクセスログの監視

#### **DON'T（してはいけないこと）**
- パスワードをコードに直接記述
- 設定ファイルをGitにコミット
- 弱いパスワードの使用
- APIキーの平文保存

---

**🎉 セキュリティ強化完了！**
**機密情報は完全に保護され、管理者が自由に変更可能です。**