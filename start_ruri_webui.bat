@echo off
echo ルリちゃんWebUI固定ポート起動中...
echo ポート: http://localhost:8501
echo.

REM 既存のStreamlitプロセスを終了
taskkill /F /IM streamlit.exe 2>nul

REM 少し待つ
timeout /t 2 /nobreak >nul

REM 固定ポートで起動
python -m streamlit run webui\app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

pause
