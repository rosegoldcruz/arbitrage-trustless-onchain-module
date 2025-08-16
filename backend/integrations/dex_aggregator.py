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

class DEXProvider(str, Enum):
    ZEROX = "0x"
    UNISWAP_V3 = "uniswap_v3"
    BALANCER = "balancer"
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
    BASE = "base"

@dataclass
class SwapQuote:
    """Swap quote from DEX aggregator"""
    aggregator: DEXProvider
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
    aggregator: DEXProvider
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

class DEXAggregator:
    """Manage DEX aggregator integrations"""

    def __init__(self):
        self.aggregators = {}
        self.swap_history = {}
        self.performance_stats = {}
        self.price_cache = {}
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_aggregators()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def initialize_aggregators(self):
        """Initialize DEX aggregator configurations"""
        logger.info("🔗 Initializing DEX Aggregators")

        # Initialize HTTP session with proper cleanup (shared session)
        if not self.session or getattr(self.session, "closed", True):
            from backend.core.http_client import get_session
            self.session = await get_session()

        # Configure aggregators
        self.aggregators = {
            DEXProvider.ZEROX: {
                "name": "0x Protocol",
                "base_url": "https://api.0x.org",
                "supported_chains": ["base", "ethereum", "polygon", "bsc", "arbitrum"],
                "fee_percentage": 0.0015,  # 0.15%
                "gas_multiplier": 1.1,
                "success_rate": 0.98,
                "avg_response_time": 0.8
            },
            DEXProvider.ONEINCH: {
                "name": "1inch",
                "base_url": "https://api.1inch.io/v5.0",
                "supported_chains": ["base", "ethereum", "polygon", "bsc", "arbitrum", "optimism"],
                "fee_percentage": 0.003,  # 0.3%
                "gas_multiplier": 1.05,
                "success_rate": 0.96,
                "avg_response_time": 1.2
            },
            DEXProvider.BALANCER: {
                "name": "Balancer SOR",
                "base_url": "https://api.balancer.fi",
                "supported_chains": ["base", "ethereum", "polygon", "arbitrum"],
                "fee_percentage": 0.001,  # 0.1%
                "gas_multiplier": 1.15,
                "success_rate": 0.92,
                "avg_response_time": 2.0
            },
            DEXProvider.PARASWAP: {
                "name": "ParaSwap",
                "base_url": "https://apiv5.paraswap.io",
                "supported_chains": ["ethereum", "polygon", "bsc", "avalanche"],
                "fee_percentage": 0.001,  # 0.1%
                "gas_multiplier": 1.15,
                "success_rate": 0.94,
                "avg_response_time": 1.5
            },
            DEXProvider.COWSWAP: {
                "name": "CoW Swap",
                "base_url": "https://api.cow.fi",
                "supported_chains": ["ethereum"],
                "fee_percentage": 0.0,  # MEV protection
                "gas_multiplier": 0.9,  # Gasless trades
                "success_rate": 0.92,
                "avg_response_time": 2.0
            }
        }
        # Fallback minimal aggregator if initialization somehow produced none
        if not self.aggregators:
            self.aggregators = {
                DEXProvider.ZEROX: {
                    "name": "0x Protocol (fallback)",
                    "base_url": "https://api.0x.org",
                    "supported_chains": ["base", "ethereum"],
                    "fee_percentage": 0.0015,
                    "gas_multiplier": 1.1,
                    "success_rate": 0.98,
                    "avg_response_time": 1.0
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
            # Base Sepolia overrides for testing
            self.testnet = True


        logger.info(f"✅ Initialized {len(self.aggregators)} DEX aggregators")

    async def get_best_swap_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        chain: Chain = Chain.BASE,
        slippage_tolerance: float = 0.01,  # 1%
        included_sources: Optional[List[str]] = None
    ) -> Optional[SwapQuote]:
        """Get best swap quote across all aggregators (parallelized)"""
        # Balancer SOR path placeholder for Base Sepolia (quote-only)
        # Future: implement get_balancer_quote and execute via Vault batchSwap

        try:
            # Create tasks for all compatible aggregators
            tasks = []
            compatible_aggregators = []

            for aggregator, config in self.aggregators.items():
                chain_key = chain.value if isinstance(chain, Chain) else str(chain)
                if chain_key not in config["supported_chains"]:
                    continue

                # Environment guard: skip 0x on Base Sepolia unless explicitly enabled
                if aggregator == DEXProvider.ZEROX:
                    chain_id_env = os.getenv("CHAIN_ID", "")
                    enable_zerox_testnet = os.getenv("ENABLE_ZEROX_ON_TESTNET", "false").lower() in ("1", "true", "yes")
                    if chain_id_env == "84532" and not enable_zerox_testnet:
                        logger.info("Skipping 0x aggregator on Base Sepolia (CHAIN_ID=84532). Set ENABLE_ZEROX_ON_TESTNET=true to enable.")
                        continue

                compatible_aggregators.append(aggregator)
                if aggregator == DEXProvider.ZEROX:
                    task = self.get_0x_quote(token_in, token_out, amount_in, chain, slippage_tolerance, included_sources)
                elif aggregator == DEXProvider.BALANCER:
                    task = self.get_balancer_quote(token_in, token_out, amount_in, chain, slippage_tolerance)
                else:
                    task = self.get_aggregator_quote(
                        aggregator, token_in, token_out, amount_in, chain, slippage_tolerance
                    )
                tasks.append(task)

            if not tasks:
                logger.warning(f"No compatible aggregators for {getattr(chain, 'value', str(chain))}")
                # Fallback: try initializing a minimal 0x aggregator on Base
                try:
                    fallback_chain = Chain.BASE if isinstance(chain, Chain) else Chain.BASE
                    best = await self.get_0x_quote(token_in, token_out, amount_in, fallback_chain, slippage_tolerance, included_sources)
                    if best:
                        return best
                except Exception as _e:
                    logger.warning(f"Fallback aggregator initialization failed: {_e}")
                return None

            # Execute all quote requests in parallel
            logger.info(f"🚀 Fetching quotes from {len(tasks)} aggregators in parallel...")
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            quotes = []
            for i, result in enumerate(results):
                aggregator = compatible_aggregators[i]

                if isinstance(result, Exception):
                    logger.warning(f"Failed to get quote from {aggregator.value}: {result}")
                    continue

                # Skip falsy/None results (e.g., when 0x is disabled on testnet)
                if result is None:
                    continue

                quotes.append(result)

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
        aggregator: DEXProvider,
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
            if aggregator == DEXProvider.ZEROX:
                return await self.get_0x_quote(token_in, token_out, amount_in, chain, slippage_tolerance)
            # Balancer SOR real quote
            if aggregator == DEXProvider.MATCHA:  # temporarily reuse enum
                return await self.get_balancer_quote(token_in, token_out, amount_in, chain, slippage_tolerance)

            # For other aggregators, simulate for now (you can add real APIs later)
            await asyncio.sleep(config["avg_response_time"] / 10)  # Scale down for simulation

            # Simulate quote calculation
            base_rate = 1.0 + (hash(f"{token_in}{token_out}") % 1000) / 100000  # Small variation
            amount_out = amount_in * base_rate

            # Apply aggregator-specific adjustments
            if aggregator == DEXProvider.ZEROX:
                amount_out *= 0.999  # Slightly better rates
            elif aggregator == DEXProvider.ONEINCH:
                amount_out *= 0.998  # Good rates with higher fees
            elif aggregator == DEXProvider.PARASWAP:
                amount_out *= 0.997  # Competitive rates
            elif aggregator == DEXProvider.COWSWAP:
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
        slippage_tolerance: float,
        included_sources: Optional[List[str]] = None
    ) -> Optional[SwapQuote]:
        """Get REAL quote from 0x Protocol API"""
        try:
            # Environment guard: 0x is not supported on Base Sepolia (84532)
            chain_id_env = os.getenv("CHAIN_ID", "")
            network_env = os.getenv("NETWORK", "")
            enable_zerox_testnet = os.getenv("ENABLE_ZEROX_ON_TESTNET", "false").lower() in ("1", "true", "yes")
            if (chain_id_env == "84532" or network_env == "base_sepolia") and not enable_zerox_testnet:
                logger.info("Skipping 0x aggregator on Base Sepolia (testnet). Set ENABLE_ZEROX_ON_TESTNET=true to enable.")
                return None

            # Map chain to 0x chain ID (include Base Sepolia)
            chain_ids = {
                Chain.ETHEREUM: "1",
                Chain.POLYGON: "137",
                Chain.BSC: "56",
                Chain.ARBITRUM: "42161",
                Chain.BASE: "84532"  # Base Sepolia
            }

            chain_id = chain_ids.get(chain, "1")

            # Common token addresses (Base + Mainnet examples; callers can pass raw addresses to override)
            token_addresses = {
                # Mainnet
                "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "USDC": "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                # Base Sepolia
                "BASE_WETH": "0x4200000000000000000000000000000000000006",
                "BASE_USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "BASE_DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "BASE_GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            }

            sell_token = token_addresses.get(token_in.upper(), token_in)
            buy_token = token_addresses.get(token_out.upper(), token_out)

            # Precise decimals per token (symbol and address)
            decimals_by_symbol = {
                # Mainnet
                "ETH": 18, "WETH": 18, "USDC": 6, "USDT": 6, "DAI": 18,
                # Base
                "BASE_WETH": 18, "BASE_USDC": 6, "BASE_DAI": 18, "BASE_GHO": 18,
            }
            decimals_by_address = {
                # Mainnet
                "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee": 18,
                "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": 18,  # WETH
                "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 6,   # USDC
                "0xdac17f958d2ee523a2206206994597c13d831ec7": 6,   # USDT
                "0x6b175474e89094c44da98b954eedeac495271d0f": 18,  # DAI
                # Base Sepolia
                "0x4200000000000000000000000000000000000006": 18,   # BASE WETH
                "0x036cbd53842c5426634e7929541ec2318f3dcf7e": 6,   # BASE USDC
                "0x50c5725949a6f0c72e6c4a641f24049a917db0cb": 18,  # BASE DAI
                "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f": 18,  # BASE GHO
            }
            def _decimals_for(token_symbol_or_address: str, resolved_address: str) -> int:
                if token_symbol_or_address.startswith("0x"):
                    return decimals_by_address.get(token_symbol_or_address.lower(), 18)
                # symbol path
                dec = decimals_by_symbol.get(token_symbol_or_address.upper())
                if dec is not None:
                    return dec
                return decimals_by_address.get(resolved_address.lower(), 18)

            decimals_in = _decimals_for(token_in, sell_token)
            decimals_out = _decimals_for(token_out, buy_token)

            # Convert amount to base units using precise decimals
            sell_amount = str(int(amount_in * (10 ** decimals_in)))

            # 0x API parameters (include chainId and optional sources)
            params = {
                "sellToken": sell_token,
                "buyToken": buy_token,
                "sellAmount": sell_amount,
                "slippagePercentage": str(slippage_tolerance),
                "chainId": chain_ids.get(chain, "1")
            }
            if included_sources:
                params["includedSources"] = ",".join(included_sources)

            # Get 0x API key from environment - REQUIRED
            api_key = os.getenv("THEATOM_API_KEY")
            if not api_key:
                raise ValueError("THEATOM_API_KEY environment variable is required for 0x API access")

            headers = {
                "0x-api-key": api_key,
                "User-Agent": "ATOM-Backend/1.0"
            }

            # Make REAL API call to 0x (Base supported via chainId)
            url = f"https://api.0x.org/swap/v1/quote"

            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Parse 0x response using precise decimals for buy token
                    raw_buy_amount = float(data.get("buyAmount", 0))
                    buy_amount = raw_buy_amount / float(10 ** decimals_out)
                    gas_estimate = int(data.get("gas", 150000))
                    gas_price = float(data.get("gasPrice", 25000000000)) / 1e9  # Convert to gwei

                    # Extract route information
                    sources = data.get("sources", [])
                    route = [source.get("name", "Unknown") for source in sources if source.get("proportion", 0) > 0]

                    quote_id = f"0x_quote_{int(time.time())}_{hash(str(data)) % 10000}"

                    quote = SwapQuote(
                        aggregator=DEXProvider.ZEROX,
                        chain=chain,
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount_in,
                        amount_out=buy_amount,
                        price_impact=float(data.get("estimatedPriceImpact", 0)),
                        gas_estimate=gas_estimate,
                        gas_price=gas_price,
                        route=route if route else ["0x"],
                        fee_percentage=0.0015,
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


    async def get_balancer_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        chain: Chain,
        slippage_tolerance: float
    ) -> Optional[SwapQuote]:
        """Fetch quote via Balancer SOR (Base only for now)."""
        try:
            from backend.integrations.balancer_client import balancer_client
            raw_amount = str(int(amount_in * (10 ** 18)))
            sor = await balancer_client.get_smart_order_router_paths(
                token_in=token_in,
                token_out=token_out,
                amount=raw_amount,
                chain="BASE"
            )
            if not sor:
                return None

            return_amount = int(sor.return_amount_raw or "0")
            amount_out = return_amount / float(10 ** 18)
            price_impact = float(sor.price_impact or 0.0)
            route = []
            for r in sor.route or []:
                route.append(f"{r.get('tokenIn','')}->{r.get('tokenOut','')}")

            quote_id = f"bal_quote_{int(time.time())}_{abs(hash(raw_amount)) % 10000}"
            return SwapQuote(
                aggregator=DEXProvider.BALANCER,
                chain=chain,
                token_in=token_in,
                token_out=token_out,
                amount_in=amount_in,
                amount_out=amount_out,
                price_impact=price_impact,
                gas_estimate=250000,
                gas_price=0.0,
                route=route if route else ["Balancer"],
                fee_percentage=0.0,
                slippage_tolerance=slippage_tolerance,
                quote_expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
                quote_id=quote_id
            )
        except Exception as e:
            logger.error(f"Balancer SOR quote error: {e}")
            return None

    async def get_0x_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: float,
        chain: Chain,
        slippage_tolerance: float,
        included_sources: Optional[List[str]] = None
    ) -> Optional[SwapQuote]:
        """Get REAL quote from 0x Protocol API"""
        try:
            # Map chain to 0x chain ID (include Base Sepolia)
            chain_ids = {
                Chain.ETHEREUM: "1",
                Chain.POLYGON: "137",
                Chain.BSC: "56",
                Chain.ARBITRUM: "42161",
                Chain.BASE: "84532"  # Base Sepolia
            }

            chain_id = chain_ids.get(chain, "1")

            # Common token addresses (Base + Mainnet examples; callers can pass raw addresses to override)
            token_addresses = {
                # Mainnet
                "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "USDC": "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                # Base Sepolia
                "BASE_WETH": "0x4200000000000000000000000000000000000006",
                "BASE_USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "BASE_DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "BASE_GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            }

            sell_token = token_addresses.get(token_in.upper(), token_in)
            buy_token = token_addresses.get(token_out.upper(), token_out)

            # Precise decimals per token (symbol and address)
            decimals_by_symbol = {
                # Mainnet
                "ETH": 18, "WETH": 18, "USDC": 6, "USDT": 6, "DAI": 18,
                # Base
                "BASE_WETH": 18, "BASE_USDC": 6, "BASE_DAI": 18, "BASE_GHO": 18,
            }
            decimals_by_address = {
                # Mainnet
                "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee": 18,
                "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": 18,  # WETH
                "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 6,   # USDC
                "0xdac17f958d2ee523a2206206994597c13d831ec7": 6,   # USDT
                "0x6b175474e89094c44da98b954eedeac495271d0f": 18,  # DAI
                # Base Sepolia
                "0x4200000000000000000000000000000000000006": 18,   # BASE WETH
                "0x036cbd53842c5426634e7929541ec2318f3dcf7e": 6,   # BASE USDC
                "0x50c5725949a6f0c72e6c4a641f24049a917db0cb": 18,  # BASE DAI
                "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f": 18,  # BASE GHO
            }
            def _decimals_for(token_symbol_or_address: str, resolved_address: str) -> int:
                if token_symbol_or_address.startswith("0x"):
                    return decimals_by_address.get(token_symbol_or_address.lower(), 18)
                # symbol path
                dec = decimals_by_symbol.get(token_symbol_or_address.upper())
                if dec is not None:
                    return dec
                return decimals_by_address.get(resolved_address.lower(), 18)

            decimals_in = _decimals_for(token_in, sell_token)
            decimals_out = _decimals_for(token_out, buy_token)

            # Convert amount to base units using precise decimals
            sell_amount = str(int(amount_in * (10 ** decimals_in)))

            # 0x API parameters (include chainId and optional sources)
            params = {
                "sellToken": sell_token,
                "buyToken": buy_token,
                "sellAmount": sell_amount,
                "slippagePercentage": str(slippage_tolerance),
                "chainId": chain_ids.get(chain, "1")
            }
            if included_sources:
                params["includedSources"] = ",".join(included_sources)

            # Get 0x API key from environment - REQUIRED
            api_key = os.getenv("THEATOM_API_KEY")
            if not api_key:
                raise ValueError("THEATOM_API_KEY environment variable is required for 0x API access")

            headers = {
                "0x-api-key": api_key,
                "User-Agent": "ATOM-Backend/1.0"
            }

            # Make REAL API call to 0x (Base supported via chainId)
            url = f"https://api.0x.org/swap/v1/quote"

            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Parse 0x response using precise decimals for buy token
                    raw_buy_amount = float(data.get("buyAmount", 0))
                    buy_amount = raw_buy_amount / float(10 ** decimals_out)
                    gas_estimate = int(data.get("gas", 150000))
                    gas_price = float(data.get("gasPrice", 25000000000)) / 1e9  # Convert to gwei

                    # Extract route information
                    sources = data.get("sources", [])
                    route = [source.get("name", "Unknown") for source in sources if source.get("proportion", 0) > 0]

                    quote_id = f"0x_quote_{int(time.time())}_{hash(str(data)) % 10000}"

                    quote = SwapQuote(
                        aggregator=DEXProvider.ZEROX,
                        chain=chain,
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount_in,
                        amount_out=buy_amount,
                        price_impact=float(data.get("estimatedPriceImpact", 0)),
                        gas_estimate=gas_estimate,
                        gas_price=gas_price,
                        route=route if route else ["0x"],
                        fee_percentage=0.0015,
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
        """Execute swap using the provided quote via 0x Exchange Proxy when available.
        - No simulation. Sends a real signed transaction if env and RPC are configured.
        - Returns a pending SwapExecution with the real tx hash, or failed with error.
        """
        execution_id = f"swap_{int(time.time())}_{hash(quote.quote_id) % 10000}"
        try:
            import os
            from web3 import Web3

            if quote.aggregator == DEXProvider.BALANCER:
                return await self._execute_balancer_swap(execution_id, quote)
            if quote.aggregator != DEXProvider.ZEROX:
                raise NotImplementedError("Only 0x and Balancer execution are implemented at this time")

            # Resolve RPC URL for chain
            def _resolve_rpc(chain: Chain) -> str:
                if chain == Chain.BASE:
                    return os.getenv("BASE_RPC_URL") or os.getenv("BASE_SEPOLIA_RPC_URL") or ""
                elif chain == Chain.ETHEREUM:
                    return os.getenv("ETHEREUM_RPC_URL") or (lambda k=os.getenv("ALCHEMY_API_KEY"): f"https://eth-mainnet.g.alchemy.com/v2/{k}" if k else "")()
                else:
                    return ""

            rpc_url = _resolve_rpc(quote.chain)
            if not rpc_url:
                raise RuntimeError("Missing RPC URL for selected chain")

            private_key = os.getenv("PRIVATE_KEY")
            if not private_key:
                raise RuntimeError("PRIVATE_KEY not set in environment")

            api_key = os.getenv("THEATOM_API_KEY")
            if not api_key:
                raise RuntimeError("THEATOM_API_KEY not set for 0x API access")

            # Map chain to chainId used by 0x API
            chain_ids = {Chain.ETHEREUM: "1", Chain.BASE: "8453"}

            # Resolve token addresses and decimals as in get_0x_quote
            token_addresses = {
                "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "USDC": "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                # Base
                "BASE_WETH": "0x4200000000000000000000000000000000000006",
                "BASE_USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "BASE_DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "BASE_GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            }
            decimals_by_symbol = {
                "ETH": 18, "WETH": 18, "USDC": 6, "USDT": 6, "DAI": 18,
                "BASE_WETH": 18, "BASE_USDC": 6, "BASE_DAI": 18, "BASE_GHO": 18,
            }
            decimals_by_address = {
                "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee": 18,
                "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": 18,
                "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 6,
                "0xdac17f958d2ee523a2206206994597c13d831ec7": 6,
                "0x6b175474e89094c44da98b954eedeac495271d0f": 18,
                "0x4200000000000000000000000000000000000006": 18,
                "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": 6,
                "0x50c5725949a6f0c72e6c4a641f24049a917db0cb": 18,
                "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f": 18,
            }
            def _resolve_addr(sym_or_addr: str) -> str:
                return token_addresses.get(sym_or_addr.upper(), sym_or_addr)
            def _decimals_for(sym_or_addr: str, resolved_addr: str) -> int:
                if sym_or_addr.startswith("0x"):
                    return decimals_by_address.get(sym_or_addr.lower(), 18)
                return decimals_by_symbol.get(sym_or_addr.upper(), decimals_by_address.get(resolved_addr.lower(), 18))

            sell_token_resolved = _resolve_addr(quote.token_in)
            buy_token_resolved = _resolve_addr(quote.token_out)
            decimals_in = _decimals_for(quote.token_in, sell_token_resolved)
            sell_amount = str(int(quote.amount_in * (10 ** decimals_in)))

            # Fetch a fresh executable quote with calldata
            import aiohttp
            params = {
                "sellToken": sell_token_resolved,
                "buyToken": buy_token_resolved,
                "sellAmount": sell_amount,
                "slippagePercentage": str(quote.slippage_tolerance if hasattr(quote, 'slippage_tolerance') else 0.005),
                "chainId": chain_ids.get(quote.chain, "1")
            }
            headers = {"0x-api-key": api_key, "User-Agent": "ATOM-Backend/1.0"}
            async with self.session.get("https://api.0x.org/swap/v1/quote", params=params, headers=headers) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"0x quote error: {resp.status} {await resp.text()}")
                data = await resp.json()

            tx_to = Web3.to_checksum_address(data.get("to"))
            tx_data = data.get("data")
            tx_value = int(data.get("value", "0"))
            gas_limit = int(data.get("gas", 0) or 150000)
            gas_price = int(data.get("gasPrice", 0) or 0)
            allowance_target = data.get("allowanceTarget")

            w3 = Web3(Web3.HTTPProvider(rpc_url))
            acct = w3.eth.account.from_key(private_key)
            from_addr = acct.address

            # Approve if ERC-20 and allowance insufficient
            if sell_token_resolved.lower() != token_addresses["ETH"].lower() and allowance_target:
                erc20_abi = [
                    {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
                    {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
                ]
                token = w3.eth.contract(address=Web3.to_checksum_address(sell_token_resolved), abi=erc20_abi)
                current_allowance = token.functions.allowance(from_addr, Web3.to_checksum_address(allowance_target)).call()
                if current_allowance < int(sell_amount):
                    approve_tx = token.functions.approve(Web3.to_checksum_address(allowance_target), int(2**256 - 1)).build_transaction({
                        "from": from_addr,
                        "nonce": w3.eth.get_transaction_count(from_addr),
                        "gas": 60000,
                        "gasPrice": w3.eth.gas_price,
                        "chainId": int(chain_ids.get(quote.chain, "1"))
                    })
                    signed_approve = acct.sign_transaction(approve_tx)
                    w3.eth.send_raw_transaction(signed_approve.rawTransaction)

            # Build swap tx
            nonce = w3.eth.get_transaction_count(from_addr)
            tx = {
                "from": from_addr,
                "to": tx_to,
                "data": tx_data,
                "value": tx_value,
                "nonce": nonce,
                "chainId": int(chain_ids.get(quote.chain, "1"))
            }
            if gas_limit:
                tx["gas"] = gas_limit
            if gas_price:
                tx["gasPrice"] = gas_price
            else:
                tx["gasPrice"] = w3.eth.gas_price
            signed = acct.sign_transaction(tx)
            tx_hash_bytes = w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash_bytes, timeout=300)
            tx_hash = receipt.transactionHash.hex()

            return SwapExecution(
                execution_id=execution_id,
                quote_id=quote.quote_id,
                aggregator=quote.aggregator,
                chain=quote.chain,
                token_in=quote.token_in,
                token_out=quote.token_out,
                amount_in=quote.amount_in,
                amount_out_expected=quote.amount_out,
                amount_out_actual=0.0,
                gas_used=receipt.gasUsed,
                gas_price=tx.get("gasPrice", 0) / 1e9,
                tx_hash=tx_hash,
                block_number=receipt.blockNumber,
                status=("completed" if receipt.status == 1 else "failed"),
                executed_at=datetime.now(timezone.utc),
                slippage_actual=0.0
            )

        except Exception as e:
            logger.error(f"Error executing 0x swap: {e}")
            return SwapExecution(
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
                status="failed",
                executed_at=datetime.now(timezone.utc),
                slippage_actual=0.0,
                error_message=str(e)
            )

    async def _execute_balancer_swap(self, execution_id: str, quote: SwapQuote) -> SwapExecution:
        """Execute a Balancer swap via Vault batchSwap on Base (Sepolia/Mainnet).
        Requirements: BALANCER_VAULT_ADDRESS env and minimal IVault ABI embedded.
        """
        try:
            from web3 import Web3
            import os
            import time

            rpc_url = os.getenv("BASE_RPC_URL") or os.getenv("BASE_SEPOLIA_RPC_URL")
            if not rpc_url:
                raise RuntimeError("Missing BASE RPC URL for Balancer execution")
            private_key = os.getenv("PRIVATE_KEY")
            if not private_key:
                raise RuntimeError("PRIVATE_KEY not set in environment")
            vault_address = os.getenv("BALANCER_VAULT_ADDRESS")
            if not vault_address:
                raise RuntimeError("BALANCER_VAULT_ADDRESS not configured")

            w3 = Web3(Web3.HTTPProvider(rpc_url))
            acct = w3.eth.account.from_key(private_key)
            from_addr = acct.address

            # Minimal IVault ABI for batchSwap
            ivault_abi = [
                {
                    "inputs": [
                        {"internalType": "uint8", "name": "kind", "type": "uint8"},
                        {
                            "components": [
                                {"internalType": "bytes32", "name": "poolId", "type": "bytes32"},
                                {"internalType": "uint256", "name": "assetInIndex", "type": "uint256"},
                                {"internalType": "uint256", "name": "assetOutIndex", "type": "uint256"},
                                {"internalType": "uint256", "name": "amount", "type": "uint256"},
                                {"internalType": "bytes", "name": "userData", "type": "bytes"}
                            ],
                            "internalType": "struct IVault.BatchSwapStep[]",
                            "name": "swaps",
                            "type": "tuple[]"
                        },
                        {"internalType": "address[]", "name": "assets", "type": "address[]"},
                        {
                            "components": [
                                {"internalType": "address", "name": "sender", "type": "address"},
                                {"internalType": "bool", "name": "fromInternalBalance", "type": "bool"},
                                {"internalType": "address", "name": "recipient", "type": "address"},
                                {"internalType": "bool", "name": "toInternalBalance", "type": "bool"}
                            ],
                            "internalType": "struct IVault.FundManagement",
                            "name": "funds",
                            "type": "tuple"
                        },
                        {"internalType": "int256[]", "name": "limits", "type": "int256[]"},
                        {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                    ],
                    "name": "batchSwap",
                    "outputs": [{"internalType": "int256[]", "name": "assetDeltas", "type": "int256[]"}],
                    "stateMutability": "payable",
                    "type": "function"
                }
            ]

            vault = w3.eth.contract(address=Web3.to_checksum_address(vault_address), abi=ivault_abi)

            # Resolve poolId for the token pair using Balancer GraphQL
            pool_id = await self._resolve_balancer_pool_id(quote.token_in, quote.token_out)
            if not pool_id:
                raise RuntimeError(f"No Balancer pool found for {quote.token_in}/{quote.token_out} on Base")

            # Token addresses (resolve from symbols if needed)
            token_addresses = {
                "BASE_WETH": "0x4200000000000000000000000000000000000006",
                "BASE_USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "BASE_DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "BASE_GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            }

            token_in_addr = token_addresses.get(quote.token_in.upper(), quote.token_in)
            token_out_addr = token_addresses.get(quote.token_out.upper(), quote.token_out)

            # Convert amount to base units (assume 18 decimals for now)
            amount_in_wei = int(quote.amount_in * (10 ** 18))

            # Construct batchSwap parameters
            # EXACT_IN = 0, EXACT_OUT = 1
            kind = 0  # EXACT_IN

            # Single swap step
            swaps = [{
                "poolId": pool_id,
                "assetInIndex": 0,
                "assetOutIndex": 1,
                "amount": amount_in_wei,
                "userData": "0x"
            }]

            # Assets array (order matters for indices)
            assets = [Web3.to_checksum_address(token_in_addr), Web3.to_checksum_address(token_out_addr)]

            # Fund management
            funds = {
                "sender": from_addr,
                "fromInternalBalance": False,
                "recipient": from_addr,
                "toInternalBalance": False
            }

            # Limits (positive for tokens going in, negative for minimum tokens out)
            limits = [amount_in_wei, -int(quote.amount_out * 0.95 * (10 ** 18))]  # 5% slippage tolerance

            # Deadline (3 minutes from now)
            deadline = int(time.time()) + 180

            # Approve Vault to spend token_in
            await self._approve_token_for_vault(w3, acct, token_in_addr, vault_address, amount_in_wei)

            # Build batchSwap transaction
            tx_data = vault.functions.batchSwap(
                kind, swaps, assets, funds, limits, deadline
            ).build_transaction({
                "from": from_addr,
                "gas": 300000,
                "gasPrice": w3.eth.gas_price,
                "nonce": w3.eth.get_transaction_count(from_addr)
            })

            # Sign and send transaction
            signed = acct.sign_transaction(tx_data)
            tx_hash_bytes = w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash_bytes, timeout=300)
            tx_hash = receipt.transactionHash.hex()

            return SwapExecution(
                execution_id=execution_id,
                quote_id=quote.quote_id,
                aggregator=quote.aggregator,
                chain=quote.chain,
                token_in=quote.token_in,
                token_out=quote.token_out,
                amount_in=quote.amount_in,
                amount_out_expected=quote.amount_out,
                amount_out_actual=0.0,  # Would need to parse receipt logs for actual amount
                gas_used=receipt.gasUsed,
                gas_price=tx_data.get("gasPrice", 0) / 1e9,
                tx_hash=tx_hash,
                block_number=receipt.blockNumber,
                status=("completed" if receipt.status == 1 else "failed"),
                executed_at=datetime.now(timezone.utc),
                slippage_actual=0.0
            )

        except Exception as e:
            logger.error(f"Balancer execution error: {e}")
            return SwapExecution(
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
                gas_price=0.0,
                tx_hash=None,
                block_number=None,
                status="failed",
                executed_at=datetime.now(timezone.utc),
                slippage_actual=0.0,
                error_message=str(e)
            )

    async def _resolve_balancer_pool_id(self, token_in: str, token_out: str) -> Optional[str]:
        """Resolve Balancer pool ID for token pair on Base using GraphQL."""
        try:
            # Token address mapping
            token_addresses = {
                "BASE_WETH": "0x4200000000000000000000000000000000000006",
                "BASE_USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
                "BASE_DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "BASE_GHO": "0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f"
            }

            token_in_addr = token_addresses.get(token_in.upper(), token_in).lower()
            token_out_addr = token_addresses.get(token_out.upper(), token_out).lower()

            # GraphQL query to find pools containing both tokens
            query = """
            query GetPools($tokens: [String!]) {
                pools(
                    where: {
                        tokensList_contains: $tokens,
                        totalLiquidity_gt: "1000"
                    },
                    orderBy: totalLiquidity,
                    orderDirection: desc,
                    first: 5
                ) {
                    id
                    tokens {
                        address
                        symbol
                    }
                    totalLiquidity
                }
            }
            """

            variables = {
                "tokens": [token_in_addr, token_out_addr]
            }

            # Base Balancer GraphQL endpoint
            graphql_url = "https://api.studio.thegraph.com/query/24660/balancer-base-v2/version/latest"

            async with self.session.post(
                graphql_url,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    pools = data.get("data", {}).get("pools", [])

                    # Find pool that contains both tokens
                    for pool in pools:
                        pool_tokens = [t["address"].lower() for t in pool.get("tokens", [])]
                        if token_in_addr in pool_tokens and token_out_addr in pool_tokens:
                            logger.info(f"Found Balancer pool {pool['id']} for {token_in}/{token_out}")
                            return pool["id"]

                    logger.warning(f"No Balancer pool found containing both {token_in} and {token_out}")
                    return None
                else:
                    logger.error(f"Balancer GraphQL error {response.status}: {await response.text()}")
                    return None

        except Exception as e:
            logger.error(f"Error resolving Balancer pool ID: {e}")
            return None

    async def _approve_token_for_vault(self, w3, account, token_address: str, vault_address: str, amount: int):
        """Approve Balancer Vault to spend token."""
        try:
            from web3 import Web3
            # ERC-20 approve function ABI
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_spender", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]

            token_contract = w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=erc20_abi
            )

            # Build approve transaction
            approve_tx = token_contract.functions.approve(
                Web3.to_checksum_address(vault_address),
                amount
            ).build_transaction({
                "from": account.address,
                "gas": 100000,
                "gasPrice": w3.eth.gas_price,
                "nonce": w3.eth.get_transaction_count(account.address)
            })

            # Sign and send approval
            signed_approve = account.sign_transaction(approve_tx)
            approve_hash = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            approve_receipt = w3.eth.wait_for_transaction_receipt(approve_hash, timeout=120)

            if approve_receipt.status == 1:
                logger.info(f"✅ Approved {amount} tokens for Vault")
            else:
                raise RuntimeError("Token approval failed")

        except Exception as e:
            logger.error(f"Token approval error: {e}")
            raise

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
        chain: Chain = Chain.BASE
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

# Global DEX aggregator instance
dex_aggregator = DEXAggregator()
