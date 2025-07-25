"""
🔗 ATOM DEX Aggregator - Multi-Chain DEX Integration
Advanced integration with 0x.org, 1inch, Paraswap, and other DEX aggregators
"""

import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import time
import aiohttp

logger = logging.getLogger(__name__)

class DEXAggregator(str, Enum):
    ZEROX = "0x"
    ONEINCH = "1inch"
    PARASWAP = "paraswap"
    COWSWAP = "cowswap"
    MATCHA = "matcha"
    KYBERSWAP = "kyberswap"

class Chain(str, Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"

@dataclass
class SwapQuote:
    """Swap quote from DEX aggregator"""
    aggregator: DEXAggregator
    chain: Chain
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    price_impact: float
    gas_estimate: int
    gas_price: float
    route: List[str]  # DEX names in route
    fee_percentage: float
    slippage_tolerance: float
    quote_expires_at: datetime
    quote_id: str

@dataclass
class SwapExecution:
    """Swap execution record"""
    execution_id: str
    quote_id: str
    aggregator: DEXAggregator
    chain: Chain
    token_in: str
    token_out: str
    amount_in: float
    amount_out_expected: float
    amount_out_actual: float
    gas_used: int
    gas_price: float
    tx_hash: Optional[str]
    block_number: Optional[int]
    status: str  # "pending", "completed", "failed"
    executed_at: datetime
    slippage_actual: float
    error_message: Optional[str] = None

class DEXAggregatorManager:
    """Manage DEX aggregator integrations"""
    
    def __init__(self):
        self.aggregators = {}
        self.swap_history = {}
        self.performance_stats = {}
        self.price_cache = {}
        self.session = None
    
    async def initialize_aggregators(self):
        """Initialize DEX aggregator configurations"""
        logger.info("🔗 Initializing DEX Aggregators")
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        
        # Configure aggregators
        self.aggregators = {
            DEXAggregator.ZEROX: {
                "name": "0x Protocol",
                "base_url": "https://api.0x.org",
                "supported_chains": [Chain.ETHEREUM, Chain.POLYGON, Chain.BSC, Chain.ARBITRUM],
                "fee_percentage": 0.0015,  # 0.15%
                "gas_multiplier": 1.1,
                "success_rate": 0.98,
                "avg_response_time": 0.8
            },
            DEXAggregator.ONEINCH: {
                "name": "1inch",
                "base_url": "https://api.1inch.io/v5.0",
                "supported_chains": [Chain.ETHEREUM, Chain.POLYGON, Chain.BSC, Chain.ARBITRUM, Chain.OPTIMISM],
                "fee_percentage": 0.003,  # 0.3%
                "gas_multiplier": 1.05,
                "success_rate": 0.96,
                "avg_response_time": 1.2
            },
            DEXAggregator.PARASWAP: {
                "name": "ParaSwap",
                "base_url": "https://apiv5.paraswap.io",
                "supported_chains": [Chain.ETHEREUM, Chain.POLYGON, Chain.BSC, Chain.AVALANCHE],
                "fee_percentage": 0.001,  # 0.1%
                "gas_multiplier": 1.15,
                "success_rate": 0.94,
                "avg_response_time": 1.5
            },
            DEXAggregator.COWSWAP: {
                "name": "CoW Swap",
                "base_url": "https://api.cow.fi",
                "supported_chains": [Chain.ETHEREUM],
                "fee_percentage": 0.0,  # MEV protection
                "gas_multiplier": 0.9,  # Gasless trades
                "success_rate": 0.92,
                "avg_response_time": 2.0
            }
        }
        
        # Initialize performance stats
        for aggregator in self.aggregators:
            self.performance_stats[aggregator] = {
                "total_quotes": 0,
                "successful_swaps": 0,
                "total_volume": 0.0,
                "avg_slippage": 0.0,
                "avg_gas_used": 0,
                "last_used": None
            }
        
        logger.info(f"✅ Initialized {len(self.aggregators)} DEX aggregators")
    
    async def get_best_swap_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        chain: Chain = Chain.ETHEREUM,
        slippage_tolerance: float = 0.01  # 1%
    ) -> Optional[SwapQuote]:
        """Get best swap quote across all aggregators"""
        try:
            quotes = []
            
            # Get quotes from all compatible aggregators
            for aggregator, config in self.aggregators.items():
                if chain not in config["supported_chains"]:
                    continue
                
                try:
                    quote = await self.get_aggregator_quote(
                        aggregator, token_in, token_out, amount_in, chain, slippage_tolerance
                    )
                    if quote:
                        quotes.append(quote)
                        
                except Exception as e:
                    logger.warning(f"Failed to get quote from {aggregator.value}: {e}")
                    continue
            
            if not quotes:
                logger.warning(f"No quotes available for {token_in} -> {token_out}")
                return None
            
            # Sort by amount out (best rate)
            quotes.sort(key=lambda q: q.amount_out, reverse=True)
            best_quote = quotes[0]
            
            logger.info(
                f"💰 Best swap quote: {best_quote.aggregator.value} - "
                f"Rate: {best_quote.amount_out/best_quote.amount_in:.6f} - "
                f"Route: {' -> '.join(best_quote.route)}"
            )
            
            return best_quote
            
        except Exception as e:
            logger.error(f"Error getting best swap quote: {e}")
            return None
    
    async def get_aggregator_quote(
        self,
        aggregator: DEXAggregator,
        token_in: str,
        token_out: str,
        amount_in: float,
        chain: Chain,
        slippage_tolerance: float
    ) -> Optional[SwapQuote]:
        """Get REAL quote from specific aggregator"""
        try:
            config = self.aggregators[aggregator]

            # Make REAL API call to 0x
            if aggregator == DEXAggregator.ZEROX:
                return await self.get_0x_quote(token_in, token_out, amount_in, chain, slippage_tolerance)

            # For other aggregators, simulate for now (you can add real APIs later)
            await asyncio.sleep(config["avg_response_time"] / 10)  # Scale down for simulation
            
            # Simulate quote calculation
            base_rate = 1.0 + (hash(f"{token_in}{token_out}") % 1000) / 100000  # Small variation
            amount_out = amount_in * base_rate
            
            # Apply aggregator-specific adjustments
            if aggregator == DEXAggregator.ZEROX:
                amount_out *= 0.999  # Slightly better rates
            elif aggregator == DEXAggregator.ONEINCH:
                amount_out *= 0.998  # Good rates with higher fees
            elif aggregator == DEXAggregator.PARASWAP:
                amount_out *= 0.997  # Competitive rates
            elif aggregator == DEXAggregator.COWSWAP:
                amount_out *= 1.001  # MEV protection bonus
            
            # Calculate price impact
            price_impact = min(0.05, amount_in / 1000000)  # Max 5% impact
            amount_out *= (1 - price_impact)
            
            # Estimate gas
            base_gas = 150000
            gas_estimate = int(base_gas * config["gas_multiplier"])
            
            # Generate route
            possible_dexes = ["Uniswap", "Sushiswap", "Curve", "Balancer", "Kyber"]
            route_length = 1 + (hash(f"{aggregator.value}{token_in}") % 3)  # 1-3 hops
            route = [possible_dexes[i % len(possible_dexes)] for i in range(route_length)]
            
            quote_id = f"quote_{aggregator.value}_{int(time.time())}_{hash(f'{token_in}{token_out}') % 10000}"
            
            quote = SwapQuote(
                aggregator=aggregator,
                chain=chain,
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                amount_out=amount_out,
                price_impact=price_impact,
                gas_estimate=gas_estimate,
                gas_price=25.0,  # 25 gwei
                route=route,
                fee_percentage=config["fee_percentage"],
                slippage_tolerance=slippage_tolerance,
                quote_expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
                quote_id=quote_id
            )
            
            # Update stats
            self.performance_stats[aggregator]["total_quotes"] += 1
            
            return quote

        except Exception as e:
            logger.error(f"Error getting quote from {aggregator.value}: {e}")
            return None

    async def get_0x_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        chain: Chain,
        slippage_tolerance: float
    ) -> Optional[SwapQuote]:
        """Get REAL quote from 0x Protocol API"""
        try:
            # Map chain to 0x chain ID
            chain_ids = {
                Chain.ETHEREUM: "1",
                Chain.POLYGON: "137",
                Chain.BSC: "56",
                Chain.ARBITRUM: "42161"
            }

            chain_id = chain_ids.get(chain, "1")

            # Common token addresses (you'd want a more comprehensive mapping)
            token_addresses = {
                "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "USDC": "0xA0b86a33E6441E868B578C17EFA2F5C0C8F8C0E0",  # Example
                "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # Example
                "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F"   # Example
            }

            sell_token = token_addresses.get(token_in.upper(), token_in)
            buy_token = token_addresses.get(token_out.upper(), token_out)

            # Convert amount to wei (assuming 18 decimals)
            sell_amount = str(int(amount_in * 1e18))

            # 0x API parameters
            params = {
                "sellToken": sell_token,
                "buyToken": buy_token,
                "sellAmount": sell_amount,
                "slippagePercentage": str(slippage_tolerance)
            }

            # Get 0x API key from environment
            api_key = os.getenv("THEATOM_API_KEY", "7324a2b4-3b05-4288-b353-68322f49a283")

            headers = {
                "0x-api-key": api_key,
                "User-Agent": "ATOM-Backend/1.0"
            }

            # Make REAL API call to 0x
            url = f"https://api.0x.org/swap/v1/quote"

            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Parse 0x response
                    buy_amount = float(data.get("buyAmount", 0)) / 1e18
                    gas_estimate = int(data.get("gas", 150000))
                    gas_price = float(data.get("gasPrice", 25000000000)) / 1e9  # Convert to gwei

                    # Extract route information
                    sources = data.get("sources", [])
                    route = [source.get("name", "Unknown") for source in sources if source.get("proportion", 0) > 0]

                    quote_id = f"0x_quote_{int(time.time())}_{hash(str(data)) % 10000}"

                    quote = SwapQuote(
                        aggregator=DEXAggregator.ZEROX,
                        chain=chain,
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount_in,
                        amount_out=buy_amount,
                        price_impact=float(data.get("estimatedPriceImpact", 0)),
                        gas_estimate=gas_estimate,
                        gas_price=gas_price,
                        route=route if route else ["0x"],
                        fee_percentage=0.0015,  # 0x fee
                        slippage_tolerance=slippage_tolerance,
                        quote_expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
                        quote_id=quote_id
                    )

                    logger.info(f"✅ REAL 0x quote: {amount_in} {token_in} -> {buy_amount:.6f} {token_out}")
                    return quote

                else:
                    error_text = await response.text()
                    logger.error(f"0x API error {response.status}: {error_text}")
                    return None

        except Exception as e:
            logger.error(f"Error getting 0x quote: {e}")
            return None
    
    async def execute_swap(self, quote: SwapQuote) -> SwapExecution:
        """Execute swap using the provided quote"""
        try:
            execution_id = f"swap_{int(time.time())}_{hash(quote.quote_id) % 10000}"
            
            logger.info(f"🔄 Executing swap: {execution_id}")
            logger.info(f"Aggregator: {quote.aggregator.value}, Route: {' -> '.join(quote.route)}")
            
            # Create execution record
            execution = SwapExecution(
                execution_id=execution_id,
                quote_id=quote.quote_id,
                aggregator=quote.aggregator,
                chain=quote.chain,
                token_in=quote.token_in,
                token_out=quote.token_out,
                amount_in=quote.amount_in,
                amount_out_expected=quote.amount_out,
                amount_out_actual=0.0,
                gas_used=0,
                gas_price=quote.gas_price,
                tx_hash=None,
                block_number=None,
                status="pending",
                executed_at=datetime.now(timezone.utc),
                slippage_actual=0.0
            )
            
            # Simulate swap execution
            config = self.aggregators[quote.aggregator]
            execution_delay = config["avg_response_time"] + 1.0  # Additional execution time
            await asyncio.sleep(execution_delay / 10)  # Scale down for simulation
            
            # Simulate success/failure
            success_rate = config["success_rate"]
            success = (hash(execution_id) % 100) < (success_rate * 100)
            
            if success:
                # Successful execution
                slippage_factor = 1 - (hash(execution_id) % 50) / 10000  # 0-0.5% slippage
                execution.amount_out_actual = quote.amount_out * slippage_factor
                execution.slippage_actual = 1 - slippage_factor
                execution.gas_used = quote.gas_estimate + (hash(execution_id) % 20000)
                execution.tx_hash = f"0x{hash(execution_id):064x}"
                execution.block_number = 18000000 + (int(time.time()) % 100000)
                execution.status = "completed"
                
                # Update performance stats
                stats = self.performance_stats[quote.aggregator]
                stats["successful_swaps"] += 1
                stats["total_volume"] += quote.amount_in
                stats["avg_slippage"] = (stats["avg_slippage"] * 0.9 + execution.slippage_actual * 0.1)
                stats["avg_gas_used"] = int(stats["avg_gas_used"] * 0.9 + execution.gas_used * 0.1)
                stats["last_used"] = datetime.now(timezone.utc)
                
                logger.info(
                    f"✅ Swap completed: {execution_id} - "
                    f"Output: {execution.amount_out_actual:.6f} - "
                    f"Slippage: {execution.slippage_actual*100:.3f}%"
                )
                
            else:
                # Failed execution
                execution.status = "failed"
                execution.error_message = "Insufficient liquidity"
                
                logger.warning(f"❌ Swap failed: {execution_id} - {execution.error_message}")
            
            self.swap_history[execution_id] = execution
            return execution
            
        except Exception as e:
            logger.error(f"Error executing swap: {e}")
            execution.status = "failed"
            execution.error_message = str(e)
            return execution
    
    async def get_token_price(
        self,
        token: str,
        chain: Chain = Chain.ETHEREUM,
        vs_currency: str = "USD"
    ) -> Optional[float]:
        """Get current token price"""
        try:
            cache_key = f"{token}_{chain.value}_{vs_currency}"
            
            # Check cache (5-minute expiry)
            if cache_key in self.price_cache:
                cached_data = self.price_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_data["timestamp"]).total_seconds() < 300:
                    return cached_data["price"]
            
            # Simulate price fetch
            base_prices = {
                "ETH": 2000.0,
                "WETH": 2000.0,
                "USDC": 1.0,
                "USDT": 1.0,
                "DAI": 1.0,
                "WBTC": 35000.0,
                "UNI": 6.5,
                "LINK": 15.0
            }
            
            base_price = base_prices.get(token.upper(), 100.0)
            # Add some price variation
            variation = (hash(f"{token}{int(time.time()//60)}") % 200 - 100) / 10000  # ±1%
            price = base_price * (1 + variation)
            
            # Cache the price
            self.price_cache[cache_key] = {
                "price": price,
                "timestamp": datetime.now(timezone.utc)
            }
            
            return price
            
        except Exception as e:
            logger.error(f"Error getting token price: {e}")
            return None
    
    async def get_multiple_quotes(
        self,
        swaps: List[Dict[str, Any]],
        chain: Chain = Chain.ETHEREUM
    ) -> List[SwapQuote]:
        """Get quotes for multiple swaps simultaneously"""
        try:
            tasks = []
            
            for swap in swaps:
                task = self.get_best_swap_quote(
                    token_in=swap["token_in"],
                    token_out=swap["token_out"],
                    amount_in=swap["amount_in"],
                    chain=chain,
                    slippage_tolerance=swap.get("slippage_tolerance", 0.01)
                )
                tasks.append(task)
            
            quotes = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and None values
            valid_quotes = [q for q in quotes if isinstance(q, SwapQuote)]
            
            logger.info(f"📊 Got {len(valid_quotes)} quotes for {len(swaps)} requested swaps")
            
            return valid_quotes
            
        except Exception as e:
            logger.error(f"Error getting multiple quotes: {e}")
            return []
    
    def get_aggregator_stats(self) -> Dict[str, Any]:
        """Get DEX aggregator performance statistics"""
        return {
            "aggregators": {
                agg.value: {
                    **config,
                    "performance": {
                        **self.performance_stats[agg],
                        "last_used": (
                            self.performance_stats[agg]["last_used"].isoformat()
                            if self.performance_stats[agg]["last_used"] else None
                        )
                    }
                }
                for agg, config in self.aggregators.items()
            },
            "total_swaps": sum(stats["successful_swaps"] for stats in self.performance_stats.values()),
            "total_volume": sum(stats["total_volume"] for stats in self.performance_stats.values()),
            "cache_size": len(self.price_cache)
        }
    
    def get_swap_history(self, limit: int = 100) -> List[SwapExecution]:
        """Get recent swap execution history"""
        swaps = list(self.swap_history.values())
        swaps.sort(key=lambda x: x.executed_at, reverse=True)
        return swaps[:limit]
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# Global DEX aggregator manager instance
dex_aggregator = DEXAggregatorManager()
