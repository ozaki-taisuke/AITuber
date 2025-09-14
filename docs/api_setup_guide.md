# API設定手順ガイド

## 🔧 ローカル開発環境での設定

### 方法1: .envファイル（推奨）

1. プロジェクトルートに`.env`ファイルを作成：
```bash
# .env ファイル（ローカル開発用）
OPENAI_API_KEY=sk-your-actual-api-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
OLLAMA_BASE_URL=http://localhost:11434

# その他のプロバイダー（オプション）
HUGGINGFACE_API_TOKEN=your-huggingface-token
COHERE_API_KEY=your-cohere-key
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

2. WebUIを起動：
```powershell
cd "d:\dev\pupa-Ruri"
python -m streamlit run app.py
```

### 方法2: 環境変数（一時的）

PowerShellで設定：
```powershell
# 一時的な設定
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
python -m streamlit run app.py
```

### 動作確認

```powershell
cd "d:\dev\pupa-Ruri"
python -c "
import sys
sys.path.insert(0, 'src')
from api_config import APIConfig
print('🔧 API設定確認')
print('OpenAI:', '✅ 設定済み' if APIConfig.get_openai_api_key() else '❌ 未設定')
print('利用可能:', APIConfig.get_available_providers())
"
```

## 🌐 リモートサーバーでの設定

### Streamlit Cloud

1. **Streamlit Cloudのダッシュボード**で設定
2. **App settings > Secrets**に以下を追加：
```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
ANTHROPIC_API_KEY = "your-anthropic-key-here"
GOOGLE_API_KEY = "your-google-key-here"
```

3. **または Environment variables**に設定：
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### その他のクラウドサービス

#### Heroku
```bash
heroku config:set OPENAI_API_KEY=sk-your-actual-api-key-here
heroku config:set ANTHROPIC_API_KEY=your-anthropic-key-here
```

#### Railway
```bash
railway variables set OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### Vercel
```bash
vercel env add OPENAI_API_KEY
# プロンプトに従ってキーを入力
```

#### Docker
```yaml
# docker-compose.yml
version: '3'
services:
  ruri-app:
    build: .
    environment:
      - OPENAI_API_KEY=sk-your-actual-api-key-here
      - ANTHROPIC_API_KEY=your-anthropic-key-here
    ports:
      - "8501:8501"
```

または実行時：
```bash
docker run -e OPENAI_API_KEY=sk-your-key-here -p 8501:8501 ruri-app
```

## 📁 ファイル構成とセキュリティ

### ✅ 実際の設定ファイル（Git除外済み）
```
project/
├── .env                 # ローカル開発用
├── .streamlit/
│   └── secrets.toml     # Streamlit用
```

### 📝 設定例ファイル（リポジトリ内）
```
project/
├── .env.example         # 設定例
├── .env.template        # テンプレート
├── docs/
│   └── api_setup_guide.md  # この手順書
```

## 🔍 設定読み込み優先順位

1. **環境変数** (最優先)
2. **`.env`ファイル**
3. **Streamlit secrets**
4. **デフォルト値**

## 🚨 セキュリティ注意点

### ✅ 安全な方法
- `.env`ファイル使用（Git除外済み）
- 環境変数設定
- クラウドサービスのSecrets管理

### ❌ 危険な方法
- ソースコードに直接記述
- 公開リポジトリにAPIキー含む
- `.env`をGitにコミット

## 🔧 トラブルシューティング

### APIキーが認識されない場合

1. **設定確認**：
```python
import os
print("環境変数:", os.getenv('OPENAI_API_KEY', '未設定'))
```

2. **ファイル確認**：
```bash
# .envファイルの存在確認
ls -la .env

# 内容確認（Windows）
type .env
```

3. **APIConfig確認**：
```python
from src.api_config import APIConfig
print("APIConfig:", APIConfig.get_openai_api_key())
```

### よくあるエラー

- **ImportError**: `pip install python-dotenv`
- **API key not found**: `.env`ファイルの場所を確認
- **Permission denied**: ファイルの権限を確認

## 📞 サポート

設定で困った場合は、以下を確認してください：
1. APIキーの形式（`sk-`で始まる）
2. ファイルの場所（プロジェクトルート）
3. 環境変数の設定
4. クラウドサービスのSecrets設定

---

📁 **プロジェクト**: AITuber ルリ  
🔧 **最終更新**: 2025年9月14日