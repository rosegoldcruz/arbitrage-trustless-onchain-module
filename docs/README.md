# ⚛️ ATOM - Arbitrage Trustless On-chain Module

**Mission**: Maximize real on-chain yield through intelligent execution across Base L2

## 🚀 Quick Start

```bash
# Bootstrap sequence
pnpm install
cp .env.example .env.local
# Populate all required secrets in .env.local
pnpm run dev                    # Frontend
python agents/atom/main.py      # Backend test
```

## 🏗️ Architecture

### Frontend Stack
- **Framework**: Next.js 14 (App Router, Server Components)
- **Language**: TypeScript (strict mode enforced)
- **Styling**: Tailwind CSS, shadcn/ui, Framer Motion
- **Auth**: Clerk + Web3Auth wallet sync (Wagmi, Viem)

### Backend/Execution Layer
- **Web Server**: FastAPI (Python) for hybrid bot triggers
- **Bots**: ATOM (Node.js) + ADOM (Python) for strategy & routing
- **Arbitrage Logic**: AEONMath.sol (Solidity) + off-chain signal generation

### Smart Contracts
- **AEONArbitrageCore.sol**: Main contract for Base Sepolia/Mainnet
- **AEONMath.sol**: BPS, slippage, virtual price, Balancer math
- **FlashLoanExecutor.sol**: AAVE / Base-compatible

### Database & Infrastructure
- **Database**: Supabase (PostgreSQL) with RLS enforcement
- **Auth**: Clerk authentication system
- **Deployment**: Vercel (frontend), DigitalOcean (backend bots)

### DeFi Integration
- **Chains**: Base Sepolia, Base Mainnet
- **Oracles**: Chainlink price feeds
- **DEXs**: Balancer, Curve, Uniswap v3, 1inch, 0x
- **Flash Loans**: AAVE v3

## 🧠 Arbitrage Engine Rules

### Core Requirements
- All bots run as 24/7 daemons (PM2 or systemd)
- All arbitrage math validated against:
  - Balancer weighted pool math
  - Curve StableSwap formulas
  - 0x, Uniswap, 1inch API spreads
- All routes enforce **spreadBps > 23bps**
- Token path examples (Base Sepolia): WETH → USDC → GHO → DAI

### Smart Contract Requirements
- FlashLoanExecutor implementation
- Dynamic DEX router detection
- Slippage, gas, and ROI simulation logic

## 📊 Dashboard Features

### Real-time Monitoring
- Bot status display (active/inactive/failed)
- Manual execution with terminal output
- Strategy selection (flash loan, MEV, triangle, spread)
- Web3Auth wallet connection modal
- Visualized spreadBps, ROI %, and slippage risk

## 🧪 Validation & Testing

### Pre-execution Requirements
- Simulate all trades before execution (dry-run mode)
- All bot endpoints: `/trigger`, `/deploy`, `/flash-loan`
- Logs sent to Supabase audit table

### Deployment Requirements
- Contracts verified on Basescan
- Token pair approval confirmed
- Health check API tests passing

## ❌ Non-Negotiables

### Development Standards
- **Never use `npm install`** — use `pnpm` only
- **Never commit `.env.local` or API keys**
- **Never deploy to Vercel** without passing TS, lint, Zod
- **Never ignore failed arbitrage simulations**
- **Never run bots** without daemon protection (PM2/systemd)

## 🔐 Security & Environment

### Environment Setup
1. Copy `.env.example` to `.env.local`
2. Populate all required secrets (never commit these)
3. Ensure proper file permissions on environment files
4. Use testnet funds only for Base Sepolia testing

### Contract Addresses (Base Sepolia)
```bash
# Update after deployment
ATOM_TRIANGULAR_ARBITRAGE_ADDRESS=0x[DEPLOYED_ADDRESS]
ATOM_PRICE_MONITOR_ADDRESS=0x[DEPLOYED_ADDRESS]
ATOM_EXECUTION_ENGINE_ADDRESS=0x[DEPLOYED_ADDRESS]
```

## 🛠️ Development Workflow

### Local Development
```bash
# Frontend
cd frontend
pnpm dev

# Backend testing
python agents/atom/main.py

# Contract deployment
npx hardhat run scripts/deploy-base-sepolia.js --network baseSepolia
```

### Production Deployment
1. **Frontend**: Vercel deployment with environment validation
2. **Backend**: DigitalOcean droplet with PM2/systemd
3. **Contracts**: Base Sepolia → Base Mainnet migration

## 📋 Project Structure

```
atom/
├── frontend/           # Next.js application
├── backend/           # Python FastAPI + bots
├── contracts/         # Solidity smart contracts
├── agents/           # ATOM/ADOM bot implementations
├── scripts/          # Deployment and utility scripts
└── .env.local        # Environment variables (never commit)
```

## 🎯 Key Features

### Arbitrage Strategies
- **Triangular Arbitrage**: Multi-hop token swaps
- **Flash Loan Arbitrage**: Capital-efficient execution
- **MEV Protection**: Front-running resistance
- **Spread Trading**: Cross-DEX price differences

### Risk Management
- Minimum 23bps spread enforcement
- Gas optimization algorithms
- Slippage protection mechanisms
- Real-time ROI calculations

## 🔗 Important Links

- **Base Sepolia Faucet**: https://www.alchemy.com/faucets/base-sepolia
- **Basescan Testnet**: https://sepolia.basescan.org/
- **Supabase Dashboard**: [Your Supabase URL]
- **Vercel Deployment**: [Your Vercel URL]

## ⚠️ Legal Disclaimers

- AEON Investment Technologies is not a registered financial advisor
- All content is for informational purposes only
- Digital assets involve significant risk of loss
- Users are responsible for their own investment decisions

---

**🔐 Security First**: Never commit private keys or sensitive environment variables. Always audit wallet access before deployment.
