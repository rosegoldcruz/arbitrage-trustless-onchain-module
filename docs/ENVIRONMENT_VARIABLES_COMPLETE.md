# COMPLETE ENVIRONMENT VARIABLES REFERENCE

## 🔧 WHAT THIS TELLS YOU ABOUT THE TECH STACK

Based on these environment variables, this is what's running:

### **Frontend Stack**
- **Next.js 14** (NEXT_PUBLIC_ variables)
- **Vercel Deployment** (vercel.json configuration)
- **Clerk Authentication** (CLERK_ variables)
- **TypeScript + Tailwind CSS** (based on build commands)

### **Backend Stack**
- **FastAPI (Python)** (uvicorn server, Python dependencies)
- **Supabase Database** (DATABASE_URL, SUPABASE_ variables)
- **Redis Caching** (REDIS_ variables)
- **Web3 Integration** (RPC URLs, API keys)

### **Blockchain Integration**
- **Base Network** (Base Sepolia/Mainnet RPC)
- **Multi-chain Support** (Ethereum, Polygon, BSC)
- **DEX Integrations** (0x, 1inch APIs)
- **Flash Loans** (AAVE integration)

### **Bot Architecture**
- **Hybrid Bots** (Node.js ATOM + Python ADOM)
- **24/7 Daemon Operation** (PM2/systemd)
- **Real-time Arbitrage** (WebSocket connections)

---

## 📋 FRONTEND ENVIRONMENT VARIABLES

