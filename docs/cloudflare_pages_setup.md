# Cloudflare Pages デプロイメント設定

## 🌐 Cloudflare Pages でのデプロイ手順

### 1. Cloudflare ダッシュボードでの設定

1. **[Cloudflare Dashboard](https://dash.cloudflare.com/)** にログイン
2. **Pages** セクションに移動
3. **Create a project** をクリック
4. **Connect to Git** を選択してGitHubを連携

### 2. プロジェクト設定

#### 基本設定
- **Project name**: `ruri-aituber`
- **Production branch**: `main`
- **Framework preset**: None (Custom)
- **Build command**: `pip install -r requirements.txt`
- **Build output directory**: `.`
- **Root directory**: (空白のまま)

#### 環境変数設定
```bash
# 必須設定
ENVIRONMENT=production
DEBUG=False
BETA_AUTH_REQUIRED=False

# 機能制御
ENABLE_AI_FEATURES=True
ENABLE_OBS_INTEGRATION=False
ENABLE_STREAMING_FEATURES=False

# Streamlit設定
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 3. カスタムドメイン設定（オプション）

Cloudflare Pagesでは以下のドメインオプションがあります：

#### 無料ドメイン
- `ruri-aituber.pages.dev`
- 自動SSL証明書付き

#### カスタムドメイン
- 独自ドメインの設定可能
- Cloudflare DNS経由で管理

### 4. 自動デプロイ設定

#### トリガー条件
- `main` ブランチへのpush
- Pull Requestのマージ

#### ビルドログの確認
- Cloudflareダッシュボードでビルド状況を監視
- エラー時のログ確認が可能

---

## 🔧 Streamlit on Cloudflare Pages の制約

### 制限事項
- **WebSocket制限**: 一部のインタラクティブ機能に制約
- **ファイルアップロード**: サイズ制限あり
- **セッション管理**: 永続化データの制限

### 推奨対応
- 軽量なWebUI機能に特化
- 重い処理は外部API連携で対応
- データ永続化は外部サービス利用

---

## 📊 パフォーマンス最適化

### 1. 起動時間の短縮
```python
# 遅延読み込みの活用
@st.cache_data
def load_heavy_data():
    return expensive_computation()
```

### 2. 静的ファイルの最適化
- 画像ファイルの圧縮
- CSSの最小化
- 不要な依存関係の削除

### 3. キャッシュ戦略
- Streamlitキャッシュの活用
- Cloudflare Edgeキャッシュの利用

---

## 🚀 デプロイ後の確認項目

### 基本動作確認
- [ ] ページの正常な読み込み
- [ ] 認証機能の無効化確認
- [ ] 各ページの動作確認
- [ ] 画像アップロード機能
- [ ] レスポンシブデザインの確認

### パフォーマンス確認
- [ ] 初回読み込み時間
- [ ] ページ遷移の速度
- [ ] モバイル表示の確認

### セキュリティ確認
- [ ] HTTPS通信の確認
- [ ] 環境変数の適切な設定
- [ ] エラーログの機密情報チェック

---

## 🛠️ トラブルシューティング

### よくある問題

#### 1. ビルドエラー
```bash
# requirements.txt の依存関係エラー
Solution: Python 3.11対応の依存関係に更新
```

#### 2. Streamlit起動エラー
```bash
# ポート設定エラー
Solution: 環境変数の確認とポート設定の調整
```

#### 3. 静的ファイル読み込みエラー
```bash
# パス設定エラー
Solution: 相対パスから絶対パスへの変更
```

### サポート情報
- **Cloudflare Pages Docs**: [公式ドキュメント](https://developers.cloudflare.com/pages/)
- **Streamlit Deployment**: [デプロイガイド](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- **Community Support**: GitHub Issues で質問可能