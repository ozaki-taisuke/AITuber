# ルリちゃんWebUI固定ポート起動スクリプト
Write-Host "ルリちゃんWebUI固定ポート起動中..." -ForegroundColor Cyan
Write-Host "ポート: http://localhost:8501" -ForegroundColor Green
Write-Host ""

# 既存のStreamlitプロセスを終了
Write-Host "既存のStreamlitプロセスを終了中..." -ForegroundColor Yellow
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 固定ポートで起動
Write-Host "Streamlitを固定ポート8501で起動中..." -ForegroundColor Green
python -m streamlit run app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
