#!/usr/bin/env python3
"""
ATOM Bot - Advanced Trading Optimization Module
Hybrid execution system that triggers smart contracts with off-chain intelligence
Part of AEON Network Option 2 ecosystem
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import aiohttp
import websockets
from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    token_a: str
    token_b: str
    token_c: str
    amount_in: int
    spread_bps: int
    estimated_profit: float
    gas_estimate: int
    dex_path: str
    confidence: float
    detected_at: float

@dataclass
class ATOMConfig:
    # Network Configuration
    rpc_url: str
    wss_url: str
    chain_id: int
    private_key: str
    contract_address: str
    
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

class ATOMBot:
    """
    ATOM - Advanced Trading Optimization Module
    Hybrid bot that combines off-chain analysis with on-chain execution
    """
    
    def __init__(self, config: ATOMConfig):
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract ABI
        self.contract_abi = self._load_contract_abi()
        self.contract = self.w3.eth.contract(
            address=config.contract_address,
            abi=self.contract_abi
        )
        
        # Bot state
        self.is_running = False
        self.opportunities: List[ArbitrageOpportunity] = []
        self.execution_stats = {
            'total_scans': 0,
            'opportunities_found': 0,
            'executions_attempted': 0,
            'successful_executions': 0,
            'total_profit': 0.0,
            'total_gas_spent': 0
        }
        
        # Token addresses (Base Sepolia)
        self.tokens = {
            'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
            'USDC': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
            'WETH': '0x4200000000000000000000000000000000000006',
            'GHO': '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f'
        }
        
        logger.info(f"🔁 ATOM Bot initialized for {config.chain_id}")
        logger.info(f"Contract: {config.contract_address}")
        logger.info(f"Min Spread: {config.min_spread_bps} bps")

    def _load_contract_abi(self) -> List[Dict]:
        """Load contract ABI from artifacts"""
        try:
            # In production, load from compiled artifacts
            return [
                {
                    "inputs": [
                        {"name": "tokenA", "type": "address"},
                        {"name": "tokenB", "type": "address"},
                        {"name": "tokenC", "type": "address"},
                        {"name": "amount", "type": "uint256"}
                    ],
                    "name": "executeTriangularArbitrageWithAEON",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "getEcosystemHealth",
                    "outputs": [
                        {"name": "totalExecutions", "type": "uint256"},
                        {"name": "successfulExecutions", "type": "uint256"},
                        {"name": "totalProfitUSD", "type": "uint256"},
                        {"name": "isHealthy", "type": "bool"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
        except Exception as e:
            logger.error(f"Failed to load contract ABI: {e}")
            return []

    async def start(self):
        """Start the ATOM bot"""
        logger.info("🚀 Starting ATOM Bot...")
        self.is_running = True
        
        # Start parallel tasks
        tasks = [
            self._opportunity_scanner(),
            self._execution_engine(),
            self._health_monitor(),
            self._stats_reporter()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 ATOM Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ ATOM Bot error: {e}")
        finally:
            self.is_running = False

    async def _opportunity_scanner(self):
        """Continuously scan for arbitrage opportunities"""
        logger.info("🔍 Starting opportunity scanner...")
        
        while self.is_running:
            try:
                self.execution_stats['total_scans'] += 1
                
                # Scan triangular arbitrage paths
                opportunities = await self._scan_triangular_paths()
                
                # Filter profitable opportunities
                profitable_opps = [
                    opp for opp in opportunities 
                    if opp.spread_bps >= self.config.min_spread_bps
                ]
                
                if profitable_opps:
                    logger.info(f"📈 Found {len(profitable_opps)} profitable opportunities")
                    self.opportunities.extend(profitable_opps)
                    self.execution_stats['opportunities_found'] += len(profitable_opps)
                
                await asyncio.sleep(self.config.scan_interval)
                
            except Exception as e:
                logger.error(f"Scanner error: {e}")
                await asyncio.sleep(5)

    async def _scan_triangular_paths(self) -> List[ArbitrageOpportunity]:
        """Scan predefined triangular arbitrage paths"""
        opportunities = []
        
        # High-volume triangular paths
        paths = [
            ('DAI', 'USDC', 'GHO'),   # DAI → USDC → GHO → DAI
            ('WETH', 'USDC', 'DAI'),  # WETH → USDC → DAI → WETH
            ('USDC', 'DAI', 'GHO')    # USDC → DAI → GHO → USDC
        ]
        
        for token_a, token_b, token_c in paths:
            try:
                opportunity = await self._analyze_triangular_path(token_a, token_b, token_c)
                if opportunity:
                    opportunities.append(opportunity)
            except Exception as e:
                logger.error(f"Error analyzing path {token_a}→{token_b}→{token_c}: {e}")
        
        return opportunities

    async def _analyze_triangular_path(self, token_a: str, token_b: str, token_c: str) -> Optional[ArbitrageOpportunity]:
        """Analyze a specific triangular arbitrage path"""
        try:
            # Get prices from 0x API
            prices = await self._get_0x_prices([token_a, token_b, token_c])
            
            if not all(prices.values()):
                return None
            
            # Calculate triangular arbitrage
            amount_in = 10_000 * 10**18  # $10k test amount
            
            # A → B → C → A calculation
            amount_b = amount_in * prices[f"{token_a}_USDC"] / prices[f"{token_b}_USDC"]
            amount_c = amount_b * prices[f"{token_b}_USDC"] / prices[f"{token_c}_USDC"]
            final_amount = amount_c * prices[f"{token_c}_USDC"] / prices[f"{token_a}_USDC"]
            
            # Calculate profit and spread
            profit = final_amount - amount_in
            spread_bps = int((profit / amount_in) * 10000) if amount_in > 0 else 0
            
            if spread_bps < self.config.min_spread_bps:
                return None
            
            # Estimate gas and confidence
            gas_estimate = 450_000  # Triangular arbitrage gas estimate
            confidence = min(95.0, 70.0 + (spread_bps - 23) * 0.5)  # Higher spread = higher confidence
            
            return ArbitrageOpportunity(
                token_a=self.tokens[token_a],
                token_b=self.tokens[token_b],
                token_c=self.tokens[token_c],
                amount_in=amount_in,
                spread_bps=spread_bps,
                estimated_profit=profit / 10**18,  # Convert to human readable
                gas_estimate=gas_estimate,
                dex_path=f"Curve → Balancer → Curve",
                confidence=confidence,
                detected_at=time.time()
            )
            
        except Exception as e:
            logger.error(f"Error in triangular analysis: {e}")
            return None

    async def _get_0x_prices(self, tokens: List[str]) -> Dict[str, float]:
        """Get token prices from 0x API"""
        prices = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for token in tokens:
                    if token == 'USDC':
                        prices[f"{token}_USDC"] = 1.0
                        continue
                    
                    url = "https://api.0x.org/swap/v1/price"
                    params = {
                        'sellToken': self.tokens[token],
                        'buyToken': self.tokens['USDC'],
                        'sellAmount': str(10**18)  # 1 token
                    }
                    headers = {'0x-api-key': self.config.theatom_api_key}
                    
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            prices[f"{token}_USDC"] = float(data.get('price', 1.0))
                        else:
                            # Fallback prices
                            fallback_prices = {'DAI': 1.0, 'GHO': 1.0, 'WETH': 2000.0}
                            prices[f"{token}_USDC"] = fallback_prices.get(token, 1.0)
        
        except Exception as e:
            logger.error(f"Error fetching 0x prices: {e}")
            # Return fallback prices
            for token in tokens:
                fallback_prices = {'DAI': 1.0, 'USDC': 1.0, 'GHO': 1.0, 'WETH': 2000.0}
                prices[f"{token}_USDC"] = fallback_prices.get(token, 1.0)
        
        return prices

    async def _execution_engine(self):
        """Execute profitable arbitrage opportunities"""
        logger.info("⚡ Starting execution engine...")
        
        while self.is_running:
            try:
                if self.opportunities:
                    # Get best opportunity
                    best_opp = max(self.opportunities, key=lambda x: x.spread_bps)
                    self.opportunities.remove(best_opp)
                    
                    # Check if opportunity is still valid (not too old)
                    if time.time() - best_opp.detected_at < 60:  # 1 minute max age
                        await self._execute_arbitrage(best_opp)
                    else:
                        logger.info(f"⏰ Opportunity expired: {best_opp.spread_bps} bps")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Execution engine error: {e}")
                await asyncio.sleep(5)

    async def _execute_arbitrage(self, opportunity: ArbitrageOpportunity):
        """Execute arbitrage opportunity on-chain"""
        logger.info(f"🎯 Executing arbitrage: {opportunity.spread_bps} bps spread")
        
        try:
            self.execution_stats['executions_attempted'] += 1
            
            # Check gas price
            gas_price = self.w3.eth.gas_price
            if gas_price > self.config.max_gas_price:
                logger.warning(f"⛽ Gas price too high: {gas_price / 1e9:.1f} gwei")
                return
            
            # Build transaction
            account = self.w3.eth.account.from_key(self.config.private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            # Call smart contract function
            function_call = self.contract.functions.executeTriangularArbitrageWithAEON(
                opportunity.token_a,
                opportunity.token_b,
                opportunity.token_c,
                opportunity.amount_in
            )
            
            # Estimate gas
            try:
                gas_estimate = function_call.estimate_gas({'from': account.address})
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
            except Exception as e:
                logger.error(f"Gas estimation failed: {e}")
                gas_limit = opportunity.gas_estimate
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.config.chain_id
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.config.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"📤 Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=self.config.execution_timeout)
            
            if receipt.status == 1:
                logger.info(f"✅ Arbitrage executed successfully!")
                logger.info(f"   Gas used: {receipt.gasUsed:,}")
                logger.info(f"   Profit: ${opportunity.estimated_profit:.2f}")
                
                self.execution_stats['successful_executions'] += 1
                self.execution_stats['total_profit'] += opportunity.estimated_profit
                self.execution_stats['total_gas_spent'] += receipt.gasUsed
            else:
                logger.error(f"❌ Transaction failed")
                
        except Exception as e:
            logger.error(f"Execution failed: {e}")

    async def _health_monitor(self):
        """Monitor bot and contract health"""
        while self.is_running:
            try:
                # Check contract health
                health = self.contract.functions.getEcosystemHealth().call()
                
                # Check bot balance
                account = self.w3.eth.account.from_key(self.config.private_key)
                balance = self.w3.eth.get_balance(account.address)
                
                if balance < self.w3.to_wei(0.01, 'ether'):  # Less than 0.01 ETH
                    logger.warning(f"⚠️  Low balance: {self.w3.from_wei(balance, 'ether'):.4f} ETH")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)

    async def _stats_reporter(self):
        """Report bot statistics periodically"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                stats = self.execution_stats
                success_rate = (stats['successful_executions'] / max(stats['executions_attempted'], 1)) * 100
                
                logger.info("📊 ATOM Bot Statistics:")
                logger.info(f"   Total Scans: {stats['total_scans']:,}")
                logger.info(f"   Opportunities Found: {stats['opportunities_found']:,}")
                logger.info(f"   Executions Attempted: {stats['executions_attempted']:,}")
                logger.info(f"   Success Rate: {success_rate:.1f}%")
                logger.info(f"   Total Profit: ${stats['total_profit']:.2f}")
                logger.info(f"   Total Gas Spent: {stats['total_gas_spent']:,}")
                
            except Exception as e:
                logger.error(f"Stats reporter error: {e}")

    def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping ATOM Bot...")
        self.is_running = False

async def main():
    """Main entry point"""
    # Load configuration from environment
    config = ATOMConfig(
        rpc_url=os.getenv('BASE_SEPOLIA_RPC_URL', 'https://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d'),
        wss_url=os.getenv('BASE_SEPOLIA_WSS_URL', 'wss://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d'),
        chain_id=84532,
        private_key=os.getenv('PRIVATE_KEY', ''),
        contract_address=os.getenv('BASE_SEPOLIA_CONTRACT_ADDRESS', '0xb3800E6bC7847E5d5a71a03887EDc5829DF4133b'),
        theatom_api_key=os.getenv('THEATOM_API_KEY', '7324a2b4-3b05-4288-b353-68322f49a283')
    )
    
    if not config.private_key:
        logger.error("❌ PRIVATE_KEY environment variable not set")
        return
    
    # Create and start bot
    bot = ATOMBot(config)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        bot.stop()
        logger.info("👋 ATOM Bot shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
