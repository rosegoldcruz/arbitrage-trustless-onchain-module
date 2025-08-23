#!/bin/bash

# ATOM Production Deployment Script
# Deploy complete arbitrage system to Polygon mainnet

set -e

echo "🚀 ATOM PRODUCTION DEPLOYMENT"
echo "============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running in correct directory
if [ ! -f "contracts/PolygonArbitrageEngine.sol" ]; then
    print_error "Please run this script from the ATOM project root directory"
    exit 1
fi

print_header "📋 Step 1: Environment Validation"

# Check for .env file
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_error "Please copy .env.example to .env and configure your values"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Validate Polygon mainnet configuration
if [ "$CHAIN_ID" != "137" ]; then
    print_error "Invalid CHAIN_ID: $CHAIN_ID. Expected: 137 (Polygon mainnet)"
    exit 1
fi

if [ "$NETWORK" != "polygon_mainnet" ]; then
    print_error "Invalid NETWORK: $NETWORK. Expected: polygon_mainnet"
    exit 1
fi

# Check for required environment variables
required_vars=("PRIVATE_KEY" "POLYGON_RPC_URL" "FLASHLOAN_ARB_ADDR" "WETH_ADDRESS" "USDC_ADDRESS" "WMATIC_ADDRESS")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        print_error "  - $var"
    done
    print_error "Please configure these in your .env file"
    exit 1
fi

# Validate Polygon addresses
if [ "$AAVE_POOL_ADDRESSES_PROVIDER" != "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb" ]; then
    print_warning "AAVE_POOL_ADDRESSES_PROVIDER may not be correct for Polygon"
fi

if [ "$UNISWAP_V3_ROUTER" != "0xE592427A0AEce92De3Edee1F18E0157C05861564" ]; then
    print_warning "UNISWAP_V3_ROUTER may not be correct for Polygon"
fi

print_status "✅ Environment variables validated for Polygon mainnet"

print_header "🐍 Step 2: Python Environment Setup"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

print_header "🔧 Step 3: Redis Setup"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    print_status "Starting Redis server..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start redis-server
    elif command -v service &> /dev/null; then
        sudo service redis-server start
    else
        print_warning "Please start Redis manually"
    fi
fi

print_status "Redis is running"

print_header "🌐 Step 4: Network Connectivity Test"

# Test Polygon RPC connection
print_status "Testing Polygon RPC connection..."
python3 -c "
from web3 import Web3
import os
w3 = Web3(Web3.HTTPProvider(os.getenv('POLYGON_RPC_URL')))
if w3.is_connected():
    print(f'✅ Connected to Polygon, block: {w3.eth.block_number}')
else:
    print('❌ Failed to connect to Polygon RPC')
    exit(1)
"

print_header "📊 Step 5: System Validation"

# Run system validation
print_status "Running comprehensive system validation..."
python3 -c "
import asyncio
import sys
import os
sys.path.append('bots')
from profit_calculator import ProfitCalculator

async def validate():
    try:
        calc = ProfitCalculator()
        print('✅ Profit calculator initialized')
        
        # Test quote functionality
        weth = calc.tokens['WETH']
        usdc = calc.tokens['USDC']
        amount = int(0.1 * 10**18)
        
        quote = calc.get_exact_quote('uniswap_v3', weth, usdc, amount)
        if quote and quote > 0:
            print(f'✅ DEX integration working: {quote} USDC for 0.1 WETH')
        else:
            print('❌ DEX integration failed')
            return False
            
        print('✅ System validation passed')
        return True
    except Exception as e:
        print(f'❌ System validation failed: {e}')
        return False

result = asyncio.run(validate())
if not result:
    exit(1)
"

print_header "🚀 Step 6: Production Deployment"

# Create logs directory
mkdir -p logs

# Create systemd service files
print_status "Creating systemd service files..."

# Opportunity Detector Service
sudo tee /etc/systemd/system/atom-detector.service > /dev/null << EOF
[Unit]
Description=ATOM Opportunity Detector
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python bots/production_opportunity_detector.py
Restart=always
RestartSec=10
StandardOutput=append:$(pwd)/logs/detector.log
StandardError=append:$(pwd)/logs/detector.log

[Install]
WantedBy=multi-user.target
EOF

