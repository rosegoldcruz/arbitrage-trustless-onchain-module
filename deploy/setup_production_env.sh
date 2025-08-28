#!/bin/bash
set -euo pipefail

# ENV Promotion + Systemd Wiring (Production Only)
echo "🚀 Setting up ATOM Backend API for production..."

PROJECT=/srv/atom/backend-api
SRC=$PROJECT/.env.production
DEST=/etc/atom/backend-api.env

# Check if source exists
if [[ ! -f "$SRC" ]]; then
    echo "❌ Missing $SRC"
    echo "Please ensure .env.production exists in the project root"
    exit 1
fi

# 1) Promote .env.production to /etc/atom/backend-api.env
echo "📁 Creating /etc/atom directory..."
sudo mkdir -p /etc/atom

echo "📋 Installing environment file..."
sudo install -m 0600 -o root -g root "$SRC" "$DEST"
sudo chown root:root "$DEST"
sudo chmod 600 "$DEST"

echo "🔍 Verifying environment file..."
diff -u "$SRC" "$DEST" || true

# 2) Install systemd service
echo "⚙️ Installing systemd service..."
sudo cp /srv/atom/deploy/systemd/atom-api.service /etc/systemd/system/
sudo systemctl daemon-reload

# 3) Create atom user if doesn't exist
if ! id "atom" &>/dev/null; then
    echo "👤 Creating atom user..."
    sudo useradd -r -s /bin/false -d /srv/atom atom
fi

# 4) Set permissions
echo "🔐 Setting permissions..."
sudo chown -R atom:atom /srv/atom/backend-api
sudo chmod +x /srv/atom/backend-api/scripts/verify_env.py

# 5) Enable and start service
echo "🎯 Enabling and starting service..."
sudo systemctl enable atom-api
sudo systemctl start atom-api

# 6) Check status
echo "📊 Service status:"
sudo systemctl status atom-api --no-pager

# 7) Verify environment
echo "🧪 Verifying environment..."
sudo /usr/bin/env -i $(cat /etc/atom/backend-api.env | xargs) python3 /srv/atom/backend-api/scripts/verify_env.py

# 8) Show recent logs
echo "📝 Recent logs:"
journalctl -u atom-api -n 20 --no-pager

echo "✅ ATOM Backend API setup complete!"
echo ""
echo "Commands for monitoring:"
echo "  sudo systemctl status atom-api"
echo "  journalctl -u atom-api -f"
echo "  curl -fsS http://127.0.0.1:8000/health"