#!/usr/bin/env python3
"""
PRODUCTION CONFIGURATION FOR ATOM BOTS
Real DEX connections and smart contract addresses
"""

import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class ProductionConfig:
    """Production configuration for ATOM bot ecosystem"""
    
    # Network Configuration
    rpc_url: str = "https://sepolia.base.org"
    wss_url: str = "wss://sepolia.base.org"
    chain_id: int = 84532  # Base Sepolia
    
    # Smart Contract Addresses (Base Sepolia)
    arbitrage_bot_address: str = "0x0000000000000000000000000000000000000000"  # Deploy first
    flash_loan_address: str = "0x0000000000000000000000000000000000000000"     # Deploy first
    triangular_arbitrage_address: str = "0x0000000000000000000000000000000000000000"  # Deploy first
    
    # Token Addresses (Base Sepolia)
    tokens: Dict[str, str] = None
    
    # DEX Addresses (Base Sepolia)
    dex_addresses: Dict[str, str] = None
    
    # Trading Parameters
    min_spread_bps: int = 23  # 0.23% minimum
    max_gas_price: int = 50_000_000_000  # 50 gwei
    min_profit_usd: float = 10.0
    max_trade_size: float = 100_000.0
    
    # Bot Configuration
    scan_interval: float = 3.0  # 3 seconds
    execution_timeout: int = 30
    retry_attempts: int = 3
    
    # API Keys
    theatom_api_key: str = ""
    alchemy_api_key: str = ""
    
    def __post_init__(self):
        """Initialize token and DEX addresses"""
        if self.tokens is None:
            self.tokens = {
                'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
                'USDC': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
                'WETH': '0x4200000000000000000000000000000000000006',
                'GHO': '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f'
            }
        
        if self.dex_addresses is None:
            self.dex_addresses = {
                'balancer_vault': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                'uniswap_v3_router': '0x2626664c2603336E57B271c5C0b26F421741e481',
                'curve_dai_usdc': '0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E',
                'curve_usdc_gho': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
            }
        
        # Load from environment variables
        self.private_key = os.getenv('PRIVATE_KEY', '')
        self.theatom_api_key = os.getenv('THEATOM_API_KEY', '7324a2b4-3b05-4288-b353-68322f49a283')
        self.alchemy_api_key = os.getenv('ALCHEMY_API_KEY', '')

def get_atom_config() -> ProductionConfig:
    """Get ATOM bot configuration"""
    return ProductionConfig()

def get_adom_config() -> dict:
    """Get ADOM bot configuration"""
    config = get_atom_config()
    
    return {
        'rpcUrl': config.rpc_url,
        'chainId': config.chain_id,
        'privateKey': config.private_key,
        'arbitrageBotAddress': config.arbitrage_bot_address,
        'flashLoanAddress': config.flash_loan_address,
        'tokens': config.tokens,
        'dexAddresses': config.dex_addresses,
        'minSpreadBps': config.min_spread_bps,
        'maxGasPrice': config.max_gas_price,
        'scanInterval': config.scan_interval * 1000,  # Convert to milliseconds
        'executionTimeout': config.execution_timeout
    }

def get_hybrid_config() -> dict:
    """Get hybrid bot configuration"""
    config = get_atom_config()
    
    return {
        'rpc_url': config.rpc_url,
        'private_key': config.private_key,
        'contract_addresses': {
            'triangular_arbitrage': config.triangular_arbitrage_address,
            'price_monitor': '0x0000000000000000000000000000000000000000',
            'execution_engine': config.arbitrage_bot_address
        },
        'tokens': config.tokens,
        'min_profit_bps': config.min_spread_bps,
        'max_gas_price': config.max_gas_price,
        'scan_interval': config.scan_interval
    }

# Production startup check
def validate_production_config():
    """Validate that all required configuration is present"""
    config = get_atom_config()
    
    missing = []
    
    if not config.private_key:
        missing.append("PRIVATE_KEY environment variable")
    
    if config.arbitrage_bot_address == "0x0000000000000000000000000000000000000000":
        missing.append("Arbitrage bot contract address")
    
    if config.flash_loan_address == "0x0000000000000000000000000000000000000000":
        missing.append("Flash loan contract address")
    
    if missing:
        print("❌ PRODUCTION CONFIG MISSING:")
        for item in missing:
            print(f"   - {item}")
        print("\n🔧 Deploy contracts and set environment variables first!")
        return False
    
    print("✅ Production configuration validated")
    return True

if __name__ == "__main__":
    validate_production_config()
