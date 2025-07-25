#!/bin/bash

# AEON NETWORK FULL STACK DEPLOYMENT
# Deploys all three parallel ecosystems and starts monitoring

set -e

echo "🚀 DEPLOYING AEON NETWORK - ADVANCED, EFFICIENT, OPTIMIZED"
echo "============================================================"
echo "🧠 Option 1: AEON (On-chain Intelligence)"
echo "🔁 Option 2: ATOM/ADOM (Hybrid Execution)" 
echo "⚙️ Option 3: SPECTRE (Off-chain Analytics)"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if required environment variables are set
check_env() {
    echo -e "${BLUE}🔍 Checking environment variables...${NC}"
    
    if [ -z "$PRIVATE_KEY" ]; then
        echo -e "${RED}❌ PRIVATE_KEY not set${NC}"
        exit 1
    fi
    
    if [ -z "$BASE_SEPOLIA_RPC" ]; then
        echo -e "${YELLOW}⚠️  BASE_SEPOLIA_RPC not set, using default${NC}"
        export BASE_SEPOLIA_RPC="https://sepolia.base.org"
    fi
    
    echo -e "${GREEN}✅ Environment variables checked${NC}"
}

# Deploy smart contracts (Option 1: AEON)
deploy_contracts() {
    echo -e "\n${BLUE}🧠 DEPLOYING AEON SMART CONTRACTS (Option 1)${NC}"
    echo "Chainlink + Smart Contract Logic + Flash Loans"
    echo "------------------------------------------------------------"
    
    cd contracts
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing contract dependencies...${NC}"
        npm install
    fi
    
    # Deploy contracts to Base Sepolia
    echo -e "${BLUE}🚀 Deploying to Base Sepolia...${NC}"
    npx hardhat run scripts/deploy-aeon-network.js --network baseSepolia
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ AEON contracts deployed successfully${NC}"
    else
        echo -e "${RED}❌ Contract deployment failed${NC}"
        exit 1
    fi
    
    cd ..
}

# Start ATOM/ADOM hybrid bot (Option 2)
start_atom_bot() {
    echo -e "\n${PURPLE}🔁 STARTING ATOM/ADOM HYBRID BOT (Option 2)${NC}"
    echo "Bot-triggered Smart Contracts + RPC Calls"
    echo "------------------------------------------------------------"
    
    cd bots
    
    # Install Python dependencies if needed
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start ATOM hybrid bot in background
    echo -e "${PURPLE}🤖 Starting ATOM/ADOM hybrid bot...${NC}"
    nohup python3 atom_hybrid_bot.py > ../logs/atom_bot.log 2>&1 &
    ATOM_PID=$!
    echo $ATOM_PID > ../logs/atom_bot.pid
    
    echo -e "${GREEN}✅ ATOM/ADOM bot started (PID: $ATOM_PID)${NC}"
    
    cd ..
}

# Start SPECTRE analytics engine (Option 3)
start_spectre_analytics() {
    echo -e "\n${CYAN}⚙️ STARTING SPECTRE ANALYTICS ENGINE (Option 3)${NC}"
    echo "Pure Off-chain Simulation + Analytics"
    echo "------------------------------------------------------------"
    
    cd bots
    
    # Ensure virtual environment is active
    source venv/bin/activate
    
    # Start SPECTRE analytics in background
    echo -e "${CYAN}📊 Starting SPECTRE analytics engine...${NC}"
    nohup python3 spectre_analytics.py > ../logs/spectre.log 2>&1 &
    SPECTRE_PID=$!
    echo $SPECTRE_PID > ../logs/spectre.pid
    
    echo -e "${GREEN}✅ SPECTRE analytics started (PID: $SPECTRE_PID)${NC}"
    
    cd ..
}

# Start frontend dashboard
start_frontend() {
    echo -e "\n${BLUE}🖥️  STARTING AEON FRONTEND DASHBOARD${NC}"
    echo "------------------------------------------------------------"
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
        pnpm install
    fi
    
    # Start development server
    echo -e "${BLUE}🌐 Starting Next.js development server...${NC}"
    pnpm dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo -e "${GREEN}🌐 Dashboard available at: http://localhost:3000${NC}"
    echo -e "${GREEN}🧠 AEON Network: http://localhost:3000/aeon${NC}"
    echo -e "${GREEN}🚀 Arbitrage Engine: http://localhost:3000/arbitrage${NC}"
    
    cd ..
}

# Create log directory
setup_logging() {
    echo -e "${BLUE}📝 Setting up logging...${NC}"
    mkdir -p logs
    
    # Create log files
    touch logs/atom_bot.log
    touch logs/spectre.log
    touch logs/deployment.log
    
    echo -e "${GREEN}✅ Logging setup complete${NC}"
}

