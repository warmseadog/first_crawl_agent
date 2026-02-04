# 启动后端服务
Write-Host "🚀 正在启动舆情监测平台后端服务..." -ForegroundColor Green
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "api\main.py")) {
    Write-Host "❌ 错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  警告：未找到 .env 文件，请确保已配置 API 密钥" -ForegroundColor Yellow
}

# 进入 api 目录并启动服务
Set-Location api
Write-Host "📡 启动 FastAPI 服务 (http://localhost:8000)" -ForegroundColor Cyan
Write-Host "📚 API 文档地址: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn main:app --reload --port 8000
