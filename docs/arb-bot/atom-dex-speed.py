#!/usr/bin/env python3
"""
ATOM v2 - Arbitrage Trustless On-chain Module
Core DEX monitoring engine with ultra-low latency
"""

import asyncio
import json
import time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import aiohttp
from web3 import Web3
from web3.providers import WebsocketProvider
from eth_abi import decode_abi
import numpy as np
from sortedcontainers import SortedDict

# DEX Configuration
DEX_CONFIGS = {
    'uniswap_v2': {
        'factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
        'router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
        'init_code_hash': '0x96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f'
    },
    'uniswap_v3': {
        'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
        'quoter': '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6',
        'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
    },
    'sushiswap': {
        'factory': '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac',
        'router': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
        'init_code_hash': '0xe18a34eb0e04b04f7a0ac29a6e80748dca96319b42c54d679cb821dca90c6303'
    },
    'curve': {
        'registry': '0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5',
        'pools': {}  # Populated dynamically
    }
}

@dataclass
class PriceQuote:
    """Optimized price quote structure"""
    dex: str
    token_in: str
    token_out: str
    amount_in: int
    amount_out: int
    gas_estimate: int
    pool_address: str
    timestamp: float
    block_number: int
    
    @property
    def rate(self) -> Decimal:
        return Decimal(self.amount_out) / Decimal(self.amount_in)

@dataclass
class ArbitrageOpportunity:
    """Identified arbitrage opportunity"""
    buy_quote: PriceQuote
    sell_quote: PriceQuote
    profit_wei: int
    profit_percentage: Decimal
    gas_cost_wei: int
    net_profit_wei: int
    path: List[str]
    timestamp: float = field(default_factory=time.time)

