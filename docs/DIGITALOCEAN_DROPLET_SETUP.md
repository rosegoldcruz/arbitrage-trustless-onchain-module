# 🚀 ATOM - DigitalOcean Droplet Complete Setup Guide

## 📋 Prerequisites
- DigitalOcean account with billing enabled
- SSH key pair generated locally
- Domain name (optional but recommended)

## 🖥️ Step 1: Create Droplet

### Droplet Configuration:
```bash
# Recommended Specs for ATOM Production
- OS: Ubuntu 22.04 LTS
- Plan: Basic ($24/month)
- CPU: 2 vCPUs
- Memory: 4 GB
- Storage: 80 GB SSD
- Bandwidth: 4 TB
- Region: Choose closest to your users
```

### Create via CLI (Optional):
```bash
# Install doctl
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz | tar -xzv
sudo mv doctl /usr/local/bin

# Authenticate
doctl auth init

# Create droplet
doctl compute droplet create atom-production \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys YOUR_SSH_KEY_ID
```

## 🔧 Step 2: Initial Server Setup

### Connect to Droplet:
```bash
ssh root@YOUR_DROPLET_IP
```

### Update System:
```bash
apt update && apt upgrade -y
apt install -y curl wget git htop nano ufw fail2ban
```

### Create Non-Root User:
```bash
adduser atom
usermod -aG sudo atom
rsync --archive --chown=atom:atom ~/.ssh /home/atom
```

### Configure Firewall:
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp  # FastAPI backend
ufw --force enable
```

## 🐍 Step 3: Install Python & Dependencies

### Install Python 3.11:
```bash
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 🟢 Step 4: Install Node.js & PM2

### Install Node.js 20:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt install -y nodejs
```

### Install PM2 Globally:
```bash
npm install -g pm2
pm2 startup
# Follow the instructions to enable PM2 on boot
```

## 🐳 Step 5: Install Docker (Optional)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker atom
systemctl enable docker
systemctl start docker
```

## 📁 Step 6: Deploy ATOM Backend

### Switch to atom user:
```bash
su - atom
```

### Clone Repository:
```bash
git clone https://github.com/rosegoldcruz/arbitrage-trustless-onchain-module.git
cd arbitrage-trustless-onchain-module
```

### Setup Backend Environment:
```bash
cd backend
cp .env.template .env
nano .env  # Fill in your actual values
```

### Install Python Dependencies:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Test Backend:
```bash
python main.py
# Should start on http://0.0.0.0:8000
```

## 🤖 Step 7: Setup ATOM Bots

### Install Bot Dependencies:
```bash
cd ../backend/bots
npm install
```

### Configure Bot Environment:
```bash
cp .env.example .env
nano .env  # Add your API keys and configuration
```

### Test Bots:
```bash
node working/atom.js
# Should connect and start monitoring
```

## 🔄 Step 8: Setup PM2 Process Management

### Create PM2 Ecosystem File:
```bash
cd ~/arbitrage-trustless-onchain-module
nano ecosystem.config.js
```

```javascript
module.exports = {
  apps: [
    {
      name: 'atom-backend',
      script: 'backend/main.py',
      interpreter: 'backend/venv/bin/python',
      cwd: '/home/atom/arbitrage-trustless-onchain-module',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_file: './logs/backend-combined.log',
      time: true
    },
    {
      name: 'atom-bot',
      script: 'backend/bots/working/atom.js',
      cwd: '/home/atom/arbitrage-trustless-onchain-module',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/bot-error.log',
      out_file: './logs/bot-out.log',
      log_file: './logs/bot-combined.log',
      time: true
    }
  ]
};
```

### Start Services with PM2:
```bash
mkdir logs
pm2 start ecosystem.config.js
pm2 save
```

## 🌐 Step 9: Setup Nginx Reverse Proxy

### Install Nginx:
```bash
sudo apt install -y nginx
```

### Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/atom
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

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

### Enable Site:
```bash
sudo ln -s /etc/nginx/sites-available/atom /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Step 10: SSL Certificate (Optional)

### Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Get SSL Certificate:
```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

## 📊 Step 11: Setup Monitoring

### Install System Monitoring:
```bash
sudo apt install -y htop iotop nethogs
```

### PM2 Monitoring:
```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
```

## 🔧 Step 12: Environment Variables

### Backend .env Configuration:
```bash
# Copy from your local .env.example and fill in:
DATABASE_URL=postgresql://user:pass@localhost:5432/atom
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
PRIVATE_KEY=your_private_key_without_0x
ALCHEMY_API_KEY=your_alchemy_key
THEATOM_API_KEY=your_theatom_key
```

## 🚀 Step 13: Final Verification

### Check All Services:
```bash
pm2 status
sudo systemctl status nginx
curl http://localhost:8000/health
```

### View Logs:
```bash
pm2 logs
tail -f logs/backend-combined.log
```

## 🔄 Step 14: Maintenance Commands

### Update Code:
```bash
cd ~/arbitrage-trustless-onchain-module
git pull origin main
pm2 restart all
```

### Monitor Resources:
```bash
htop
pm2 monit
df -h
free -h
```

### Backup Important Files:
```bash
tar -czf atom-backup-$(date +%Y%m%d).tar.gz \
  ~/arbitrage-trustless-onchain-module \
  ~/.env \
  /etc/nginx/sites-available/atom
```

