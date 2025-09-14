# OpenAI API 設定ガイド

## 概要
ルリちゃんでOpenAI APIを使用するための設定手順です。

## 1. OpenAI APIキーの取得
1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. アカウント作成/ログイン
3. API Keys ページでAPIキーを生成
4. 生成されたキーをコピー（sk-で始まる文字列）

## 2. 設定方法

### 方法A: 環境変数設定（推奨）
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="sk-your-api-key-here"
```

### 方法B: 設定ファイル編集
`ai_provider_config.json`を編集：
```json
{
  "openai": {
    "enabled": true,
    "priority": 1,
    "config": {
      "model": "gpt-3.5-turbo",
      "api_key": "sk-your-api-key-here"
    }
  }
}
```

### 方法C: バッチファイル使用（Windows）
1. `start_with_openai.bat`を編集
2. `YOUR_OPENAI_API_KEY_HERE`を実際のAPIキーに変更
3. バッチファイルを実行

## 3. 起動確認
```bash
python -m streamlit run app.py
```

コンソールに以下が表示されればOK：
```
✅ OpenAI API接続成功: gpt-3.5-turbo
```

## 4. トラブルシューティング

### エラー: 利用可能なAIプロバイダーがありません
- APIキーが正しく設定されているか確認
- `ai_provider_config.json`でOpenAIが`enabled: true`になっているか確認
- ネットワーク接続を確認

### エラー: OpenAI library not installed
```bash
pip install openai>=1.0.0
```

### エラー: OpenAI API接続失敗
- APIキーが有効か確認
- OpenAI Platform でクレジット残高を確認
- API利用制限を確認

## 5. 料金について
- GPT-3.5-turbo: 約$0.0015/1K tokens（入力）
- GPT-4: より高額なので注意
- 月額利用制限の設定を推奨

## 6. セキュリティ注意事項
- APIキーを公開しない
- Gitにコミットしない
- 環境変数での管理を推奨