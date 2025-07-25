#!/usr/bin/env python3
"""
ATOM/ADOM Hybrid Bot (Option 2)
Off-chain calculation + On-chain execution via RPC calls
Calculates arbitrage opportunities and triggers smart contracts
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import aiohttp
from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ATOM_HYBRID_BOT')

@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity data structure"""
    token_a: str
    token_b: str
    token_c: str
    path: str
    spread_bps: float
    estimated_profit: float
    amount_in: float
    confidence: float
    dex_route: List[str]
    timestamp: float

@dataclass
class PriceData:
    """Price data from various sources"""
    token: str
    chainlink_price: float
    external_price: float
    implied_price: float
    spread_bps: float
    source: str
    timestamp: float

class AtomHybridBot:
    """
    ATOM/ADOM Hybrid Arbitrage Bot
    Calculates opportunities off-chain, executes on-chain
    """
    
    def __init__(self):
        # Base Sepolia configuration
        self.rpc_url = os.getenv('BASE_SEPOLIA_RPC', 'https://sepolia.base.org')
        self.private_key = os.getenv('PRIVATE_KEY')
        self.contract_addresses = {
            'triangular_arbitrage': os.getenv('ATOM_TRIANGULAR_ARBITRAGE_ADDRESS'),
            'price_monitor': os.getenv('ATOM_PRICE_MONITOR_ADDRESS'),
            'execution_engine': os.getenv('ATOM_EXECUTION_ENGINE_ADDRESS')
        }
        
        # Token addresses (Base Sepolia)
        self.tokens = {
            'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
            'USDC': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
            'WETH': '0x4200000000000000000000000000000000000006',
            'GHO': '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f'
        }
        
        # DEX APIs for price fetching
        self.price_apis = {
            '0x': 'https://api.0x.org/swap/v1/quote',
            '1inch': 'https://api.1inch.io/v5.0/8453/quote',
            'paraswap': 'https://apiv5.paraswap.io/prices'
        }
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            logger.info(f"🔑 Loaded account: {self.account.address}")
        
        # Trading parameters
        self.min_profit_bps = 23  # 0.23% minimum profit
        self.max_gas_price = Web3.toWei(50, 'gwei')
        self.max_slippage_bps = 300  # 3%
        self.min_trade_amount = Web3.toWei(100, 'ether')  # $100 minimum
        self.max_trade_amount = Web3.toWei(10000, 'ether')  # $10K maximum
        
        # Performance tracking
        self.total_opportunities = 0
        self.successful_executions = 0
        self.total_profit = 0.0
        self.start_time = time.time()
        
        logger.info("🤖 ATOM/ADOM Hybrid Bot initialized")
    
    async def fetch_external_prices(self) -> Dict[str, PriceData]:
        """Fetch prices from external APIs (0x, 1inch, etc.)"""
        prices = {}
        
        async with aiohttp.ClientSession() as session:
            for token_symbol, token_address in self.tokens.items():
                try:
                    # Fetch from 0x API
                    params = {
                        'sellToken': token_address,
                        'buyToken': self.tokens['USDC'],  # Price in USDC
                        'sellAmount': Web3.toWei(1, 'ether')  # 1 token
                    }
                    
                    async with session.get(self.price_apis['0x'], params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            buy_amount = float(data.get('buyAmount', 0))
                            
                            if buy_amount > 0:
                                price = buy_amount / 1e6  # USDC has 6 decimals
                                prices[token_symbol] = PriceData(
                                    token=token_address,
                                    chainlink_price=0,  # Will be fetched separately
                                    external_price=price,
                                    implied_price=0,
                                    spread_bps=0,
                                    source='0x_api',
                                    timestamp=time.time()
                                )
                                logger.debug(f"📊 {token_symbol} price from 0x: ${price:.4f}")
                
                except Exception as e:
                    logger.warning(f"⚠️  Failed to fetch {token_symbol} price from 0x: {e}")
                    
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.1)
        
        return prices
    
    def calculate_triangular_arbitrage(self, prices: Dict[str, PriceData]) -> List[ArbitrageOpportunity]:
        """Calculate triangular arbitrage opportunities"""
        opportunities = []
        
        # Define triangular paths
        triangular_paths = [
            ('DAI', 'USDC', 'GHO'),
            ('WETH', 'USDC', 'DAI'),
            ('USDC', 'DAI', 'GHO'),
            ('GHO', 'USDC', 'DAI'),
            ('WETH', 'DAI', 'USDC')
        ]
        
        for token_a, token_b, token_c in triangular_paths:
            try:
                if token_a not in prices or token_b not in prices or token_c not in prices:
                    continue
                
                # Get prices
                price_a = prices[token_a].external_price
                price_b = prices[token_b].external_price  
                price_c = prices[token_c].external_price
                
                if price_a <= 0 or price_b <= 0 or price_c <= 0:
                    continue
                
                # Calculate triangular arbitrage
                # A -> B -> C -> A
                amount_a = 1000.0  # Start with $1000
                amount_b = amount_a * (price_a / price_b)
                amount_c = amount_b * (price_b / price_c)
                final_amount_a = amount_c * (price_c / price_a)
                
                profit = final_amount_a - amount_a
                profit_bps = (profit / amount_a) * 10000
                
                if profit_bps >= self.min_profit_bps:
                    opportunity = ArbitrageOpportunity(
                        token_a=self.tokens[token_a],
                        token_b=self.tokens[token_b],
                        token_c=self.tokens[token_c],
                        path=f"{token_a} → {token_b} → {token_c} → {token_a}",
                        spread_bps=profit_bps,
                        estimated_profit=profit,
                        amount_in=amount_a,
                        confidence=85.0 + (profit_bps * 2),  # Higher profit = higher confidence
                        dex_route=['curve', 'balancer', 'uniswap'],
                        timestamp=time.time()
                    )
                    
                    opportunities.append(opportunity)
                    self.total_opportunities += 1
                    
                    logger.info(f"🎯 Found opportunity: {opportunity.path}")
                    logger.info(f"   Spread: {profit_bps:.2f} bps, Profit: ${profit:.2f}")
            
            except Exception as e:
                logger.error(f"❌ Error calculating triangular arbitrage for {token_a}-{token_b}-{token_c}: {e}")
        
        return opportunities
    
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> bool:
        """Execute arbitrage opportunity via smart contract"""
        try:
            if not self.private_key or not self.contract_addresses['triangular_arbitrage']:
                logger.warning("⚠️  Cannot execute: Missing private key or contract address")
                return False
            
            # Load contract ABI (simplified)
            triangular_arbitrage_abi = [
                {
                    "inputs": [
                        {
                            "components": [
                                {"name": "tokenA", "type": "address"},
                                {"name": "tokenB", "type": "address"},
                                {"name": "tokenC", "type": "address"},
                                {"name": "poolAB", "type": "address"},
                                {"name": "poolBC", "type": "address"},
                                {"name": "poolCA", "type": "address"},
                                {"name": "amountIn", "type": "uint256"},
                                {"name": "minProfitBps", "type": "uint256"},
                                {"name": "useBalancer", "type": "bool"},
                                {"name": "useCurve", "type": "bool"}
                            ],
                            "name": "path",
                            "type": "tuple"
                        }
                    ],
                    "name": "executeTriangularArbitrage",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            # Create contract instance
            contract = self.w3.eth.contract(
                address=self.contract_addresses['triangular_arbitrage'],
                abi=triangular_arbitrage_abi
            )
            
            # Prepare transaction data
            path_data = {
                'tokenA': opportunity.token_a,
                'tokenB': opportunity.token_b,
                'tokenC': opportunity.token_c,
                'poolAB': '0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E',  # Mock pool addresses
                'poolBC': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0',
                'poolCA': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                'amountIn': Web3.toWei(opportunity.amount_in, 'ether'),
                'minProfitBps': int(self.min_profit_bps),
                'useBalancer': False,
                'useCurve': True
            }
            
            # Build transaction
            transaction = contract.functions.executeTriangularArbitrage(path_data).buildTransaction({
                'from': self.account.address,
                'gas': 500000,
                'gasPrice': min(self.w3.eth.gas_price, self.max_gas_price),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"🚀 Arbitrage transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                logger.info(f"✅ Arbitrage executed successfully!")
                logger.info(f"   Gas used: {receipt.gasUsed:,}")
                logger.info(f"   Estimated profit: ${opportunity.estimated_profit:.2f}")
                
                self.successful_executions += 1
                self.total_profit += opportunity.estimated_profit
                return True
            else:
                logger.error(f"❌ Arbitrage transaction failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to execute arbitrage: {e}")
            return False
    
    async def monitor_and_execute(self):
        """Main monitoring and execution loop"""
        logger.info("🔄 Starting ATOM/ADOM hybrid monitoring loop")
        
        while True:
            try:
                # Fetch external prices
                logger.debug("📊 Fetching external prices...")
                prices = await self.fetch_external_prices()
                
                if not prices:
                    logger.warning("⚠️  No price data available, retrying...")
                    await asyncio.sleep(10)
                    continue
                
                # Calculate arbitrage opportunities
                opportunities = self.calculate_triangular_arbitrage(prices)
                
                if opportunities:
                    logger.info(f"🎯 Found {len(opportunities)} arbitrage opportunities")
                    
                    # Sort by profitability
                    opportunities.sort(key=lambda x: x.estimated_profit, reverse=True)
                    
                    # Execute the most profitable opportunity
                    best_opportunity = opportunities[0]
                    
                    if best_opportunity.spread_bps >= self.min_profit_bps:
                        logger.info(f"🚀 Executing best opportunity: {best_opportunity.path}")
                        success = await self.execute_arbitrage(best_opportunity)
                        
                        if success:
                            logger.info("✅ Arbitrage execution completed successfully")
                        else:
                            logger.warning("⚠️  Arbitrage execution failed")
                else:
                    logger.debug("📊 No profitable opportunities found")
                
                # Print performance stats every 10 minutes
                if int(time.time()) % 600 == 0:
                    self.print_performance_stats()
                
                # Wait before next iteration
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    def print_performance_stats(self):
        """Print performance statistics"""
        runtime = time.time() - self.start_time
        success_rate = (self.successful_executions / max(self.total_opportunities, 1)) * 100
        
        logger.info("📊 ATOM/ADOM PERFORMANCE STATS")
        logger.info(f"   Runtime: {runtime/3600:.1f} hours")
        logger.info(f"   Total opportunities: {self.total_opportunities}")
        logger.info(f"   Successful executions: {self.successful_executions}")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        logger.info(f"   Total profit: ${self.total_profit:.2f}")
        logger.info(f"   Avg profit per execution: ${self.total_profit/max(self.successful_executions, 1):.2f}")

async def main():
    """Main entry point"""
    logger.info("🤖 Starting ATOM/ADOM Hybrid Bot")
    logger.info("🔁 Option 2: Off-chain calculation + On-chain execution")
    
    bot = AtomHybridBot()
    
    try:
        await bot.monitor_and_execute()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        bot.print_performance_stats()
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        bot.print_performance_stats()

if __name__ == "__main__":
    asyncio.run(main())
