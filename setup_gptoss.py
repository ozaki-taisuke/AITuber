#!/usr/bin/env python3
# GPT-OSS統合のためのインストール・テストスクリプト
import subprocess
import sys
import os
import json

def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n🔧 {description}")
    print(f"実行中: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            if result.stdout:
                print(f"出力:\n{result.stdout}")
        else:
            print(f"❌ 失敗: {description}")
            print(f"エラー:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 例外発生: {e}")
        return False

def check_python_version():
    """Python バージョンチェック"""
    print(f"🐍 Python バージョン: {sys.version}")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python 3.8以上が必要です")
        return False
    print("✅ Python バージョンOK")
    return True

def check_system_requirements():
    """システム要件チェック"""
    print(f"\n💻 システム要件チェック")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"💾 利用可能メモリ: {memory_gb:.1f} GB")
        
        if memory_gb < 16:
            print("⚠️  警告: GPT-OSS 20Bモデルには16GB以上のRAMが推奨されます")
        else:
            print("✅ メモリ要件を満たしています")
        
        return True
    except ImportError:
        print("⚠️  psutilがインストールされていないため、メモリチェックをスキップします")
        return True

def install_dependencies():
    """依存関係のインストール"""
    print(f"\n📦 依存関係のインストール")
    
    # requirements.txtから読み込み
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} が見つかりません")
        return False
    
    # pip install
    success = run_command(
        f"pip install -r {requirements_file}",
        "基本依存関係のインストール"
    )
    
    if not success:
        print("⚠️  requirements.txtの一部のパッケージでエラーが発生しました")
        print("GPT-OSS関連のパッケージを個別にインストールしてみます...")
    
    # オプション: 個別インストール
    optional_packages = [
        ("gpt-oss", "GPT-OSSコアライブラリ"),
        ("openai-harmony", "Harmony形式ライブラリ"),
        ("ollama", "Ollamaクライアント")
    ]
    
    for package, description in optional_packages:
        success = run_command(
            f"pip install {package}",
            description
        )
        if not success:
            print(f"⚠️  {package} のインストールに失敗しました（オプション）")
    
    return True

def test_imports():
    """インポートテスト"""
    print(f"\n🧪 インポートテスト")
    
    # 基本ライブラリ
    basic_imports = [
        ("streamlit", "Streamlit"),
        ("opencv-cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("plotly", "Plotly")
    ]
    
    for module, name in basic_imports:
        try:
            __import__(module)
            print(f"✅ {name}: インポート成功")
        except ImportError as e:
            print(f"❌ {name}: インポート失敗 - {e}")
    
    # GPT-OSS関連
    gptoss_imports = [
        ("ollama", "Ollama"),
        ("openai_harmony", "OpenAI Harmony"),
        ("gpt_oss", "GPT-OSS")
    ]
    
    print(f"\n🤖 GPT-OSS関連インポートテスト")
    for module, name in gptoss_imports:
        try:
            __import__(module)
            print(f"✅ {name}: インポート成功")
        except ImportError as e:
            print(f"⚠️  {name}: インポート失敗 - {e} (オプション)")

def check_ollama_installation():
    """Ollamaインストール状況確認"""
    print(f"\n🦙 Ollamaインストール確認")
    
    # Ollamaコマンドの確認
    if run_command("ollama --version", "Ollamaバージョン確認"):
        print("✅ Ollamaがインストールされています")
        
        # モデル一覧確認
        if run_command("ollama list", "インストール済みモデル一覧"):
            print("📋 gpt-oss:20bモデルがリストにあるか確認してください")
            print("💡 モデルをインストールするには: ollama pull gpt-oss:20b")
    else:
        print("⚠️  Ollamaがインストールされていません")
        print("💡 インストール方法: https://ollama.com/download")

def test_ruri_gptoss():
    """RuriGPTOSSクラスのテスト"""
    print(f"\n🌠 RuriGPTOSSクラステスト")
    
    try:
        sys.path.append("src")
        from ruri_gptoss import RuriGPTOSS
        
        # インスタンス作成
        ruri = RuriGPTOSS()
        print("✅ RuriGPTOSSインスタンス作成成功")
        
        # 状態確認
        status = ruri.get_status_info()
        print(f"📊 ステータス: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # 基本応答テスト（フォールバックモード）
        response = ruri.generate_stream_response("テストメッセージです")
        print(f"💬 応答テスト: {response[:100]}...")
        
        print("✅ RuriGPTOSSテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ RuriGPTOSSテストエラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🚀 GPT-OSS統合 セットアップ・テストスクリプト")
    print("=" * 50)
    
    # Python バージョンチェック
    if not check_python_version():
        sys.exit(1)
    
    # システム要件チェック
    check_system_requirements()
    
    # 依存関係インストール
    if not install_dependencies():
        print("❌ 依存関係のインストールに問題があります")
    
    # インポートテスト
    test_imports()
    
    # Ollama確認
    check_ollama_installation()
    
    # RuriGPTOSSテスト
    test_ruri_gptoss()
    
    print("\n🎉 セットアップ・テスト完了")
    print("=" * 50)
    print("💡 次のステップ:")
    print("1. Ollamaサーバーを起動: ollama serve")
    print("2. GPT-OSSモデルをダウンロード: ollama pull gpt-oss:20b")
    print("3. WebUIを起動: streamlit run webui/app.py")
    print("4. 本番環境モードを有効にしてGPT-OSS機能をテスト")

if __name__ == "__main__":
    main()
