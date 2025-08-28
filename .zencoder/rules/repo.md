---
description: Repository Information Overview
alwaysApply: true
---

# ATOM Arbitrage System Information

## Repository Summary
ATOM is an advanced DeFi arbitrage system that executes flash loan arbitrage via AAVE. The system includes smart contracts for on-chain execution, backend services for opportunity detection, and a frontend dashboard for monitoring and management.

## Repository Structure
- **contracts/**: Solidity smart contracts for flash loan arbitrage
- **backend-api/**: FastAPI service providing REST endpoints
- **backend-bots/**: Python-based arbitrage opportunity detection and execution
- **bots/**: Additional trading bots for various strategies
- **frontend/**: Next.js web application for monitoring and management
- **scripts/**: Deployment and management scripts
- **deploy/**: Production deployment configurations
- **config/**: System configuration files

## Projects

### Smart Contracts
**Configuration File**: hardhat.config.ts

#### Language & Runtime
**Language**: Solidity
**Version**: 0.8.22
**Build System**: Hardhat 2.26.3
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- @aave/core-v3: 1.19.3
- @aave/periphery-v3: 2.0.3
- @openzeppelin/contracts: 5.4.0
- @openzeppelin/contracts-upgradeable: 5.4.0
- @chainlink/contracts: 1.2.0

#### Build & Installation
```bash
npm install
npx hardhat compile
npx hardhat run scripts/deploy_mev_uups.ts --network sepolia
```

#### Testing
**Framework**: Hardhat test
**Test Location**: tests/
**Run Command**:
```bash
npx hardhat test
```

### Backend API
**Configuration File**: backend-api/main.py

#### Language & Runtime
**Language**: Python
**Version**: 3.x
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- fastapi: 0.103.1
- uvicorn: 0.23.2
- web3: 6.11.0
- redis: 5.0.8
- pydantic-settings: 2.0.3

#### Build & Installation
```bash
pip install -r requirements.txt
cd backend-api
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Docker
**Dockerfile**: config/Dockerfile.bots
**Configuration**: docker-compose.yml
**Services**: backend-api, redis, prometheus

### Backend Bots
**Configuration File**: backend-bots/orchestrator/README.md

#### Language & Runtime
**Language**: Python
**Version**: 3.x
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- web3: 6.11.0
- eth-account: 0.9.0
- redis: 5.0.8
- prometheus_client: 0.20.0
- pandas: 2.1.0
- numpy: 1.24.3
- scikit-learn: 1.3.0

#### Build & Installation
```bash
pip install -r requirements.txt
python scripts/start_production_bots.py
```

### Frontend
**Configuration File**: frontend/package.json

#### Language & Runtime
**Language**: TypeScript
**Version**: 5.x
**Build System**: Next.js 15.4.2
**Package Manager**: npm/pnpm

#### Dependencies
**Main Dependencies**:
- react: 19.1.0
- next: 15.4.2
- ethers: 6.15.0
- @web3auth/modal: 10.0.7
- @clerk/nextjs: 6.25.4
- tailwindcss: 3.4.15
- @tanstack/react-query: 5.83.0

#### Build & Installation
```bash
cd frontend
pnpm install
pnpm build
pnpm start
```

#### Docker
**Dockerfile**: frontend/Dockerfile

## Deployment
The system uses systemd services for production deployment:
- **API Service**: deploy/systemd/atom-api.service
- **Bot Services**: Multiple services in deploy/systemd/ for different arbitrage strategies
- **Environment**: Configuration via .env files and /etc/atom.secrets

## Integration Points
- **Blockchain**: Connects to Ethereum/Polygon via RPC
- **AAVE**: Uses AAVE V3 for flash loans
- **DEXs**: Interacts with various DEX routers for arbitrage execution
- **Monitoring**: Prometheus metrics for system health


- **Authentication**: Clerk for frontend user management