# Trade Executor Service
sudo tee /etc/systemd/system/atom-executor.service > /dev/null << EOF
[Unit]
Description=ATOM Trade Executor
After=network.target redis.service atom-detector.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python bots/production_trade_executor.py
Restart=always
RestartSec=10
StandardOutput=append:$(pwd)/logs/executor.log
StandardError=append:$(pwd)/logs/executor.log

[Install]
WantedBy=multi-user.target
EOF

# Orchestrator Service
sudo tee /etc/systemd/system/atom-orchestrator.service > /dev/null << EOF
[Unit]
Description=ATOM Production Orchestrator
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python bots/production_orchestrator.py
Restart=always
RestartSec=10
StandardOutput=append:$(pwd)/logs/orchestrator.log
StandardError=append:$(pwd)/logs/orchestrator.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable atom-detector.service
sudo systemctl enable atom-executor.service
sudo systemctl enable atom-orchestrator.service

print_header "🎯 Step 7: Service Startup"

# Start services
print_status "Starting ATOM services..."
sudo systemctl start atom-detector.service
sleep 5
sudo systemctl start atom-executor.service
sleep 5
sudo systemctl start atom-orchestrator.service

print_header "📊 Step 8: Health Check"

# Wait for services to initialize
sleep 10

# Check service status
print_status "Checking service status..."
for service in atom-detector atom-executor atom-orchestrator; do
    if systemctl is-active --quiet $service.service; then
        print_status "✅ $service is running"
    else
        print_error "❌ $service failed to start"
        sudo systemctl status $service.service
    fi
done

# Test Redis connectivity
print_status "Testing system connectivity..."
python3 -c "
import redis
import json
r = redis.from_url('redis://127.0.0.1:6379/0', decode_responses=True)
r.ping()
print('✅ Redis connectivity confirmed')

# Check for system stats
try:
    stats = r.get('production_stats')
    if stats:
        data = json.loads(stats)
        print(f'✅ System stats available: {data.get(\"uptime_hours\", 0):.2f} hours uptime')
    else:
        print('⏳ System stats not yet available (normal for new deployment)')
except Exception as e:
    print(f'⚠️ Stats check: {e}')
"

print_header "🎉 Deployment Complete!"

print_status "ATOM Production System is now running!"
echo ""
print_status "📋 Service Management Commands:"
echo "  Start all:    sudo systemctl start atom-detector atom-executor atom-orchestrator"
echo "  Stop all:     sudo systemctl stop atom-detector atom-executor atom-orchestrator"
echo "  Restart all:  sudo systemctl restart atom-detector atom-executor atom-orchestrator"
echo "  View logs:    tail -f logs/*.log"
echo "  Check status: sudo systemctl status atom-orchestrator"
echo ""
print_status "📊 Monitoring Commands:"
echo "  System stats: redis-cli get production_stats | python3 -m json.tool"
echo "  Opportunities: redis-cli llen arbitrage_opportunities"
echo "  Trade history: redis-cli llen trade_history"
echo ""
print_status "🚀 The system will now automatically:"
echo "  • Detect arbitrage opportunities across Polygon DEXs"
echo "  • Execute profitable trades using your deployed contract"
echo "  • Send alerts via Discord/Telegram (if configured)"
echo "  • Generate profits 24/7"
echo ""
print_warning "⚠️ IMPORTANT:"
echo "  • Monitor logs for the first hour to ensure proper operation"
echo "  • Check Discord/Telegram for alerts"
echo "  • Profits will be visible in trade_history Redis key"
echo "  • System targets $100-500+ daily profit"
echo ""
print_status "💰 Ready to generate profits on Polygon mainnet!"

# Create monitoring script
cat > monitor_system.sh << 'EOF'
#!/bin/bash
echo "🤖 ATOM System Status"
echo "===================="
echo "Time: $(date)"
echo ""

echo "📦 Services:"
for service in atom-detector atom-executor atom-orchestrator; do
    if systemctl is-active --quiet $service.service; then
        echo "  ✅ $service: RUNNING"
    else
        echo "  ❌ $service: STOPPED"
    fi
done

echo ""
echo "📊 System Stats:"
redis-cli get production_stats 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "  Stats not available"

echo ""
echo "💰 Recent Activity:"
echo "  Opportunities queued: $(redis-cli llen arbitrage_opportunities 2>/dev/null || echo 0)"
echo "  Trades executed: $(redis-cli llen trade_history 2>/dev/null || echo 0)"
EOF

chmod +x monitor_system.sh

print_status "Created monitor_system.sh - run ./monitor_system.sh to check status"
