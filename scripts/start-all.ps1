# 🚀 ATOM/AEON Complete System Startup Script
# Starts frontend, backend, and bots in the correct order

Write-Host "🧬 ATOM/AEON System Startup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Check if required tools are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python" -ForegroundColor Red
    exit 1
}

# Check pnpm
try {
    $pnpmVersion = pnpm --version
    Write-Host "✅ pnpm: $pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pnpm not found. Installing..." -ForegroundColor Yellow
    npm install -g pnpm
}

Write-Host "`n🚀 Starting ATOM/AEON System..." -ForegroundColor Cyan

# Start Backend (FastAPI)
Write-Host "📡 Starting Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start Frontend (Next.js)
Write-Host "🌐 Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; pnpm dev"

# Wait for frontend to start
Start-Sleep -Seconds 10

# Start ATOM Bot (Node.js)
Write-Host "🤖 Starting ATOM Bot..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd bots; npm run atom"

# Start ADOM Engine (Python)
Write-Host "🐍 Starting ADOM Engine..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd bots; python adom_engine.py"

Write-Host "`n✅ ATOM/AEON System Started!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "📡 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📈 Monitor: http://localhost:3000/monitor" -ForegroundColor Cyan
Write-Host "`n🤖 Bots are running in background terminals" -ForegroundColor Yellow
Write-Host "Press Ctrl+C in each terminal to stop services" -ForegroundColor Gray
