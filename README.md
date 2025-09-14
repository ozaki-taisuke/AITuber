# AITuber プロジェクト - ルリ

このプロジェクトは、自作戯曲『あいのいろ』の主人公「ルリ」をAI技術で再現し、バーチャルYouTuber（AITuber）として展開するためのものです。

## 🌈 ルリについて

ルリは自作戯曲『あいのいろ』の主人公として生まれたキャラクターです。原作では「感情を学んで色づいていく」という特殊な体質を持つ存在として描かれており、このAITuberプロジェクトでもその設定を忠実に再現しています。感情のない世界から来た少女的存在で、視聴者との交流を通じて新しい感情を学習し、段階的に色彩豊かになっていく成長物語を配信で体験できます。

## 主な機能

- **AIキャラクター管理**: ルリの感情学習状況を管理
- **感情学習システム**: 視聴者コメントから新しい感情を学習
- **色彩分析**: イメージボードから色彩情報を抽出・分析
- **画像生成支援**: AI画像生成用のプロンプト自動生成
- **配信管理**: OBS設定や配信コンテンツの提案
- **Web UI**: Streamlitベースの直感的な管理画面

## 技術スタック

- **Python 3.11+**
- **Streamlit** - Web UI
- **OpenAI API** - AI機能（オプション）
- **OpenCV, Pillow** - 画像処理
- **NumPy** - 数値計算

## 🚀 使い方

### 1. 環境セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/ozaki-taisuke/AITuber.git
cd AITuber

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. WebUI起動

#### ローカル環境
```bash
# Streamlit WebUIを起動
python -m streamlit run webui/app.py
```

ブラウザで `http://localhost:8501` または `http://localhost:8502` にアクセス

#### Cloudflare Pages デプロイ
```bash
# 1. Cloudflare Dashboard でプロジェクト作成
# 2. GitHubリポジトリを連携
# 3. 環境変数を設定:
#    ENVIRONMENT=production
#    DEBUG=False
#    BETA_AUTH_REQUIRED=False
```

詳細な手順: [Cloudflare Pages セットアップガイド](docs/cloudflare_pages_setup.md)

### 3. 各機能の使い方

#### 📊 キャラクター状態
- ルリの現在の色彩段階と学習済み感情を確認
- システムプロンプトの内容を表示

#### 💭 感情学習
1. 学習させたい感情を選択（喜び、怒り、哀しみ、愛など）
2. 視聴者コメントを入力
3. 「感情学習を実行」ボタンをクリック
4. ルリの反応と色彩段階の変化を確認

#### 🎨 イメージボード分析
1. 「イメージボード分析を実行」をクリック
2. `assets/ruri_imageboard.png` から主要色を自動抽出
3. 色彩分析結果とキャラクター発展提案を確認

#### 🖼️ 画像生成プロンプト
1. 感情段階を選択（monochrome → partial_color → rainbow_transition → full_color）
2. 「プロンプト生成」をクリック
3. 生成されたプロンプトをStable Diffusion、Midjourney、DALL-Eなどで使用

#### 📺 配信設定
- 現在の感情学習段階に応じた推奨配信コンテンツを確認
- OBS設定の参考情報を表示

### 4. OpenAI API設定（オプション）

より高度なAI機能を使用する場合：

```bash
# 環境変数でAPIキーを設定
export OPENAI_API_KEY="your-api-key-here"
```

## 📁 プロジェクト構造

```
AITuber/
├── src/                     # メインソースコード
│   ├── main.py             # エントリーポイント
│   ├── character_ai.py     # ルリちゃんのAI制御
│   └── image_analyzer.py   # 画像・色彩分析
├── webui/                  # Web UI
│   └── app.py             # Streamlit アプリケーション
├── assets/                 # 画像・設定ファイル
│   ├── image.png          # キャラクター画像
│   ├── ruri_imageboard.png # イメージボード
│   ├── ruri_character_profile.md # キャラクター基本設定
│   └── ruri_detailed_settings.md # 詳細設定
├── requirements.txt        # 依存パッケージ
└── README.md              # このファイル
```

## 🎭 ルリの感情学習段階

| 段階 | 色彩状態 | 説明 |
|------|----------|------|
| **monochrome** | モノクロ | 初期状態、感情未学習 |
| **partial_color** | 部分カラー | 1-2個の感情を学習 |
| **rainbow_transition** | 虹色移行 | 3-4個の感情を学習 |
| **full_color** | フルカラー | 多数の感情を学習完了 |

## 📝 ライセンス・権利関係

### 原案・企画
- **原作者**: ozaki-taisuke（戯曲『あいのいろ』作者）
- **キャラクター原案**: ozaki-taisuke（原作戯曲より）
- **AITuber化企画**: ozaki-taisuke

### アートワーク・画像
- **image.png**（原画）: まつはち さん
- **ruri_imageboard.png**（イメージボード化）:DALL-E 

### ソースコード
- **MIT License** - 自由に改変・再配布可能
- **作成者**: ozaki-taisuke

### 使用・改変について

#### 🆓 自由に使用できるもの
- **ソースコード**：MIT License - 自由に使用・改変・商用利用可能
- **キャラクター設定**：ルリの基本設定・世界観は二次創作歓迎
- **戯曲の世界観**：『あいのいろ』の設定を活用した創作活動

#### ⚠️ 制限があるもの
- **原画（image.png）**：まつはち さん作 - **使用には個別許諾が必要**
- **商用利用**：大規模な商用化は事前相談をお願いします

#### 📋 詳細ガイドライン
- **二次創作ガイドライン**：[docs/fan_creation_guidelines.md](docs/fan_creation_guidelines.md)
- **原画使用制限**：[docs/artwork_usage_restrictions.md](docs/artwork_usage_restrictions.md)
- **商用利用申請**：[docs/commercial_license_application.md](docs/commercial_license_application.md)

## 🤝 コントリビューション

プルリクエストやIssueは歓迎します！

### 開発に参加する場合

1. このリポジトリをフォーク
2. feature ブランチを作成
3. 変更をコミット
4. プルリクエストを送信

## 📞 お問い合わせ

- **GitHub**: [ozaki-taisuke](https://github.com/ozaki-taisuke)
- **プロジェクト**: [AITuber](https://github.com/ozaki-taisuke/AITuber)

---

このREADMEは随時更新されます。ご質問やご提案があればお気軽にお知らせください！
