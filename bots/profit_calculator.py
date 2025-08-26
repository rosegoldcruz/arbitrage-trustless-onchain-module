#!/usr/bin/env python3
"""
Profit Calculator
- Real-time triangular arb validation
- Aave flashloan fees, gas, thresholds
STRICT: No hardcoded RPCs or addresses. All via SecureConfig.
"""

import logging
import time
from decimal import Decimal
from typing import Dict, Optional

from web3 import Web3
from config.secure_config import SecureConfig

logger = logging.getLogger("profit_calculator")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class ProfitCalculator:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(_cfg.get_rpc_url("polygon")))
        if not self.w3.is_connected() or self.w3.eth.chain_id != 137:
            raise RuntimeError("Polygon RPC not reachable or wrong network")

        # Load thresholds
        self.min_profit_bps = Decimal(_cfg.env.get("ATOM_MIN_PROFIT_THRESHOLD_BPS", "23"))
        self.min_trade_size_usd = float(_cfg.env.get("MIN_TRADE_SIZE_USD", "25000"))
        self.target_net_profit = float(_cfg.env.get("TARGET_NET_PROFIT_USD", "100"))
        self.flashloan_fee_bps = Decimal(_cfg.env.get("AAVE_FLASHLOAN_FEE_BPS", "9"))  # 0.09%
        self.max_gas_usd = float(_cfg.env.get("MAX_GAS_COST_USD", "50"))

        # Addresses
        self.tokens = _cfg.get_token_addresses()
        self.routers = _cfg.get_dex_routers()
        self.uniswap_quoter = self.w3.eth.contract(
            address=_cfg.require("UNISWAP_V3_QUOTER"),
            abi=[{
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
            }],
        )
        self.v2_abi = [{
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
            ],
            "name": "getAmountsOut",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function",
        }]
        self.quickswap = self.w3.eth.contract(address=self.routers["QUICKSWAP_ROUTER"], abi=self.v2_abi)
        self.sushiswap = self.w3.eth.contract(address=self.routers["SUSHISWAP_ROUTER"], abi=self.v2_abi)

    def _quote(self, dex: str, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        try:
            if dex == "uniswap_v3":
                return self.uniswap_quoter.functions.quoteExactInputSingle(token_in, token_out, 3000, amount_in, 0).call()
            if dex == "quickswap":
                return self.quickswap.functions.getAmountsOut(amount_in, [token_in, token_out]).call()[-1]
            if dex == "sushiswap":
                return self.sushiswap.functions.getAmountsOut(amount_in, [token_in, token_out]).call()[-1]
        except Exception as e:
            logger.debug(f"Quote error {dex} {token_in}->{token_out}: {e}")
        return None

    def validate_opportunity(self, opp: Dict, gas_gwei: int = 50) -> Dict:
        try:
            a, b, c = opp["token_a"], opp["token_b"], opp["token_c"]
            amt = opp["amount_in"]
            ab = self._quote(opp["dex_a"], a, b, amt)
            if not ab:
                return {"profitable": False, "error": "step1"}
            bc = self._quote(opp["dex_b"], b, c, ab)
            if not bc:
                return {"profitable": False, "error": "step2"}
            ca = self._quote(opp["dex_c"], c, a, bc)
            if not ca:
                return {"profitable": False, "error": "step3"}

            fee = (amt * int(self.flashloan_fee_bps)) // 10000
            gas_cost_usd = gas_gwei * 1e-9 * 400000 * 0.8  # rough
            gross = ca - amt
            net = gross - fee
            profit_bps = (net * 10000) // amt
            net_usd = float(net) / 1e18 * 2500  # ETH≈$2500 rough

            return {
                "profitable": profit_bps >= self.min_profit_bps and net_usd >= self.target_net_profit,
                "profit_bps": profit_bps,
                "net_profit_usd": net_usd,
                "gross_profit": gross,
                "net_profit": net,
                "fee": fee,
                "gas_cost_usd": gas_cost_usd,
            }
        except Exception as e:
            return {"profitable": False, "error": str(e)}
