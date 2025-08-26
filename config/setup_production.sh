#!/bin/bash

# ATOM Arbitrage System - Production Deployment Script
# Run this on your DigitalOcean droplet to set up the complete system

set -e  # Exit on any error

echo "🚀 ATOM Arbitrage System - Production Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

print_header "📋 Step 1: System Updates and Dependencies"
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_status "Installing required packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    redis-server \
    git \
    curl \
    wget \
    htop \
    screen \
    ufw \
    fail2ban

print_header "🐳 Step 2: Docker Installation"
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
fi

if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose already installed"
fi

print_header "🔧 Step 3: Project Setup"
PROJECT_DIR="$HOME/atom-arbitrage"

if [ ! -d "$PROJECT_DIR" ]; then
    print_status "Creating project directory..."
    mkdir -p $PROJECT_DIR
fi

cd $PROJECT_DIR

print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
cat > requirements.txt << EOF
web3==6.11.0
eth-account==0.9.0
redis==5.0.0
aiohttp==3.8.5
websockets==11.0.2
asyncio-mqtt==0.13.0
python-dotenv==1.0.0
requests==2.31.0
pandas==2.1.0
numpy==1.24.3
python-telegram-bot==20.5
discord-webhook==1.3.0
EOF

pip install -r requirements.txt

print_header "⚙️ Step 4: Redis Configuration"
print_status "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure Redis for production
sudo tee /etc/redis/redis.conf > /dev/null << EOF
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 300
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF

sudo systemctl restart redis-server

print_header "🔥 Step 5: Firewall Configuration"
print_status "Configuring UFW firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

print_header "🛡️ Step 6: Security Hardening"
print_status "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create fail2ban jail for SSH
sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

sudo systemctl restart fail2ban

print_header "📁 Step 7: Directory Structure"
print_status "Creating directory structure..."
mkdir -p {bots,contracts,logs,backups,config}

print_header "🔐 Step 8: Environment Configuration"
print_status "Creating environment file..."

# Check if .env already exists
if [ -f ".env" ]; then
    print_warning "Environment file already exists. Creating backup..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Create production environment file
cat > .env << EOF
# Polygon Mainnet Production Configuration
NETWORK=polygon_mainnet
CHAIN_ID=137
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGON_RPC_BACKUP=https://rpc-mainnet.matic.network

# Flash Loan Contract (Load from environment)
FLASH_LOAN_CONTRACT=${ATOM_CONTRACT_ADDRESS}

# Trading Parameters
ALLOW_MAINNET=true
DRY_RUN=false
ATOM_MIN_PROFIT_THRESHOLD_BPS=23
ATOM_MAX_GAS_PRICE=100
MAX_SLIPPAGE_BPS=300
MIN_TRADE_AMOUNT_USD=10
MAX_TRADE_AMOUNT_USD=50000

# Gas Optimization
GAS_PRICE_MULTIPLIER=1.1
MAX_GAS_LIMIT=500000

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/0

# Profit Targets
DAILY_PROFIT_TARGET_USD=500
WEEKLY_PROFIT_TARGET_USD=3500

# Risk Management
MAX_DAILY_LOSS_USD=200
MAX_SINGLE_TRADE_LOSS_USD=50

# System Configuration
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL_SECONDS=30
OPPORTUNITY_SCAN_INTERVAL_MS=1000

# IMPORTANT: You MUST update these with your actual values:
# WALLET_PRIVATE_KEY_1=YOUR_MAIN_WALLET_PRIVATE_KEY_HERE
# WALLET_PRIVATE_KEY_2=YOUR_ROTATION_WALLET_2_PRIVATE_KEY_HERE
# DISCORD_WEBHOOK_URL=YOUR_DISCORD_WEBHOOK_URL_HERE
# TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
# TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE
EOF

print_header "🐳 Step 9: Docker Configuration"
print_status "Creating Docker Compose configuration..."

cat > docker-compose.yml << EOF
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: atom-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  arbitrage-bot:
    build: .
    container_name: atom-arbitrage-bot
    restart: unless-stopped
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - REDIS_URL=redis://redis:6379/0
    command: python bots/arbitrage_orchestrator.py

volumes:
  redis_data:
EOF

cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run as non-root user
RUN useradd -m -u 1000 atom && chown -R atom:atom /app
USER atom

CMD ["python", "bots/arbitrage_orchestrator.py"]
EOF

print_header "📊 Step 10: Monitoring Setup"
print_status "Creating monitoring scripts..."

cat > monitor.sh << 'EOF'
#!/bin/bash
# System monitoring script

echo "🤖 ATOM Arbitrage System Status"
echo "==============================="
echo "Time: $(date)"
echo ""

# Check if containers are running
echo "📦 Docker Containers:"
docker-compose ps

echo ""
echo "💾 Redis Status:"
redis-cli ping

echo ""
echo "📊 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{print $5}')"

echo ""
echo "📈 Trading Stats:"
if redis-cli exists system_stats > /dev/null; then
    redis-cli get system_stats | python3 -m json.tool
else
    echo "No trading stats available yet"
fi
EOF

chmod +x monitor.sh

cat > start.sh << 'EOF'
#!/bin/bash
# Start the ATOM arbitrage system

echo "🚀 Starting ATOM Arbitrage System..."

# Check if .env file exists and has required variables
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your wallet private keys and API keys"
    exit 1
fi

# Check for required environment variables
if ! grep -q "WALLET_PRIVATE_KEY_1=" .env || grep -q "YOUR_MAIN_WALLET_PRIVATE_KEY_HERE" .env; then
    echo "❌ Error: Wallet private keys not configured!"
    echo "Please update .env file with your actual wallet private keys"
    exit 1
fi

# Start the system
docker-compose up -d

echo "✅ System started successfully!"
echo "Use './monitor.sh' to check status"
echo "Use 'docker-compose logs -f' to view logs"
EOF

chmod +x start.sh

cat > stop.sh << 'EOF'
#!/bin/bash
# Stop the ATOM arbitrage system

echo "🛑 Stopping ATOM Arbitrage System..."
docker-compose down

echo "✅ System stopped successfully!"
EOF

chmod +x stop.sh

print_header "📝 Step 11: Log Rotation Setup"
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/atom-arbitrage > /dev/null << EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USER $USER
}
EOF

print_header "⏰ Step 12: Cron Jobs Setup"
print_status "Setting up automated tasks..."
(crontab -l 2>/dev/null; echo "0 0 * * * $PROJECT_DIR/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * $PROJECT_DIR/health_check.sh") | crontab -

cat > backup.sh << 'EOF'
#!/bin/bash
# Daily backup script

BACKUP_DIR="$HOME/atom-arbitrage/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup Redis data
redis-cli save
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# Backup logs
tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz logs/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

cat > health_check.sh << 'EOF'
#!/bin/bash
# Health check script

cd $HOME/atom-arbitrage

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️ Containers not running, attempting restart..."
    docker-compose up -d
fi

# Check Redis connectivity
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️ Redis not responding, restarting..."
    sudo systemctl restart redis-server
fi
EOF

chmod +x health_check.sh

print_header "✅ Setup Complete!"
print_status "ATOM Arbitrage System has been installed successfully!"

echo ""
print_warning "🔐 IMPORTANT SECURITY STEPS:"
echo "1. Update .env file with your actual wallet private keys"
echo "2. Add your Discord webhook URL for alerts"
echo "3. Configure Telegram bot token and chat ID"
echo "4. Review firewall settings"
echo "5. Change default SSH port (recommended)"

echo ""
print_status "📋 Next Steps:"
echo "1. cd $PROJECT_DIR"
echo "2. Edit .env file with your configuration"
echo "3. Run './start.sh' to start the system"
echo "4. Use './monitor.sh' to check status"
echo "5. View logs with 'docker-compose logs -f'"

echo ""
print_status "🔧 Useful Commands:"
echo "Start system: ./start.sh"
echo "Stop system: ./stop.sh"
echo "Monitor: ./monitor.sh"
echo "View logs: docker-compose logs -f"
echo "Backup: ./backup.sh"

echo ""
print_header "🎉 Ready to Generate Profits!"
print_status "Your ATOM arbitrage system is ready to start making money!"

# Final security reminder
print_warning "⚠️  REMEMBER: Never share your private keys or commit them to version control!"
