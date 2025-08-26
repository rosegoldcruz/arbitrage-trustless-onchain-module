#!/usr/bin/env python3
"""
Production Opportunity Detector
- Polygon mainnet arbitrage scanning
- Triangular arb with UniswapV3, QuickSwap, SushiSwap
- Strictly env-driven config (SecureConfig)
"""

import asyncio
import json
import logging
import time
from decimal import Decimal
from typing import Dict, List, Optional

from web3 import Web3
import redis
from config.secure_config import SecureConfig

logger = logging.getLogger("production_opportunity_detector")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class ProductionOpportunityDetector:
    def __init__(self):
        # RPC
        self.w3 = Web3(Web3.HTTPProvider(_cfg.get_rpc_url("polygon")))
        if not self.w3.is_connected():
            raise RuntimeError("Polygon RPC not reachable")
        if self.w3.eth.chain_id != 137:
            raise RuntimeError("Not connected to Polygon mainnet")

        # Redis
        self.redis = redis.from_url(_cfg.require("REDIS_URL"), decode_responses=True)

        # Config thresholds
        self.min_profit_bps = Decimal(_cfg.env.get("ATOM_MIN_PROFIT_THRESHOLD_BPS", "23"))
        self.min_trade_size_usd = float(_cfg.env.get("MIN_TRADE_SIZE_USD", "25000"))
        self.min_trade_profit_usd = float(_cfg.env.get("MIN_TRADE_PROFIT_USD", "100"))

        # Contract addresses
        self.tokens = {
            "WETH": _cfg.require("WETH_ADDRESS"),
            "USDC": _cfg.require("USDC_ADDRESS"),
            "USDT": _cfg.require("USDT_ADDRESS"),
            "DAI": _cfg.require("DAI_ADDRESS"),
            "WMATIC": _cfg.require("WMATIC_ADDRESS"),
        }
        self.routers = {
            "uniswap_v3_quoter": _cfg.require("UNISWAP_V3_QUOTER"),
            "quickswap": _cfg.require("QUICKSWAP_ROUTER"),
            "sushiswap": _cfg.require("SUSHISWAP_ROUTER"),
        }

        # ABIs
        self.v2_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                ],
                "name": "getAmountsOut",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function",
            }
        ]
        self.v3_quoter_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "name": "quoteExactInputSingle",
                "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ]

        # Contracts
        self.uniswap_quoter = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.routers["uniswap_v3_quoter"]),
            abi=self.v3_quoter_abi,
        )
        self.quickswap_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.routers["quickswap"]),
            abi=self.v2_abi,
        )
        self.sushiswap_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.routers["sushiswap"]),
            abi=self.v2_abi,
        )

        self.running = False

    def _get_v2_price(self, router, token_in, token_out, amount_in) -> Optional[int]:
        try:
            path = [token_in, token_out]
            amounts = router.functions.getAmountsOut(amount_in, path).call()
            return amounts[-1]
        except Exception as e:
            logger.debug(f"V2 price error {token_in}->{token_out}: {e}")
            return None

    def _get_v3_price(self, token_in, token_out, amount_in, fee=3000) -> Optional[int]:
        try:
            return self.uniswap_quoter.functions.quoteExactInputSingle(
                token_in, token_out, fee, amount_in, 0
            ).call()
        except Exception as e:
            logger.debug(f"V3 price error {token_in}->{token_out}: {e}")
            return None

    async def calculate_triangular(self, a, b, c, amount) -> Optional[Dict]:
        try:
            ab = self._get_v3_price(a, b, amount) or self._get_v2_price(self.quickswap_router, a, b, amount)
            if not ab:
                return None
            bc = self._get_v3_price(b, c, ab) or self._get_v2_price(self.sushiswap_router, b, c, ab)
            if not bc:
                return None
            ca = self._get_v3_price(c, a, bc) or self._get_v2_price(self.sushiswap_router, c, a, bc)
            if not ca:
                return None

            if ca > amount:
                profit = ca - amount
                profit_bps = (profit * 10000) // amount
                if profit_bps >= self.min_profit_bps:
                    trade_size_usd = float(amount) / 1e18 * 2500
                    net_profit_usd = float(profit) / 1e18 * 2500
                    if trade_size_usd >= self.min_trade_size_usd and net_profit_usd >= self.min_trade_profit_usd:
                        return {
                            "token_a": a,
                            "token_b": b,
                            "token_c": c,
                            "amount_in": amount,
                            "amount_out": ca,
                            "profit_bps": profit_bps,
                            "net_profit_usd": net_profit_usd,
                            "timestamp": time.time(),
                        }
        except Exception as e:
            logger.error(f"Triangular calc error: {e}")
        return None

    async def scan(self):
        logger.info("🔎 Starting production opportunity scan...")
        triangles = [
            ("WETH", "USDC", "WMATIC"),
            ("WETH", "USDT", "WMATIC"),
            ("WETH", "DAI", "WMATIC"),
            ("USDC", "USDT", "DAI"),
        ]
        test_amounts = [int(10 * 1e18), int(20 * 1e18), int(40 * 1e18)]

        self.running = True
        while self.running:
            found = []
            for a, b, c in triangles:
                for amt in test_amounts:
                    opp = await self.calculate_triangular(self.tokens[a], self.tokens[b], self.tokens[c], amt)
                    if opp:
                        found.append(opp)
                        self.redis.lpush("arbitrage_opportunities", json.dumps(opp))
                        logger.info(
                            f"💰 Opp: {a}->{b}->{c} | {opp['profit_bps']} bps | ${opp['net_profit_usd']:.2f}"
                        )
            await asyncio.sleep(2)

    def get_best(self, limit=5) -> List[Dict]:
        return self.redis.lrange("arbitrage_opportunities", 0, limit - 1)


if __name__ == "__main__":
    det = ProductionOpportunityDetector()
    asyncio.run(det.scan())
