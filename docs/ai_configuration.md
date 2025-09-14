# AI Provider Configuration Guide

## 概要
AITuber ルリは複数のAIプロバイダーに対応しており、環境に応じて柔軟な設定が可能です。

## 設定方法

### 1. 環境変数ファイル（推奨）
`.env.example`をコピーして`.env`を作成し、必要な情報を設定してください。

```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 2. Streamlit Secrets（Streamlit Cloud用）
`.streamlit/secrets.toml`にAPIキーを設定してください。

### 3. 環境変数（システムレベル）
```bash
export OPENAI_API_KEY="your-api-key"
export DEFAULT_AI_PROVIDER="openai"
```

## 対応プロバイダー

### OpenAI
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### Anthropic Claude
```env
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### Google Gemini
```env
GOOGLE_API_KEY=your-key-here
GEMINI_MODEL=gemini-pro
```

### Ollama（ローカル）
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### HuggingFace
```env
HUGGINGFACE_API_KEY=your-token-here
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium
```

## プロバイダー優先順位
```env
AI_PROVIDER_PRIORITY=openai,anthropic,gemini,ollama,simple
```

## デプロイメント別設定

### ローカル開発
- `.env`ファイルを使用
- 複数プロバイダーのテスト可能

### Streamlit Cloud
- `.streamlit/secrets.toml`を使用
- Streamlit Cloud のSecrets機能で管理

### Docker / 他のクラウド
- 環境変数で設定
- CI/CDパイプラインで管理

## セキュリティ注意事項
- APIキーは公開しない
- `.env`ファイルはGitにコミットしない
- 本番環境では環境変数を使用推奨

## トラブルシューティング
- `config_manager.get_debug_info()`でデバッグ情報確認
- 設定の優先順位: 環境変数 > .env > Streamlit secrets