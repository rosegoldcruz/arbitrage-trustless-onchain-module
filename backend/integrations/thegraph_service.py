"""
📊 THE GRAPH PROTOCOL SERVICE (PYTHON)
Production-grade subgraph queries for Base Sepolia
API Key: f187a007e656031f58294838b7219a0f
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

# Environment configuration
THE_GRAPH_API_KEY = os.getenv('THE_GRAPH_API_KEY', 'f187a007e656031f58294838b7219a0f')
THE_GRAPH_STUDIO_URL = os.getenv('THE_GRAPH_STUDIO_URL', 'https://api.studio.thegraph.com/query/atom')

# Base Sepolia subgraph endpoints
SUBGRAPH_ENDPOINTS = {
    'BALANCER_V3': f"{THE_GRAPH_STUDIO_URL}/balancer-v3-base-sepolia/{THE_GRAPH_API_KEY}",
    'UNISWAP_V3': f"{THE_GRAPH_STUDIO_URL}/uniswap-v3-base-sepolia/{THE_GRAPH_API_KEY}",
    'AAVE_V3': f"{THE_GRAPH_STUDIO_URL}/aave-v3-base-sepolia/{THE_GRAPH_API_KEY}",
    'COMPOUND_V3': f"{THE_GRAPH_STUDIO_URL}/compound-v3-base-sepolia/{THE_GRAPH_API_KEY}"
}

@dataclass
class Token:
    id: str
    symbol: str
    name: str
    decimals: int
    total_supply: str
    volume: Optional[str] = None
    volume_usd: Optional[str] = None
    price_usd: Optional[str] = None

@dataclass
class Pool:
    id: str
    token0: Token
    token1: Token
    liquidity: str
    sqrt_price: str
    tick: Optional[int] = None
    fee_growth_global0_x128: Optional[str] = None
    fee_growth_global1_x128: Optional[str] = None
    volume_usd: str = "0"
    fees_usd: Optional[str] = None
    tx_count: str = "0"
    total_value_locked_usd: str = "0"

@dataclass
class Swap:
    id: str
    transaction_id: str
    block_number: str
    timestamp: str
    pool_id: str
    token0_symbol: str
    token1_symbol: str
    sender: str
    recipient: str
    amount0: str
    amount1: str
    amount_usd: Optional[str] = None
    sqrt_price_x96: str = "0"
    tick: Optional[int] = None

@dataclass
class ArbitrageOpportunity:
    id: str
    token_pair: str
    pool1_id: str
    pool1_price: float
    pool1_tvl: float
    pool2_id: str
    pool2_price: float
    pool2_tvl: float
    spread_bps: int
    estimated_profit_usd: float
    timestamp: int
    source: str = "thegraph"

# GraphQL query templates
QUERIES = {
    'TOP_POOLS': """
        query GetTopPools($first: Int!, $orderBy: String!, $orderDirection: String!) {
            pools(
                first: $first
                orderBy: $orderBy
                orderDirection: $orderDirection
                where: { totalValueLockedUSD_gt: "1000" }
            ) {
                id
                token0 {
                    id
                    symbol
                    name
                    decimals
                }
                token1 {
                    id
                    symbol
                    name
                    decimals
                }
                liquidity
                sqrtPrice
                tick
                volumeUSD
                feesUSD
                txCount
                totalValueLockedUSD
            }
        }
    """,

    'RECENT_SWAPS': """
        query GetRecentSwaps($first: Int!, $pool: String) {
            swaps(
                first: $first
                orderBy: timestamp
                orderDirection: desc
                where: { pool: $pool }
            ) {
                id
                transaction {
                    id
                    blockNumber
                    timestamp
                }
                pool {
                    id
                    token0 {
                        symbol
                    }
                    token1 {
                        symbol
                    }
                }
                sender
                recipient
                amount0
                amount1
                amountUSD
                sqrtPriceX96
                tick
            }
        }
    """,

    'TOKEN_PRICES': """
        query GetTokenPrices($tokens: [String!]!) {
            tokens(where: { id_in: $tokens }) {
                id
                symbol
                name
                decimals
                totalSupply
                volume
                volumeUSD
                priceUSD
            }
        }
    """,

    'POOL_HOURLY_DATA': """
        query GetPoolHourlyData($pool: String!, $first: Int!) {
            poolHourDatas(
                first: $first
                orderBy: periodStartUnix
                orderDirection: desc
                where: { pool: $pool }
            ) {
                id
                periodStartUnix
                liquidity
                sqrtPrice
                token0Price
                token1Price
                volumeToken0
                volumeToken1
                volumeUSD
                feesUSD
                txCount
                open
                high
                low
                close
            }
        }
    """
}

class TheGraphService:
    """Production-grade The Graph Protocol service for Base Sepolia"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'ATOM-Arbitrage-Engine/1.0'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def _execute_query(
        self,
        endpoint: str,
        query: str,
        variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute GraphQL query against specified subgraph"""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
            
        # Rate limiting
        await asyncio.sleep(self.rate_limit_delay)
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            async with self.session.post(endpoint, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                    
                result = await response.json()
                
                if 'errors' in result:
                    raise Exception(f"GraphQL errors: {result['errors']}")
                    
                return result.get('data', {})
                
        except Exception as e:
            logger.error(f"The Graph query failed: {e}")
            logger.error(f"Endpoint: {endpoint}")
            logger.error(f"Query: {query[:200]}...")
            raise
            
    async def get_top_pools(
        self,
        limit: int = 20,
        order_by: str = 'totalValueLockedUSD',
        order_direction: str = 'desc'
    ) -> List[Pool]:
        """Get top pools by TVL from Uniswap V3 subgraph"""
        try:
            data = await self._execute_query(
                SUBGRAPH_ENDPOINTS['UNISWAP_V3'],
                QUERIES['TOP_POOLS'],
                {
                    'first': limit,
                    'orderBy': order_by,
                    'orderDirection': order_direction
                }
            )
            
            pools = []
            for pool_data in data.get('pools', []):
                try:
                    # Parse token data
                    token0 = Token(
                        id=pool_data['token0']['id'],
                        symbol=pool_data['token0']['symbol'],
                        name=pool_data['token0']['name'],
                        decimals=int(pool_data['token0']['decimals'])
                    )
                    
                    token1 = Token(
                        id=pool_data['token1']['id'],
                        symbol=pool_data['token1']['symbol'],
                        name=pool_data['token1']['name'],
                        decimals=int(pool_data['token1']['decimals'])
                    )
                    
                    # Parse pool data
                    pool = Pool(
                        id=pool_data['id'],
                        token0=token0,
                        token1=token1,
                        liquidity=pool_data['liquidity'],
                        sqrt_price=pool_data['sqrtPrice'],
                        tick=pool_data.get('tick'),
                        volume_usd=pool_data.get('volumeUSD', '0'),
                        fees_usd=pool_data.get('feesUSD'),
                        tx_count=pool_data.get('txCount', '0'),
                        total_value_locked_usd=pool_data.get('totalValueLockedUSD', '0')
                    )
                    
                    pools.append(pool)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse pool data: {e}")
                    continue
                    
            logger.info(f"Successfully fetched {len(pools)} pools from The Graph")
            return pools
            
        except Exception as e:
            logger.error(f"Failed to get top pools: {e}")
            return []
            
    async def get_recent_swaps(self, pool_id: str, first: int = 100) -> List[Swap]:
        """Get recent swaps for a specific pool"""
        try:
            data = await self._execute_query(
                SUBGRAPH_ENDPOINTS['UNISWAP_V3'],
                QUERIES['RECENT_SWAPS'],
                {'first': first, 'pool': pool_id}
            )
            
            swaps = []
            for swap_data in data.get('swaps', []):
                try:
                    swap = Swap(
                        id=swap_data['id'],
                        transaction_id=swap_data['transaction']['id'],
                        block_number=swap_data['transaction']['blockNumber'],
                        timestamp=swap_data['transaction']['timestamp'],
                        pool_id=swap_data['pool']['id'],
                        token0_symbol=swap_data['pool']['token0']['symbol'],
                        token1_symbol=swap_data['pool']['token1']['symbol'],
                        sender=swap_data['sender'],
                        recipient=swap_data['recipient'],
                        amount0=swap_data['amount0'],
                        amount1=swap_data['amount1'],
                        amount_usd=swap_data.get('amountUSD'),
                        sqrt_price_x96=swap_data['sqrtPriceX96'],
                        tick=swap_data.get('tick')
                    )
                    swaps.append(swap)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse swap data: {e}")
                    continue
                    
            logger.info(f"Successfully fetched {len(swaps)} swaps for pool {pool_id}")
            return swaps
            
        except Exception as e:
            logger.error(f"Failed to get recent swaps: {e}")
            return []
            
    async def get_token_prices(self, token_addresses: List[str]) -> List[Token]:
        """Get token prices for specified token addresses"""
        try:
            # Convert to lowercase for subgraph compatibility
            addresses = [addr.lower() for addr in token_addresses]
            
            data = await self._execute_query(
                SUBGRAPH_ENDPOINTS['UNISWAP_V3'],
                QUERIES['TOKEN_PRICES'],
                {'tokens': addresses}
            )
            
            tokens = []
            for token_data in data.get('tokens', []):
                try:
                    token = Token(
                        id=token_data['id'],
                        symbol=token_data['symbol'],
                        name=token_data['name'],
                        decimals=int(token_data['decimals']),
                        total_supply=token_data['totalSupply'],
                        volume=token_data.get('volume'),
                        volume_usd=token_data.get('volumeUSD'),
                        price_usd=token_data.get('priceUSD')
                    )
                    tokens.append(token)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse token data: {e}")
                    continue
                    
            logger.info(f"Successfully fetched {len(tokens)} token prices")
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to get token prices: {e}")
            return []
            
    def _calculate_price_from_sqrt_price(self, sqrt_price_x96: str) -> float:
        """Calculate price from Uniswap V3 sqrtPriceX96"""
        try:
            sqrt_price = float(sqrt_price_x96)
            Q96 = 2 ** 96
            price = (sqrt_price / Q96) ** 2
            return price
        except:
            return 0.0
            
    def _estimate_profit(self, price_diff: float, avg_price: float) -> float:
        """Estimate profit from price difference"""
        if avg_price == 0:
            return 0.0
            
        trade_amount = 1000  # $1000 trade
        profit_ratio = price_diff / avg_price
        return trade_amount * profit_ratio * 0.8  # 80% efficiency factor
        
    async def find_arbitrage_opportunities(
        self,
        min_spread_bps: int = 23,
        min_tvl: float = 10000
    ) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities by comparing prices across pools"""
        try:
            # Get top pools
            pools = await self.get_top_pools(50)
            
            # Filter pools by TVL
            eligible_pools = [
                pool for pool in pools
                if float(pool.total_value_locked_usd) >= min_tvl
            ]
            
            # Group pools by token pairs
            token_pair_groups = {}
            for pool in eligible_pools:
                pair_key = '-'.join(sorted([pool.token0.symbol, pool.token1.symbol]))
                if pair_key not in token_pair_groups:
                    token_pair_groups[pair_key] = []
                token_pair_groups[pair_key].append(pool)
                
            # Find arbitrage opportunities
            opportunities = []
            
            for pair_key, pools_for_pair in token_pair_groups.items():
                if len(pools_for_pair) < 2:
                    continue
                    
                # Calculate price differences between pools
                for i in range(len(pools_for_pair)):
                    for j in range(i + 1, len(pools_for_pair)):
                        pool1 = pools_for_pair[i]
                        pool2 = pools_for_pair[j]
                        
                        # Calculate prices from sqrtPrice
                        price1 = self._calculate_price_from_sqrt_price(pool1.sqrt_price)
                        price2 = self._calculate_price_from_sqrt_price(pool2.sqrt_price)
                        
                        if price1 == 0 or price2 == 0:
                            continue
                            
                        price_diff = abs(price1 - price2)
                        avg_price = (price1 + price2) / 2
                        spread_bps = (price_diff / avg_price) * 10000
                        
                        if spread_bps >= min_spread_bps:
                            opportunity = ArbitrageOpportunity(
                                id=f"{pool1.id}-{pool2.id}",
                                token_pair=pair_key,
                                pool1_id=pool1.id,
                                pool1_price=price1,
                                pool1_tvl=float(pool1.total_value_locked_usd),
                                pool2_id=pool2.id,
                                pool2_price=price2,
                                pool2_tvl=float(pool2.total_value_locked_usd),
                                spread_bps=int(spread_bps),
                                estimated_profit_usd=self._estimate_profit(price_diff, avg_price),
                                timestamp=int(datetime.now().timestamp())
                            )
                            opportunities.append(opportunity)
                            
            # Sort by spread (highest first)
            opportunities.sort(key=lambda x: x.spread_bps, reverse=True)
            
            logger.info(f"Found {len(opportunities)} arbitrage opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to find arbitrage opportunities: {e}")
            return []
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check for The Graph service"""
        start_time = datetime.now()
        
        try:
            # Try to fetch one pool
            pools = await self.get_top_pools(1)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'status': 'healthy',
                'latency_ms': latency,
                'pools_available': len(pools) > 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            latency = (datetime.now() - start_time).total_seconds() * 1000
            return {
                'status': 'unhealthy',
                'error': str(e),
                'latency_ms': latency,
                'timestamp': datetime.now().isoformat()
            }

# Export singleton instance
thegraph_service = TheGraphService()
