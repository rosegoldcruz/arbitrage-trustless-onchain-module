# 🚀 DigitalOcean Droplet Setup & Backend Authentication Guide

## 🔐 Step 1: Access Your Droplet

### Option A: SSH with Password (if you have it)
```bash
ssh root@your-droplet-ip-address
# Enter your root password when prompted
```

### Option B: SSH with SSH Key (recommended)
```bash
ssh -i ~/.ssh/your-private-key root@your-droplet-ip-address
```

### Option C: DigitalOcean Console (if SSH fails)
1. Go to https://cloud.digitalocean.com/
2. Navigate to Droplets → Your Droplet
3. Click "Console" to open web-based terminal

---

## 📋 Step 2: Find Your Droplet IP Address

If you don't know your droplet IP:
1. Go to https://cloud.digitalocean.com/droplets
2. Your droplet IP will be listed next to your droplet name
3. Copy the public IP address

---

## 🛠 Step 3: Initial Droplet Setup

Once you're logged into your droplet:

```bash
# Update system packages
apt update && apt upgrade -y

# Install essential tools
apt install -y git curl wget nano htop

# Install Node.js (for deployment scripts)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

# Install Python 3 and pip (if not already installed)
apt install -y python3 python3-pip python3-venv

# Install PM2 for process management
npm install -g pm2

# Check installations
node --version
python3 --version
pm2 --version
```

---

## 📁 Step 4: Clone Your Repository

```bash
# Navigate to web directory
cd /var/www

# Clone your ATOM repository
git clone https://github.com/rosegoldcruz/arbitrage-trustless-onchain-module.git
cd arbitrage-trustless-onchain-module

# Or if already cloned, pull latest changes
git pull origin main
```

---

## 🔐 Step 5: Set Up Environment Variables

Create the production environment file:

```bash
# Create .env.local file
nano .env.local
```

Add your production configuration:
```bash
# 🔒 CLERK AUTHENTICATION (PRODUCTION)
CLERK_SECRET_KEY=sk_test_nWN6IKQiD15R9ZVrfGwUSuTlCREBAvJjvaMiDMcmBm
CLERK_PUBLISHABLE_KEY=pk_test_aW5mb3JtZWQtcGVhY29jay0yNS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_ISSUER_URL=https://informed-peacock-25.clerk.accounts.dev
CLERK_JWKS_URL=https://informed-peacock-25.clerk.accounts.dev/.well-known/jwks.json

# 🌐 BASE SEPOLIA CONFIGURATION
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASESCAN_API_KEY=your_basescan_api_key_here
PRIVATE_KEY=your_wallet_private_key_here

# 🔗 API KEYS
THEATOM_API_KEY=your_0x_api_key_here
ZRX_API_URL=https://api.0x.org

# 📊 SUPABASE
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# 🎯 PRODUCTION ENDPOINTS
NEXT_PUBLIC_API_URL=https://api.aeoninvestmentstechnologies.com
NEXT_PUBLIC_BACKEND_URL=https://api.aeoninvestmentstechnologies.com
API_URL=https://api.aeoninvestmentstechnologies.com

# 📱 FRONTEND
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_aW5mb3JtZWQtcGVhY29jay0yNS5jbGVyay5hY2NvdW50cy5kZXYk
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## 🐍 Step 6: Set Up Python Backend

```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install additional JWT libraries for Clerk authentication
pip install PyJWT[crypto]>=2.8.0 cryptography>=41.0.7 jwcrypto>=1.5.0

# Test backend can start
cd backend
python main.py
```

If successful, you should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

Press `Ctrl+C` to stop the test.

---

## 🚀 Step 7: Deploy Backend with PM2

```bash
# Create PM2 ecosystem file
nano ecosystem.config.js
```

Add this configuration:
```javascript
module.exports = {
  apps: [{
    name: 'atom-backend',
    script: 'python',
    args: 'backend/main.py',
    cwd: '/var/www/arbitrage-trustless-onchain-module',
    interpreter: '/var/www/arbitrage-trustless-onchain-module/venv/bin/python',
    env: {
      NODE_ENV: 'production',
      PORT: 8000
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
```

```bash
# Create logs directory
mkdir -p logs

# Start backend with PM2
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs atom-backend

# Save PM2 configuration
pm2 save
pm2 startup
```

---

## 🔥 Step 8: Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8000

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

## 🌐 Step 9: Set Up Nginx (Optional - for production)

```bash
# Install Nginx
apt install -y nginx

# Create Nginx configuration
nano /etc/nginx/sites-available/atom-api
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name api.aeoninvestmentstechnologies.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable the site
ln -s /etc/nginx/sites-available/atom-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

## 🧪 Step 10: Test Authentication

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with authentication (should fail without JWT)
curl -X POST http://localhost:8000/trigger \
  -H "Content-Type: application/json" \
  -d '{"mode": "manual", "strategy": "atom"}'
```

You should get a 401 Unauthorized response, confirming authentication is working.

---

## 📊 Step 11: Monitor Your Backend

```bash
# Check PM2 status
pm2 status

# View real-time logs
pm2 logs atom-backend --lines 50

# Monitor system resources
htop

# Check if backend is responding
curl http://localhost:8000/health
```

---

## 🔧 Troubleshooting

### If you can't SSH:
1. Check your droplet is running in DigitalOcean dashboard
2. Use the web console from DigitalOcean dashboard
3. Reset root password if needed

### If backend won't start:
```bash
# Check Python path
which python3

# Check if port 8000 is in use
netstat -tlnp | grep :8000

# Check logs
pm2 logs atom-backend
```

### If authentication fails:
```bash
# Verify environment variables are loaded
cd /var/www/arbitrage-trustless-onchain-module
source venv/bin/activate
python -c "import os; print('CLERK_SECRET_KEY:', os.getenv('CLERK_SECRET_KEY')[:20] + '...')"
```

---

## ✅ Success Checklist

- [ ] SSH access to droplet established
- [ ] Repository cloned and updated
- [ ] Environment variables configured
- [ ] Python dependencies installed
- [ ] Backend starts successfully with PM2
- [ ] Health endpoint responds
- [ ] Authentication returns 401 for unauthorized requests
- [ ] Firewall configured
- [ ] Monitoring set up

**Your backend is now running with enterprise Clerk JWT authentication!** 🔒🚀
