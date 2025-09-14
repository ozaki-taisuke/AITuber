# 🚀 APIキー設定 - クイックスタート

## ⚡ 1分で設定：ローカル開発

### ステップ1: .envファイル作成
プロジェクトルート（`d:\dev\pupa-Ruri\`）に`.env`ファイルを作成：

```bash
# .env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### ステップ2: 起動
```powershell
cd "d:\dev\pupa-Ruri"
python -m streamlit run app.py
```

### ステップ3: 確認
ブラウザで http://localhost:8501 にアクセス

---

## 🌐 リモートサーバー設定

### Streamlit Cloud
1. アプリ設定 → **Secrets** 
2. 以下を追加：
```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

### その他（Heroku、Railway等）
環境変数に設定：
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

---

## 🔍 トラブルシューティング

### 「利用可能なAIプロバイダーがありません」エラー
```powershell
# 設定確認
cd "d:\dev\pupa-Ruri"
python -c "
import sys
sys.path.insert(0, 'src')
from api_config import APIConfig
print('設定状況:', '✅ OK' if APIConfig.get_openai_api_key() else '❌ 設定が必要')
"
```

### APIキーが認識されない
1. `.env`ファイルがプロジェクトルートにあるか確認
2. APIキーが`sk-`で始まっているか確認
3. ファイル保存後、アプリを再起動

---

## 📁 ファイル配置

```
d:\dev\pupa-Ruri\          # ← ここに.envファイル作成
├── .env                   # ← APIキー設定ファイル
├── app.py                 # メインアプリ
├── src/
│   └── api_config.py      # 設定管理
└── docs/
    └── api_setup_guide.md # 詳細手順
```

---

**重要**: `.env`ファイルはGitで管理されないため、APIキーが外部に漏れる心配はありません。