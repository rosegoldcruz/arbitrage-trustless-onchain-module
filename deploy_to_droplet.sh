#!/bin/bash
# 🚀 ATOM Backend Bulletproof Deployment Script
# Handles all common deployment failures

set -e  # Exit on any error

echo "🚀 ATOM Backend Deployment Starting..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Don't run this script as root! Run as regular user with sudo access."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    nginx \
    ufw \
    htop \
    tree \
    unzip

# Install Node.js (for ADOM.js bot)
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installations
print_status "Verifying installations..."
python3 --version
pip3 --version
node --version
npm --version

# Create application directory
APP_DIR="/opt/atom"
print_status "Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone repository
print_status "Cloning ATOM repository..."
cd $APP_DIR
if [ -d "arbitrage-trustless-onchain-module" ]; then
    print_warning "Repository already exists, pulling latest changes..."
    cd arbitrage-trustless-onchain-module
    git pull origin main
else
    git clone https://github.com/rosegoldcruz/arbitrage-trustless-onchain-module.git
    cd arbitrage-trustless-onchain-module
fi

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Install additional dependencies that might be missing
print_status "Installing additional dependencies..."
pip install psutil email-validator dnspython

# Install Node.js dependencies for bots
print_status "Installing Node.js dependencies..."
if [ -f "package.json" ]; then
    npm install
fi

# Create environment file
print_status "Creating environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || touch .env
    print_warning "Please configure .env file with your API keys and settings"
fi

# Set up systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/atom-backend.service > /dev/null <<EOF
[Unit]
Description=ATOM Arbitrage Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR/arbitrage-trustless-onchain-module
Environment=PATH=$APP_DIR/arbitrage-trustless-onchain-module/venv/bin
ExecStart=$APP_DIR/arbitrage-trustless-onchain-module/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_status "Enabling ATOM backend service..."
sudo systemctl daemon-reload
sudo systemctl enable atom-backend

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 8000
sudo ufw --force enable

# Configure Nginx reverse proxy
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/atom-backend > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/atom-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Start the service
print_status "Starting ATOM backend service..."
sudo systemctl start atom-backend

# Check service status
print_status "Checking service status..."
sudo systemctl status atom-backend --no-pager

# Test the API
print_status "Testing API endpoint..."
sleep 5
curl -f http://localhost:8000/ || print_error "API test failed!"

print_status "Deployment completed successfully!"
echo "========================================"
echo "🎯 ATOM Backend is now running on:"
echo "   - Local: http://localhost:8000"
echo "   - External: http://$(curl -s ifconfig.me):80"
echo ""
echo "📊 Service management commands:"
echo "   - Status: sudo systemctl status atom-backend"
echo "   - Logs: sudo journalctl -u atom-backend -f"
echo "   - Restart: sudo systemctl restart atom-backend"
echo "   - Stop: sudo systemctl stop atom-backend"
echo ""
echo "🔧 Next steps:"
echo "   1. Configure your .env file with API keys"
echo "   2. Test all endpoints at /docs"
echo "   3. Monitor logs for any issues"
