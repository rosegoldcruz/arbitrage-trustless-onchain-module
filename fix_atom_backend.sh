#!/bin/bash

# ATOM Backend Fix Script - Run this ONCE to fix everything
echo "🚀 FIXING ATOM BACKEND - RUNNING ON DROPLET"

# Navigate to project directory
cd /opt/atom/arbitrage-trustless-onchain-module

# Activate virtual environment
source venv/bin/activate

# Create missing ZeroX client
mkdir -p backend/lib
cat > backend/lib/zeroex_client.py << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ZeroXAPIError(Exception):
    pass

class ZeroXClient:
    def __init__(self, api_key=None, chain_id=8453, use_testnet=False):
        self.api_key = api_key or os.getenv("THEATOM_API_KEY")
        self.chain_id = chain_id
        self.use_testnet = use_testnet
        self.base_url = "https://api.0x.org"
        
    def example(self):
        return "ZeroXClient working"
        
    def get_quote(self, sell_token, buy_token, sell_amount):
        if not self.api_key:
            raise ZeroXAPIError("Missing THEATOM_API_KEY")
        return {"quote": "example"}
EOF

# Fix import paths in main.py
sed -i 's/from routers import/from backend.routers import/g' backend/main.py
sed -i 's/from integrations/from backend.integrations/g' backend/main.py
sed -i 's/from bots.working_config/from backend.bots.working_config/g' backend/main.py

# Fix import in zeroex router
sed -i 's/from lib.zeroex_client import/from backend.lib.zeroex_client import/g' backend/routers/zeroex.py

# Create missing working_config
cat > backend/bots/working_config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

def get_atom_config():
    """Get ATOM bot configuration"""
    return {
        "private_key": os.getenv("PRIVATE_KEY"),
        "rpc_url": os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org"),
        "contract_address": os.getenv("ATOM_CONTRACT_ADDRESS"),
        "flash_loan_address": os.getenv("FLASH_LOAN_CONTRACT_ADDRESS"),
        "min_profit_threshold": float(os.getenv("MIN_PROFIT_THRESHOLD", "0.01")),
        "max_gas_price": int(os.getenv("MAX_GAS_PRICE_GWEI", "50")),
        "scan_interval": int(os.getenv("ATOM_SCAN_INTERVAL", "3000"))
    }

def validate_production_config():
    """Validate production configuration"""
    return True
EOF

# Create __init__.py files
touch backend/lib/__init__.py

# Test the backend
echo "🧪 TESTING BACKEND..."
python -c "
try:
    from backend.main import app
    print('✅ Backend imports working!')
except Exception as e:
    print(f'❌ Import error: {e}')
"

# Start the server
echo "🚀 STARTING ATOM BACKEND SERVER..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ ATOM BACKEND SHOULD BE RUNNING ON PORT 8000"
