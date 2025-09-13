# Live2D・OBS連携設定ファイル

## 🎭 Live2D Cubism連携

### 必要なソフトウェア
- **Live2D Cubism Editor** (モデル作成)
- **Live2D Cubism SDK for Web** (WebSocket連携用)
- **NodeJS** (WebSocketサーバー)

### セットアップ手順

#### 1. Live2Dモデルの準備
```bash
# Live2D Cubism Editorでルリモデルを作成
# 以下のパラメータを必ず含める：
- ParamHairColorR/G/B (髪の色)
- ParamEyeColorR/G/B (瞳の色)  
- ParamClothesColorR/G/B (服の色)
- ParamMouthForm (口の形)
- ParamEyeForm (目の形)
- ParamBreath (呼吸)
```

#### 2. WebSocketサーバーの起動
```javascript
// live2d-server.js
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8001 });

wss.on('connection', function connection(ws) {
  console.log('Live2D connection established');
  
  ws.on('message', function incoming(message) {
    const command = JSON.parse(message);
    // Live2Dモデルにパラメータを送信
    updateLive2DParameter(command);
  });
});
```

#### 3. Pythonから制御
```python
# 使用例
from src.streaming_integration import Live2DController

controller = Live2DController()
controller.connect_live2d()
controller.update_emotion_colors("joy", 1.0)
```

## 📺 OBS Studio連携

### 必要なソフトウェア
- **OBS Studio 28.0+**
- **obs-websocket プラグイン**

### セットアップ手順

#### 1. OBS WebSocketの有効化
1. OBS Studio → ツール → WebSocket Server Settings
2. 「Enable WebSocket server」にチェック
3. ポート: 4444 (デフォルト)
4. パスワードを設定

#### 2. 感情別シーンの作成

**基本シーン構成:**
```
シーン: ルリ_通常
├── ソース: Live2Dキャプチャ
├── ソース: 背景画像
└── フィルター: 感情カラーフィルター

シーン: ルリ_喜び  
├── ソース: Live2Dキャプチャ
├── ソース: 明るい背景
└── フィルター: 暖色系カラーフィルター

シーン: ルリ_怒り
├── ソース: Live2Dキャプチャ  
├── ソース: 赤系背景
└── フィルター: 赤色強調フィルター

# 同様に哀しみ、愛シーンも作成
```

#### 3. カラーフィルターの設定
各シーンに以下のフィルターを追加：
- **色補正フィルター**: 色相、彩度、明度を感情に応じて調整
- **クロマキー**: 背景透過（必要に応じて）
- **シャープネス**: 画像の鮮明さ調整

## 🎨 イメージボード連動システム

### 色彩分析結果の活用

#### 1. リアルタイム色抽出
```python
# ruri_imageboard.pngから色を抽出してLive2D/OBSに反映
analyzer = RuriImageAnalyzer("assets/ruri_imageboard.png")
colors = analyzer.analyze_colors()

# 抽出した色をLive2Dパラメータに変換
for color in colors[:3]:  # 上位3色を使用
    rgb = color['rgb']
    # Live2Dの髪・瞳・服の色に適用
```

#### 2. 感情段階別カラーパレット
```python
color_stages = {
    "monochrome": {
        "hair": [128, 128, 128],
        "eyes": [100, 100, 100], 
        "clothes": [150, 150, 150]
    },
    "partial_color": {
        "hair": [200, 200, 100],  # 黄色いハイライト
        "eyes": [150, 150, 200],  # 青いハイライト
        "clothes": [128, 128, 128] # まだグレー
    },
    "full_color": {
        "hair": [255, 200, 100],  # 暖色系
        "eyes": [100, 150, 255],  # 鮮やかな青
        "clothes": [255, 100, 150] # ピンク系
    }
}
```

## 🔄 自動化ワークフロー

### 配信開始時の自動セットアップ
1. **Live2D起動確認**
2. **OBS接続確認** 
3. **イメージボード分析実行**
4. **初期シーン設定**
5. **感情学習システム開始**

### 視聴者コメント処理フロー
1. **コメント受信**
2. **感情分析** (OpenAI API)
3. **ルリちゃん反応生成**
4. **Live2D色変更送信**
5. **OBSシーン切り替え**
6. **学習結果保存**

## 🛠️ 技術仕様

### WebSocket通信仕様
```json
// Live2Dへのコマンド例
{
  "command": "setParameterValue",
  "parameterId": "ParamHairColorR",
  "value": 0.8,
  "duration": 1000
}

// OBSへのコマンド例  
{
  "request-type": "SetCurrentScene",
  "scene-name": "ルリちゃん_喜び"
}
```

### パフォーマンス最適化
- **フレームレート**: 30fps維持
- **遅延**: 100ms以下での反応
- **メモリ使用量**: 最適化されたテクスチャ
- **CPU負荷**: マルチスレッド処理

## 🎯 実装優先度

### Phase 1 (基本連携)
- [ ] Live2D WebSocket接続
- [ ] OBS基本制御
- [ ] 感情別色変更

### Phase 2 (高度な表現)  
- [ ] リアルタイム色分析
- [ ] 表情アニメーション
- [ ] 背景エフェクト

### Phase 3 (AI強化)
- [ ] 視聴者コメント自動分析
- [ ] 学習結果のビジュアル化
- [ ] 予測的シーン切り替え
