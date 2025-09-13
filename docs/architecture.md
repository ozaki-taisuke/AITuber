# コードの構造とアーキテクチャ

## 📁 プロジェクト構成

```
AITuber/
├── src/                         # コアロジック
│   ├── character_ai.py         # キャラクター管理・感情学習
│   ├── image_analyzer.py       # 画像・色彩分析
│   ├── streaming_integration.py # Live2D・OBS連携
│   └── main.py                 # エントリーポイント
├── webui/                      # ユーザーインターフェース
│   └── app.py                  # Streamlit WebUI
├── assets/                     # リソースファイル
│   ├── ruri_character_profile.md
│   ├── ruri_detailed_settings.md
│   ├── ruri_imageboard.png
│   └── live2d_obs_setup.md
├── .github/
│   └── copilot-instructions.md # 開発ガイドライン
├── requirements.txt            # 依存関係
└── README.md                   # プロジェクト概要
```

## 🎯 主要クラス設計

### RuriCharacter (character_ai.py)
```python
class RuriCharacter:
    """ルリのAI管理クラス"""
    - emotions_learned: List[str]     # 学習済み感情
    - current_color_stage: str        # 現在の色彩段階
    - personality_traits: Dict        # 性格特性
    
    + learn_emotion(emotion, comment) # 感情学習
    + generate_stream_response()      # 配信応答生成
    + get_system_prompt()            # AIプロンプト取得
```

### RuriImageAnalyzer (image_analyzer.py)
```python
class RuriImageAnalyzer:
    """画像分析・色彩抽出クラス"""
    - imageboard_path: str           # イメージボードパス
    - dominant_colors: List[Dict]    # 主要色情報
    
    + analyze_colors()               # 色彩分析
    + generate_character_inspiration() # キャラクター提案
    + create_color_palette_config()   # パレット設定生成
```

### StreamingIntegration (streaming_integration.py)
```python
class StreamingIntegration:
    """配信システム統合クラス"""
    - live2d: Live2DController       # Live2D制御
    - obs: OBSController            # OBS制御
    - ruri: RuriCharacter           # キャラクター管理
    
    + start_streaming_mode()         # 配信開始
    + process_viewer_comment()       # コメント処理
```

## 🔄 データフロー

### 1. 感情学習フロー
```
視聴者コメント
    ↓
RuriCharacter.learn_emotion()
    ↓
OpenAI API (オプション)
    ↓
感情データ更新
    ↓
色彩段階変更
```

### 2. ビジュアル更新フロー  
```
感情変更イベント
    ↓
Live2DController.update_emotion_colors()
    ↓
WebSocket → Live2D Cubism
    ↓
OBSController.update_scene_by_emotion()
    ↓
OBS WebSocket → シーン切り替え
```

### 3. 色彩分析フロー
```
ruri_imageboard.png
    ↓
RuriImageAnalyzer.analyze_colors()
    ↓
OpenCV/Pillow処理
    ↓
HSV色空間変換
    ↓
感情マッピング
    ↓
Live2D/OBS設定生成
```

## 🛠️ 技術スタック詳細

### フロントエンド
- **Streamlit**: Web UI フレームワーク
- **リアルタイム更新**: session_state管理

### バックエンド
- **OpenAI API**: 感情分析・応答生成（オプション）
- **OpenCV/Pillow**: 画像処理・色彩分析
- **WebSocket**: Live2D/OBS制御

### 外部システム連携
- **Live2D Cubism SDK**: キャラクターモデル制御
- **OBS Studio**: 配信シーン管理
- **VoiSona**: 音声合成（将来的な拡張）

## 📊 設定管理

### 色彩段階定義
```python
COLOR_STAGES = {
    "monochrome": {"threshold": 0, "description": "感情未学習"},
    "partial_color": {"threshold": 2, "description": "初期感情学習"},
    "rainbow_transition": {"threshold": 4, "description": "感情発展期"},
    "full_color": {"threshold": 6, "description": "感情習得完了"}
}
```

### 感情-色マッピング
```python
EMOTION_COLORS = {
    "joy": {"r": 255, "g": 255, "b": 0},      # 黄色
    "anger": {"r": 255, "g": 0, "b": 0},      # 赤色
    "sadness": {"r": 0, "g": 0, "b": 255},    # 青色
    "love": {"r": 255, "g": 192, "b": 203}    # ピンク
}
```

## 🔧 拡張性設計

### プラグインアーキテクチャ
- 新しい感情タイプの追加
- 追加の外部サービス連携
- カスタム色彩分析アルゴリズム

### 設定の外部化
- JSON設定ファイル対応
- 環境変数による動的設定
- ユーザーカスタマイズ機能

## 🚀 パフォーマンス最適化

### メモリ管理
- 画像データの効率的なキャッシュ
- 不要なオブジェクトの適切な解放

### 通信最適化
- WebSocket接続の永続化
- バッチ処理による負荷軽減

### エラーハンドリング
- Graceful degradation
- フォールバック機能の実装
