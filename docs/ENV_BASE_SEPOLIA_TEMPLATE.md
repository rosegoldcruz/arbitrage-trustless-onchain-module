# ATOM Environment Template — Base Sepolia (Chain ID 84532)

Copy this entire template into your .env file (do NOT commit). Replace placeholders with real values.

```
# =====================
# Core Network Settings
# =====================
# Base Sepolia testnet only
NETWORK=base_sepolia
CHAIN_ID=84532

# RPC endpoints
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASE_SEPOLIA_WSS_URL=wss://sepolia.base.org

# Optional Base mainnet (leave empty in testnet-only mode)
BASE_RPC_URL=

# =====================
# Backend Public API (Frontend <-> Backend)
# =====================
API_URL=https://api.aeoninvestmentstechnologies.com
NEXT_PUBLIC_API_URL=https://api.aeoninvestmentstechnologies.com
NEXT_PUBLIC_BACKEND_URL=https://api.aeoninvestmentstechnologies.com

# =====================
# Wallet & Contracts
# =====================
# Private key of the executor wallet (DO NOT COMMIT)
PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE

# Contract addresses (update after deployment)
ATOM_CONTRACT_ADDRESS=
ADOM_CONTRACT_ADDRESS=
FLASH_LOAN_CONTRACT_ADDRESS=0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b

# =====================
# Token Addresses (Base Sepolia)
# =====================
BASE_SEPOLIA_TOKEN_WETH=0x4200000000000000000000000000000000000006
BASE_SEPOLIA_TOKEN_USDC=0x036CbD53842c5426634e7929541eC2318f3dCF7e
BASE_SEPOLIA_TOKEN_DAI=0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb
BASE_SEPOLIA_TOKEN_GHO=0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f

# =====================
# DEX Providers & Aggregators
# =====================
# 0x is NOT supported on Base Sepolia. Keep disabled unless you know what you are doing.
ENABLE_ZEROX_ON_TESTNET=false
THEATOM_API_KEY= # Optional 0x API key (Base mainnet only)
ZRX_API_URL=https://api.0x.org
ZRX_GASLESS_API_URL=https://gasless.api.0x.org

# Balancer / The Graph
THE_GRAPH_STUDIO_URL=https://api.studio.thegraph.com
BALANCER_GRAPH_URL=https://api.studio.thegraph.com/query/24660/balancer-base-v2/version/latest
BALANCER_VAULT_ADDRESS= # Leave empty on Sepolia unless you have a compatible vault

# =====================
# External Services
# =====================
BASESCAN_API_KEY=
ALCHEMY_API_KEY=
INFURA_API_KEY=
ETHERSCAN_API_KEY=

# =====================
# Authentication (Clerk)
# =====================
# Used by Next.js frontend only
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

# =====================
# Supabase (Analytics/Logs)
# =====================
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=

# =====================
# Backend Service
# =====================
ATOM_DASH_TOKEN=
POSTGRES_URL=
PYTHONUNBUFFERED=1

# =====================
# App Runtime Tunables (optional)
# =====================
MIN_PROFIT_THRESHOLD=0.01
MAX_GAS_PRICE_GWEI=50
ATOM_SCAN_INTERVAL=3000
ADOM_SCAN_INTERVAL=5000
```

Notes
- 0x (THEATOM_API_KEY) is intentionally disabled on Base Sepolia via ENABLE_ZEROX_ON_TESTNET=false.
- Keep all .env* files out of Git. They are already ignored in .gitignore.
- After deploying contracts on Base Sepolia, paste the new addresses above and restart services.

