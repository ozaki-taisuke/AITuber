<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AITuber プロジェクト - ルリ 開発指針

このプロジェクトは、自作戯曲『あいのいろ』の主人公「ルリ」をAI技術で現代に蘇らせ、感情を学習して色づいていくAIバーチャルYouTuberとして展開するシステムです。

## プロジェクト概要
- **原作**: 自作戯曲『あいのいろ』（ozaki-taisuke 作）
- **主人公**: ルリ（原作から継承されたキャラクター設定）
- **コンセプト**: 戯曲の「感情学習による段階的な色彩変化」をAI技術で実現
- **技術**: Python + Streamlit + OpenAI API（オプション）
- **目的**: 原作の世界観を活かしたAITuber配信システムの構築

## 開発ガイドライン

### コーディング規則
- Python 3.11+を使用
- 型ヒントを積極的に活用
- OpenAI API依存は必須ではなく、フォールバック機能を提供
- エラーハンドリングを適切に実装

### ファイル構成
- `src/`: メインのロジック（キャラクターAI、画像分析）
- `webui/`: Streamlit WebUI
- `assets/`: キャラクター設定、画像ファイル

### キャラクター仕様
- 原作戯曲の設定を忠実に継承
- 感情学習段階: monochrome → partial_color → rainbow_transition → full_color
- 学習可能感情: 喜び、怒り、哀しみ、愛、驚き、恐れ、嫌悪、期待
- 色彩システム: HSV値による動的色変更（原作の視覚表現を技術で実現）

### 権利関係
- 原作・企画: ozaki-taisuke（戯曲『あいのいろ』作者）
- アートワーク: まつはち さん
- ソースコード: MIT License

## 拡張時の注意点
- 原作戯曲の世界観・キャラクター設定の一貫性を保つ
- 戯曲のテーマ「感情とは何か」を尊重した実装
- 色彩変化システムの整合性を維持
- APIエラー時のグレースフルな対応
- ユーザビリティを重視したUI設計

Work through each checklist item systematically.
Keep communication concise and focused.
Follow development best practices.