# Monitor all systems
monitor_systems() {
    echo -e "\n${GREEN}📊 AEON NETWORK STATUS MONITOR${NC}"
    echo "============================================================"
    
    while true; do
        clear
        echo -e "${GREEN}🧠 AEON NETWORK - LIVE STATUS${NC}"
        echo "============================================================"
        echo -e "Timestamp: $(date)"
        echo ""
        
        # Check ATOM bot
        if [ -f "logs/atom_bot.pid" ]; then
            ATOM_PID=$(cat logs/atom_bot.pid)
            if ps -p $ATOM_PID > /dev/null; then
                echo -e "${GREEN}✅ ATOM/ADOM Bot: RUNNING (PID: $ATOM_PID)${NC}"
            else
                echo -e "${RED}❌ ATOM/ADOM Bot: STOPPED${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  ATOM/ADOM Bot: NOT STARTED${NC}"
        fi
        
        # Check SPECTRE analytics
        if [ -f "logs/spectre.pid" ]; then
            SPECTRE_PID=$(cat logs/spectre.pid)
            if ps -p $SPECTRE_PID > /dev/null; then
                echo -e "${GREEN}✅ SPECTRE Analytics: RUNNING (PID: $SPECTRE_PID)${NC}"
            else
                echo -e "${RED}❌ SPECTRE Analytics: STOPPED${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  SPECTRE Analytics: NOT STARTED${NC}"
        fi
        
        # Check frontend
        if [ -f "logs/frontend.pid" ]; then
            FRONTEND_PID=$(cat logs/frontend.pid)
            if ps -p $FRONTEND_PID > /dev/null; then
                echo -e "${GREEN}✅ Frontend Dashboard: RUNNING (PID: $FRONTEND_PID)${NC}"
            else
                echo -e "${RED}❌ Frontend Dashboard: STOPPED${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Frontend Dashboard: NOT STARTED${NC}"
        fi
        
        echo ""
        echo -e "${BLUE}📊 Recent Activity:${NC}"
        echo "------------------------------------------------------------"
        
        # Show last few lines from logs
        if [ -f "logs/atom_bot.log" ]; then
            echo -e "${PURPLE}🔁 ATOM/ADOM Bot (last 3 lines):${NC}"
            tail -n 3 logs/atom_bot.log | sed 's/^/   /'
            echo ""
        fi
        
        if [ -f "logs/spectre.log" ]; then
            echo -e "${CYAN}⚙️ SPECTRE Analytics (last 3 lines):${NC}"
            tail -n 3 logs/spectre.log | sed 's/^/   /'
            echo ""
        fi
        
        echo "============================================================"
        echo -e "${GREEN}🎯 AEON Network is operational!${NC}"
        echo -e "${BLUE}Press Ctrl+C to stop monitoring${NC}"
        echo ""
        
        sleep 10
    done
}

# Stop all systems
stop_systems() {
    echo -e "\n${YELLOW}🛑 Stopping AEON Network...${NC}"
    
    # Stop ATOM bot
    if [ -f "logs/atom_bot.pid" ]; then
        ATOM_PID=$(cat logs/atom_bot.pid)
        if ps -p $ATOM_PID > /dev/null; then
            kill $ATOM_PID
            echo -e "${GREEN}✅ ATOM/ADOM bot stopped${NC}"
        fi
        rm -f logs/atom_bot.pid
    fi
    
    # Stop SPECTRE analytics
    if [ -f "logs/spectre.pid" ]; then
        SPECTRE_PID=$(cat logs/spectre.pid)
        if ps -p $SPECTRE_PID > /dev/null; then
            kill $SPECTRE_PID
            echo -e "${GREEN}✅ SPECTRE analytics stopped${NC}"
        fi
        rm -f logs/spectre.pid
    fi
    
    # Stop frontend
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null; then
            kill $FRONTEND_PID
            echo -e "${GREEN}✅ Frontend stopped${NC}"
        fi
        rm -f logs/frontend.pid
    fi
    
    echo -e "${GREEN}🛑 AEON Network stopped${NC}"
}

# Trap Ctrl+C to stop systems gracefully
trap stop_systems INT

# Main deployment function
main() {
    echo -e "${GREEN}🚀 Starting AEON Network deployment...${NC}"
    
    # Setup
    check_env
    setup_logging
    
    # Deploy all systems
    deploy_contracts
    start_atom_bot
    start_spectre_analytics
    start_frontend
    
    echo -e "\n${GREEN}🎉 AEON NETWORK DEPLOYMENT COMPLETE!${NC}"
    echo "============================================================"
    echo -e "${GREEN}🧠 AEON (On-chain): Smart contracts deployed to Base Sepolia${NC}"
    echo -e "${PURPLE}🔁 ATOM/ADOM (Hybrid): Bot monitoring and executing trades${NC}"
    echo -e "${CYAN}⚙️ SPECTRE (Analytics): Continuous market analysis running${NC}"
    echo -e "${BLUE}🌐 Frontend: Dashboard available at http://localhost:3000${NC}"
    echo ""
    echo -e "${YELLOW}🎯 TARGET: $150K daily across all three systems${NC}"
    echo -e "${YELLOW}🔥 REDUNDANCY: If one fails, two remain. If one spikes, others learn.${NC}"
    echo ""
    echo -e "${GREEN}✨ This isn't just an arbitrage bot. This is AEON. ✨${NC}"
    echo ""
    
    # Start monitoring
    monitor_systems
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        stop_systems
        exit 0
        ;;
    "monitor")
        monitor_systems
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [stop|monitor]"
        echo "  stop    - Stop all AEON systems"
        echo "  monitor - Monitor running systems"
        echo "  (no args) - Deploy and start all systems"
        exit 1
        ;;
esac
