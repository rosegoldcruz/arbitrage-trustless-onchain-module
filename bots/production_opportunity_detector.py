#!/usr/bin/env python3
"""
Production Opportunity Detector - Real Polygon Mainnet Arbitrage Detection
SECURE: Environment Variables Only - NO HARDCODED SECRETS
"""

import asyncio
import json
import logging
import os
import sys
import time
from decimal import Decimal
from typing import Dict, List, Optional
import aiohttp
from web3 import Web3
import redis

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.secure_config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionOpportunityDetector:
    def __init__(self):
        self.config = config
        self.setup_web3()
        self.setup_redis()
        self.setup_contracts()
        self.opportunities = []
        self.running = False
        
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

        logger.info(f"✅ Connected to Polygon mainnet, block: {self.w3.eth.block_number}")

        # Load configuration from secure config
        self.min_profit_bps = self.config.get('min_profit_threshold_bps')
        self.min_trade_size_usd = self.config.get('min_trade_size_usd')
        self.min_trade_profit_usd = self.config.get('min_trade_profit_usd')
        self.max_gas_price = self.config.get('max_gas_price')
        self.scan_interval = self.config.get('scan_interval')
        self.opportunity_scan_interval = self.config.get('opportunity_scan_interval')

        # Contract addresses from environment
        self.flash_loan_contract = self.config.get('flashloan_contract')
        if not self.flash_loan_contract:
            raise ValueError("FLASHLOAN_ARB_ADDR environment variable required")

        # Token addresses from secure config
        self.tokens = self.config.get_tokens()

        # DEX addresses from secure config
        self.dex_routers = self.config.get_dex_routers()

    def setup_redis(self):
        """Initialize Redis connection - SECURE: Environment Variables Only"""
        redis_url = self.config.get('redis_url')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable required")

        self.redis_client = redis.from_url(redis_url, decode_responses=True)

        # Test Redis connection
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {e}")
        
    def setup_contracts(self):
        """Initialize contract instances"""
        # Uniswap V3 Quoter ABI
        quoter_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "name": "quoteExactInputSingle",
                "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # V2 Router ABI
        v2_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Get quoter address from secure config
        uniswap_quoter_addr = self.config.get('uniswap_v3_quoter')
        if not uniswap_quoter_addr:
            raise ValueError("UNISWAP_V3_QUOTER environment variable required")

        self.uniswap_quoter = self.w3.eth.contract(
            address=uniswap_quoter_addr,
            abi=quoter_abi
        )

        self.quickswap_router = self.w3.eth.contract(
            address=self.dex_routers['quickswap'],
            abi=v2_abi
        )

        self.sushiswap_router = self.w3.eth.contract(
            address=self.dex_routers['sushiswap'],
            abi=v2_abi
        )
        
    async def get_uniswap_v3_price(self, token_in: str, token_out: str, amount_in: int, fee: int = 3000) -> Optional[int]:
        """Get price quote from Uniswap V3"""
        try:
            amount_out = self.uniswap_quoter.functions.quoteExactInputSingle(
                token_in, token_out, fee, amount_in, 0
            ).call()
            return amount_out
        except Exception as e:
            logger.debug(f"Uniswap V3 quote error: {e}")
            return None
            
    async def get_v2_price(self, router_contract, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Get price quote from V2-style DEX"""
        try:
            path = [token_in, token_out]
            amounts = router_contract.functions.getAmountsOut(amount_in, path).call()
            return amounts[-1]
        except Exception as e:
            logger.debug(f"V2 quote error: {e}")
            return None
            
    async def calculate_triangular_arbitrage(self, token_a: str, token_b: str, token_c: str, amount: int) -> Optional[Dict]:
        """Calculate triangular arbitrage opportunity"""
        
        # All possible DEX combinations
        dex_combinations = [
            ('uniswap_v3', 'quickswap', 'sushiswap'),
            ('uniswap_v3', 'sushiswap', 'quickswap'),
            ('quickswap', 'uniswap_v3', 'sushiswap'),
            ('quickswap', 'sushiswap', 'uniswap_v3'),
            ('sushiswap', 'uniswap_v3', 'quickswap'),
            ('sushiswap', 'quickswap', 'uniswap_v3'),
        ]
        
        best_opportunity = None
        max_profit = 0
        
        for dex_a, dex_b, dex_c in dex_combinations:
            try:
                # Step 1: A -> B
                if dex_a == 'uniswap_v3':
                    amount_b = await self.get_uniswap_v3_price(token_a, token_b, amount)
                elif dex_a == 'quickswap':
                    amount_b = await self.get_v2_price(self.quickswap_router, token_a, token_b, amount)
                elif dex_a == 'sushiswap':
                    amount_b = await self.get_v2_price(self.sushiswap_router, token_a, token_b, amount)
                
                if not amount_b or amount_b == 0:
                    continue
                    
                # Step 2: B -> C
                if dex_b == 'uniswap_v3':
                    amount_c = await self.get_uniswap_v3_price(token_b, token_c, amount_b)
                elif dex_b == 'quickswap':
                    amount_c = await self.get_v2_price(self.quickswap_router, token_b, token_c, amount_b)
                elif dex_b == 'sushiswap':
                    amount_c = await self.get_v2_price(self.sushiswap_router, token_b, token_c, amount_b)
                
                if not amount_c or amount_c == 0:
                    continue
                    
                # Step 3: C -> A
                if dex_c == 'uniswap_v3':
                    final_amount = await self.get_uniswap_v3_price(token_c, token_a, amount_c)
                elif dex_c == 'quickswap':
                    final_amount = await self.get_v2_price(self.quickswap_router, token_c, token_a, amount_c)
                elif dex_c == 'sushiswap':
                    final_amount = await self.get_v2_price(self.sushiswap_router, token_c, token_a, amount_c)
                
                if not final_amount or final_amount == 0:
                    continue
                    
                # Calculate profit accounting for AAVE flash loan fee (0.09%) and premium gas
                aave_flash_loan_fee = (amount * 9) // 10000  # 0.09% AAVE fee
                estimated_gas_cost = amount // 400  # Premium gas estimate for fast execution
                total_costs = aave_flash_loan_fee + estimated_gas_cost

                if final_amount > amount + total_costs:
                    gross_profit = final_amount - amount
                    net_profit = gross_profit - total_costs
                    profit_bps = (net_profit * 10000) // amount

                    # Convert to USD for validation
                    trade_size_usd = float(amount) / 10**18 * 2500  # Rough ETH price
                    net_profit_usd = float(net_profit) / 10**18 * 2500

                    # AAVE HIGH VALUE FILTER: Must meet ALL thresholds
                    meets_size_threshold = trade_size_usd >= float(self.min_trade_size_usd)
                    meets_bps_threshold = profit_bps >= self.min_profit_bps
                    meets_profit_threshold = net_profit_usd >= float(self.min_trade_profit_usd)

                    if (meets_size_threshold and meets_bps_threshold and
                        meets_profit_threshold and net_profit > max_profit):
                        max_profit = net_profit
                        best_opportunity = {
                            'token_a': token_a,
                            'token_b': token_b,
                            'token_c': token_c,
                            'amount_in': amount,
                            'amount_out': final_amount,
                            'gross_profit': gross_profit,
                            'net_profit': net_profit,
                            'net_profit_usd': net_profit_usd,
                            'trade_size_usd': trade_size_usd,
                            'profit_bps': profit_bps,
                            'dex_a': dex_a,
                            'dex_b': dex_b,
                            'dex_c': dex_c,
                            'timestamp': time.time(),
                            'gas_estimate': estimated_gas_cost,
                            'aave_flash_loan_fee': aave_flash_loan_fee,
                            'meets_size_threshold': meets_size_threshold,
                            'meets_bps_threshold': meets_bps_threshold,
                            'meets_profit_threshold': meets_profit_threshold
                        }
                        
            except Exception as e:
                logger.debug(f"Error calculating arbitrage for {dex_a}-{dex_b}-{dex_c}: {e}")
                continue
                
        return best_opportunity
        
    async def scan_opportunities(self):
        """Continuously scan for arbitrage opportunities"""
        logger.info("🔍 Starting production opportunity scanning...")
        
        # Token triangles to monitor
        token_triangles = [
            ('WETH', 'USDC', 'WMATIC'),
            ('WETH', 'USDT', 'WMATIC'),
            ('WETH', 'DAI', 'WMATIC'),
            ('USDC', 'USDT', 'DAI'),
            ('WETH', 'USDC', 'DAI'),
            ('WMATIC', 'USDC', 'USDT'),
        ]
        
        # HIGH VALUE TEST AMOUNTS - $25K minimum
        test_amounts = [
            int(10 * 10**18),    # 10 ETH equivalent (~$25K)
            int(20 * 10**18),    # 20 ETH equivalent (~$50K)
            int(40 * 10**18),    # 40 ETH equivalent (~$100K)
        ]
        
        while self.running:
            try:
                opportunities_found = 0
                
                for token_a_name, token_b_name, token_c_name in token_triangles:
                    token_a = self.tokens[token_a_name]
                    token_b = self.tokens[token_b_name]
                    token_c = self.tokens[token_c_name]
                    
                    for amount in test_amounts:
                        opportunity = await self.calculate_triangular_arbitrage(token_a, token_b, token_c, amount)
                        if opportunity:
                            opportunity['token_a_name'] = token_a_name
                            opportunity['token_b_name'] = token_b_name
                            opportunity['token_c_name'] = token_c_name
                            
                            # Queue opportunity for execution
                            self.redis_client.lpush('arbitrage_opportunities', json.dumps(opportunity))
                            opportunities_found += 1
                            
                            logger.info(f"💰 AAVE FLASH LOAN OPPORTUNITY: {token_a_name}->{token_b_name}->{token_c_name}")
                            logger.info(f"   Route: {opportunity['dex_a']}-{opportunity['dex_b']}-{opportunity['dex_c']}")
                            logger.info(f"   Size: ${opportunity['trade_size_usd']:.0f} | Net: ${opportunity['net_profit_usd']:.2f} | BPS: {opportunity['profit_bps']}")
                
                if opportunities_found > 0:
                    logger.info(f"📊 Found {opportunities_found} opportunities this scan")
                
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in opportunity scanning: {e}")
                await asyncio.sleep(5)
                
    async def start(self):
        """Start the opportunity detection system"""
        self.running = True
        logger.info("🚀 Production Opportunity Detector Starting...")
        
        try:
            await self.scan_opportunities()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False

if __name__ == "__main__":
    detector = ProductionOpportunityDetector()
    asyncio.run(detector.start())
