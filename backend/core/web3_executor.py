"""
Web3 Executor for ATOM Arbitrage System
Handles actual on-chain transaction execution for Base Sepolia/Mainnet
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple, Any
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_typing import ChecksumAddress

logger = logging.getLogger(__name__)

@dataclass
class TransactionResult:
    success: bool
    tx_hash: Optional[str] = None
    gas_used: Optional[int] = None
    actual_profit: Optional[float] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass
class ContractConfig:
    address: ChecksumAddress
    abi: list

class Web3Executor:
    """
    Executes arbitrage trades on-chain via deployed smart contracts
    """
    
    def __init__(self):
        self.w3 = None
        self.account = None
        self.contracts = {}
        self.chain_id = None
        self._initialize_web3()
        self._load_contracts()
    
    def _initialize_web3(self):
        """Initialize Web3 connection to Base Sepolia"""
        rpc_url = os.getenv("BASE_SEPOLIA_RPC_URL")
        if not rpc_url:
            raise ValueError("BASE_SEPOLIA_RPC_URL environment variable required")
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Add PoA middleware for Base Sepolia
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Base Sepolia: {rpc_url}")
        
        self.chain_id = self.w3.eth.chain_id
        logger.info(f"✅ Connected to Base network (Chain ID: {self.chain_id})")
        
        # Initialize account
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise ValueError("PRIVATE_KEY environment variable required")
        
        self.account = Account.from_key(private_key)
        logger.info(f"✅ Loaded account: {self.account.address}")
        
        # Check balance
        balance = self.w3.eth.get_balance(self.account.address)
        logger.info(f"Account balance: {self.w3.from_wei(balance, 'ether')} ETH")
        
        if balance < self.w3.to_wei(0.001, 'ether'):
            logger.warning("⚠️ Low ETH balance! May not be able to execute transactions")
    
    def _load_contracts(self):
        """Load deployed contract addresses and ABIs"""
        
        # Contract addresses from environment
        contract_addresses = {
            'flashloan_executor': os.getenv("FLASHLOAN_EXECUTOR_ADDRESS"),
            'aeon_core': os.getenv("AEON_ARBITRAGE_CORE_ADDRESS"),
            'triangular_arbitrage': os.getenv("TRIANGULAR_ARBITRAGE_ADDRESS"),
            'price_monitor': os.getenv("PRICE_MONITOR_ADDRESS")
        }
        
        # Load ABIs from compiled contracts
        artifacts_path = "artifacts/backend/contracts"
        
        contract_configs = {
            'flashloan_executor': {
                'address': contract_addresses['flashloan_executor'],
                'abi_path': f"{artifacts_path}/FlashLoanArbitrage.sol/FlashLoanArbitrage.json"
            },
            'aeon_core': {
                'address': contract_addresses['aeon_core'],
                'abi_path': f"{artifacts_path}/AEON.sol/AEON.json"
            },
            'triangular_arbitrage': {
                'address': contract_addresses['triangular_arbitrage'],
                'abi_path': f"{artifacts_path}/TriangularArbitrage.sol/TriangularArbitrage.json"
            },
            'price_monitor': {
                'address': contract_addresses['price_monitor'],
                'abi_path': f"{artifacts_path}/PriceMonitor.sol/PriceMonitor.json"
            }
        }
        
        for name, config in contract_configs.items():
            if not config['address']:
                logger.warning(f"⚠️ No address configured for {name}")
                continue
            
            try:
                # Load ABI from artifacts
                with open(config['abi_path'], 'r') as f:
                    artifact = json.load(f)
                    abi = artifact['abi']
                
                # Create contract instance
                address = self.w3.to_checksum_address(config['address'])
                contract = self.w3.eth.contract(address=address, abi=abi)
                
                self.contracts[name] = contract
                logger.info(f"✅ Loaded {name} contract: {address}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load {name} contract: {e}")
    
    def execute_flash_loan_arbitrage(
        self,
        asset: str,
        amount: int,
        dex_path: list,
        min_profit: int
    ) -> TransactionResult:
        """
        Execute flash loan arbitrage via FlashLoanArbitrage contract
        
        Args:
            asset: Token address to flash loan
            amount: Amount to flash loan (in wei)
            dex_path: List of DEX addresses for arbitrage path
            min_profit: Minimum profit required (in wei)
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            if 'flashloan_executor' not in self.contracts:
                return TransactionResult(
                    success=False,
                    error_message="FlashLoanArbitrage contract not loaded"
                )
            
            contract = self.contracts['flashloan_executor']
            
            # Build transaction
            function = contract.functions.executeFlashLoanArbitrage(
                asset,
                amount,
                dex_path,
                min_profit
            )
            
            # Estimate gas
            try:
                gas_estimate = function.estimate_gas({'from': self.account.address})
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
            except Exception as e:
                logger.error(f"Gas estimation failed: {e}")
                return TransactionResult(
                    success=False,
                    error_message=f"Gas estimation failed: {str(e)}"
                )
            
            # Get gas price
            gas_price = self.w3.eth.gas_price
            
            # Build transaction
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"📤 Flash loan arbitrage transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            if receipt.status == 1:
                # Parse logs to get actual profit
                actual_profit = self._parse_profit_from_logs(receipt.logs)
                
                logger.info(f"✅ Flash loan arbitrage successful!")
                logger.info(f"   Gas used: {receipt.gasUsed}")
                logger.info(f"   Actual profit: {actual_profit}")
                
                return TransactionResult(
                    success=True,
                    tx_hash=tx_hash.hex(),
                    gas_used=receipt.gasUsed,
                    actual_profit=actual_profit,
                    execution_time=execution_time
                )
            else:
                return TransactionResult(
                    success=False,
                    tx_hash=tx_hash.hex(),
                    gas_used=receipt.gasUsed,
                    error_message="Transaction reverted",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"❌ Flash loan arbitrage failed: {e}")
            return TransactionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def execute_triangular_arbitrage(
        self,
        token_a: str,
        token_b: str,
        token_c: str,
        amount_in: int,
        min_profit_bps: int
    ) -> TransactionResult:
        """
        Execute triangular arbitrage via TriangularArbitrage contract
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            if 'triangular_arbitrage' not in self.contracts:
                return TransactionResult(
                    success=False,
                    error_message="TriangularArbitrage contract not loaded"
                )
            
            contract = self.contracts['triangular_arbitrage']
            
            # Build transaction
            function = contract.functions.executeTriangularArbitrage(
                token_a,
                token_b,
                token_c,
                amount_in,
                min_profit_bps
            )
            
            # Estimate gas and execute similar to flash loan
            gas_estimate = function.estimate_gas({'from': self.account.address})
            gas_limit = int(gas_estimate * 1.2)
            
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.chain_id
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"📤 Triangular arbitrage transaction sent: {tx_hash.hex()}")
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            if receipt.status == 1:
                actual_profit = self._parse_profit_from_logs(receipt.logs)
                
                return TransactionResult(
                    success=True,
                    tx_hash=tx_hash.hex(),
                    gas_used=receipt.gasUsed,
                    actual_profit=actual_profit,
                    execution_time=execution_time
                )
            else:
                return TransactionResult(
                    success=False,
                    tx_hash=tx_hash.hex(),
                    gas_used=receipt.gasUsed,
                    error_message="Transaction reverted",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"❌ Triangular arbitrage failed: {e}")
            return TransactionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _parse_profit_from_logs(self, logs: list) -> Optional[float]:
        """Parse actual profit from transaction logs"""
        try:
            # Look for ArbitrageExecuted or FlashLoanArbitrageExecuted events
            for log in logs:
                # This would need to be implemented based on actual contract events
                # For now, return None to indicate profit parsing not implemented
                pass
            return None
        except Exception as e:
            logger.error(f"Failed to parse profit from logs: {e}")
            return None
    
    def get_contract_balance(self, contract_name: str) -> Optional[float]:
        """Get ETH balance of a contract"""
        if contract_name not in self.contracts:
            return None
        
        try:
            address = self.contracts[contract_name].address
            balance = self.w3.eth.get_balance(address)
            return float(self.w3.from_wei(balance, 'ether'))
        except Exception as e:
            logger.error(f"Failed to get balance for {contract_name}: {e}")
            return None
    
    def validate_transaction_parameters(
        self,
        amount: int,
        min_profit: int,
        gas_limit: int
    ) -> Tuple[bool, Optional[str]]:
        """Validate transaction parameters before execution"""
        
        # Check account balance
        balance = self.w3.eth.get_balance(self.account.address)
        gas_cost = gas_limit * self.w3.eth.gas_price
        
        if balance < gas_cost:
            return False, f"Insufficient ETH for gas: need {self.w3.from_wei(gas_cost, 'ether')} ETH"
        
        # Check amount is positive
        if amount <= 0:
            return False, "Amount must be positive"
        
        # Check min profit is reasonable
        if min_profit <= 0:
            return False, "Minimum profit must be positive"
        
        return True, None

# Global instance
web3_executor = Web3Executor()
