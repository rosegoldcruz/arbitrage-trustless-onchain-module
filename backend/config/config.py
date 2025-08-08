"""
Centralized configuration for secrets and environment variables
All sensitive values are loaded from environment variables only.
"""
import os

# API Keys and Providers
AAVE_API_KEY = os.getenv("AAVE_API_KEY")
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
INFURA_API_KEY = os.getenv("INFURA_API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY")
THEATOM_API_KEY = os.getenv("THEATOM_API_KEY")

# Wallet / Contracts
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
BASE_SEPOLIA_CONTRACT_ADDRESS = os.getenv("BASE_SEPOLIA_CONTRACT_ADDRESS")
ATOM_CONTRACT_ADDRESS = os.getenv("ATOM_CONTRACT_ADDRESS")
FLASH_LOAN_CONTRACT = os.getenv("FLASH_LOAN_CONTRACT") or os.getenv("AAVE_POOL_ADDRESS")

# Network
BASE_SEPOLIA_RPC_URL = os.getenv("BASE_SEPOLIA_RPC_URL")
BASE_SEPOLIA_WSS_URL = os.getenv("BASE_SEPOLIA_WSS_URL")

# Auth for dashboard/backend
ATOM_DASH_TOKEN = os.getenv("ATOM_DASH_TOKEN")

# Database
POSTGRES_URL = os.getenv("POSTGRES_URL")

# External APIs (non-sensitive base URLs)
ZRX_API_URL = os.getenv("ZRX_API_URL", "https://api.0x.org")
ZRX_GASLESS_API_URL = os.getenv("ZRX_GASLESS_API_URL", "https://gasless.api.0x.org")
THE_GRAPH_STUDIO_URL = os.getenv("THE_GRAPH_STUDIO_URL", "https://api.studio.thegraph.com")

# Helper accessors

def require(name: str, value: str | None):
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

