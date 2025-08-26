#!/usr/bin/env python3
"""
ATOM Opportunity Detector
- Scans Polygon DEXs for arbitrage spreads
- Supports Uniswap V3, QuickSwap, SushiSwap
- Detects triangular arbitrage routes
"""

import asyncio
import logging
import time
from decimal import Decimal
from typing import Dict, List, Optional

from web3 import Web3
from config.secure_config import SecureConfig

logger = logging.getLogger("opportunity_detector")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class OpportunityDetector:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(_cfg.get_rpc_url("polygon")))
        if not self.w3.is_connected():
            raise RuntimeError("Polygon RPC not reachable")

        self.min_profit_bps = Decimal(_cfg.env.get("ATOM_MIN_PROFIT_THRESHOLD_BPS", "23"))

        # Load addresses from env
        self.tokens = {
            "WETH": _cfg.require("WETH_ADDRESS"),
            "USDC": _cfg.require("USDC_ADDRESS"),
            "USDT": _cfg.require("USDT_ADDRESS"),
            "DAI": _cfg.require("DAI_ADDRESS"),
            "WMATIC": _cfg.require("WMATIC_ADDRESS"),
        }
        self.uniswap_quoter = self.w3.eth.contract(
            address=Web3.to_checksum_address("0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"),
            abi=[
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
            ],
        )
        self.router_abi = [
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
        self.quickswap_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(_cfg.require("QUICKSWAP_ROUTER")),
            abi=self.router_abi,
        )
        self.sushiswap_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(_cfg.require("SUSHISWAP_ROUTER")),
            abi=self.router_abi,
        )
        self.opportunities: List[Dict] = []
        self.running = False

    def _get_v2_price(self, router, token_in, token_out, amount_in) -> Optional[int]:
        try:
            path = [token_in, token_out]
            amounts = router.functions.getAmountsOut(amount_in, path).call()
            return amounts[-1]
        except Exception as e:
            logger.debug(f"V2 price fail {token_in}->{token_out}: {e}")
            return None

    def _get_v3_price(self, token_in, token_out, amount_in, fee=3000) -> Optional[int]:
        try:
            return self.uniswap_quoter.functions.quoteExactInputSingle(
                token_in, token_out, fee, amount_in, 0
            ).call()
        except Exception as e:
            logger.debug(f"V3 price fail {token_in}->{token_out}: {e}")
            return None

    async def calculate_triangular(self, a, b, c, amount) -> Optional[Dict]:
        try:
            # a -> b
            ab = self._get_v3_price(a, b, amount) or self._get_v2_price(self.quickswap_router, a, b, amount)
            if not ab:
                return None
            # b -> c
            bc = self._get_v3_price(b, c, ab) or self._get_v2_price(self.sushiswap_router, b, c, ab)
            if not bc:
                return None
            # c -> a
            ca = self._get_v3_price(c, a, bc) or self._get_v2_price(self.sushiswap_router, c, a, bc)
            if not ca:
                return None

            if ca > amount:
                profit = ca - amount
                profit_bps = (profit * 10000) // amount
                if profit_bps >= self.min_profit_bps:
                    return {
                        "token_a": a,
                        "token_b": b,
                        "token_c": c,
                        "amount_in": amount,
                        "amount_out": ca,
                        "profit": profit,
                        "profit_bps": profit_bps,
                        "timestamp": time.time(),
                    }
        except Exception as e:
            logger.error(f"Triangular arb error: {e}")
        return None

    async def scan(self):
        logger.info("🔎 Starting opportunity scan...")
        triangles = [
            ("WETH", "USDC", "WMATIC"),
            ("WETH", "USDT", "WMATIC"),
            ("WETH", "DAI", "WMATIC"),
            ("USDC", "USDT", "DAI"),
        ]
        test_amounts = [int(100 * 1e18), int(1000 * 1e18)]
        self.running = True

        while self.running:
            found = []
            for a, b, c in triangles:
                for amt in test_amounts:
                    opp = await self.calculate_triangular(
                        self.tokens[a], self.tokens[b], self.tokens[c], amt
                    )
                    if opp:
                        logger.info(
                            f"🚀 Opportunity {a}->{b}->{c} profit {opp['profit_bps']} bps"
                        )
                        found.append(opp)
            self.opportunities = sorted(found, key=lambda x: x["profit_bps"], reverse=True)
            await asyncio.sleep(2)

    def get_best(self, limit=5) -> List[Dict]:
        return self.opportunities[:limit]


if __name__ == "__main__":
    det = OpportunityDetector()
    asyncio.run(det.scan())
