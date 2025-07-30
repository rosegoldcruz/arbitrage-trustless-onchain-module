@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM 🚀 ATOM PLUG & PLAY SETUP SCRIPT (Windows)
REM ============================================================================

echo ============================================================================
echo 🧬 ATOM - ARBITRAGE TRUSTLESS ON-CHAIN MODULE
echo 🚀 PLUG ^& PLAY SETUP SCRIPT
echo ============================================================================

REM Check if we're in the frontend directory
if not exist "package.json" (
    echo ❌ Error: Please run this script from the frontend directory
    pause
    exit /b 1
)

REM 1. Install dependencies
echo.
echo 📦 Installing dependencies...
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm install
    echo ✅ Dependencies installed with pnpm
) else (
    echo ⚠️  pnpm not found, using npm...
    npm install
    echo ✅ Dependencies installed with npm
)

REM 2. Check environment file
echo.
echo 🔧 Checking environment configuration...
if exist ".env.local" (
    echo ✅ .env.local file exists
    
    REM Check for placeholder contract addresses
    findstr /C:"0x0000000000000000000000000000000000000000" .env.local >nul
    if !errorlevel! == 0 (
        echo ⚠️  WARNING: Some contract addresses are placeholders
        echo    Please update the following in .env.local:
        echo    - ATOM_TRIANGULAR_ARBITRAGE_ADDRESS
        echo    - ATOM_PRICE_MONITOR_ADDRESS
        echo    - ATOM_EXECUTION_ENGINE_ADDRESS
    )
) else (
    echo ❌ .env.local file not found
    echo 📋 Creating .env.local from .env.example...
    if exist ".env.example" (
        copy .env.example .env.local
        echo ✅ .env.local created
    ) else (
        echo ❌ .env.example not found either
        pause
        exit /b 1
    )
)

REM 3. Verify Clerk configuration
echo.
echo 🔐 Checking Clerk configuration...
findstr /C:"pk_test_" .env.local >nul && findstr /C:"sk_test_" .env.local >nul
if !errorlevel! == 0 (
    echo ✅ Clerk keys configured
    echo 📝 Remember to enable Web3 in Clerk Dashboard:
    echo    1. Go to https://dashboard.clerk.com/
    echo    2. Navigate to: User ^& Authentication ^> Web3
    echo    3. Enable: MetaMask, Coinbase Wallet, OKX Wallet
) else (
    echo ⚠️  Clerk keys may need configuration
)

REM 4. Check Supabase configuration
echo.
echo 🗄️  Checking Supabase configuration...
findstr /C:"nmjvebcauoyqzjlnluos.supabase.co" .env.local >nul
if !errorlevel! == 0 (
    echo ✅ Supabase configured for ATOM project
) else (
    echo ⚠️  Supabase configuration may need updates
)

REM 5. Check blockchain configuration
echo.
echo ⛓️  Checking blockchain configuration...
findstr /C:"84532" .env.local >nul
if !errorlevel! == 0 (
    echo ✅ Base Sepolia network configured
) else (
    echo ⚠️  Blockchain network configuration may need updates
)

REM 6. Start development server
echo.
echo 🌐 Starting development server...
echo Press Ctrl+C to stop the server
echo.
echo 🎯 ATOM Dashboard will be available at:
echo    Frontend: http://localhost:3000
echo    Dashboard: http://localhost:3000/dashboard
echo    Wallet Test: http://localhost:3000/wallet-test
echo.

REM Start the server
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    pnpm run dev
) else (
    npm run dev
)

pause