class ATOMDexMonitor:
    """High-performance DEX monitoring engine"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.w3 = self._setup_web3()
        
        # Price storage with automatic expiry
        self.price_book: Dict[str, SortedDict] = defaultdict(SortedDict)
        self.quote_cache: Dict[str, PriceQuote] = {}
        
        # WebSocket connections
        self.ws_connections: Dict[str, aiohttp.ClientWebSocketResponse] = {}
        self.subscriptions: Set[str] = set()
        
        # Performance metrics
        self.metrics = {
            'quotes_processed': 0,
            'opportunities_found': 0,
            'ws_reconnects': 0,
            'avg_latency_ms': 0
        }
        
    def _setup_web3(self) -> Web3:
        """Setup Web3 with WebSocket provider for speed"""
        providers = self.config['rpc_endpoints']
        
        for endpoint in providers:
            if endpoint.startswith('wss://'):
                try:
                    w3 = Web3(WebsocketProvider(endpoint, websocket_timeout=60))
                    if w3.isConnected():
                        return w3
                except Exception as e:
                    print(f"Failed to connect to {endpoint}: {e}")
        
        raise ConnectionError("No WebSocket RPC available")
    
    async def start_monitoring(self, tokens: List[str]):
        """Start monitoring token pairs across all DEXs"""
        tasks = []
        
        # Setup WebSocket subscriptions for each DEX
        for dex in ['uniswap_v2', 'uniswap_v3', 'sushiswap']:
            tasks.append(self._monitor_dex_events(dex, tokens))
        
        # Curve requires different approach
        tasks.append(self._monitor_curve_pools(tokens))
        
        # Start arbitrage scanner
        tasks.append(self._scan_arbitrage_opportunities())
        
        await asyncio.gather(*tasks)
    
    async def _monitor_dex_events(self, dex: str, tokens: List[str]):
        """Monitor swap events via WebSocket for a specific DEX"""
        sync_topic = Web3.keccak(text="Sync(uint112,uint112)").hex()
        swap_topic = Web3.keccak(text="Swap(address,uint256,uint256,uint256,uint256,address)").hex()
        
        # Generate pair addresses for all token combinations
        pairs = self._generate_pair_addresses(dex, tokens)
        
        # Subscribe to events
        subscription_id = await self._subscribe_to_logs(pairs, [sync_topic, swap_topic])
        
        while True:
            try:
                # Process incoming events
                async for event in self._process_ws_events(subscription_id):
                    await self._handle_dex_event(dex, event)
                    
            except Exception as e:
                print(f"WebSocket error for {dex}: {e}")
                self.metrics['ws_reconnects'] += 1
                await asyncio.sleep(1)
                # Reconnect
                subscription_id = await self._subscribe_to_logs(pairs, [sync_topic, swap_topic])
    
    def _generate_pair_addresses(self, dex: str, tokens: List[str]) -> List[str]:
        """Generate pair addresses for token combinations"""
        pairs = []
        config = DEX_CONFIGS[dex]
        
        for i, token0 in enumerate(tokens):
            for token1 in tokens[i+1:]:
                # Sort tokens
                if int(token0, 16) > int(token1, 16):
                    token0, token1 = token1, token0
                
                # Calculate pair address
                if dex in ['uniswap_v2', 'sushiswap']:
                    pair = self._calculate_uniswap_v2_pair(
                        config['factory'],
                        token0,
                        token1,
                        config['init_code_hash']
                    )
                    pairs.append(pair)
                elif dex == 'uniswap_v3':
                    # V3 has multiple fee tiers
                    for fee in [500, 3000, 10000]:
                        pair = self._calculate_uniswap_v3_pool(
                            config['factory'],
                            token0,
                            token1,
                            fee
                        )
                        pairs.append(pair)
        
        return pairs
    
    def _calculate_uniswap_v2_pair(self, factory: str, token0: str, token1: str, init_code: str) -> str:
        """Calculate Uniswap V2 style pair address"""
        salt = Web3.solidityKeccak(['address', 'address'], [token0, token1])
        pair = Web3.keccak(
            b'\xff' + 
            bytes.fromhex(factory[2:]) + 
            salt + 
            bytes.fromhex(init_code[2:])
        )[-20:]
        
        return Web3.toChecksumAddress(pair.hex())
    
    async def _subscribe_to_logs(self, addresses: List[str], topics: List[str]) -> str:
        """Subscribe to contract events via WebSocket"""
        params = {
            "jsonrpc": "2.0",
            "method": "eth_subscribe",
            "params": [
                "logs",
                {
                    "address": addresses,
                    "topics": [topics]
                }
            ],
            "id": 1
        }
        
        async with aiohttp.ClientSession() as session:
            ws = await session.ws_connect(self.config['rpc_endpoints'][0])
            await ws.send_json(params)
            
            response = await ws.receive_json()
            subscription_id = response['result']
            
            self.ws_connections[subscription_id] = ws
            return subscription_id
    
    async def _process_ws_events(self, subscription_id: str):
        """Process WebSocket events stream"""
        ws = self.ws_connections.get(subscription_id)
        if not ws:
            return
        
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                if 'params' in data and data['params']['subscription'] == subscription_id:
                    yield data['params']['result']
    
    async def _handle_dex_event(self, dex: str, event: Dict):
        """Handle incoming DEX event and update price book"""
        start_time = time.time()
        
        try:
            # Decode event based on topic
            topic = event['topics'][0]
            
            if topic == Web3.keccak(text="Sync(uint112,uint112)").hex():
                # Sync event - update reserves
                await self._handle_sync_event(dex, event)
            elif topic == Web3.keccak(text="Swap(address,uint256,uint256,uint256,uint256,address)").hex():
                # Swap event - update prices
                await self._handle_swap_event(dex, event)
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            self.metrics['avg_latency_ms'] = (
                self.metrics['avg_latency_ms'] * self.metrics['quotes_processed'] + latency_ms
            ) / (self.metrics['quotes_processed'] + 1)
            self.metrics['quotes_processed'] += 1
            
        except Exception as e:
            print(f"Error handling {dex} event: {e}")
    
    async def _handle_sync_event(self, dex: str, event: Dict):
        """Handle Sync event to update reserves"""
        # Decode reserves
        reserves = decode_abi(['uint112', 'uint112'], bytes.fromhex(event['data'][2:]))
        pool_address = event['address']
        block_number = int(event['blockNumber'], 16)
        
        # Get token addresses from pool
        pool_contract = self.w3.eth.contract(
            address=pool_address,
            abi=[
                {"name": "token0", "type": "function", "outputs": [{"type": "address"}]},
                {"name": "token1", "type": "function", "outputs": [{"type": "address"}]}
            ]
        )
        
        token0 = pool_contract.functions.token0().call()
        token1 = pool_contract.functions.token1().call()
        
        # Calculate rates in both directions
        if reserves[0] > 0 and reserves[1] > 0:
            # Token0 -> Token1
            amount_in = Web3.toWei(1, 'ether')
            amount_out = self._calculate_output_amount(amount_in, reserves[0], reserves[1])
            
            quote_0_1 = PriceQuote(
                dex=dex,
                token_in=token0,
                token_out=token1,
                amount_in=amount_in,
                amount_out=amount_out,
                gas_estimate=self._estimate_gas_for_dex(dex),
                pool_address=pool_address,
                timestamp=time.time(),
                block_number=block_number
            )
            
            self._update_price_book(token0, token1, quote_0_1)
            
            # Token1 -> Token0
            amount_out = self._calculate_output_amount(amount_in, reserves[1], reserves[0])
            
            quote_1_0 = PriceQuote(
                dex=dex,
                token_in=token1,
                token_out=token0,
                amount_in=amount_in,
                amount_out=amount_out,
                gas_estimate=self._estimate_gas_for_dex(dex),
                pool_address=pool_address,
                timestamp=time.time(),
                block_number=block_number
            )
            
            self._update_price_book(token1, token0, quote_1_0)
    
    def _calculate_output_amount(self, amount_in: int, reserve_in: int, reserve_out: int) -> int:
        """Calculate output amount using constant product formula"""
        amount_in_with_fee = amount_in * 997
        numerator = amount_in_with_fee * reserve_out
        denominator = (reserve_in * 1000) + amount_in_with_fee
        return numerator // denominator
    
    def _update_price_book(self, token_in: str, token_out: str, quote: PriceQuote):
        """Update price book with new quote"""
        pair_key = f"{token_in}-{token_out}"
        
        # Remove old quotes (older than 10 blocks)
        current_block = quote.block_number
        self.price_book[pair_key] = SortedDict(
            (k, v) for k, v in self.price_book[pair_key].items()
            if v.block_number >= current_block - 10
        )
        
        # Add new quote
        quote_key = f"{quote.dex}-{quote.pool_address}"
        self.price_book[pair_key][quote_key] = quote
        self.quote_cache[f"{pair_key}-{quote_key}"] = quote
    
    async def _monitor_curve_pools(self, tokens: List[str]):
        """Monitor Curve pools (different architecture)"""
        registry = self.w3.eth.contract(
            address=DEX_CONFIGS['curve']['registry'],
            abi=[{"name": "get_pool_from_lp_token", "type": "function", "inputs": [{"type": "address"}], "outputs": [{"type": "address"}]}]
        )
        
        # Curve monitoring implementation
        while True:
            try:
                for token in tokens:
                    # Check if token is in any Curve pool
                    await self._check_curve_rates(token, tokens)
                
                await asyncio.sleep(2)  # Curve updates less frequently
                
            except Exception as e:
                print(f"Curve monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _scan_arbitrage_opportunities(self):
        """Continuously scan for arbitrage opportunities"""
        while True:
            try:
                # Check all token pairs
                opportunities = []
                
                for pair_key, quotes in self.price_book.items():
                    if len(quotes) >= 2:
                        # Find best buy and sell prices
                        sorted_quotes = sorted(quotes.values(), key=lambda q: q.rate)
                        
                        best_buy = sorted_quotes[0]  # Lowest rate (best for buying)
                        best_sell = sorted_quotes[-1]  # Highest rate (best for selling)
                        
                        if best_buy.dex != best_sell.dex:
                            # Calculate potential profit
                            opportunity = self._calculate_arbitrage_profit(best_buy, best_sell)
                            
                            if opportunity and opportunity.net_profit_wei > self.config['min_profit_wei']:
                                opportunities.append(opportunity)
                                self.metrics['opportunities_found'] += 1
                
                # Process opportunities
                if opportunities:
                    # Sort by profit
                    opportunities.sort(key=lambda o: o.net_profit_wei, reverse=True)
                    
                    # Execute best opportunity
                    await self._execute_arbitrage(opportunities[0])
                
                await asyncio.sleep(0.1)  # 100ms scan interval
                
            except Exception as e:
                print(f"Arbitrage scan error: {e}")
                await asyncio.sleep(1)
    
    def _calculate_arbitrage_profit(self, buy_quote: PriceQuote, sell_quote: PriceQuote) -> Optional[ArbitrageOpportunity]:
        """Calculate potential arbitrage profit"""
        # Ensure we're comparing same token pair
        if buy_quote.token_in != sell_quote.token_out or buy_quote.token_out != sell_quote.token_in:
            return None
        
        # Calculate profit
        amount_in = self.config['trade_amount_wei']
        
        # Buy on first DEX
        amount_received = (amount_in * buy_quote.amount_out) // buy_quote.amount_in
        
        # Sell on second DEX
        amount_back = (amount_received * sell_quote.amount_out) // sell_quote.amount_in
        
        # Gross profit
        gross_profit = amount_back - amount_in
        
        if gross_profit <= 0:
            return None
        
        # Calculate gas costs
        gas_cost = (buy_quote.gas_estimate + sell_quote.gas_estimate) * self.w3.eth.gas_price
        
        # Net profit
        net_profit = gross_profit - gas_cost
        
        if net_profit <= 0:
            return None
        
        return ArbitrageOpportunity(
            buy_quote=buy_quote,
            sell_quote=sell_quote,
            profit_wei=gross_profit,
            profit_percentage=Decimal(gross_profit) / Decimal(amount_in) * 100,
            gas_cost_wei=gas_cost,
            net_profit_wei=net_profit,
            path=[buy_quote.token_in, buy_quote.token_out, sell_quote.token_out]
        )
    
    def _estimate_gas_for_dex(self, dex: str) -> int:
        """Estimate gas for DEX swap"""
        gas_estimates = {
            'uniswap_v2': 150000,
            'uniswap_v3': 180000,
            'sushiswap': 150000,
            'curve': 200000
        }
        return gas_estimates.get(dex, 150000)
    
    async def _execute_arbitrage(self, opportunity: ArbitrageOpportunity):
        """Execute arbitrage opportunity (placeholder for Step 2)"""
        print(f"🎯 Arbitrage opportunity found!")
        print(f"   Buy on {opportunity.buy_quote.dex}, Sell on {opportunity.sell_quote.dex}")
        print(f"   Profit: {Web3.fromWei(opportunity.net_profit_wei, 'ether')} ETH")
        print(f"   Path: {' -> '.join(opportunity.path)}")
        
        # Execution will be implemented in Step 2 with MEV protection
        pass

# Configuration loader
def load_config() -> Dict:
    """Load configuration from environment and files"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Override with environment variables
    config['rpc_endpoints'] = os.getenv('RPC_ENDPOINTS', '').split(',') or config['rpc_endpoints']
    config['min_profit_wei'] = int(os.getenv('MIN_PROFIT_WEI', config.get('min_profit_wei', Web3.toWei(0.01, 'ether'))))
    config['trade_amount_wei'] = int(os.getenv('TRADE_AMOUNT_WEI', config.get('trade_amount_wei', Web3.toWei(10, 'ether'))))
    
    return config

# Main entry point
async def main():
    """Main entry point for ATOM v2"""
    config = load_config()
    
    # Initialize DEX monitor
    monitor = ATOMDexMonitor(config)
    
    # Token list to monitor
    tokens = config.get('tokens', [
        '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
        '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC
        '0x6B175474E89094C44Da98b954EedeAC495271d0F',  # DAI
        '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT
    ])
    
    print("🚀 ATOM v2 - Starting DEX monitoring...")
    print(f"📊 Monitoring {len(tokens)} tokens across {len(DEX_CONFIGS)} DEXs")
    
    await monitor.start_monitoring(tokens)

if __name__ == "__main__":
    asyncio.run(main())