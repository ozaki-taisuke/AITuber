# 開発・運用ガイド

## 🚀 セットアップ & 開発環境

### 前提条件
- Python 3.11+
- Git
- VS Code (推奨)

### 開発環境構築
```bash
# 1. リポジトリクローン
git clone https://github.com/ozaki-taisuke/AITuber.git
cd AITuber

# 2. 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. 環境変数設定（オプション）
export OPENAI_API_KEY="your-api-key"

# 5. WebUI起動
python -m streamlit run webui/app.py
```

## 🔧 開発ワークフロー

### ブランチ戦略
```
main: 安定版
├── feature/emotion-system: 感情システム機能
├── feature/live2d-integration: Live2D連携
└── hotfix/ui-fixes: 緊急修正
```

### コミット規約
```bash
# 機能追加
git commit -m "feat: 新しい感情学習アルゴリズムを追加"

# バグ修正  
git commit -m "fix: Live2D接続エラーを修正"

# ドキュメント
git commit -m "docs: Live2D設定手順を更新"

# リファクタリング
git commit -m "refactor: キャラクター名をルリちゃん→ルリに統一"
```

### コードレビューチェックリスト
- [ ] 型ヒントの記述
- [ ] エラーハンドリングの実装
- [ ] ドキュメント文字列の追加
- [ ] テストケースの作成
- [ ] セキュリティ考慮事項の確認

## 🎯 機能別開発ガイド

### 新しい感情を追加する場合

1. **character_ai.py を更新**
```python
# 新しい感情の定義
AVAILABLE_EMOTIONS = [
    "joy", "anger", "sadness", "love", 
    "surprise", "fear", "disgust", "anticipation"  # 新規追加
]
```

2. **色彩マッピングを追加**
```python
# image_analyzer.py
color_emotions = {
    # 既存の感情...
    "surprise": "驚き・突発性・明るさ",
    "anticipation": "期待・希望・未来"
}
```

3. **Live2D/OBS設定を更新**
```python
# streaming_integration.py
scene_mapping = {
    # 既存のシーン...
    "surprise": "ルリ_驚き",
    "anticipation": "ルリ_期待"
}
```

### 新しい外部サービス連携

1. **基底クラスの作成**
```python
class ExternalServiceController:
    def __init__(self, config):
        self.config = config
    
    def connect(self):
        raise NotImplementedError
    
    def send_emotion_data(self, emotion, intensity):
        raise NotImplementedError
```

2. **具体実装**
```python
class VoiSonaController(ExternalServiceController):
    def connect(self):
        # VoiSona API接続
        pass
    
    def send_emotion_data(self, emotion, intensity):
        # 音声合成パラメータ調整
        pass
```

## 📊 モニタリング & ログ

### ログ設定
```python
import logging

# ログレベルの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 機能別ログ
character_logger = logging.getLogger('ruri.character')
streaming_logger = logging.getLogger('ruri.streaming')
```

### パフォーマンス監視
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f}s")
        return result
    return wrapper
```

## 🔐 セキュリティ考慮事項

### API キー管理
```python
# 環境変数による管理
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OpenAI API key not found")
```

### 入力検証
```python
def validate_emotion_input(emotion: str) -> bool:
    """感情入力の検証"""
    allowed_emotions = ["joy", "anger", "sadness", "love"]
    return emotion.lower() in allowed_emotions
```

### WebSocket セキュリティ
```python
# 接続元IPの制限
ALLOWED_IPS = ["127.0.0.1", "localhost"]

def validate_websocket_connection(ip_address):
    return ip_address in ALLOWED_IPS
```

## 🧪 テスト戦略

### 単体テスト
```python
import unittest
from src.character_ai import RuriCharacter

class TestRuriCharacter(unittest.TestCase):
    def setUp(self):
        self.ruri = RuriCharacter()
    
    def test_emotion_learning(self):
        initial_count = len(self.ruri.emotions_learned)
        self.ruri.learn_emotion("joy", "test comment")
        self.assertEqual(len(self.ruri.emotions_learned), initial_count + 1)
```

### 統合テスト
```python
def test_streaming_integration():
    """配信システム全体のテスト"""
    integration = StreamingIntegration()
    result = integration.process_viewer_comment("嬉しい！", "joy")
    
    assert result["emotion"] == "joy"
    assert "Live2D" in result["systems_updated"]
```

## 📈 デプロイメント

### 本番環境セットアップ
```bash
# 1. プロダクション用設定
export ENVIRONMENT=production
export LOG_LEVEL=WARNING

# 2. リバースプロキシ設定（nginx）
upstream streamlit_backend {
    server 127.0.0.1:8501;
}

# 3. SSL証明書設定
# 4. ファイアウォール設定
```

### 継続的インテグレーション
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. Live2D接続エラー
```
症状: WebSocket connection failed
原因: Live2D Cubism SDKが起動していない
解決: Live2D WebSocketサーバーを先に起動
```

#### 2. OBS連携失敗
```
症状: obs-websocket connection refused
原因: OBS WebSocketプラグインが無効
解決: OBS設定でWebSocketを有効化
```

#### 3. 画像分析エラー
```
症状: OpenCV import error
原因: opencv-pythonがインストールされていない
解決: pip install opencv-python
```

### ログ分析
```bash
# エラーログの確認
grep "ERROR" logs/ruri.log

# パフォーマンスログの確認  
grep "executed in" logs/ruri.log | sort -k5 -nr
```

## 📚 参考資料

### 技術ドキュメント
- [Live2D Cubism SDK](https://docs.live2d.com/)
- [OBS WebSocket Protocol](https://github.com/obsproject/obs-websocket)
- [Streamlit Documentation](https://docs.streamlit.io/)

### コミュニティ
- GitHub Issues: バグ報告・機能要望
- Discord: リアルタイム討議（将来的）
- Wiki: 詳細なドキュメント
