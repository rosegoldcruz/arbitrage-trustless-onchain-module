#!/usr/bin/env python3
"""
Polygon Arbitrage Opportunity Detection Bot
Scans for profitable arbitrage opportunities across multiple DEXs in real-time
"""

import asyncio
import json
import logging
import os
import time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import websockets
import aiohttp
from web3 import Web3
from eth_account import Account

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpportunityDetector:
    def __init__(self):
        self.load_config()
        self.setup_web3()
        self.setup_contracts()
        self.price_feeds = {}
        self.opportunities = []
        self.running = False
        
    def load_config(self):
        """Load configuration from environment variables"""
        self.polygon_rpc = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
        self.min_profit_bps = Decimal(os.getenv('ATOM_MIN_PROFIT_THRESHOLD_BPS', '23'))
        self.max_gas_price = Decimal(os.getenv('ATOM_MAX_GAS_PRICE', '100'))
        self.min_trade_amount = Decimal(os.getenv('MIN_TRADE_AMOUNT_USD', '10'))
        self.max_trade_amount = Decimal(os.getenv('MAX_TRADE_AMOUNT_USD', '50000'))
        
        # Token addresses from environment
        self.tokens = {
            'WETH': os.getenv('WETH_ADDRESS', '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'),
            'USDC': os.getenv('USDC_ADDRESS', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'),
            'USDT': os.getenv('USDT_ADDRESS', '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'),
            'DAI': os.getenv('DAI_ADDRESS', '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'),
            'WMATIC': os.getenv('WMATIC_ADDRESS', '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270')
        }

        # DEX router addresses from environment
        self.dex_routers = {
            'uniswap_v3': os.getenv('UNISWAP_V3_ROUTER', '0xE592427A0AEce92De3Edee1F18E0157C05861564'),
            'quickswap': os.getenv('QUICKSWAP_ROUTER', '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'),
            'sushiswap': os.getenv('SUSHISWAP_ROUTER', '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506')
        }
        
        # Flash loan contract
        self.flash_loan_contract = os.getenv('FLASH_LOAN_CONTRACT', '0x34d560b34d3dB2671260092AbAcbA05399121E9a')
        
    def setup_web3(self):
        """Initialize Web3 connection"""
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Polygon RPC")
        logger.info(f"Connected to Polygon network, block: {self.w3.eth.block_number}")
        
    def setup_contracts(self):
        """Initialize contract instances"""
        # Simplified ABI for price quotes
        self.uniswap_quoter_abi = [
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
        
        self.v2_router_abi = [
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
        
        # Initialize contract instances
        self.uniswap_quoter = self.w3.eth.contract(
            address='0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6',
            abi=self.uniswap_quoter_abi
        )
        
        self.quickswap_router = self.w3.eth.contract(
            address=self.dex_routers['quickswap'],
            abi=self.v2_router_abi
        )
        
        self.sushiswap_router = self.w3.eth.contract(
            address=self.dex_routers['sushiswap'],
            abi=self.v2_router_abi
        )
        
    async def get_uniswap_v3_price(self, token_in: str, token_out: str, amount_in: int, fee: int = 3000) -> Optional[int]:
        """Get price quote from Uniswap V3"""
        try:
            amount_out = self.uniswap_quoter.functions.quoteExactInputSingle(
                token_in, token_out, fee, amount_in, 0
            ).call()
            return amount_out
        except Exception as e:
            logger.error(f"Uniswap V3 quote error: {e}")
            return None
            
    async def get_v2_price(self, router_contract, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Get price quote from V2-style DEX"""
        try:
            path = [token_in, token_out]
            amounts = router_contract.functions.getAmountsOut(amount_in, path).call()
            return amounts[-1]
        except Exception as e:
            logger.error(f"V2 quote error: {e}")
            return None
            
    async def calculate_triangular_arbitrage(self, token_a: str, token_b: str, token_c: str, amount: int) -> Dict:
        """Calculate potential profit for triangular arbitrage"""
        
        # Define all possible DEX combinations for triangular arbitrage
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
                # Step 1: token_a -> token_b
                if dex_a == 'uniswap_v3':
                    amount_b = await self.get_uniswap_v3_price(token_a, token_b, amount)
                elif dex_a == 'quickswap':
                    amount_b = await self.get_v2_price(self.quickswap_router, token_a, token_b, amount)
                elif dex_a == 'sushiswap':
                    amount_b = await self.get_v2_price(self.sushiswap_router, token_a, token_b, amount)
                
                if not amount_b:
                    continue
                    
                # Step 2: token_b -> token_c
                if dex_b == 'uniswap_v3':
                    amount_c = await self.get_uniswap_v3_price(token_b, token_c, amount_b)
                elif dex_b == 'quickswap':
                    amount_c = await self.get_v2_price(self.quickswap_router, token_b, token_c, amount_b)
                elif dex_b == 'sushiswap':
                    amount_c = await self.get_v2_price(self.sushiswap_router, token_b, token_c, amount_b)
                
                if not amount_c:
                    continue
                    
                # Step 3: token_c -> token_a
                if dex_c == 'uniswap_v3':
                    final_amount = await self.get_uniswap_v3_price(token_c, token_a, amount_c)
                elif dex_c == 'quickswap':
                    final_amount = await self.get_v2_price(self.quickswap_router, token_c, token_a, amount_c)
                elif dex_c == 'sushiswap':
                    final_amount = await self.get_v2_price(self.sushiswap_router, token_c, token_a, amount_c)
                
                if not final_amount:
                    continue
                    
                # Calculate profit
                if final_amount > amount:
                    profit = final_amount - amount
                    profit_bps = (profit * 10000) // amount
                    
                    if profit > max_profit and profit_bps >= self.min_profit_bps:
                        max_profit = profit
                        best_opportunity = {
                            'token_a': token_a,
                            'token_b': token_b,
                            'token_c': token_c,
                            'amount_in': amount,
                            'amount_out': final_amount,
                            'profit': profit,
                            'profit_bps': profit_bps,
                            'dex_a': dex_a,
                            'dex_b': dex_b,
                            'dex_c': dex_c,
                            'timestamp': time.time()
                        }
                        
            except Exception as e:
                logger.error(f"Error calculating arbitrage for {dex_a}-{dex_b}-{dex_c}: {e}")
                continue
                
        return best_opportunity
        
    async def scan_opportunities(self):
        """Continuously scan for arbitrage opportunities"""
        logger.info("Starting opportunity scanning...")
        
        # Define token triangles to monitor
        token_triangles = [
            ('WETH', 'USDC', 'WMATIC'),
            ('WETH', 'USDT', 'WMATIC'),
            ('WETH', 'DAI', 'WMATIC'),
            ('USDC', 'USDT', 'DAI'),
            ('WETH', 'USDC', 'DAI'),
            ('WMATIC', 'USDC', 'USDT'),
        ]
        
        # Test amounts (in wei/smallest unit)
        test_amounts = [
            int(10 * 10**18),    # $10 equivalent
            int(100 * 10**18),   # $100 equivalent
            int(1000 * 10**18),  # $1000 equivalent
        ]
        
        while self.running:
            try:
                current_opportunities = []
                
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
                            current_opportunities.append(opportunity)
                            
                            logger.info(f"🚀 OPPORTUNITY FOUND: {token_a_name}->{token_b_name}->{token_c_name} "
                                      f"via {opportunity['dex_a']}-{opportunity['dex_b']}-{opportunity['dex_c']} "
                                      f"Profit: {opportunity['profit_bps']} bps (${opportunity['profit']/10**18:.2f})")
                
                # Update opportunities list
                self.opportunities = current_opportunities
                
                # Sort by profit potential
                self.opportunities.sort(key=lambda x: x['profit_bps'], reverse=True)
                
                # Wait before next scan
                await asyncio.sleep(2)  # Scan every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in opportunity scanning: {e}")
                await asyncio.sleep(5)
                
    async def start(self):
        """Start the opportunity detection bot"""
        self.running = True
        logger.info("🤖 Opportunity Detection Bot Starting...")
        
        # Start scanning task
        scan_task = asyncio.create_task(self.scan_opportunities())
        
        try:
            await scan_task
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
            scan_task.cancel()
            
    def get_best_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get the best current opportunities"""
        return self.opportunities[:limit]

if __name__ == "__main__":
    detector = OpportunityDetector()
    asyncio.run(detector.start())
