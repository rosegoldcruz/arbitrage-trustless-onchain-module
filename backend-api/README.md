# ATOM Backend API

Production-ready FastAPI backend for ATOM arbitrage system.

## Production Deployment

### Prerequisites

1. Ubuntu/Debian server with systemd
2. Redis server running
3. Python 3.11+
4. Project deployed to `/srv/atom/backend-api`

### Setup

1. **Deploy the code:**
   ```bash
   sudo mkdir -p /srv/atom
   sudo git clone <repo> /srv/atom
   cd /srv/atom/backend-api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create production environment:**
   ```bash
   # Copy your .env.production to the project root
   cp .env.production.example .env.production
   # Edit with your actual values
   nano .env.production
   ```

4. **Run production setup:**
   ```bash
   chmod +x deploy/setup_production_env.sh
   sudo ./deploy/setup_production_env.sh
   ```

This will:
- Create `/etc/atom/backend-api.env` from your `.env.production`
- Install systemd service
- Create `atom` user
- Start and enable the service

### Environment Variables

Required in `/etc/atom/backend-api.env`:

```bash
ENV=production
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
STREAM_NAMESPACE=atom
```

Optional stream keys:
```bash
MEV_STREAM_KEY=atom:opps:mev
TRIANGULAR_STREAM_KEY=atom:opps:triangular
LIQUIDITY_STREAM_KEY=atom:opps:liquidity
STAT_ARB_STREAM_KEY=atom:opps:stat_arb
VOLATILITY_STREAM_KEY=atom:opps:volatility
```

### Service Management

```bash
# Check status
sudo systemctl status atom-api

# View logs
journalctl -u atom-api -f

# Restart service
sudo systemctl restart atom-api

# Stop service
sudo systemctl stop atom-api
```

### Health Checks

```bash
# Local health check
curl -fsS http://127.0.0.1:8000/health

# API endpoints
curl -fsS http://127.0.0.1:8000/mev/latest | head
curl -fsS "http://127.0.0.1:8000/triangular/range?count=5" | jq .

# Run health check script
./scripts/health_check.sh 127.0.0.1:8000 http
```

### Local Development

```bash
# Run locally (loads .env.production)
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

### Environment Verification

```bash
# Verify environment in systemd context
sudo /usr/bin/env -i $(cat /etc/atom/backend-api.env | xargs) python3 scripts/verify_env.py
```

## API Endpoints

- `GET /health` - Health check
- `GET /mev/latest?count=50` - Latest MEV opportunities
- `GET /mev/range?start=-&end=+&count=100` - MEV range query
- `GET /triangular/latest` - Latest triangular arbitrage opportunities
- `GET /triangular/range` - Triangular arbitrage range query
- `GET /liquidity/latest` - Latest liquidity opportunities
- `GET /stat_arb/latest` - Latest statistical arbitrage opportunities
- `GET /volatility/latest` - Latest volatility opportunities

## Architecture

- **FastAPI** - Web framework
- **Redis Streams** - Message queuing and data storage
- **Pydantic Settings** - Configuration management
- **Systemd** - Process management
- **uvloop** - High-performance event loop