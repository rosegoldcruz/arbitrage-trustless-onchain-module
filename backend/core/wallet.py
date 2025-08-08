"""
🔐 ATOM Secure Wallet Integration - Real Private Key Management
Secure wallet operations with private key management and transaction signing
"""

import os
import logging
from typing import Dict, Optional, Any
from decimal import Decimal
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SecureWallet:
    """Secure wallet management with private key integration"""

    def __init__(self):
        self.account: Optional[LocalAccount] = None
        self.web3_connections: Dict[str, Web3] = {}
        self.is_initialized = False
        self.wallet_address = None

    @classmethod
    def from_env(cls) -> 'SecureWallet':
        """Create wallet from environment variables"""
        wallet = cls()
        return wallet
        
    async def initialize_wallet(self):
        """Initialize wallet with private key from environment"""
        try:
            logger.info("🔐 Initializing Secure Wallet...")
            
            # Get private key from environment
            private_key = os.getenv("PRIVATE_KEY")
            if not private_key:
                raise ValueError("PRIVATE_KEY not found in environment variables")
            
            # Ensure private key has 0x prefix
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            
            # Create account from private key
            self.account = Account.from_key(private_key)
            self.wallet_address = self.account.address
            
            logger.info(f"✅ Wallet initialized: {self.wallet_address}")
            
            # Initialize Web3 connections
            await self.initialize_web3_connections()
            
            self.is_initialized = True
            logger.info("🔐 Secure wallet fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize wallet: {e}")
            raise
    
    async def initialize_web3_connections(self):
        """Initialize Web3 connections for different networks"""
        try:
            # Network configurations with your real API keys
            networks = {
                "ethereum": {
                    "rpc_url": f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                    "chain_id": 1,
                    "name": "Ethereum Mainnet"
                },
                "base_sepolia": {
                    "rpc_url": os.getenv("BASE_SEPOLIA_RPC_URL"),
                    "chain_id": 84532,
                    "name": "Base Sepolia"
                },
                "polygon": {
                    "rpc_url": f"https://polygon-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                    "chain_id": 137,
                    "name": "Polygon Mainnet"
                },
                "arbitrum": {
                    "rpc_url": f"https://arb-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                    "chain_id": 42161,
                    "name": "Arbitrum One"
                }
            }
            
            for network_name, config in networks.items():
                if not config["rpc_url"]:
                    logger.warning(f"⚠️ No RPC URL for {network_name}")
                    continue
                
                try:
                    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
                    
                    # Add PoA middleware for networks that need it
                    if network_name in ["polygon", "base_sepolia"]:
                        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                    
                    # Test connection
                    if w3.is_connected():
                        latest_block = w3.eth.block_number
                        self.web3_connections[network_name] = w3
                        logger.info(f"✅ Connected to {config['name']} - Block: {latest_block}")
                    else:
                        logger.error(f"❌ Failed to connect to {config['name']}")
                        
                except Exception as e:
                    logger.error(f"❌ Error connecting to {config['name']}: {e}")
            
            logger.info(f"🌐 Initialized {len(self.web3_connections)} network connections")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Web3 connections: {e}")
            raise
    
    async def get_balance(self, network: str = "ethereum", token_address: Optional[str] = None) -> float:
        """Get wallet balance for native token or ERC20"""
        try:
            if network not in self.web3_connections:
                raise ValueError(f"Network {network} not available")
            
            w3 = self.web3_connections[network]
            
            if token_address is None:
                # Get native token balance (ETH, MATIC, etc.)
                balance_wei = w3.eth.get_balance(self.wallet_address)
                balance_eth = w3.from_wei(balance_wei, 'ether')
                return float(balance_eth)
            else:
                # Get ERC20 token balance
                # ERC20 ABI for balanceOf function
                erc20_abi = [
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "type": "function"
                    },
                    {
                        "constant": True,
                        "inputs": [],
                        "name": "decimals",
                        "outputs": [{"name": "", "type": "uint8"}],
                        "type": "function"
                    }
                ]
                
                contract = w3.eth.contract(address=token_address, abi=erc20_abi)
                balance = contract.functions.balanceOf(self.wallet_address).call()
                decimals = contract.functions.decimals().call()
                
                return float(balance / (10 ** decimals))
                
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return 0.0
    
    async def sign_transaction(self, transaction: Dict[str, Any], network: str = "ethereum") -> str:
        """Sign a transaction with the wallet's private key"""
        try:
            if not self.is_initialized:
                raise ValueError("Wallet not initialized")
            
            if network not in self.web3_connections:
                raise ValueError(f"Network {network} not available")
            
            w3 = self.web3_connections[network]
            
            # Get current nonce
            nonce = w3.eth.get_transaction_count(self.wallet_address)
            
            # Prepare transaction
            tx = {
                'nonce': nonce,
                'gasPrice': w3.eth.gas_price,
                'gas': transaction.get('gas', 21000),
                'to': transaction['to'],
                'value': transaction.get('value', 0),
                'data': transaction.get('data', '0x'),
                'chainId': w3.eth.chain_id
            }
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(tx)
            
            logger.info(f"✅ Transaction signed: {signed_txn.hash.hex()}")
            return signed_txn.rawTransaction.hex()

        except Exception as e:
            logger.error(f"❌ Error signing transaction: {e}")
            raise

    async def sign_and_send(self, transaction: Dict[str, Any], network: str = "base_sepolia") -> str:
        """Sign and send a transaction"""
        try:
            if not self.is_initialized:
                raise ValueError("Wallet not initialized")

            if network not in self.web3_connections:
                raise ValueError(f"Network {network} not available")

            w3 = self.web3_connections[network]

            # Get current nonce
            nonce = w3.eth.get_transaction_count(self.wallet_address)

            # Prepare transaction
            tx = {
                'nonce': nonce,
                'gasPrice': w3.eth.gas_price,
                'gas': transaction.get('gas', 21000),
                'to': transaction['to'],
                'value': transaction.get('value', 0),
                'data': transaction.get('data', '0x'),
                'chainId': w3.eth.chain_id
            }

            # Sign transaction
            signed_tx = self.account.sign_transaction(tx)

            # Send transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            logger.info(f"✅ Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"❌ Transaction failed: {e}")
            raise

# Singleton instance
secure_wallet = SecureWallet()
