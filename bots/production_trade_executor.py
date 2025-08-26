#!/usr/bin/env python3
"""
Production Trade Executor - Real Polygon Mainnet Trade Execution
SECURE: Environment Variables Only - NO HARDCODED SECRETS
"""

import asyncio
import json
import logging
import os
import sys
import time
from decimal import Decimal
from typing import Dict, Optional
from web3 import Web3
from eth_account import Account
import redis

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.secure_config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionTradeExecutor:
    def __init__(self):
        self.config = config
        self.setup_web3()
        self.setup_redis()
        self.setup_contract()
        self.setup_wallets()
        self.current_wallet_index = 0
        self.running = False
        self.trade_history = []
        
    def setup_web3(self):
        """Initialize Web3 connection - SECURE: Environment Variables Only"""
        self.polygon_rpc = self.config.get('polygon_rpc_url')
        if not self.polygon_rpc:
            raise ValueError("POLYGON_RPC_URL environment variable required")

        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        if not self.w3.is_connected():
            # Try backup RPC
            backup_rpc = self.config.get('polygon_rpc_backup')
            if backup_rpc:
                self.w3 = Web3(Web3.HTTPProvider(backup_rpc))
                if not self.w3.is_connected():
                    raise Exception("Failed to connect to Polygon RPC (primary and backup)")
            else:
                raise Exception("Failed to connect to Polygon RPC")

        # Validate Polygon mainnet
        chain_id = self.w3.eth.chain_id
        if chain_id != 137:
            raise ValueError(f"Connected to wrong network. Expected Polygon (137), got {chain_id}")


        # Load configuration from secure config
        self.min_profit_bps = self.config.get('min_profit_threshold_bps')
        self.min_trade_size_usd = self.config.get('min_trade_size_usd')
        self.target_net_profit = self.config.get('target_net_profit')
        self.max_gas_price = self.config.get('max_gas_price') * 10**9  # Convert to wei
        self.gas_price_multiplier = self.config.get('gas_price_multiplier')
        self.max_gas_limit = self.config.get('max_gas_limit')
        self.max_gas_cost_usd = self.config.get('max_gas_cost_usd')
        self.execution_timeout = self.config.get('execution_timeout')

        # Contract address from environment
        self.flash_loan_contract_address = self.config.get('flashloan_contract')
        if not self.flash_loan_contract_address:
            raise ValueError("FLASHLOAN_ARB_ADDR environment variable required")

        # Risk management from config
        self.max_single_trade_loss = self.config.get('max_single_trade_loss_usd')
        self.max_daily_loss = self.config.get('max_daily_loss_usd')

    def setup_redis(self):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

        # Test Redis connection
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {e}")
        
    def setup_contract(self):
        """Initialize flash loan contract"""
        # Flash loan contract ABI
        self.flash_loan_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "asset", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "bytes", "name": "params", "type": "bytes"}
                ],
                "name": "executeFlashLoanArbitrage",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        self.flash_loan_contract = self.w3.eth.contract(
            address=self.flash_loan_contract_address,
            abi=self.flash_loan_abi
        )
        
    def setup_wallets(self):
        """Initialize wallet system - SECURE: Environment Variables Only"""
        self.wallets = []

        # Load main wallet from secure config
        private_key = self.config.get('private_key')
        if not private_key:
            raise ValueError("PRIVATE_KEY environment variable required")

        try:
            account = Account.from_key(private_key)
            self.wallets.append({
                'account': account,
                'address': account.address,
                'private_key': private_key,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'last_used': 0,
                'total_profit': Decimal('0')
            })
            logger.info(f"✅ Loaded main wallet: {account.address}")
        except Exception as e:
            raise ValueError(f"Invalid private key: {e}")

        if not self.wallets:
            raise Exception("No valid wallets configured!")
            
    def get_current_wallet(self):
        """Get current wallet for trading"""
        return self.wallets[self.current_wallet_index]
        
    def rotate_wallet(self):
        """Rotate to next wallet"""
        if len(self.wallets) > 1:
            self.current_wallet_index = (self.current_wallet_index + 1) % len(self.wallets)
            logger.info(f"Rotated to wallet: {self.get_current_wallet()['address']}")
        
    def estimate_gas_cost(self) -> Decimal:
        """Estimate gas cost for arbitrage transaction - AAVE optimized"""
        try:
            gas_price = self.w3.eth.gas_price
            if gas_price > self.max_gas_price:
                logger.warning(f"Gas price {gas_price/10**9:.1f} gwei exceeds maximum {self.max_gas_price/10**9:.1f}")
                return Decimal('-1')

            # Premium gas estimation for AAVE flash loans
            estimated_gas = self.max_gas_limit  # 600,000 gas for complex arbitrage
            premium_gas_price = int(gas_price * self.gas_price_multiplier)  # 20% premium
            gas_cost_wei = premium_gas_price * estimated_gas
            gas_cost_matic = Decimal(gas_cost_wei) / Decimal(10**18)

            # Convert to USD (approximate MATIC price)
            matic_price_usd = Decimal('0.8')
            gas_cost_usd = gas_cost_matic * matic_price_usd

            # Cap at maximum gas budget
            if gas_cost_usd > self.max_gas_cost_usd:
                logger.warning(f"Gas cost ${gas_cost_usd:.2f} exceeds budget ${self.max_gas_cost_usd}")
                return Decimal('-1')

            return gas_cost_usd

        except Exception as e:
            logger.error(f"Error estimating gas cost: {e}")
            return self.max_gas_cost_usd
            
    def encode_arbitrage_params(self, opportunity: Dict) -> bytes:
        """Encode arbitrage parameters for smart contract"""
        # Map DEX names to enum values
        dex_mapping = {
            'uniswap_v3': 0,
            'quickswap': 1,
            'sushiswap': 2,
            'balancer': 3
        }
        
        # Encode parameters as ABI-encoded struct
        from eth_abi import encode_abi
        
        param_types = [
            'address',  # tokenA
            'address',  # tokenB
            'address',  # tokenC
            'uint8',    # dexA
            'uint8',    # dexB
            'uint8',    # dexC
            'uint24',   # feeA
            'uint24',   # feeB
            'uint24',   # feeC
            'bytes32',  # poolIdA
            'bytes32',  # poolIdB
            'bytes32',  # poolIdC
            'uint256'   # minProfitBps
        ]
        
        param_values = [
            opportunity['token_a'],
            opportunity['token_b'],
            opportunity['token_c'],
            dex_mapping[opportunity['dex_a']],
            dex_mapping[opportunity['dex_b']],
            dex_mapping[opportunity['dex_c']],
            3000,  # Default Uniswap V3 fee
            3000,
            3000,
            b'\x00' * 32,  # Default empty pool ID
            b'\x00' * 32,
            b'\x00' * 32,
            int(self.min_profit_bps)
        ]
        
        return encode_abi(param_types, param_values)
        
    async def execute_arbitrage(self, opportunity: Dict) -> bool:
        """Execute arbitrage opportunity"""
        wallet = self.get_current_wallet()
        
        try:
            # Estimate gas cost
            gas_cost_usd = self.estimate_gas_cost()
            if gas_cost_usd == -1:
                logger.warning("Gas price too high, skipping trade")
                return False

            # Calculate expected profit after AAVE fees and gas
            expected_profit_usd = Decimal(opportunity['profit']) / Decimal(10**18) * Decimal('2500')  # ETH price
            aave_fee_usd = Decimal(opportunity['amount_in']) / Decimal(10**18) * Decimal('2500') * Decimal('0.0009')  # 0.09%
            net_profit = expected_profit_usd - gas_cost_usd - aave_fee_usd

            # HIGH VALUE FILTER: Must meet minimum net profit
            if net_profit < self.target_net_profit:
                logger.debug(f"Trade below target: ${net_profit:.2f} < ${self.target_net_profit}")
                return False
                
            logger.info(f"🚀 AAVE FLASH LOAN: {opportunity['token_a_name']}->{opportunity['token_b_name']}->{opportunity['token_c_name']}")
            logger.info(f"Trade Size: ${Decimal(opportunity['amount_in'])/Decimal(10**18)*Decimal('2500'):.0f}")
            logger.info(f"Expected: ${expected_profit_usd:.2f}, AAVE: ${aave_fee_usd:.2f}, Gas: ${gas_cost_usd:.2f}, Net: ${net_profit:.2f}")
            
            # Encode parameters
            params = self.encode_arbitrage_params(opportunity)
            
            # Build transaction
            transaction = self.flash_loan_contract.functions.executeFlashLoanArbitrage(
                opportunity['token_a'],
                opportunity['amount_in'],
                params
            ).build_transaction({
                'from': wallet['address'],
                'gas': self.max_gas_limit,
                'gasPrice': int(self.w3.eth.gas_price * self.gas_price_multiplier),
                'nonce': wallet['nonce']
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, wallet['private_key'])
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                logger.info(f"✅ Arbitrage successful! Gas used: {receipt.gasUsed}")
                
                # Update wallet
                wallet['nonce'] += 1
                wallet['last_used'] = time.time()
                wallet['total_profit'] += net_profit
                
                # Record trade
                trade_record = {
                    'timestamp': time.time(),
                    'tx_hash': tx_hash.hex(),
                    'wallet': wallet['address'],
                    'opportunity': opportunity,
                    'gas_used': receipt.gasUsed,
                    'gas_cost_usd': float(gas_cost_usd),
                    'expected_profit_usd': float(expected_profit_usd),
                    'net_profit_usd': float(net_profit),
                    'success': True
                }
                
                self.trade_history.append(trade_record)
                self.redis_client.lpush('trade_history', json.dumps(trade_record))
                
                # Rotate wallet after successful trade
                if net_profit > 10:
                    self.rotate_wallet()
                    
                return True
            else:
                logger.error(f"❌ Transaction failed: {tx_hash.hex()}")
                wallet['nonce'] += 1
                return False
                
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}")
            return False
            
    async def monitor_opportunities(self):
        """Monitor Redis for opportunities and execute them"""
        logger.info("🔍 Monitoring for arbitrage opportunities...")
        
        while self.running:
            try:
                # Get opportunity from Redis
                opportunity_data = self.redis_client.lpop('arbitrage_opportunities')
                
                if opportunity_data:
                    opportunity = json.loads(opportunity_data)
                    
                    # Check if opportunity is still fresh (< 30 seconds)
                    if time.time() - opportunity['timestamp'] < 30:
                        # Check profit threshold
                        if opportunity['profit_bps'] >= self.min_profit_bps:
                            success = await self.execute_arbitrage(opportunity)
                            if success:
                                logger.info(f"🎉 Successful arbitrage execution!")
                    else:
                        logger.debug("Opportunity too old, skipping")
                        
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Error monitoring opportunities: {e}")
                await asyncio.sleep(1)
                
    async def start(self):
        """Start the trade execution system"""
        self.running = True
        logger.info("🚀 Production Trade Executor Starting...")
        
        try:
            await self.monitor_opportunities()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
            
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        successful_trades = len([t for t in self.trade_history if t['success']])
        total_trades = len(self.trade_history)
        total_profit = sum(t['net_profit_usd'] for t in self.trade_history if t['success'])
        
        return {
            'total_trades': total_trades,
            'successful_trades': successful_trades,
            'success_rate': (successful_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_profit_usd': total_profit,
            'current_wallet': self.get_current_wallet()['address']
        }

if __name__ == "__main__":
    executor = ProductionTradeExecutor()
    asyncio.run(executor.start())
