"""
🤖 Bot Configuration Management
Centralized configuration for ATOM and ADOM bots
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AtomConfig:
    """ATOM Bot Configuration"""
    private_key: str
    rpc_url: str
    contract_address: str
    flash_loan_address: str
    min_profit_threshold: float
    max_gas_price: int
    scan_interval: int
    tokens: Dict[str, str]
    
    @classmethod
    def from_env(cls) -> 'AtomConfig':
        """Create AtomConfig from environment variables"""
        return cls(
            private_key=os.getenv("PRIVATE_KEY", ""),
            rpc_url=os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org"),
            contract_address=os.getenv("ATOM_CONTRACT_ADDRESS", ""),
            flash_loan_address=os.getenv("FLASH_LOAN_CONTRACT_ADDRESS", ""),
            min_profit_threshold=float(os.getenv("MIN_PROFIT_THRESHOLD", "0.01")),
            max_gas_price=int(os.getenv("MAX_GAS_PRICE_GWEI", "50")),
            scan_interval=int(os.getenv("ATOM_SCAN_INTERVAL", "3000")),
            tokens={
                "WETH": "0x4200000000000000000000000000000000000006",
                "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            }
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_fields = ["private_key", "contract_address", "flash_loan_address"]
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            raise ValueError(f"Missing required ATOM configuration: {missing_fields}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "private_key": self.private_key,
            "rpc_url": self.rpc_url,
            "contract_address": self.contract_address,
            "flash_loan_address": self.flash_loan_address,
            "min_profit_threshold": self.min_profit_threshold,
            "max_gas_price": self.max_gas_price,
            "scan_interval": self.scan_interval,
            "tokens": self.tokens
        }

@dataclass
class AdomConfig:
    """ADOM Bot Configuration"""
    private_key: str
    rpc_url: str
    contract_address: str
    flash_loan_address: str
    min_profit_threshold: float
    max_gas_price: int
    scan_interval: int
    tokens: Dict[str, str]
    mev_strategies: list
    
    @classmethod
    def from_env(cls) -> 'AdomConfig':
        """Create AdomConfig from environment variables"""
        return cls(
            private_key=os.getenv("PRIVATE_KEY", ""),
            rpc_url=os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org"),
            contract_address=os.getenv("ADOM_CONTRACT_ADDRESS", ""),
            flash_loan_address=os.getenv("FLASH_LOAN_CONTRACT_ADDRESS", ""),
            min_profit_threshold=float(os.getenv("MIN_PROFIT_THRESHOLD", "0.01")),
            max_gas_price=int(os.getenv("MAX_GAS_PRICE_GWEI", "50")),
            scan_interval=int(os.getenv("ADOM_SCAN_INTERVAL", "5000")),
            tokens={
                "WETH": "0x4200000000000000000000000000000000000006",
                "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            },
            mev_strategies=[
                'triangular_arbitrage',
                'sandwich_protection',
                'liquidation_frontrun',
                'dex_arbitrage'
            ]
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        required_fields = ["private_key", "contract_address", "flash_loan_address"]
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        
        if missing_fields:
            raise ValueError(f"Missing required ADOM configuration: {missing_fields}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "private_key": self.private_key,
            "rpc_url": self.rpc_url,
            "contract_address": self.contract_address,
            "flash_loan_address": self.flash_loan_address,
            "min_profit_threshold": self.min_profit_threshold,
            "max_gas_price": self.max_gas_price,
            "scan_interval": self.scan_interval,
            "tokens": self.tokens,
            "mev_strategies": self.mev_strategies
        }
