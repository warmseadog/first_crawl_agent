# 启动前端界面
Write-Host "🎨 正在启动舆情监测平台前端界面..." -ForegroundColor Green
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "frontend\app.py")) {
    Write-Host "❌ 错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查后端是否运行
Write-Host "⚠️  请确保后端服务已启动 (运行 .\start_backend.ps1)" -ForegroundColor Yellow
Write-Host ""

# 进入 frontend 目录并启动服务
Set-Location frontend
Write-Host "🌐 启动 Streamlit 界面 (通常在 http://localhost:8501)" -ForegroundColor Cyan
Write-Host ""

streamlit run app.py
