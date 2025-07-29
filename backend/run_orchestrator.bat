@echo off
REM Real Arbitrage Orchestrator Startup Script for Windows
REM No fake quantum bullshit - just working bot coordination

echo 🚀 REAL ARBITRAGE ORCHESTRATOR STARTUP
echo ======================================

REM Check if we're in the right directory
if not exist "orchestrator_config.json" (
    echo ❌ orchestrator_config.json not found
    echo Please run this script from the backend directory
    pause
    exit /b 1
)

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    pause
    exit /b 1
)

REM Check Node.js for ADOM bot
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found - required for ADOM bot
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set node_version=%%i
echo ✅ Node.js version: %node_version%

REM Install Python dependencies if needed
echo 🔧 Checking Python dependencies...
pip install -q requests psutil

REM Install Node.js dependencies for ADOM bot
if exist "bots\package.json" (
    echo 🔧 Installing Node.js dependencies...
    cd bots
    npm install --silent
    cd ..
)

REM Create required directories
echo 📁 Creating communication directories...
if not exist "comm\commands" mkdir comm\commands
if not exist "comm\results" mkdir comm\results
if not exist "comm\heartbeats" mkdir comm\heartbeats
if not exist "logs" mkdir logs

REM Check if bots exist
if not exist "bots\ATOM.py" (
    echo ❌ ATOM.py bot not found
    pause
    exit /b 1
)

if not exist "bots\ADOM.js" (
    echo ❌ ADOM.js bot not found
    pause
    exit /b 1
)

echo ✅ All prerequisites checked
echo.
echo 🎯 Starting Real Orchestrator...
echo    - ATOM.py (Python arbitrage bot)
echo    - ADOM.js (Node.js MEV bot)
echo    - Real DEX API scanning
echo    - File-based bot communication
echo    - SQLite performance tracking
echo.
echo Press Ctrl+C to stop
echo.

REM Start the orchestrator
python start_orchestrator.py

echo.
echo 👋 Orchestrator shutdown complete
pause
