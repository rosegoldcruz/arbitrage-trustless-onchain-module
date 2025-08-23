#!/usr/bin/env python3
"""
WebSocket Price Feed Connections
Real-time price monitoring across major Polygon DEXs
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Callable
import websockets
import aiohttp
from decimal import Decimal

logger = logging.getLogger(__name__)

class WebSocketPriceFeeds:
    def __init__(self):
        self.load_config()
        self.connections = {}
        self.price_callbacks = []
        self.latest_prices = {}
        self.connection_status = {}
        self.running = False
        
    def load_config(self):
        """Load WebSocket configuration"""
        # The Graph Protocol endpoints for Polygon
        self.subgraph_endpoints = {
            'uniswap_v3': 'wss://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3-polygon',
            'quickswap': 'wss://api.thegraph.com/subgraphs/name/sameepsi/quickswap06',
            'sushiswap': 'wss://api.thegraph.com/subgraphs/name/sushiswap/exchange-polygon',
            'balancer': 'wss://api.thegraph.com/subgraphs/name/balancer-labs/balancer-polygon-v2'
        }
        
        # Backup HTTP endpoints
        self.http_endpoints = {
            'uniswap_v3': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3-polygon',
            'quickswap': 'https://api.thegraph.com/subgraphs/name/sameepsi/quickswap06',
            'sushiswap': 'https://api.thegraph.com/subgraphs/name/sushiswap/exchange-polygon',
            'balancer': 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-polygon-v2'
        }
        
        # Token addresses to monitor from environment
        self.monitored_tokens = {
            'WETH': os.getenv('WETH_ADDRESS', '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'),
            'USDC': os.getenv('USDC_ADDRESS', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'),
            'USDT': os.getenv('USDT_ADDRESS', '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'),
            'DAI': os.getenv('DAI_ADDRESS', '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'),
            'WMATIC': os.getenv('WMATIC_ADDRESS', '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270')
        }
        
        # WebSocket configuration
        self.reconnect_attempts = int(os.getenv('WS_RECONNECT_ATTEMPTS', '5'))
        self.reconnect_delay = int(os.getenv('WS_RECONNECT_DELAY_MS', '5000')) / 1000
        self.heartbeat_interval = int(os.getenv('WS_HEARTBEAT_INTERVAL_MS', '30000')) / 1000
        
    def add_price_callback(self, callback: Callable):
        """Add callback function for price updates"""
        self.price_callbacks.append(callback)
        
    async def start_all_feeds(self):
        """Start all WebSocket price feeds"""
        self.running = True
        logger.info("Starting WebSocket price feeds...")
        
        # Start connections for each DEX
        tasks = []
        for dex_name in self.subgraph_endpoints.keys():
            task = asyncio.create_task(self._maintain_connection(dex_name))
            tasks.append(task)
            
        # Start price aggregation task
        aggregation_task = asyncio.create_task(self._aggregate_prices())
        tasks.append(aggregation_task)
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in price feeds: {e}")
        finally:
            self.running = False
            
    async def _maintain_connection(self, dex_name: str):
        """Maintain WebSocket connection for a specific DEX"""
        reconnect_count = 0
        
        while self.running and reconnect_count < self.reconnect_attempts:
            try:
                logger.info(f"Connecting to {dex_name} WebSocket...")
                
                # Try WebSocket connection first
                try:
                    await self._connect_websocket(dex_name)
                except Exception as ws_error:
                    logger.warning(f"WebSocket failed for {dex_name}: {ws_error}")
                    # Fallback to HTTP polling
                    await self._poll_http_endpoint(dex_name)
                    
                reconnect_count = 0  # Reset on successful connection
                
            except Exception as e:
                reconnect_count += 1
                logger.error(f"Connection failed for {dex_name} (attempt {reconnect_count}): {e}")
                
                if reconnect_count < self.reconnect_attempts:
                    await asyncio.sleep(self.reconnect_delay * reconnect_count)
                else:
                    logger.error(f"Max reconnection attempts reached for {dex_name}")
                    self.connection_status[dex_name] = 'failed'
                    
    async def _connect_websocket(self, dex_name: str):
        """Connect to WebSocket endpoint"""
        endpoint = self.subgraph_endpoints[dex_name]
        
        async with websockets.connect(endpoint) as websocket:
            self.connections[dex_name] = websocket
            self.connection_status[dex_name] = 'connected'
            logger.info(f"Connected to {dex_name} WebSocket")
            
            # Subscribe to price updates
            subscription = self._get_subscription_query(dex_name)
            await websocket.send(json.dumps(subscription))
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_price_data(dex_name, data)
                except Exception as e:
                    logger.error(f"Error processing {dex_name} message: {e}")
                    
    async def _poll_http_endpoint(self, dex_name: str):
        """Fallback HTTP polling for price data"""
        endpoint = self.http_endpoints[dex_name]
        self.connection_status[dex_name] = 'http_polling'
        
        while self.running:
            try:
                query = self._get_price_query(dex_name)
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(endpoint, json={'query': query}) as response:
                        data = await response.json()
                        await self._process_price_data(dex_name, data)
                        
                await asyncio.sleep(2)  # Poll every 2 seconds
                
            except Exception as e:
                logger.error(f"HTTP polling error for {dex_name}: {e}")
                await asyncio.sleep(5)
                
    def _get_subscription_query(self, dex_name: str) -> Dict:
        """Get GraphQL subscription query for real-time updates"""
        if dex_name == 'uniswap_v3':
            return {
                "id": "1",
                "type": "start",
                "payload": {
                    "query": """
                        subscription {
                            pools(
                                where: {
                                    token0_in: ["0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"]
                                    token1_in: ["0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"]
                                }
                                orderBy: totalValueLockedUSD
                                orderDirection: desc
                                first: 50
                            ) {
                                id
                                token0 { id symbol decimals }
                                token1 { id symbol decimals }
                                token0Price
                                token1Price
                                totalValueLockedUSD
                                volumeUSD
                                feeTier
                            }
                        }
                    """
                }
            }
        else:
            # Similar queries for other DEXs
            return {
                "id": "1",
                "type": "start",
                "payload": {
                    "query": f"""
                        subscription {{
                            pairs(
                                where: {{
                                    token0_in: {list(self.monitored_tokens.values())}
                                    token1_in: {list(self.monitored_tokens.values())}
                                }}
                                orderBy: reserveUSD
                                orderDirection: desc
                                first: 50
                            ) {{
                                id
                                token0 {{ id symbol decimals }}
                                token1 {{ id symbol decimals }}
                                token0Price
                                token1Price
                                reserveUSD
                                volumeUSD
                            }}
                        }}
                    """
                }
            }
            
    def _get_price_query(self, dex_name: str) -> str:
        """Get GraphQL query for HTTP polling"""
        if dex_name == 'uniswap_v3':
            return """
                query {
                    pools(
                        where: {
                            token0_in: ["0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"]
                            token1_in: ["0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"]
                        }
                        orderBy: totalValueLockedUSD
                        orderDirection: desc
                        first: 50
                    ) {
                        id
                        token0 { id symbol decimals }
                        token1 { id symbol decimals }
                        token0Price
                        token1Price
                        totalValueLockedUSD
                        volumeUSD
                        feeTier
                    }
                }
            """
        else:
            return """
                query {
                    pairs(
                        where: {
                            token0_in: ["0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"]
                            token1_in: ["0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"]
                        }
                        orderBy: reserveUSD
                        orderDirection: desc
                        first: 50
                    ) {
                        id
                        token0 { id symbol decimals }
                        token1 { id symbol decimals }
                        token0Price
                        token1Price
                        reserveUSD
                        volumeUSD
                    }
                }
            """
            
    async def _process_price_data(self, dex_name: str, data: Dict):
        """Process incoming price data"""
        try:
            if 'data' in data:
                pools_or_pairs = data['data'].get('pools', data['data'].get('pairs', []))
                
                for pool in pools_or_pairs:
                    token0 = pool['token0']
                    token1 = pool['token1']
                    
                    # Create price update
                    price_update = {
                        'dex': dex_name,
                        'timestamp': time.time(),
                        'pool_id': pool['id'],
                        'token0': {
                            'address': token0['id'],
                            'symbol': token0['symbol'],
                            'decimals': int(token0['decimals'])
                        },
                        'token1': {
                            'address': token1['id'],
                            'symbol': token1['symbol'],
                            'decimals': int(token1['decimals'])
                        },
                        'token0_price': float(pool['token0Price']),
                        'token1_price': float(pool['token1Price']),
                        'liquidity_usd': float(pool.get('totalValueLockedUSD', pool.get('reserveUSD', 0))),
                        'volume_usd': float(pool.get('volumeUSD', 0))
                    }
                    
                    # Store latest price
                    pair_key = f"{token0['symbol']}/{token1['symbol']}"
                    if dex_name not in self.latest_prices:
                        self.latest_prices[dex_name] = {}
                    self.latest_prices[dex_name][pair_key] = price_update
                    
                    # Notify callbacks
                    for callback in self.price_callbacks:
                        try:
                            await callback(price_update)
                        except Exception as e:
                            logger.error(f"Error in price callback: {e}")
                            
        except Exception as e:
            logger.error(f"Error processing price data from {dex_name}: {e}")
            
    async def _aggregate_prices(self):
        """Aggregate prices across DEXs for arbitrage detection"""
        while self.running:
            try:
                # Create aggregated price view
                aggregated = {}
                
                for dex_name, pairs in self.latest_prices.items():
                    for pair_key, price_data in pairs.items():
                        if pair_key not in aggregated:
                            aggregated[pair_key] = {}
                        aggregated[pair_key][dex_name] = price_data
                        
                # Detect arbitrage opportunities
                for pair_key, dex_prices in aggregated.items():
                    if len(dex_prices) >= 2:
                        await self._detect_arbitrage_opportunity(pair_key, dex_prices)
                        
                await asyncio.sleep(1)  # Aggregate every second
                
            except Exception as e:
                logger.error(f"Error in price aggregation: {e}")
                await asyncio.sleep(5)
                
    async def _detect_arbitrage_opportunity(self, pair_key: str, dex_prices: Dict):
        """Detect arbitrage opportunities between DEXs"""
        try:
            prices = []
            for dex_name, price_data in dex_prices.items():
                prices.append({
                    'dex': dex_name,
                    'price': price_data['token0_price'],
                    'liquidity': price_data['liquidity_usd'],
                    'data': price_data
                })
                
            # Sort by price
            prices.sort(key=lambda x: x['price'])
            
            if len(prices) >= 2:
                lowest = prices[0]
                highest = prices[-1]
                
                # Calculate potential profit
                price_diff = highest['price'] - lowest['price']
                profit_percentage = (price_diff / lowest['price']) * 100
                
                # Check if opportunity meets minimum threshold
                min_profit_threshold = 0.1  # 0.1%
                if profit_percentage > min_profit_threshold:
                    opportunity = {
                        'pair': pair_key,
                        'buy_dex': lowest['dex'],
                        'sell_dex': highest['dex'],
                        'buy_price': lowest['price'],
                        'sell_price': highest['price'],
                        'profit_percentage': profit_percentage,
                        'min_liquidity': min(lowest['liquidity'], highest['liquidity']),
                        'timestamp': time.time()
                    }
                    
                    # Notify opportunity callbacks
                    for callback in self.price_callbacks:
                        try:
                            await callback(opportunity)
                        except Exception as e:
                            logger.error(f"Error in opportunity callback: {e}")
                            
        except Exception as e:
            logger.error(f"Error detecting arbitrage opportunity: {e}")
            
    def get_connection_status(self) -> Dict:
        """Get status of all WebSocket connections"""
        return {
            'connections': self.connection_status,
            'total_pairs_monitored': sum(len(pairs) for pairs in self.latest_prices.values()),
            'last_update': max([
                max([price['timestamp'] for price in pairs.values()] + [0])
                for pairs in self.latest_prices.values()
            ] + [0])
        }
        
    def get_latest_prices(self, pair: Optional[str] = None) -> Dict:
        """Get latest prices for a specific pair or all pairs"""
        if pair:
            result = {}
            for dex_name, pairs in self.latest_prices.items():
                if pair in pairs:
                    result[dex_name] = pairs[pair]
            return result
        else:
            return self.latest_prices
            
    async def stop(self):
        """Stop all WebSocket connections"""
        self.running = False
        for connection in self.connections.values():
            if connection:
                await connection.close()
        logger.info("All WebSocket connections closed")
