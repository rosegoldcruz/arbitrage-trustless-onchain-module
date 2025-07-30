"""
🏊 ATOM Balancer GraphQL Client - Real-time Pool Data & Arbitrage Intelligence
Advanced integration with Balancer's v3 GraphQL API for opportunity detection
"""

import asyncio
import logging
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

@dataclass
class BalancerPool:
    """Balancer pool data structure"""
    id: str
    address: str
    name: str
    chain: str
    pool_type: str
    version: int
    tokens: List[Dict[str, Any]]
    total_liquidity: float
    swap_fee: float
    apr_items: List[Dict[str, Any]]
    balances: List[str]
    weights: List[float]

@dataclass
class SwapPath:
    """Smart Order Router swap path"""
    swap_amount_raw: str
    return_amount_raw: str
    price_impact: float
    route: List[Dict[str, Any]]

@dataclass
class PoolEvent:
    """Pool event (swap, add, remove)"""
    event_type: str
    value_usd: float
    timestamp: int
    pool_id: str
    tokens: List[Dict[str, Any]]

class BalancerClient:
    """Advanced Balancer GraphQL API client for ATOM arbitrage system"""
    
    def __init__(self):
        self.api_url = "https://api-v3.balancer.fi/graphql"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """Execute GraphQL query with error handling"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            payload = {"query": query}
            if variables:
                payload["variables"] = variables
                
            async with self.session.post(self.api_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "errors" in data:
                        logger.error(f"GraphQL errors: {data['errors']}")
                        return None
                    return data.get("data")
                else:
                    logger.error(f"HTTP error {response.status}: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return None

    async def get_user_pool_balances(self, user_address: str, chains: List[str] = ["BASE"]) -> List[BalancerPool]:
        """Get pool balances for a specific user"""
        query = """
        {
          poolGetPools(where: {chainIn: %s, userAddress: "%s"}) {
            address
            name
            chain
            userBalance {
              stakedBalances {
                balance
                balanceUsd
                stakingType
              }
              walletBalance
              walletBalanceUsd
              totalBalance
              totalBalanceUsd
            }
            dynamicData {
              totalLiquidity
              aprItems {
                apr
                title
                type
              }
            }
          }
        }
        """ % (str(chains).replace("'", ""), user_address)
        
        result = await self._execute_query(query)
        if not result or "poolGetPools" not in result:
            return []
            
        pools = []
        for pool_data in result["poolGetPools"]:
            try:
                pool = BalancerPool(
                    id=pool_data.get("address", ""),
                    address=pool_data.get("address", ""),
                    name=pool_data.get("name", ""),
                    chain=pool_data.get("chain", ""),
                    pool_type="weighted",  # Default
                    version=3,
                    tokens=[],
                    total_liquidity=pool_data.get("dynamicData", {}).get("totalLiquidity", 0),
                    swap_fee=0.003,  # Default 0.3%
                    apr_items=pool_data.get("dynamicData", {}).get("aprItems", []),
                    balances=[],
                    weights=[]
                )
                pools.append(pool)
            except Exception as e:
                logger.warning(f"Failed to parse pool data: {e}")
                continue
                
        return pools

    async def get_pool_events(self, pool_ids: List[str], event_types: List[str] = ["SWAP"], 
                            chains: List[str] = ["BASE"], limit: int = 1000) -> List[PoolEvent]:
        """Get pool events (swaps, adds, removes) for analysis"""
        pool_ids_str = '", "'.join(pool_ids)
        query = """
        {
          poolEvents(
            where: {
              typeIn: %s,
              chainIn: %s,
              poolIdIn: ["%s"]
            },
            first: %d
          ) {
            type
            valueUsd
            timestamp
            poolId
            ... on GqlPoolSwapEventV3 {
              fee {
                address
                amount
                valueUsd
              }
            }
            ... on GqlPoolAddRemoveEventV3 {
              tokens {
                address
                amount
                valueUsd
              }
            }
          }
        }
        """ % (str(event_types).replace("'", ""), str(chains).replace("'", ""), pool_ids_str, limit)
        
        result = await self._execute_query(query)
        if not result or "poolEvents" not in result:
            return []
            
        events = []
        for event_data in result["poolEvents"]:
            try:
                event = PoolEvent(
                    event_type=event_data.get("type", ""),
                    value_usd=float(event_data.get("valueUsd", 0)),
                    timestamp=int(event_data.get("timestamp", 0)),
                    pool_id=event_data.get("poolId", ""),
                    tokens=event_data.get("tokens", [])
                )
                events.append(event)
            except Exception as e:
                logger.warning(f"Failed to parse event data: {e}")
                continue
                
        return events

    async def get_smart_order_router_paths(self, token_in: str, token_out: str, 
                                         amount: str, chain: str = "BASE") -> Optional[SwapPath]:
        """Query Smart Order Router for best swap paths"""
        query = """
        {
          sorGetSwapPaths(
            chain: %s,
            swapAmount: "%s",
            swapType: EXACT_IN,
            tokenIn: "%s",
            tokenOut: "%s"
          ) {
            swapAmountRaw
            returnAmountRaw
            priceImpact {
              priceImpact
              error
            }
            routes {
              tokenIn
              tokenOut
              tokenInAmount
              tokenOutAmount
            }
          }
        }
        """ % (chain, amount, token_in, token_out)
        
        result = await self._execute_query(query)
        if not result or "sorGetSwapPaths" not in result:
            return None
            
        sor_data = result["sorGetSwapPaths"]
        try:
            return SwapPath(
                swap_amount_raw=sor_data.get("swapAmountRaw", "0"),
                return_amount_raw=sor_data.get("returnAmountRaw", "0"),
                price_impact=float(sor_data.get("priceImpact", {}).get("priceImpact", 0)),
                route=sor_data.get("routes", [])
            )
        except Exception as e:
            logger.error(f"Failed to parse SOR data: {e}")
            return None

    async def get_high_tvl_pools(self, chains: List[str] = ["BASE"], min_tvl: float = 10000, 
                               limit: int = 50) -> List[BalancerPool]:
        """Get pools with high TVL for arbitrage opportunities"""
        query = """
        {
          poolGetPools(where: {chainIn: %s, minTvl: %f}, first: %d, orderBy: totalLiquidity) {
            id
            address
            name
            chain
            type
            version
            allTokens {
              address
              name
              symbol
            }
            poolTokens {
              address
              symbol
              balance
              weight
            }
            dynamicData {
              totalLiquidity
              aprItems {
                apr
                title
                type
              }
              swapFee
            }
          }
        }
        """ % (str(chains).replace("'", ""), min_tvl, limit)
        
        result = await self._execute_query(query)
        if not result or "poolGetPools" not in result:
            return []
            
        pools = []
        for pool_data in result["poolGetPools"]:
            try:
                tokens = pool_data.get("poolTokens", [])
                balances = [token.get("balance", "0") for token in tokens]
                weights = [float(token.get("weight", 0)) for token in tokens]
                
                pool = BalancerPool(
                    id=pool_data.get("id", ""),
                    address=pool_data.get("address", ""),
                    name=pool_data.get("name", ""),
                    chain=pool_data.get("chain", ""),
                    pool_type=pool_data.get("type", "weighted"),
                    version=int(pool_data.get("version", 3)),
                    tokens=pool_data.get("allTokens", []),
                    total_liquidity=float(pool_data.get("dynamicData", {}).get("totalLiquidity", 0)),
                    swap_fee=float(pool_data.get("dynamicData", {}).get("swapFee", 0.003)),
                    apr_items=pool_data.get("dynamicData", {}).get("aprItems", []),
                    balances=balances,
                    weights=weights
                )
                pools.append(pool)
            except Exception as e:
                logger.warning(f"Failed to parse pool data: {e}")
                continue
                
        return pools

    async def get_pool_details(self, pool_id: str, chain: str = "BASE") -> Optional[BalancerPool]:
        """Get detailed information for a specific pool"""
        query = """
        {
          poolGetPool(
            id: "%s",
            chain: %s
          ) {
            id
            name
            type
            version
            address
            allTokens {
              address
              name
              symbol
            }
            poolTokens {
              address
              symbol
              balance
              weight
            }
            dynamicData {
              totalLiquidity
              swapFee
              aprItems {
                title
                type
                apr
              }
            }
          }
        }
        """ % (pool_id, chain)
        
        result = await self._execute_query(query)
        if not result or "poolGetPool" not in result:
            return None
            
        pool_data = result["poolGetPool"]
        try:
            tokens = pool_data.get("poolTokens", [])
            balances = [token.get("balance", "0") for token in tokens]
            weights = [float(token.get("weight", 0)) for token in tokens]
            
            return BalancerPool(
                id=pool_data.get("id", ""),
                address=pool_data.get("address", ""),
                name=pool_data.get("name", ""),
                chain=chain,
                pool_type=pool_data.get("type", "weighted"),
                version=int(pool_data.get("version", 3)),
                tokens=pool_data.get("allTokens", []),
                total_liquidity=float(pool_data.get("dynamicData", {}).get("totalLiquidity", 0)),
                swap_fee=float(pool_data.get("dynamicData", {}).get("swapFee", 0.003)),
                apr_items=pool_data.get("dynamicData", {}).get("aprItems", []),
                balances=balances,
                weights=weights
            )
        except Exception as e:
            logger.error(f"Failed to parse pool details: {e}")
            return None

    async def find_arbitrage_opportunities(self, chains: List[str] = ["BASE"],
                                         min_spread_bps: int = 23) -> List[Dict[str, Any]]:
        """Find cross-pool arbitrage opportunities using real Balancer data"""
        try:
            # Get high-TVL pools for analysis
            pools = await self.get_high_tvl_pools(chains=chains, min_tvl=50000, limit=100)

            opportunities = []

            # Analyze each pool for arbitrage potential
            for pool in pools:
                if len(pool.tokens) < 2:
                    continue

                # Check each token pair in the pool
                for i, token_a in enumerate(pool.tokens):
                    for j, token_b in enumerate(pool.tokens[i+1:], i+1):
                        try:
                            # Get SOR path for this pair
                            swap_path = await self.get_smart_order_router_paths(
                                token_in=token_a["address"],
                                token_out=token_b["address"],
                                amount="1000000000000000000",  # 1 ETH equivalent
                                chain=pool.chain
                            )

                            if swap_path and swap_path.price_impact > 0:
                                # Calculate potential spread
                                spread_bps = int(swap_path.price_impact * 10000)

                                if spread_bps >= min_spread_bps:
                                    opportunity = {
                                        "pool_id": pool.id,
                                        "pool_address": pool.address,
                                        "token_in": token_a,
                                        "token_out": token_b,
                                        "spread_bps": spread_bps,
                                        "price_impact": swap_path.price_impact,
                                        "tvl": pool.total_liquidity,
                                        "swap_fee": pool.swap_fee,
                                        "chain": pool.chain,
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    }
                                    opportunities.append(opportunity)

                        except Exception as e:
                            logger.warning(f"Failed to analyze pair {token_a['symbol']}/{token_b['symbol']}: {e}")
                            continue

            # Sort by spread (highest first)
            opportunities.sort(key=lambda x: x["spread_bps"], reverse=True)

            logger.info(f"🎯 Found {len(opportunities)} Balancer arbitrage opportunities")
            return opportunities[:20]  # Return top 20

        except Exception as e:
            logger.error(f"Failed to find arbitrage opportunities: {e}")
            return []

    async def get_pool_liquidity_changes(self, pool_ids: List[str], hours: int = 24) -> Dict[str, List[PoolEvent]]:
        """Track liquidity changes for opportunity detection"""
        try:
            events = await self.get_pool_events(
                pool_ids=pool_ids,
                event_types=["ADD", "REMOVE"],
                limit=1000
            )

            # Group events by pool
            pool_events = {}
            for event in events:
                if event.pool_id not in pool_events:
                    pool_events[event.pool_id] = []
                pool_events[event.pool_id].append(event)

            return pool_events

        except Exception as e:
            logger.error(f"Failed to get liquidity changes: {e}")
            return {}

    async def monitor_high_volume_pools(self, chains: List[str] = ["BASE"]) -> List[Dict[str, Any]]:
        """Monitor pools with high trading volume for MEV opportunities"""
        try:
            pools = await self.get_high_tvl_pools(chains=chains, limit=50)

            high_volume_pools = []
            for pool in pools:
                # Get recent swap events
                events = await self.get_pool_events(
                    pool_ids=[pool.id],
                    event_types=["SWAP"],
                    limit=100
                )

                if len(events) > 10:  # High activity threshold
                    total_volume = sum(event.value_usd for event in events)

                    pool_info = {
                        "pool_id": pool.id,
                        "name": pool.name,
                        "tvl": pool.total_liquidity,
                        "recent_volume": total_volume,
                        "swap_count": len(events),
                        "avg_swap_size": total_volume / len(events) if events else 0,
                        "tokens": [token["symbol"] for token in pool.tokens],
                        "chain": pool.chain
                    }
                    high_volume_pools.append(pool_info)

            # Sort by recent volume
            high_volume_pools.sort(key=lambda x: x["recent_volume"], reverse=True)

            return high_volume_pools

        except Exception as e:
            logger.error(f"Failed to monitor high volume pools: {e}")
            return []

# Singleton instance for global use
balancer_client = BalancerClient()
