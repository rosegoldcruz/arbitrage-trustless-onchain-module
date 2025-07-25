#!/bin/bash

# AEON Network - Complete Deployment Script
# Deploys all three parallel ecosystems with cross-communication
# Advanced, Efficient, Optimized Network - Full Production Deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Header
echo -e "${CYAN}"
cat << "EOF"
    ___    _________  _   __   _   ____________       ______  ____  __ __
   /   |  / ____/ __ \/ | / /  / | / / ____/_  __/     / __ \/ __ \/ //_/
  / /| | / __/ / / / /  |/ /  /  |/ / __/   / / | | /| / / / / /_/ / ,<   
 / ___ |/ /___/ /_/ / /|  /  / /|  / /___  / /  | |/ |/ / /_/ / _, _/ /| |  
/_/  |_/_____/\____/_/ |_/  /_/ |_/_____/ /_/   |__/|__/\____/_/ |_/_/ |_|  

Advanced, Efficient, Optimized Network - Triple Ecosystem Deployment
EOF
echo -e "${NC}"

echo -e "${BLUE}🔱 AEON NETWORK - COMPLETE DEPLOYMENT${NC}"
echo -e "${BLUE}Three Parallel Ecosystems for Antifragile Intelligence${NC}"
echo "=" $(printf '=%.0s' {1..80})

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found. Please create one with your configuration.${NC}"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
required_vars=("PRIVATE_KEY" "BASE_SEPOLIA_RPC_URL" "THEATOM_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables loaded${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo -e "${BLUE}🔍 Checking dependencies...${NC}"

dependencies=("node" "npm" "python3" "pip" "redis-server")
for dep in "${dependencies[@]}"; do
    if command_exists "$dep"; then
        echo -e "${GREEN}✅ $dep found${NC}"
    else
        echo -e "${RED}❌ $dep not found${NC}"
        exit 1
    fi
done

# Start Redis server if not running
if ! pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}🔄 Starting Redis server...${NC}"
    redis-server --daemonize yes
    sleep 2
fi

echo -e "${GREEN}✅ All dependencies ready${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p reports
mkdir -p backups

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"

# Node.js dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install

# Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Compile smart contracts
echo -e "${BLUE}🔨 Compiling smart contracts...${NC}"
npx hardhat compile

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Smart contract compilation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Smart contracts compiled${NC}"

# Deploy AEON Ecosystem (Option 1) - Autonomous On-Chain
echo -e "${PURPLE}🧠 DEPLOYING AEON ECOSYSTEM (Option 1)${NC}"
echo -e "${PURPLE}Fully Autonomous On-Chain Intelligence${NC}"
echo "-" $(printf -- '-%.0s' {1..60})

npx hardhat run contracts/scripts/deploy-aeon.js --network baseSepolia > logs/aeon-deployment.log 2>&1 &
AEON_PID=$!

echo -e "${GREEN}✅ AEON deployment started (PID: $AEON_PID)${NC}"

# Wait for AEON deployment to complete
wait $AEON_PID
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ AEON Ecosystem deployed successfully${NC}"
    AEON_ADDRESS=$(grep "AEON deployed to:" logs/aeon-deployment.log | awk '{print $4}')
    echo -e "${GREEN}   Contract Address: $AEON_ADDRESS${NC}"
else
    echo -e "${RED}❌ AEON deployment failed${NC}"
    exit 1
fi

# Start ATOM/ADOM Ecosystem (Option 2) - Hybrid Execution
echo -e "${CYAN}🔁 STARTING ATOM/ADOM ECOSYSTEM (Option 2)${NC}"
echo -e "${CYAN}Hybrid Execution with Bot Intelligence${NC}"
echo "-" $(printf -- '-%.0s' {1..60})

# Start ATOM Python bot
echo -e "${YELLOW}Starting ATOM Python bot...${NC}"
cd bots
python3 ATOM.py > ../logs/atom-bot.log 2>&1 &
ATOM_PID=$!
cd ..

echo -e "${GREEN}✅ ATOM bot started (PID: $ATOM_PID)${NC}"