## 🆘 Troubleshooting

### Common Issues:
1. **Port 8000 not accessible**: Check firewall and nginx config
2. **PM2 processes crashing**: Check logs with `pm2 logs`
3. **Database connection issues**: Verify environment variables
4. **Bot not connecting**: Check API keys and network connectivity

### Useful Commands:
```bash
# Restart all services
pm2 restart all

# Check system resources
htop
df -h

# View real-time logs
pm2 logs --lines 100

# Check network connections
netstat -tulpn | grep :8000
```

## 📞 Support

If you encounter issues:
1. Check the logs: `pm2 logs`
2. Verify environment variables are set correctly
3. Ensure all required ports are open
4. Check system resources with `htop`

## 🔐 Step 15: Security Hardening

### SSH Security:
```bash
sudo nano /etc/ssh/sshd_config
```

```bash
# Disable root login
PermitRootLogin no

# Change default SSH port (optional)
Port 2222

# Disable password authentication (use keys only)
PasswordAuthentication no
PubkeyAuthentication yes
```

```bash
sudo systemctl restart sshd
```

### Install Additional Security:
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📈 Step 16: Performance Optimization

### System Limits:
```bash
sudo nano /etc/security/limits.conf
```

```bash
# Add these lines:
atom soft nofile 65536
atom hard nofile 65536
atom soft nproc 32768
atom hard nproc 32768
```

### Kernel Parameters:
```bash
sudo nano /etc/sysctl.conf
```

```bash
# Add these lines:
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
vm.swappiness = 10
```

```bash
sudo sysctl -p
```

## 🔄 Step 17: Automated Backups

### Create Backup Script:
```bash
nano ~/backup-atom.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/atom/backups"
mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/atom-app-$DATE.tar.gz \
  ~/arbitrage-trustless-onchain-module \
  --exclude=node_modules \
  --exclude=venv \
  --exclude=logs

# Backup configs
tar -czf $BACKUP_DIR/atom-configs-$DATE.tar.gz \
  ~/.env \
  /etc/nginx/sites-available/atom \
  ~/ecosystem.config.js

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x ~/backup-atom.sh
```

### Setup Cron Job:
```bash
crontab -e
```

```bash
# Daily backup at 2 AM
0 2 * * * /home/atom/backup-atom.sh >> /home/atom/backup.log 2>&1
```

## 📊 Step 18: Advanced Monitoring

### Install Node Exporter (for Prometheus):
```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
```

### Create Systemd Service:
```bash
sudo nano /etc/systemd/system/node_exporter.service
```

```ini
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=atom
Group=atom
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

## 🚨 Step 19: Alerting Setup

### Create Health Check Script:
```bash
nano ~/health-check.sh
```

```bash
#!/bin/bash
BACKEND_URL="http://localhost:8000/health"
WEBHOOK_URL="YOUR_DISCORD_OR_SLACK_WEBHOOK"

if ! curl -f $BACKEND_URL > /dev/null 2>&1; then
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🚨 ATOM Backend is DOWN on '$(hostname)'"}' \
    $WEBHOOK_URL
fi

# Check PM2 processes
if ! pm2 jlist | jq -e '.[] | select(.pm2_env.status != "online")' > /dev/null; then
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"⚠️ Some ATOM processes are not running on '$(hostname)'"}' \
    $WEBHOOK_URL
fi
```

```bash
chmod +x ~/health-check.sh
```

### Add to Cron:
```bash
crontab -e
```

```bash
# Health check every 5 minutes
*/5 * * * * /home/atom/health-check.sh
```

## 🔧 Step 20: Database Setup (if using PostgreSQL)

### Install PostgreSQL:
```bash
sudo apt install -y postgresql postgresql-contrib
```

### Setup Database:
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE atom;
CREATE USER atomuser WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE atom TO atomuser;
\q
```

### Configure Connection:
```bash
# Update .env file
DATABASE_URL=postgresql://atomuser:your_secure_password@localhost:5432/atom
```

## 🎯 Final Production Checklist

### ✅ Pre-Launch Verification:
- [ ] All environment variables configured
- [ ] SSL certificate installed and working
- [ ] Firewall properly configured
- [ ] PM2 processes running and stable
- [ ] Nginx reverse proxy working
- [ ] Database connections tested
- [ ] Bot connectivity verified
- [ ] Backup system operational
- [ ] Monitoring and alerting active
- [ ] Security hardening applied

### 🚀 Launch Commands:
```bash
# Final restart of all services
pm2 restart all
sudo systemctl restart nginx

# Verify everything is running
pm2 status
curl https://your-domain.com/health
```

**Your ATOM production environment is now FULLY OPERATIONAL! 🚀**

## 📞 Emergency Contacts & Resources

- **Server IP**: `YOUR_DROPLET_IP`
- **SSH Access**: `ssh atom@YOUR_DROPLET_IP -p 22`
- **Backend URL**: `https://your-domain.com`
- **PM2 Dashboard**: `pm2 monit`
- **Logs Location**: `/home/atom/arbitrage-trustless-onchain-module/logs/`

**Remember to keep your environment variables secure and never commit them to version control!** 🔐
