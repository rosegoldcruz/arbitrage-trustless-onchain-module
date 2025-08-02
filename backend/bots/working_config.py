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
    config = get_atom_config()
    
    required_fields = ["private_key", "contract_address", "flash_loan_address"]
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required configuration: {missing_fields}")
    
    return True
