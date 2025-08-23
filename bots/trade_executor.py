#!/usr/bin/env python3
"""
Polygon Arbitrage Trade Execution Bot
Automatically executes profitable arbitrage opportunities
"""

import asyncio
import json
import logging
import os
import time
from decimal import Decimal
from typing import Dict, List, Optional
from web3 import Web3
from eth_account import Account
import redis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self):
        self.load_config()
        self.setup_web3()
        self.setup_contracts()
        self.setup_redis()
        self.setup_wallets()
        self.current_wallet_index = 0
        self.running = False
        self.trade_history = []
        
    def load_config(self):
        """Load configuration from environment variables"""
        self.polygon_rpc = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
        self.min_profit_bps = Decimal(os.getenv('ATOM_MIN_PROFIT_THRESHOLD_BPS', '23'))
        self.max_gas_price = int(os.getenv('ATOM_MAX_GAS_PRICE', '100')) * 10**9  # Convert to wei
        self.gas_price_multiplier = Decimal(os.getenv('GAS_PRICE_MULTIPLIER', '1.1'))
        self.max_gas_limit = int(os.getenv('MAX_GAS_LIMIT', '500000'))
        
        # Flash loan contract
        self.flash_loan_contract_address = os.getenv('ATOM_CONTRACT_ADDRESS')
        if not self.flash_loan_contract_address:
            raise ValueError("ATOM_CONTRACT_ADDRESS environment variable is required")
        
        # Risk management
        self.max_single_trade_loss = Decimal(os.getenv('MAX_SINGLE_TRADE_LOSS_USD', '50'))
        self.max_daily_loss = Decimal(os.getenv('MAX_DAILY_LOSS_USD', '200'))
        
    def setup_web3(self):
        """Initialize Web3 connection"""
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Polygon RPC")
        logger.info(f"Connected to Polygon network, block: {self.w3.eth.block_number}")
        
    def setup_contracts(self):
        """Initialize contract instances"""
        # Flash loan contract ABI (simplified)
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
            },
            {
                "inputs": [],
                "name": "getStats",
                "outputs": [
                    {"internalType": "uint256", "name": "_totalTrades", "type": "uint256"},
                    {"internalType": "uint256", "name": "_successfulTrades", "type": "uint256"},
                    {"internalType": "uint256", "name": "_totalProfit", "type": "uint256"},
                    {"internalType": "uint256", "name": "_successRate", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.flash_loan_contract = self.w3.eth.contract(
            address=self.flash_loan_contract_address,
            abi=self.flash_loan_abi
        )
        
    def setup_redis(self):
        """Initialize Redis connection for shared state"""
        redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    def setup_wallets(self):
        """Initialize wallet rotation system"""
        self.wallets = []
        for i in range(1, 6):  # Support up to 5 wallets
            private_key = os.getenv(f'WALLET_PRIVATE_KEY_{i}')
            if private_key and private_key != f'YOUR_ROTATION_WALLET_{i}_PRIVATE_KEY_HERE':
                account = Account.from_key(private_key)
                self.wallets.append({
                    'account': account,
                    'address': account.address,
                    'private_key': private_key,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'last_used': 0,
                    'total_profit': Decimal('0')
                })
                logger.info(f"Loaded wallet {i}: {account.address}")
        
        if not self.wallets:
            raise Exception("No valid wallets configured!")
            
    def get_current_wallet(self):
        """Get current wallet for trading"""
        return self.wallets[self.current_wallet_index]
        
    def rotate_wallet(self):
        """Rotate to next wallet"""
        self.current_wallet_index = (self.current_wallet_index + 1) % len(self.wallets)
        logger.info(f"Rotated to wallet: {self.get_current_wallet()['address']}")
        
    def estimate_gas_cost(self) -> Decimal:
        """Estimate gas cost for arbitrage transaction"""
        try:
            gas_price = self.w3.eth.gas_price
            if gas_price > self.max_gas_price:
                logger.warning(f"Gas price {gas_price/10**9:.1f} gwei exceeds maximum {self.max_gas_price/10**9:.1f} gwei")
                return Decimal('-1')  # Signal to skip
                
            # Estimate gas cost in ETH
            estimated_gas = self.max_gas_limit
            gas_cost_wei = int(gas_price * self.gas_price_multiplier) * estimated_gas
            gas_cost_eth = Decimal(gas_cost_wei) / Decimal(10**18)
            
            # Convert to USD (approximate MATIC price)
            matic_price_usd = Decimal('0.8')  # Approximate, should be fetched from API
            gas_cost_usd = gas_cost_eth * matic_price_usd
            
            return gas_cost_usd
            
        except Exception as e:
            logger.error(f"Error estimating gas cost: {e}")
            return Decimal('10')  # Conservative estimate
            
    def encode_arbitrage_params(self, opportunity: Dict) -> bytes:
        """Encode arbitrage parameters for smart contract"""
        # Map DEX names to enum values
        dex_mapping = {
            'uniswap_v3': 0,
            'quickswap': 1,
            'sushiswap': 2,
            'balancer': 3
        }
        
        # Create arbitrage parameters struct
        params = {
            'tokenA': opportunity['token_a'],
            'tokenB': opportunity['token_b'],
            'tokenC': opportunity['token_c'],
            'dexA': dex_mapping[opportunity['dex_a']],
            'dexB': dex_mapping[opportunity['dex_b']],
            'dexC': dex_mapping[opportunity['dex_c']],
            'feeA': 3000,  # Default Uniswap V3 fee
            'feeB': 3000,
            'feeC': 3000,
            'poolIdA': b'\x00' * 32,  # Default empty pool ID for Balancer
            'poolIdB': b'\x00' * 32,
            'poolIdC': b'\x00' * 32,
            'minProfitBps': int(self.min_profit_bps)
        }
        
        # Encode parameters (simplified - in production use proper ABI encoding)
        return json.dumps(params).encode('utf-8')
        
    async def execute_arbitrage(self, opportunity: Dict) -> bool:
        """Execute arbitrage opportunity"""
        wallet = self.get_current_wallet()
        
        try:
            # Estimate gas cost
            gas_cost_usd = self.estimate_gas_cost()
            if gas_cost_usd == -1:
                logger.warning("Gas price too high, skipping trade")
                return False
                
            # Calculate expected profit after gas
            expected_profit_usd = Decimal(opportunity['profit']) / Decimal(10**18)  # Convert from wei
            net_profit = expected_profit_usd - gas_cost_usd
            
            if net_profit <= 0:
                logger.info(f"Trade not profitable after gas costs: {net_profit:.4f} USD")
                return False
                
            logger.info(f"🚀 Executing arbitrage: {opportunity['token_a_name']}->{opportunity['token_b_name']}->{opportunity['token_c_name']}")
            logger.info(f"Expected profit: ${expected_profit_usd:.4f}, Gas cost: ${gas_cost_usd:.4f}, Net: ${net_profit:.4f}")
            
            # Encode arbitrage parameters
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
                
                # Update wallet nonce
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
                
                # Store in Redis
                self.redis_client.lpush('trade_history', json.dumps(trade_record))
                
                # Rotate wallet after successful trade
                if net_profit > 10:  # Rotate after $10+ profit
                    self.rotate_wallet()
                    
                return True
            else:
                logger.error(f"❌ Transaction failed: {tx_hash.hex()}")
                wallet['nonce'] += 1  # Still increment nonce
                return False
                
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}")
            return False
            
    async def monitor_opportunities(self):
        """Monitor Redis for new opportunities and execute them"""
        logger.info("🔍 Monitoring for arbitrage opportunities...")
        
        while self.running:
            try:
                # Get opportunities from Redis (published by opportunity detector)
                opportunity_data = self.redis_client.lpop('arbitrage_opportunities')
                
                if opportunity_data:
                    opportunity = json.loads(opportunity_data)
                    
                    # Validate opportunity is still fresh (< 10 seconds old)
                    if time.time() - opportunity['timestamp'] < 10:
                        # Check if profit meets threshold
                        if opportunity['profit_bps'] >= self.min_profit_bps:
                            success = await self.execute_arbitrage(opportunity)
                            if success:
                                logger.info(f"🎉 Successful arbitrage execution!")
                            else:
                                logger.warning(f"⚠️ Arbitrage execution failed")
                    else:
                        logger.debug("Opportunity too old, skipping")
                        
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Error monitoring opportunities: {e}")
                await asyncio.sleep(1)
                
    async def start(self):
        """Start the trade execution bot"""
        self.running = True
        logger.info("🤖 Trade Execution Bot Starting...")
        
        # Start monitoring task
        monitor_task = asyncio.create_task(self.monitor_opportunities())
        
        try:
            await monitor_task
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
            monitor_task.cancel()
            
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
            'active_wallets': len(self.wallets),
            'current_wallet': self.get_current_wallet()['address']
        }

if __name__ == "__main__":
    executor = TradeExecutor()
    asyncio.run(executor.start())
