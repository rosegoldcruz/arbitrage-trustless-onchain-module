# ATOM Polygon Mainnet - Advanced Arbitrage System

## Repository Structure
ATOM/
├── contracts/
│   └── PolygonArbitrageEngine.sol
├── scripts/
│   └── deploy-polygon.js
├── hardhat.config.cjs
├── package.json
├── .gitignore
├── .env.example
├── backend-api/                         # API-only service
│   ├── main.py
│   └── api/
│       └── metrics.py
├── backend-bots/                        # signals + orchestrator runtime
│   ├── infra/redis_bus.py
│   ├── watchers/sim_rotation_feed.py
│   ├── signals/rotation.py
│   ├── orchestrator/rotation_consumer.py
│   └── engine/exec.py
├── requirements.txt                     # python deps for BOTH backends
└── _archive/                            # all the noisy tests/scripts you’re mothballing

## Local Secrets (not in repo)
/etc/atom.secrets
  PRIVATE_KEY=<sepolia_test_key>
  TESTNET_WALLET_ADDRESS=0x1f62B60669E492b783E1dD1d805fBC7588A8557e
  OPENAI_API_KEY=...
  CLERK_SECRET_KEY=...
  CLERK_SIGNING_SECRET=...
  CLERK_WEBHOOK_SECRET=...

## 20-Step Runbook

### 1. Rsync code to droplet
export DROPLET_IP=<ip>; export DROPLET_USER=root; export REMOTE=/srv/atom
rsync -az --delete ./ ${DROPLET_USER}@${DROPLET_IP}:${REMOTE}/
scp .secrets/atom.secrets ${DROPLET_USER}@${DROPLET_IP}:/tmp/atom.secrets

### 2. Droplet bootstrap
ssh root@${DROPLET_IP}
install -m 600 /tmp/atom.secrets /etc/atom.secrets && rm -f /tmp/atom.secrets
apt-get update && apt-get install -y python3-venv python3-pip redis-server
systemctl enable --now redis-server

### 3. Create venvs per backend
cd /srv/atom/backend-api    && python3 -m venv .venv && . .venv/bin/activate && pip install -r ../requirements.txt && deactivate
cd /srv/atom/backend-bots   && python3 -m venv .venv && . .venv/bin/activate && pip install -r ../requirements.txt && deactivate

### 4. Systemd: API
tee /etc/systemd/system/atom-api.service > /dev/null <<'EOF'
[Unit]
Description=ATOM API (FastAPI)
After=network-online.target
[Service]
User=root
WorkingDirectory=/srv/atom/backend-api
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/etc/atom.secrets
EnvironmentFile=/srv/atom/backend-api/.env.sepolia
ExecStart=/srv/atom/backend-api/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