### Required for Next.js App (.env.local)
```bash
# Application Configuration
NEXT_PUBLIC_APP_NAME=ATOM
NEXT_PUBLIC_APP_URL=https://aeoninvestmentstechnologies.com
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Authentication (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Vercel Production Environment
```bash
# From vercel.json - Production Settings
NEXT_PUBLIC_APP_NAME=ATOM
NEXT_PUBLIC_APP_URL=https://aeoninvestmentstechnologies.com
NEXT_PUBLIC_BACKEND_URL=http://152.42.234.243:8000
```

---

## 🐍 BACKEND ENVIRONMENT VARIABLES

### Core FastAPI Configuration (.env)
```bash
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-here
API_RATE_LIMIT=1000
SESSION_TIMEOUT=3600
```

### Database Configuration
```bash
# Supabase (Primary Database)
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Redis (Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

---

## ⛓️ BLOCKCHAIN ENVIRONMENT VARIABLES

### RPC Endpoints
```bash
# Base Network (Primary)
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASE_MAINNET_RPC_URL=https://mainnet.base.org

# Ethereum
ETHEREUM_RPC_URL=https://eth-mainnet.alchemyapi.io/v2/YOUR_ALCHEMY_KEY
ETHEREUM_SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# Other Chains
POLYGON_RPC_URL=https://polygon-rpc.com
BSC_RPC_URL=https://bsc-dataseed.binance.org
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
```

### Blockchain API Keys
```bash
# Node Providers
ALCHEMY_API_KEY=your_alchemy_api_key
INFURA_API_KEY=your_infura_api_key

# Block Explorers
BASESCAN_API_KEY=your_basescan_api_key
ETHERSCAN_API_KEY=your_etherscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Wallet & Signing
PRIVATE_KEY=0x_your_private_key_here
MNEMONIC=your twelve word mnemonic phrase here
```

---

## 🔄 DEX & TRADING API VARIABLES

### DEX Aggregators
```bash
# 0x Protocol
ZEROX_API_KEY=your_0x_api_key
ZEROX_BASE_URL=https://api.0x.org

# 1inch
ONEINCH_API_KEY=your_1inch_api_key
ONEINCH_BASE_URL=https://api.1inch.dev

# Paraswap
PARASWAP_API_KEY=your_paraswap_api_key
```

### Flash Loan Configuration
```bash
# AAVE V3
AAVE_POOL_ADDRESS=0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
AAVE_POOL_DATA_PROVIDER=0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3

# Flash Loan Settings
FLASHLOAN_FEE_BPS=5  # 0.05%
MIN_PROFIT_BPS=23    # 0.23% minimum profit
MAX_GAS_PRICE=50     # 50 gwei max
```

---

## 🤖 BOT CONFIGURATION VARIABLES

### ATOM Bot (Node.js)
```bash
# Bot Identity
ATOM_BOT_NAME=ATOM
ATOM_BOT_VERSION=2.0.0
ATOM_WALLET_ADDRESS=0x_your_bot_wallet_address

# Trading Parameters
ATOM_MIN_PROFIT_BPS=23
ATOM_MAX_SLIPPAGE_BPS=50
ATOM_MAX_GAS_PRICE=50
ATOM_SCAN_INTERVAL=5000  # 5 seconds

# Risk Management
ATOM_MAX_TRADE_SIZE=10000  # $10,000 USD
ATOM_DAILY_LOSS_LIMIT=500  # $500 USD
ATOM_ENABLE_STOP_LOSS=true
```

### ADOM Bot (Python)
```bash
# Bot Identity
ADOM_BOT_NAME=ADOM
ADOM_BOT_VERSION=1.5.0
ADOM_WALLET_ADDRESS=0x_your_adom_wallet_address

# Advanced Analysis
ADOM_ML_MODEL_PATH=/models/arbitrage_predictor.pkl
ADOM_ANALYSIS_DEPTH=deep
ADOM_PREDICTION_THRESHOLD=0.85

# Multi-dimensional Analysis
ADOM_ENABLE_CROSS_CHAIN=true
ADOM_ENABLE_YIELD_FARMING=true
ADOM_ENABLE_LIQUIDITY_MINING=true
```

---

## 📊 MONITORING & LOGGING VARIABLES

### Application Monitoring
```bash
# Sentry (Error Tracking)
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
SENTRY_ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=/var/log/atom/app.log

# Health Checks
HEALTH_CHECK_INTERVAL=30  # seconds
HEALTH_CHECK_TIMEOUT=10   # seconds
```

### Discord/Slack Notifications
```bash
# Discord Webhooks
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook
DISCORD_PROFIT_WEBHOOK=https://discord.com/api/webhooks/profit_webhook
DISCORD_ERROR_WEBHOOK=https://discord.com/api/webhooks/error_webhook

# Slack (Alternative)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your_webhook
SLACK_CHANNEL=#atom-alerts
```

---

## 🔐 SECURITY & AUTHENTICATION VARIABLES

### Web3 Authentication
```bash
# WalletConnect
WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id

# Web3Auth (Alternative)
WEB3AUTH_CLIENT_ID=your_web3auth_client_id
WEB3AUTH_VERIFIER=your_verifier_name
```

### API Security
```bash
# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600  # 1 hour

# API Keys
THEATOM_API_KEY=your_custom_atom_api_key
INTERNAL_API_SECRET=your_internal_api_secret

# Encryption
ENCRYPTION_KEY=your_32_character_encryption_key
HASH_SALT=your_random_salt_string
```

---

## 🚀 DEPLOYMENT VARIABLES

### Docker Configuration
```bash
# Container Settings
DOCKER_IMAGE_TAG=atom:latest
CONTAINER_PORT=8000
CONTAINER_MEMORY=2g
CONTAINER_CPU=1

# Docker Compose
COMPOSE_PROJECT_NAME=atom
COMPOSE_FILE=docker-compose.yml
```

### Production Deployment
```bash
# Environment
NODE_ENV=production
PYTHON_ENV=production

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/atom.crt
SSL_KEY_PATH=/etc/ssl/private/atom.key

# Load Balancer
LOAD_BALANCER_URL=https://lb.aeoninvestmentstechnologies.com
```

---

## ⚠️ CRITICAL SECURITY NOTES

1. **NEVER COMMIT .env FILES** - All environment files are in .gitignore
2. **ROTATE KEYS REGULARLY** - Especially private keys and API keys
3. **USE DIFFERENT KEYS** - Separate keys for development/staging/production
4. **MONITOR USAGE** - Track API key usage for unusual activity
5. **BACKUP SECURELY** - Store environment variables in secure password manager

---

## 🔄 ENVIRONMENT SETUP COMMANDS

### Development Setup
```bash
# Copy environment template
cp .env.example .env.local

# Install dependencies
pnpm install  # Frontend
pip install -r requirements.txt  # Backend

# Start services
pnpm dev  # Frontend on :3000
python start.py  # Backend on :8000
```

### Production Deployment
```bash
# Build frontend
pnpm build

# Start backend with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Start bots with PM2
pm2 start ecosystem.config.js
```

This comprehensive list shows you're running a full-stack DeFi arbitrage platform with Next.js frontend, FastAPI backend, multi-chain blockchain integration, AI-powered bots, and production-ready monitoring.
