@echo off
REM OpenAI API Key設定用バッチファイル
REM 使用方法: このファイルを編集してAPIキーを設定してから実行

REM ここにあなたのOpenAI APIキーを入力してください
set OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

REM APIキーが設定されているかチェック
if "%OPENAI_API_KEY%"=="YOUR_OPENAI_API_KEY_HERE" (
    echo ❌ APIキーが設定されていません
    echo このファイル内の OPENAI_API_KEY を実際のAPIキーに変更してください
    pause
    exit /b 1
)

echo ✅ OpenAI APIキーが設定されました
echo 🚀 ルリちゃんWebUIを起動します...

REM Streamlit WebUI起動
python -m streamlit run app.py --server.port 8501

pause