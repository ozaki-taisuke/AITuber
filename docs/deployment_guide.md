# ベータ版デプロイメントガイド

## 🚀 推奨デプロイメント方法

### 1. Railway（推奨）
**無料枠**: 月500時間 + $5クレジット  
**特徴**: GitHub連携、自動デプロイ、環境変数管理

#### デプロイ手順
1. [Railway](https://railway.app)にGitHubアカウントでログイン
2. "New Project" → "Deploy from GitHub repo"
3. このリポジトリを選択
4. 環境変数を設定：
   ```
   ENVIRONMENT=production
   DEBUG=False
   BETA_PASSWORD=your-secure-password
   ENABLE_AI_FEATURES=True
   ENABLE_OBS_INTEGRATION=False
   ```
5. `railway.toml` の設定が自動適用される

#### カスタムドメイン設定
- 無料でランダムドメイン提供
- カスタムドメインは有料プラン

---

### 2. Render
**無料枠**: 月750時間（スリープ有り）  
**特徴**: 簡単設定、SSL自動、CDN内蔵

#### デプロイ手順
1. [Render](https://render.com)にGitHubアカウントでログイン
2. "New Web Service" → GitHubリポジトリを接続
3. 設定：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run webui/app_beta.py --server.port=$PORT --server.address=0.0.0.0`
4. 環境変数を設定

---

### 3. Heroku
**料金**: 最低$5/月（無料枠終了）  
**特徴**: 老舗、豊富な機能、アドオン充実

#### デプロイ手順
1. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)をインストール
2. ログイン: `heroku login`
3. アプリ作成: `heroku create ruri-aituber-beta`
4. 環境変数設定:
   ```bash
   heroku config:set ENVIRONMENT=production
   heroku config:set DEBUG=False
   heroku config:set BETA_PASSWORD=your-password
   ```
5. デプロイ: `git push heroku main`

---

### 4. Streamlit Cloud（プライベートリポジトリの場合）
**料金**: 無料（コミュニティ版）  
**制限**: プライベートリポジトリは有料

#### デプロイ手順
1. [Streamlit Cloud](https://streamlit.io/cloud)にログイン
2. "New app" → GitHubリポジトリを選択
3. `webui/app_beta.py` を指定
4. Secrets（環境変数）を設定

---

## 🔧 本番環境での設定

### 必須環境変数
```bash
ENVIRONMENT=production
DEBUG=False
BETA_PASSWORD=your-secure-password-here
```

### オプション環境変数
```bash
# AI機能（推奨：有効）
ENABLE_AI_FEATURES=True
OPENAI_API_KEY=your-api-key  # オプション

# 無効化推奨（ベータ版では未対応）
ENABLE_OBS_INTEGRATION=False
ENABLE_STREAMING_FEATURES=False
```

---

## 🔒 セキュリティ考慮事項

### 1. パスワード管理
- ベータ版パスワードは定期的に変更
- 複雑なパスワードを使用（英数字+記号）
- テスト期間終了後は必ず変更

### 2. アクセス制御
- 信頼できるベータテスターのみに共有
- パスワードは個別連絡で通知
- 不正アクセスの監視

### 3. データ保護
- ベータ版では永続化データなし
- セッション情報は自動削除
- ログには機密情報を含めない

---

## 📊 監視・メンテナンス

### 1. ヘルスチェック
- アプリケーションの定期的な動作確認
- エラーログの監視
- パフォーマンスの測定

### 2. フィードバック収集
- ユーザーからのバグ報告
- 機能要望の記録
- 使用統計の分析

### 3. 更新・修正
- 重要なバグ修正は即座にデプロイ
- 機能追加は慎重に検討
- ダウンタイムの最小化

---

## 🎯 ベータテスト期間の目標

### 短期目標（1-2週間）
- 基本機能の動作確認
- 明らかなバグの発見・修正
- UI/UXの改善点収集

### 中期目標（1ヶ月）
- ユーザーフィードバックの分析
- 優先機能の特定
- 本格版への機能追加計画

### 長期目標（2-3ヶ月）
- 安定した本格版のリリース
- コミュニティの形成
- 商用化の検討