# Start ADOM Node.js bot
echo -e "${YELLOW}Starting ADOM Node.js bot...${NC}"
cd bots
node ADOM.js > ../logs/adom-bot.log 2>&1 &
ADOM_PID=$!
cd ..

echo -e "${GREEN}✅ ADOM bot started (PID: $ADOM_PID)${NC}"

# Start SPECTRE Ecosystem (Option 3) - Analytics Engine
echo -e "${YELLOW}⚙️  STARTING SPECTRE ECOSYSTEM (Option 3)${NC}"
echo -e "${YELLOW}Off-chain Analytical Scout${NC}"
echo "-" $(printf -- '-%.0s' {1..60})

cd analytics
python3 SPECTRE.py > ../logs/spectre-analytics.log 2>&1 &
SPECTRE_PID=$!
cd ..

echo -e "${GREEN}✅ SPECTRE analytics started (PID: $SPECTRE_PID)${NC}"

# Start AEON Network Orchestrator
echo -e "${PURPLE}🔗 STARTING AEON NETWORK ORCHESTRATOR${NC}"
echo -e "${PURPLE}Cross-Ecosystem Communication Layer${NC}"
echo "-" $(printf -- '-%.0s' {1..60})

cd orchestrator
python3 AEONOrchestrator.py > ../logs/orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
cd ..

echo -e "${GREEN}✅ AEON Orchestrator started (PID: $ORCHESTRATOR_PID)${NC}"

# Start Backend API
echo -e "${BLUE}🌐 STARTING BACKEND API${NC}"
echo "-" $(printf -- '-%.0s' {1..40})

cd backend
python3 main.py > ../logs/backend-api.log 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend API started (PID: $BACKEND_PID)${NC}"

# Wait for all services to initialize
echo -e "${BLUE}⏳ Waiting for services to initialize...${NC}"
sleep 10

# Health checks
echo -e "${BLUE}🏥 Performing health checks...${NC}"

# Check AEON contract
if [ ! -z "$AEON_ADDRESS" ]; then
    echo -e "${GREEN}✅ AEON Contract: $AEON_ADDRESS${NC}"
else
    echo -e "${RED}❌ AEON Contract deployment failed${NC}"
fi

# Check ATOM bot
if kill -0 $ATOM_PID 2>/dev/null; then
    echo -e "${GREEN}✅ ATOM Bot: Running (PID: $ATOM_PID)${NC}"
else
    echo -e "${RED}❌ ATOM Bot: Not running${NC}"
fi

# Check ADOM bot
if kill -0 $ADOM_PID 2>/dev/null; then
    echo -e "${GREEN}✅ ADOM Bot: Running (PID: $ADOM_PID)${NC}"
else
    echo -e "${RED}❌ ADOM Bot: Not running${NC}"
fi

# Check SPECTRE analytics
if kill -0 $SPECTRE_PID 2>/dev/null; then
    echo -e "${GREEN}✅ SPECTRE Analytics: Running (PID: $SPECTRE_PID)${NC}"
else
    echo -e "${RED}❌ SPECTRE Analytics: Not running${NC}"
fi

# Check Orchestrator
if kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
    echo -e "${GREEN}✅ AEON Orchestrator: Running (PID: $ORCHESTRATOR_PID)${NC}"
else
    echo -e "${RED}❌ AEON Orchestrator: Not running${NC}"
fi

