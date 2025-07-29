@echo off
REM 🚀 ATOM REAL-TIME DASHBOARD LAUNCHER (Windows)
REM Starts backend with REAL DEX connections + frontend with live data

echo 🚀 STARTING ATOM REAL-TIME DASHBOARD
echo =====================================

REM Check if required environment variables are set
echo 🔍 Checking environment variables...

if "%PRIVATE_KEY%"=="" (
    echo ❌ PRIVATE_KEY not set
    echo    set PRIVATE_KEY=your_private_key_here
    pause
    exit /b 1
)

if "%THEATOM_API_KEY%"=="" (
    echo ⚠️  THEATOM_API_KEY not set, using default
    set THEATOM_API_KEY=7324a2b4-3b05-4288-b353-68322f49a283
)

echo ✅ Environment variables configured

REM Start backend with REAL DEX connections
echo.
echo 🔧 Starting backend with REAL DEX integrations...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

REM Start backend server in background
echo 🚀 Launching FastAPI backend with REAL data...
start "ATOM Backend" cmd /c "python main.py"

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

REM Start frontend
echo.
echo 🎨 Starting frontend with REAL-TIME dashboard...
cd ..\frontend

REM Install Node.js dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    call pnpm install
)

REM Start frontend development server
echo 🚀 Launching Next.js frontend...
start "ATOM Frontend" cmd /c "pnpm run dev"

REM Wait for frontend to start
echo ⏳ Waiting for frontend to initialize...
timeout /t 12 /nobreak >nul

REM Display status
echo.
echo 🎯 ATOM REAL-TIME DASHBOARD IS LIVE!
echo =====================================
echo 📊 Dashboard: http://localhost:3000/dashboard
echo 🔧 API Docs:  http://localhost:8000/docs
echo 💹 Health:    http://localhost:8000/health
echo.
echo 🔗 REAL DEX INTEGRATIONS:
echo    ✅ 0x Protocol
echo    ✅ 1inch
echo    ✅ ParaSwap
echo    ✅ Balancer
echo    ✅ Curve
echo    ✅ Uniswap
echo.
echo 📈 LIVE DATA FEATURES:
echo    🔴 Real-time DEX quotes
echo    🔴 Live arbitrage opportunities
echo    🔴 Production bot status
echo    🔴 Actual profit tracking
echo    🔴 Gas price monitoring
echo    🔴 Transaction execution
echo.
echo 🎮 CONTROLS:
echo    • View live opportunities in dashboard
echo    • Execute real arbitrage trades
echo    • Monitor bot performance
echo    • Track DEX connection health
echo.
echo Opening dashboard in browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000/dashboard

echo.
echo ✅ Dashboard launched! Check your browser.
echo 🔴 Both backend and frontend are running in separate windows.
echo 🛑 Close those windows to stop the services.
echo.
pause
