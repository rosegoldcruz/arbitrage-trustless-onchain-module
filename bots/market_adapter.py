#!/usr/bin/env python3
"""
Market Condition Adapter
Adjusts arbitrage thresholds based on volatility, liquidity, and gas.
"""

import time
import logging
from decimal import Decimal
from collections import deque
import numpy as np

from config.secure_config import SecureConfig

logger = logging.getLogger("market_adapter")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()

class MarketConditionAdapter:
    def __init__(self):
        self.price_history = deque(maxlen=1000)
        self.volume_history = deque(maxlen=100)
        self.gas_history = deque(maxlen=100)
        self.current_conditions = {}
        self.strategy = {}

        # Thresholds from env
        self.low_vol = Decimal(_cfg.env.get("LOW_VOLATILITY_THRESHOLD", "0.5"))
        self.high_vol = Decimal(_cfg.env.get("HIGH_VOLATILITY_THRESHOLD", "3.0"))
        self.low_liq = Decimal(_cfg.env.get("LOW_LIQUIDITY_THRESHOLD", "10000"))
        self.high_liq = Decimal(_cfg.env.get("HIGH_LIQUIDITY_THRESHOLD", "1000000"))
        self.low_gas = Decimal(_cfg.env.get("LOW_GAS_THRESHOLD", "20"))
        self.high_gas = Decimal(_cfg.env.get("HIGH_GAS_THRESHOLD", "100"))

        self.base_profit_bps = Decimal(_cfg.env.get("ATOM_MIN_PROFIT_THRESHOLD_BPS", "23"))
        self.base_trade_size = Decimal(_cfg.env.get("MAX_TRADE_AMOUNT_USD", "50000"))
        self.base_slippage_bps = Decimal(_cfg.env.get("MAX_SLIPPAGE_BPS", "300"))

    def update_price(self, price: Decimal, volume: Decimal, pair: str):
        now = time.time()
        self.price_history.append({"t": now, "p": price})
        self.volume_history.append({"t": now, "v": volume})
        logger.debug(f"Updated price {pair}: {price} vol={volume}")

    def update_gas(self, gas_gwei: Decimal):
        self.gas_history.append({"t": time.time(), "g": gas_gwei})

    def volatility(self, minutes=60) -> Decimal:
        cutoff = time.time() - minutes * 60
        series = [float(p["p"]) for p in self.price_history if p["t"] > cutoff]
        if len(series) < 10:
            return Decimal("1.0")
        pct_changes = [(series[i] - series[i - 1]) / series[i - 1] * 100 for i in range(1, len(series))]
        return Decimal(str(np.std(pct_changes))) if pct_changes else Decimal("1.0")

    def liquidity(self) -> str:
        cutoff = time.time() - 1800
        vols = [v["v"] for v in self.volume_history if v["t"] > cutoff]
        if not vols:
            return "normal"
        avg = sum(vols) / len(vols)
        if avg < self.low_liq:
            return "low"
        if avg > self.high_liq:
            return "high"
        return "normal"

    def congestion(self) -> str:
        cutoff = time.time() - 600
        gas = [g["g"] for g in self.gas_history if g["t"] > cutoff]
        if not gas:
            return "normal"
        avg = sum(gas) / len(gas)
        if avg < self.low_gas:
            return "low"
        if avg > self.high_gas:
            return "high"
        return "normal"

    def adjust_strategy(self):
        vol = self.volatility()
        vol_level = "normal"
        if vol < self.low_vol:
            vol_level = "low"
        elif vol > self.high_vol:
            vol_level = "high"

        liq = self.liquidity()
        gas = self.congestion()

        strat = {
            "min_profit_bps": self.base_profit_bps,
            "max_trade_size": self.base_trade_size,
            "max_slippage_bps": self.base_slippage_bps,
        }

        # Volatility adjustments
        if vol_level == "high":
            strat["min_profit_bps"] *= Decimal("1.5")
            strat["max_trade_size"] *= Decimal("0.7")
        elif vol_level == "low":
            strat["min_profit_bps"] *= Decimal("0.8")

        # Liquidity adjustments
        if liq == "low":
            strat["max_trade_size"] *= Decimal("0.5")
            strat["max_slippage_bps"] *= Decimal("1.5")
        elif liq == "high":
            strat["max_trade_size"] *= Decimal("1.3")

        # Congestion adjustments
        if gas == "high":
            strat["min_profit_bps"] *= Decimal("2.0")
        elif gas == "low":
            strat["min_profit_bps"] *= Decimal("0.9")

        self.current_conditions = {"volatility": vol_level, "liquidity": liq, "congestion": gas}
        self.strategy = strat
        logger.info(f"Adjusted strategy: {self.strategy} under {self.current_conditions}")
        return self.strategy

    def summary(self) -> Dict:
        return {
            "conditions": self.current_conditions,
            "strategy": self.strategy,
            "data_counts": {
                "prices": len(self.price_history),
                "volumes": len(self.volume_history),
                "gas": len(self.gas_history),
            },
        }
