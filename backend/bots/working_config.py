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
        "scan_interval": int(os.getenv("ATOM_SCAN_INTERVAL", "3000")),
        "tokens": {
            "WETH": "0x4200000000000000000000000000000000000006",
            "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
            "DAI": "0x174956bDf96C89F96B5d3d42F3C6d7E8E8F8F8F8",
            "GHO": "0x5d00fab5f2F97C4D682C1053cDCAA59c2c37900D"
        }
    }

def validate_production_config():
    """Validate production configuration"""
    config = get_atom_config()
    
    required_fields = ["private_key", "contract_address", "flash_loan_address"]
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required configuration: {missing_fields}")
    
    return True