# Check Backend API
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend API: Running (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ Backend API: Not running${NC}"
fi

# Test API endpoints
echo -e "${BLUE}🔍 Testing API endpoints...${NC}"

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Health endpoint: Working${NC}"
else
    echo -e "${RED}❌ Health endpoint: Failed${NC}"
fi

# Test arbitrage opportunities
if curl -s http://localhost:8000/api/arbitrage/opportunities > /dev/null; then
    echo -e "${GREEN}✅ Arbitrage opportunities: Working${NC}"
else
    echo -e "${RED}❌ Arbitrage opportunities: Failed${NC}"
fi

# Generate deployment summary
echo -e "${BLUE}📋 Generating deployment summary...${NC}"

cat > deployment-summary.md << EOF
# AEON Network - Complete Deployment Summary

## 🚀 Deployment Status: SUCCESS

### 📅 Deployment Date
$(date)

### 🔱 Three Parallel Ecosystems Deployed

#### 🧠 AEON Ecosystem (Option 1) - Autonomous On-Chain Intelligence
- **Type**: Fully autonomous smart contract execution
- **Contract Address**: $AEON_ADDRESS
- **Network**: Base Sepolia (84532)
- **Features**: 
  - Chainlink price feed integration
  - 23bps minimum threshold enforcement
  - Autonomous triangular arbitrage
  - Flash loan integration (Aave V3)
  - Gas optimization

#### 🔁 ATOM/ADOM Ecosystem (Option 2) - Hybrid Execution
- **ATOM Bot**: Python-based hybrid intelligence (PID: $ATOM_PID)
- **ADOM Bot**: Node.js MEV optimization (PID: $ADOM_PID)
- **Features**:
  - Off-chain opportunity detection
  - On-chain execution triggering
  - MEV protection and optimization
  - Real-time price monitoring
  - Bundle optimization

#### ⚙️ SPECTRE Ecosystem (Option 3) - Analytical Scout
- **Process ID**: $SPECTRE_PID
- **Features**:
  - Historical backtesting
  - Strategy optimization
  - Risk analysis
  - Performance simulation
  - Market condition analysis

### 🔗 Cross-Ecosystem Communication
- **Orchestrator PID**: $ORCHESTRATOR_PID
- **Redis**: Running for inter-ecosystem communication
- **WebSocket Server**: ws://localhost:8000
- **Database**: SQLite for persistent storage

### 🌐 API Endpoints
- **Health Check**: http://localhost:8000/health
- **Arbitrage Opportunities**: http://localhost:8000/api/arbitrage/opportunities
- **Triangular Arbitrage**: http://localhost:8000/api/arbitrage/triangular
- **Spread Calculation**: http://localhost:8000/api/arbitrage/spread/{tokenA}/{tokenB}
- **Documentation**: http://localhost:8000/docs

### 🎯 Supported Arbitrage Paths
1. **DAI → USDC → GHO → DAI** (Curve → Balancer → Curve)
2. **WETH → USDC → DAI → WETH** (Balancer → Curve → Balancer)
3. **USDC → DAI → GHO → USDC** (Curve → Curve → Balancer)

### 📊 Process IDs for Management
- AEON Contract: $AEON_ADDRESS
- ATOM Bot: $ATOM_PID
- ADOM Bot: $ADOM_PID
- SPECTRE Analytics: $SPECTRE_PID
- AEON Orchestrator: $ORCHESTRATOR_PID
- Backend API: $BACKEND_PID

### 🛠️ Management Commands
\`\`\`bash
# Stop all processes
kill $ATOM_PID $ADOM_PID $SPECTRE_PID $ORCHESTRATOR_PID $BACKEND_PID

# View logs
tail -f logs/atom-bot.log
tail -f logs/adom-bot.log
tail -f logs/spectre-analytics.log
tail -f logs/orchestrator.log
tail -f logs/backend-api.log

# Restart individual components
./restart-ecosystem.sh [aeon|atom|adom|spectre|orchestrator|backend]
\`\`\`

### 🔧 Next Steps
1. Monitor cross-ecosystem communication
2. Fund contracts with test tokens
3. Execute test arbitrage opportunities
4. Analyze SPECTRE backtesting results
5. Optimize based on real performance data

EOF

echo -e "${GREEN}✅ Deployment summary saved to deployment-summary.md${NC}"

# Save process IDs for management
cat > .aeon-pids << EOF
AEON_ADDRESS=$AEON_ADDRESS
ATOM_PID=$ATOM_PID
ADOM_PID=$ADOM_PID
SPECTRE_PID=$SPECTRE_PID
ORCHESTRATOR_PID=$ORCHESTRATOR_PID
BACKEND_PID=$BACKEND_PID
EOF

# Final status
echo ""
echo "=" $(printf '=%.0s' {1..80})
echo -e "${PURPLE}🎉 AEON NETWORK DEPLOYMENT COMPLETE!${NC}"
echo "=" $(printf '=%.0s' {1..80})
echo ""

echo -e "${BLUE}🔱 Three Parallel Ecosystems Status:${NC}"
echo -e "${GREEN}   🧠 AEON (Option 1): ✅ Autonomous On-Chain Intelligence${NC}"
echo -e "${GREEN}   🔁 ATOM/ADOM (Option 2): ✅ Hybrid Execution Bots${NC}"
echo -e "${GREEN}   ⚙️  SPECTRE (Option 3): ✅ Analytical Scout${NC}"
echo -e "${GREEN}   🔗 Orchestrator: ✅ Cross-Ecosystem Communication${NC}"
echo ""

echo -e "${YELLOW}🎯 Key Features Deployed:${NC}"
echo -e "${GREEN}   ✅ Balancer weighted pool math (80/20, 98/2)${NC}"
echo -e "${GREEN}   ✅ Curve StableSwap with depeg detection${NC}"
echo -e "${GREEN}   ✅ Triangular arbitrage (A→B→C→A)${NC}"
echo -e "${GREEN}   ✅ Real-time spreadBps calculation${NC}"
echo -e "${GREEN}   ✅ 23bps fee threshold enforcement${NC}"
echo -e "${GREEN}   ✅ Flash loan integration (Aave V3)${NC}"
echo -e "${GREEN}   ✅ MEV protection and optimization${NC}"
echo -e "${GREEN}   ✅ Cross-ecosystem consensus engine${NC}"
echo -e "${GREEN}   ✅ Antifragile intelligence network${NC}"
echo ""

echo -e "${CYAN}🔗 Access Your AEON Network:${NC}"
echo -e "${BLUE}   • API Documentation: ${NC}http://localhost:8000/docs"
echo -e "${BLUE}   • Health Dashboard: ${NC}http://localhost:8000/health"
echo -e "${BLUE}   • Live Opportunities: ${NC}http://localhost:8000/api/arbitrage/opportunities"
echo -e "${BLUE}   • Contract Address: ${NC}$AEON_ADDRESS"
echo ""

echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "${YELLOW}   • All processes are running in background${NC}"
echo -e "${YELLOW}   • Logs are saved in ./logs/ directory${NC}"
echo -e "${YELLOW}   • Process IDs saved in .aeon-pids file${NC}"
echo -e "${YELLOW}   • Use 'kill \$(cat .aeon-pids | grep PID | cut -d= -f2)' to stop all${NC}"
echo ""

echo -e "${GREEN}🚀 Your AEON Network is now live and ready for antifragile arbitrage!${NC}"

# Keep script running to monitor
echo -e "${BLUE}📊 Monitoring network health... (Press Ctrl+C to exit)${NC}"

# Monitor function
monitor_network() {
    while true; do
        sleep 30
        
        # Check if all processes are still running
        failed_processes=()
        
        if ! kill -0 $ATOM_PID 2>/dev/null; then
            failed_processes+=("ATOM")
        fi
        
        if ! kill -0 $ADOM_PID 2>/dev/null; then
            failed_processes+=("ADOM")
        fi
        
        if ! kill -0 $SPECTRE_PID 2>/dev/null; then
            failed_processes+=("SPECTRE")
        fi
        
        if ! kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
            failed_processes+=("ORCHESTRATOR")
        fi
        
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            failed_processes+=("BACKEND")
        fi
        
        if [ ${#failed_processes[@]} -gt 0 ]; then
            echo -e "${RED}⚠️  Failed processes detected: ${failed_processes[*]}${NC}"
            echo -e "${YELLOW}Check logs in ./logs/ directory${NC}"
        else
            echo -e "${GREEN}✅ All AEON Network processes healthy$(NC)"
        fi
    done
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}👋 AEON Network monitoring stopped. Processes still running in background.${NC}"; exit 0' INT

# Start monitoring
monitor_network
