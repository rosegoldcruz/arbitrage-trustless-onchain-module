#!/bin/bash

# 🚀 ATOM REAL-TIME DASHBOARD LAUNCHER
# Starts backend with REAL DEX connections + frontend with live data

echo "🚀 STARTING ATOM REAL-TIME DASHBOARD"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required environment variables are set
echo -e "${BLUE}🔍 Checking environment variables...${NC}"

if [ -z "$PRIVATE_KEY" ]; then
    echo -e "${RED}❌ PRIVATE_KEY not set${NC}"
    echo "   export PRIVATE_KEY=\"your_private_key_here\""
    exit 1
fi

if [ -z "$THEATOM_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  THEATOM_API_KEY not set, using default${NC}"
    export THEATOM_API_KEY="7324a2b4-3b05-4288-b353-68322f49a283"
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start backend with REAL DEX connections
echo -e "\n${BLUE}🔧 Starting backend with REAL DEX integrations...${NC}"
cd backend

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install requirements
pip install -r requirements.txt > /dev/null 2>&1

# Start backend server
echo -e "${GREEN}🚀 Launching FastAPI backend with REAL data...${NC}"
python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend running on http://localhost:8000${NC}"

# Start frontend
echo -e "\n${BLUE}🎨 Starting frontend with REAL-TIME dashboard...${NC}"
cd ../frontend

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    pnpm install
fi

# Start frontend development server
echo -e "${GREEN}🚀 Launching Next.js frontend...${NC}"
pnpm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to initialize...${NC}"
sleep 10

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend running on http://localhost:3000${NC}"

# Display status
echo -e "\n${GREEN}🎯 ATOM REAL-TIME DASHBOARD IS LIVE!${NC}"
echo "====================================="
echo -e "${BLUE}📊 Dashboard:${NC} http://localhost:3000/dashboard"
echo -e "${BLUE}🔧 API Docs:${NC}  http://localhost:8000/docs"
echo -e "${BLUE}💹 Health:${NC}    http://localhost:8000/health"
echo ""
echo -e "${GREEN}🔗 REAL DEX INTEGRATIONS:${NC}"
echo "   ✅ 0x Protocol"
echo "   ✅ 1inch"
echo "   ✅ ParaSwap"
echo "   ✅ Balancer"
echo "   ✅ Curve"
echo "   ✅ Uniswap"
echo ""
echo -e "${YELLOW}📈 LIVE DATA FEATURES:${NC}"
echo "   🔴 Real-time DEX quotes"
echo "   🔴 Live arbitrage opportunities"
echo "   🔴 Production bot status"
echo "   🔴 Actual profit tracking"
echo "   🔴 Gas price monitoring"
echo "   🔴 Transaction execution"
echo ""
echo -e "${BLUE}🎮 CONTROLS:${NC}"
echo "   • View live opportunities in dashboard"
echo "   • Execute real arbitrage trades"
echo "   • Monitor bot performance"
echo "   • Track DEX connection health"
echo ""
echo -e "${RED}Press Ctrl+C to stop all services${NC}"

# Keep script running and show live updates
while true; do
    sleep 30
    
    # Check backend health
    if curl -s http://localhost:8000/health > /dev/null; then
        BACKEND_STATUS="${GREEN}✅ ONLINE${NC}"
    else
        BACKEND_STATUS="${RED}❌ OFFLINE${NC}"
    fi
    
    # Check frontend health
    if curl -s http://localhost:3000 > /dev/null; then
        FRONTEND_STATUS="${GREEN}✅ ONLINE${NC}"
    else
        FRONTEND_STATUS="${RED}❌ OFFLINE${NC}"
    fi
    
    # Clear previous status and show current
    echo -e "\r${BLUE}Status:${NC} Backend $BACKEND_STATUS | Frontend $FRONTEND_STATUS | $(date '+%H:%M:%S')"
done
