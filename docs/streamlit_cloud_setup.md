# Streamlit Cloud デプロイ設定

## 🚀 推奨: Streamlit Cloud でのデプロイ

Cloudflare PagesはPythonアプリケーションの直接実行に制限があるため、
Streamlit Cloudでの無料デプロイを強く推奨します。

### 1. Streamlit Cloud でのデプロイ手順

1. **[Streamlit Cloud](https://share.streamlit.io/)** にアクセス
2. **GitHub アカウント**でログイン
3. **New app** をクリック
4. リポジトリ選択: `ozaki-taisuke/pupa-Ruri`
5. メインファイル: `webui/app_beta.py`
6. **Deploy!** をクリック

### 2. 環境変数設定 (Secrets)

Streamlit Cloud の Secrets 設定で以下を追加：

```toml
# .streamlit/secrets.toml

[environment]
ENVIRONMENT = "production"
DEBUG = false
BETA_AUTH_REQUIRED = false

[features]
ENABLE_AI_FEATURES = true
ENABLE_OBS_INTEGRATION = false
ENABLE_STREAMING_FEATURES = false

[ai]
# OpenAI API Key (オプション)
OPENAI_API_KEY = "your-api-key-here"
```

### 3. 自動URL

デプロイ後、以下のような URL で自動公開されます：
```
https://share.streamlit.io/ozaki-taisuke/pupa-ruri/main/webui/app_beta.py
```

### 4. カスタムドメイン（有料プラン）

Streamlit Cloud Pro では独自ドメインの設定も可能です。

---

## 🔄 Railway でのデプロイ（代替案）

### メリット
- Python アプリケーションのネイティブサポート
- 無料枠が充実
- GitHubとの自動連携

### デプロイ手順
1. **[Railway](https://railway.app)** にアクセス
2. GitHub でログイン
3. **New Project** → **Deploy from GitHub repo**
4. `pupa-Ruri` を選択
5. 環境変数を設定
6. 自動デプロイ開始

### 環境変数設定
```bash
ENVIRONMENT=production
DEBUG=False
BETA_AUTH_REQUIRED=False
ENABLE_AI_FEATURES=True
PORT=8501
```

---

## ⚡ Render でのデプロイ（代替案）

### 特徴
- 無料SSL証明書
- 自動スケーリング
- 簡単なGitHub連携

### 設定
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run webui/app_beta.py --server.port=$PORT --server.address=0.0.0.0`
- **Environment**: Python 3.11

---

## 💰 料金比較

| サービス | 無料枠 | 特徴 |
|---------|--------|------|
| **Streamlit Cloud** | 無制限* | Streamlit専用、最も簡単 |
| **Railway** | 月500時間 + $5 | 高性能、多言語対応 |
| **Render** | 月750時間 | SSL無料、CDN内蔵 |
| **Heroku** | なし（最低$5/月） | 老舗、豊富な機能 |

*Streamlit Cloudの無料版は公開リポジトリのみ対応

---

## 🎯 推奨フロー

1. **開発・テスト**: ローカル環境
2. **ベータ公開**: Streamlit Cloud
3. **本格運用**: Railway または Render
4. **静的コンテンツ**: Cloudflare Pages（ランディングページ等）