#!/usr/bin/env python3
"""
ATOM v2 - Smart Pathfinding & Trade Simulation
Multi-hop routing with 0x, 1inch, and Paraswap integration
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from decimal import Decimal
from collections import defaultdict
import networkx as nx
from web3 import Web3
import numpy as np

@dataclass
class RouteQuote:
    """Enhanced quote with full routing information"""
    aggregator: str  # '0x', '1inch', 'paraswap', 'internal'
    path: List[str]  # Full token path
    pools: List[Dict]  # Pool details for each hop
    amount_in: int
    amount_out: int
    gas_estimate: int
    price_impact: Decimal
    call_data: bytes
    to_address: str
    value: int  # ETH value if needed
    deadline: int
    
    @property
    def effective_rate(self) -> Decimal:
        """Calculate effective exchange rate"""
        return Decimal(self.amount_out) / Decimal(self.amount_in)
    
    @property
    def slippage_adjusted_output(self, slippage: Decimal = Decimal('0.005')) -> int:
        """Calculate minimum output with slippage"""
        return int(self.amount_out * (1 - slippage))

class ATOMPathfinder:
    """Smart routing engine with aggregator integration"""
    
    def __init__(self, config: Dict, w3: Web3):
        self.config = config
        self.w3 = w3
        
        # API configurations
        self.aggregators = {
            '0x': {
                'base_url': 'https://api.0x.org',
                'api_key': config.get('0x_api_key'),
                'endpoints': {
                    'quote': '/swap/v1/quote',
                    'price': '/swap/v1/price'
                }
            },
            '1inch': {
                'base_url': f"https://api.1inch.io/v5.0/{config.get('chain_id', 1)}",
                'api_key': config.get('1inch_api_key'),
                'endpoints': {
                    'quote': '/quote',
                    'swap': '/swap'
                }
            },
            'paraswap': {
                'base_url': 'https://apiv5.paraswap.io',
                'endpoints': {
                    'prices': '/prices',
                    'transactions': '/transactions/1'
                }
            }
        }
        
        # Internal routing graph
        self.routing_graph = nx.DiGraph()
        self.liquidity_map = defaultdict(dict)
        
        # Cache for recent quotes
        self.quote_cache = {}
        self.cache_duration = 2  # seconds
        
        # Simulation contract for testing
        self.simulation_contract = self._deploy_simulation_contract()
    
    async def find_best_route(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        max_hops: int = 3
    ) -> Optional[RouteQuote]:
        """Find the best route across all sources"""
        quotes = []
        
        # Get quotes from all aggregators in parallel
        tasks = [
            self._get_0x_quote(token_in, token_out, amount_in),
            self._get_1inch_quote(token_in, token_out, amount_in),
            self._get_paraswap_quote(token_in, token_out, amount_in),
            self._find_internal_route(token_in, token_out, amount_in, max_hops)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, RouteQuote):
                quotes.append(result)
        
        if not quotes:
            return None
        
        # Find best quote considering gas costs
        best_quote = max(quotes, key=lambda q: self._calculate_net_output(q))
        
        # Simulate the trade before returning
        if await self._simulate_trade(best_quote):
            return best_quote
        
        return None
    
    async def _get_0x_quote(self, token_in: str, token_out: str, amount_in: int) -> Optional[RouteQuote]:
        """Get quote from 0x Protocol"""
        cache_key = f"0x-{token_in}-{token_out}-{amount_in}"
        cached = self._get_cached_quote(cache_key)
        if cached:
            return cached
        
        params = {
            'sellToken': token_in,
            'buyToken': token_out,
            'sellAmount': str(amount_in),
            'slippagePercentage': str(self.config.get('slippage', 0.005)),
            'skipValidation': 'false',
            'enableSlippageProtection': 'true',
            'excludedSources': 'Kyber',  # Exclude problematic sources
            'affiliateAddress': self.config.get('affiliate_address', '0x0000000000000000000000000000000000000000'),
            'affiliateFee': '0.001'  # 0.1% affiliate fee
        }
        
        headers = {
            '0x-api-key': self.aggregators['0x']['api_key']
        } if self.aggregators['0x']['api_key'] else {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.aggregators['0x']['base_url']}{self.aggregators['0x']['endpoints']['quote']}",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        quote = RouteQuote(
                            aggregator='0x',
                            path=self._extract_0x_path(data),
                            pools=data.get('sources', []),
                            amount_in=int(data['sellAmount']),
                            amount_out=int(data['buyAmount']),
                            gas_estimate=int(data.get('estimatedGas', 250000)),
                            price_impact=Decimal(data.get('priceImpact', '0')),
                            call_data=bytes.fromhex(data['data'][2:]),
                            to_address=data['to'],
                            value=int(data['value']),
                            deadline=int(time.time()) + 300  # 5 minutes
                        )
                        
                        self._cache_quote(cache_key, quote)
                        return quote
                        
        except Exception as e:
            print(f"0x API error: {e}")
        
        return None
    
    async def _get_1inch_quote(self, token_in: str, token_out: str, amount_in: int) -> Optional[RouteQuote]:
        """Get quote from 1inch"""
        cache_key = f"1inch-{token_in}-{token_out}-{amount_in}"
        cached = self._get_cached_quote(cache_key)
        if cached:
            return cached
        
        params = {
            'fromTokenAddress': token_in,
            'toTokenAddress': token_out,
            'amount': str(amount_in),
            'fromAddress': self.config.get('executor_address'),
            'slippage': str(int(self.config.get('slippage', 0.005) * 100)),
            'protocols': ','.join(self.config.get('1inch_protocols', ['UNISWAP_V2', 'UNISWAP_V3', 'SUSHI', 'CURVE'])),
            'disableEstimate': 'true',
            'allowPartialFill': 'false',
            'fee': '0.1'  # 0.1% fee
        }
        
        headers = {
            'Authorization': f"Bearer {self.aggregators['1inch']['api_key']}"
        } if self.aggregators['1inch']['api_key'] else {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.aggregators['1inch']['base_url']}{self.aggregators['1inch']['endpoints']['quote']}",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        quote = RouteQuote(
                            aggregator='1inch',
                            path=self._extract_1inch_path(data),
                            pools=data.get('protocols', []),
                            amount_in=int(data['fromTokenAmount']),
                            amount_out=int(data['toTokenAmount']),
                            gas_estimate=int(data.get('estimatedGas', 300000)),
                            price_impact=Decimal('0'),  # 1inch doesn't provide this
                            call_data=bytes.fromhex(data['tx']['data'][2:]),
                            to_address=data['tx']['to'],
                            value=int(data['tx']['value']),
                            deadline=int(time.time()) + 300
                        )
                        
                        self._cache_quote(cache_key, quote)
                        return quote
                        
        except Exception as e:
            print(f"1inch API error: {e}")
        
        return None
    
    async def _get_paraswap_quote(self, token_in: str, token_out: str, amount_in: int) -> Optional[RouteQuote]:
        """Get quote from Paraswap"""
        cache_key = f"paraswap-{token_in}-{token_out}-{amount_in}"
        cached = self._get_cached_quote(cache_key)
        if cached:
            return cached
        
        # First get price quote
        price_params = {
            'srcToken': token_in,
            'destToken': token_out,
            'amount': str(amount_in),
            'side': 'SELL',
            'network': str(self.config.get('chain_id', 1)),
            'otherExchangePrices': 'true'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get price quote
                async with session.get(
                    f"{self.aggregators['paraswap']['base_url']}{self.aggregators['paraswap']['endpoints']['prices']}",
                    params=price_params
                ) as response:
                    if response.status != 200:
                        return None
                    
                    price_data = await response.json()
                    
                    if not price_data.get('priceRoute'):
                        return None
                    
                    # Build transaction
                    tx_params = {
                        'srcToken': token_in,
                        'destToken': token_out,
                        'srcAmount': str(amount_in),
                        'destAmount': price_data['priceRoute']['destAmount'],
                        'priceRoute': price_data['priceRoute'],
                        'userAddress': self.config.get('executor_address'),
                        'partner': 'atom',
                        'partnerAddress': self.config.get('affiliate_address', '0x0000000000000000000000000000000000000000'),
                        'partnerFeeBps': '10'  # 0.1%
                    }
                    
                    async with session.post(
                        f"{self.aggregators['paraswap']['base_url']}{self.aggregators['paraswap']['endpoints']['transactions']}",
                        json=tx_params
                    ) as tx_response:
                        if tx_response.status == 200:
                            tx_data = await tx_response.json()
                            
                            quote = RouteQuote(
                                aggregator='paraswap',
                                path=self._extract_paraswap_path(price_data),
                                pools=price_data['priceRoute']['bestRoute'],
                                amount_in=int(price_data['priceRoute']['srcAmount']),
                                amount_out=int(price_data['priceRoute']['destAmount']),
                                gas_estimate=int(price_data['priceRoute'].get('gasCost', 350000)),
                                price_impact=Decimal(price_data['priceRoute'].get('priceImpact', '0')),
                                call_data=bytes.fromhex(tx_data['data'][2:]),
                                to_address=tx_data['to'],
                                value=int(tx_data.get('value', '0')),
                                deadline=int(time.time()) + 300
                            )
                            
                            self._cache_quote(cache_key, quote)
                            return quote
                            
        except Exception as e:
            print(f"Paraswap API error: {e}")
        
        return None
    
    async def _find_internal_route(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        max_hops: int
    ) -> Optional[RouteQuote]:
        """Find route using internal graph (Dijkstra/A*)"""
        if not self.routing_graph.has_node(token_in) or not self.routing_graph.has_node(token_out):
            return None
        
        try:
            # Find shortest path weighted by liquidity
            path = nx.shortest_path(
                self.routing_graph,
                token_in,
                token_out,
                weight='weight',
                method='dijkstra'
            )
            
            if len(path) > max_hops + 1:
                return None
            
            # Calculate output through path
            current_amount = amount_in
            pools = []
            gas_estimate = 0
            
            for i in range(len(path) - 1):
                from_token = path[i]
                to_token = path[i + 1]
                
                # Get best pool for this hop
                pool_data = self.routing_graph[from_token][to_token]
                pool = pool_data['pool']
                
                # Calculate output for this hop
                output = self._calculate_pool_output(
                    pool['type'],
                    pool['reserves'],
                    current_amount,
                    from_token,
                    to_token
                )
                
                pools.append({
                    'pool': pool['address'],
                    'type': pool['type'],
                    'input': current_amount,
                    'output': output
                })
                
                current_amount = output
                gas_estimate += pool.get('gas', 150000)
            
            # Build call data for multi-hop swap
            call_data = self._encode_multihop_swap(path, pools, amount_in)
            
            return RouteQuote(
                aggregator='internal',
                path=path,
                pools=pools,
                amount_in=amount_in,
                amount_out=current_amount,
                gas_estimate=gas_estimate,
                price_impact=Decimal('0'),  # TODO: Calculate actual impact
                call_data=call_data,
                to_address=self.config.get('executor_address'),
                value=0,
                deadline=int(time.time()) + 300
            )
            
        except nx.NetworkXNoPath:
            return None
    
    def _calculate_pool_output(
        self,
        pool_type: str,
        reserves: Dict,
        amount_in: int,
        token_in: str,
        token_out: str
    ) -> int:
        """Calculate output amount for different pool types"""
        if pool_type == 'uniswap_v2':
            # Constant product formula
            reserve_in = reserves[token_in]
            reserve_out = reserves[token_out]
            
            amount_in_with_fee = amount_in * 997  # 0.3% fee
            numerator = amount_in_with_fee * reserve_out
            denominator = (reserve_in * 1000) + amount_in_with_fee
            
            return numerator // denominator
            
        elif pool_type == 'curve':
            # Simplified Curve calculation (actual is more complex)
            # This is a placeholder - real Curve math requires the pool's A parameter
            return int(amount_in * 0.998)  # Approximate
            
        else:
            # Default to simple ratio
            return int(amount_in * 0.997)
    
    def update_routing_graph(self, pool_updates: List[Dict]):
        """Update internal routing graph with new pool data"""
        for update in pool_updates:
            token0 = update['token0']
            token1 = update['token1']
            
            # Add nodes if they don't exist
            if not self.routing_graph.has_node(token0):
                self.routing_graph.add_node(token0)
            if not self.routing_graph.has_node(token1):
                self.routing_graph.add_node(token1)
            
            # Calculate edge weight based on liquidity
            liquidity = update.get('liquidity', 0)
            weight = 1 / (liquidity + 1)  # Inverse of liquidity for shortest path
            
            # Add edges in both directions
            self.routing_graph.add_edge(
                token0,
                token1,
                weight=weight,
                pool=update
            )
            self.routing_graph.add_edge(
                token1,
                token0,
                weight=weight,
                pool=update
            )
            
            # Update liquidity map
            self.liquidity_map[token0][token1] = liquidity
            self.liquidity_map[token1][token0] = liquidity
    
    async def _simulate_trade(self, quote: RouteQuote) -> bool:
        """Simulate trade execution using eth_call"""
        try:
            # Build simulation transaction
            sim_tx = {
                'from': self.config.get('executor_address'),
                'to': quote.to_address,
                'data': '0x' + quote.call_data.hex(),
                'value': quote.value
            }
            
            # Add access list for gas optimization
            if self.config.get('use_access_list', True):
                access_list = await self._build_access_list(quote)
                sim_tx['accessList'] = access_list
            
            # Simulate with eth_call
            result = self.w3.eth.call(sim_tx)
            
            # Decode result based on aggregator
            success = self._decode_simulation_result(quote.aggregator, result)
            
            if not success:
                print(f"⚠️  Simulation failed for {quote.aggregator} route")
                return False
            
            # Additional profitability check
            gas_cost = quote.gas_estimate * self.w3.eth.gas_price
            min_profit = self.config.get('min_profit_wei', Web3.toWei(0.01, 'ether'))
            
            # For arbitrage, we need to check full cycle profitability
            # This is handled by the caller
            
            return True
            
        except Exception as e:
            print(f"Simulation error: {e}")
            return False
    
    async def _build_access_list(self, quote: RouteQuote) -> List[Dict]:
        """Build EIP-2930 access list for gas optimization"""
        access_list = []
        
        # Add aggregator contract
        access_list.append({
            'address': quote.to_address,
            'storageKeys': []
        })
        
        # Add token contracts
        for token in quote.path:
            access_list.append({
                'address': token,
                'storageKeys': [
                    # Common storage slots for ERC20 tokens
                    '0x0',  # totalSupply
                    '0x1',  # balances mapping
                    '0x2',  # allowances mapping
                ]
            })
        
        # Add pool contracts
        for pool_data in quote.pools:
            if isinstance(pool_data, dict) and 'pool' in pool_data:
                access_list.append({
                    'address': pool_data['pool'],
                    'storageKeys': []
                })
        
        return access_list
    
    def _extract_0x_path(self, data: Dict) -> List[str]:
        """Extract token path from 0x response"""
        path = [data['sellTokenAddress']]
        
        # Parse orders to find intermediate tokens
        orders = data.get('orders', [])
        for order in orders:
            if 'makerToken' in order and order['makerToken'] not in path:
                path.append(order['makerToken'])
        
        path.append(data['buyTokenAddress'])
        return path
    
    def _extract_1inch_path(self, data: Dict) -> List[str]:
        """Extract token path from 1inch response"""
        # 1inch provides protocols used but not always the full path
        # We can infer from the protocols
        return [data['fromToken']['address'], data['toToken']['address']]
    
    def _extract_paraswap_path(self, data: Dict) -> List[str]:
        """Extract token path from Paraswap response"""
        path = [data['priceRoute']['srcToken']]
        
        # Parse best route for intermediate tokens
        for route in data['priceRoute']['bestRoute']:
            for swap in route['swaps']:
                for exchange in swap['swapExchanges']:
                    if 'destToken' in exchange and exchange['destToken'] not in path:
                        path.append(exchange['destToken'])
        
        return path
    
    def _encode_multihop_swap(self, path: List[str], pools: List[Dict], amount_in: int) -> bytes:
        """Encode call data for multi-hop swap"""
        # This should match your arbitrage contract's interface
        # Example encoding for a generic multihop swap
        function_signature = Web3.keccak(text="swapMultihop(address[],address[],uint256,uint256)")[:4]
        
        pool_addresses = [p['pool'] for p in pools]
        min_amount_out = int(pools[-1]['output'] * 0.995)  # 0.5% slippage
        
        encoded_params = Web3.encode_abi(
            ['address[]', 'address[]', 'uint256', 'uint256'],
            [path, pool_addresses, amount_in, min_amount_out]
        )
        
        return function_signature + encoded_params
    
    def _decode_simulation_result(self, aggregator: str, result: bytes) -> bool:
        """Decode simulation result based on aggregator"""
        if len(result) == 0:
            return False
        
        if aggregator in ['0x', '1inch', 'paraswap']:
            # Most aggregators return the output amount
            return len(result) >= 32 and int.from_bytes(result[:32], 'big') > 0
        else:
            # For internal routes, check success boolean
            return len(result) >= 32 and result[31] == 1
    
    def _calculate_net_output(self, quote: RouteQuote) -> int:
        """Calculate net output after gas costs"""
        gas_cost_in_token = self._estimate_gas_cost_in_tokens(
            quote.gas_estimate,
            quote.path[0],  # Assuming we measure in input token
            quote.path[-1]
        )
        
        return quote.amount_out - gas_cost_in_token
    
    def _estimate_gas_cost_in_tokens(self, gas_units: int, token: str, reference_token: str) -> int:
        """Estimate gas cost denominated in tokens"""
        # Simplified - in production, fetch actual ETH/token price
        gas_cost_eth = gas_units * self.w3.eth.gas_price
        
        # Assume 1 ETH = 2000 USDC for example
        eth_price = 2000 * 10**6  # 6 decimals for USDC
        
        if token == '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48':  # USDC
            return (gas_cost_eth * eth_price) // 10**18
        else:
            # For other tokens, would need price feed
            return 0
    
    def _get_cached_quote(self, key: str) -> Optional[RouteQuote]:
        """Get quote from cache if still valid"""
        if key in self.quote_cache:
            quote, timestamp = self.quote_cache[key]
            if time.time() - timestamp < self.cache_duration:
                return quote
        return None
    
    def _cache_quote(self, key: str, quote: RouteQuote):
        """Cache quote with timestamp"""
        self.quote_cache[key] = (quote, time.time())
        
        # Clean old entries
        current_time = time.time()
        self.quote_cache = {
            k: v for k, v in self.quote_cache.items()
            if current_time - v[1] < self.cache_duration * 2
        }
    
    def _deploy_simulation_contract(self) -> str:
        """Deploy contract for complex simulations"""
        # In production, this would deploy an actual contract
        # For now, return placeholder
        return self.config.get('simulation_contract', '0x0000000000000000000000000000000000000000')

# Arbitrage finder using pathfinding
class SmartArbitrageFinder:
    """Find arbitrage opportunities using smart routing"""
    
    def __init__(self, pathfinder: ATOMPathfinder, config: Dict):
        self.pathfinder = pathfinder
        self.config = config
        self.w3 = pathfinder.w3
    
    async def find_arbitrage_with_routing(
        self,
        tokens: List[str],
        amount: Optional[int] = None
    ) -> List[Dict]:
        """Find arbitrage opportunities using pathfinding"""
        opportunities = []
        
        if amount is None:
            amount = self.config.get('default_trade_amount', Web3.toWei(10, 'ether'))
        
        # Check all token pairs
        for i, token_a in enumerate(tokens):
            for token_b in tokens[i+1:]:
                # Find best routes A->B and B->A
                route_ab = await self.pathfinder.find_best_route(token_a, token_b, amount)
                
                if route_ab:
                    # Use output from first route as input for reverse
                    route_ba = await self.pathfinder.find_best_route(
                        token_b,
                        token_a,
                        route_ab.amount_out
                    )
                    
                    if route_ba:
                        # Check profitability
                        profit = route_ba.amount_out - amount
                        
                        # Calculate total gas
                        total_gas = route_ab.gas_estimate + route_ba.gas_estimate
                        gas_cost = total_gas * self.w3.eth.gas_price
                        
                        net_profit = profit - gas_cost
                        
                        if net_profit > self.config.get('min_profit_wei', Web3.toWei(0.01, 'ether')):
                            opportunities.append({
                                'token_a': token_a,
                                'token_b': token_b,
                                'route_ab': route_ab,
                                'route_ba': route_ba,
                                'profit': profit,
                                'gas_cost': gas_cost,
                                'net_profit': net_profit,
                                'roi': (net_profit / amount) * 100
                            })
        
        # Sort by net profit
        opportunities.sort(key=lambda x: x['net_profit'], reverse=True)
        
        return opportunities