# Streamlit Cloud デプロイメント手順書

## 🚀 統一WebUI デプロイメント

### 1. GitHub リポジトリ準備

現在のコミット状態を確認し、最新の統一環境をプッシュします。

### 2. Streamlit Cloud 設定

1. **https://share.streamlit.io** にアクセス
2. **New app** をクリック
3. **GitHub repository**: `ozaki-taisuke/pupa-Ruri`
4. **Branch**: `main`
5. **Main file path**: `webui/app_unified.py`
6. **App URL (optional)**: `aiTuber-ruri-unified` (推奨)

### 3. Secrets 設定

Streamlit Cloud のアプリ設定画面で「Secrets」タブを開き、以下を設定:

```toml
# 認証パスワード
BETA_PASSWORD = "ruri2024beta"
DEVELOPER_PASSWORD = "aiTuberDev2024"
ADMIN_PASSWORD = "ruriSuperAdmin2024"

# 機能フラグ
DEFAULT_USER_LEVEL = "PUBLIC"
ENABLE_AI_FEATURES = true
ENABLE_IMAGE_PROCESSING = true
ENABLE_OBS_INTEGRATION = false
ENABLE_STREAMING_FEATURES = false

# 環境設定
APP_ENVIRONMENT = "production"
DEBUG_MODE = false
```

### 4. デプロイメント実行

**Deploy!** ボタンをクリックしてデプロイを開始。

### 5. 予想される結果

- **URL**: `https://aiTuber-ruri-unified.streamlit.app/`
- **認証レベル**:
  - 🌐 PUBLIC: 基本機能のみ（認証なし）
  - 🧪 BETA: `ruri2024beta` でAI機能解放
  - 👨‍💻 DEVELOPER: `aiTuberDev2024` で全機能
  - 👑 ADMIN: `ruriSuperAdmin2024` で管理機能

### 6. 代替デプロイメント候補

もしStreamlit Cloudでエラーが発生した場合:

1. **Railway** (`railway.app`)
2. **Render** (`render.com`)
3. **Heroku** (有料)
4. **AWS App Runner** (本格運用)

---

### 統合環境の利点

✅ **3環境統合**: β版・Web版・本番環境が1つに
✅ **段階的認証**: レベルに応じた機能解放
✅ **運用コスト削減**: 単一デプロイメント
✅ **メンテナンス効率**: 一元管理
✅ **セキュリティ**: パスワードベース制御