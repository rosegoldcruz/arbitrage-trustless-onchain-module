"""
Centralized pre-trade validation for ATOM
- Enforces: spreadBps ≥ 23, ROI after gas ≥ 0.25%, slippage per leg ≤ 0.5%
- Base Sepolia only for this phase
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

MIN_SPREAD_BPS = 23
MIN_ROI_AFTER_GAS = 0.0025  # 0.25%
MAX_SLIPPAGE_PER_LEG = 0.005  # 0.5%

@dataclass
class RouteLeg:
    dex: str
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    slippage: float  # fraction (0.001 = 0.1%)

@dataclass
class TradeSimulation:
    amount_in: float
    amount_out: float
    gas_cost_usd: float
    spread_bps: int
    legs: List[RouteLeg]

@dataclass
class ValidationResult:
    ok: bool
    reason: Optional[str] = None

class TradeValidator:
    @staticmethod
    def validate(sim: TradeSimulation) -> ValidationResult:
        # Spread threshold
        if sim.spread_bps < MIN_SPREAD_BPS:
            return ValidationResult(False, f"Spread {sim.spread_bps}bps < {MIN_SPREAD_BPS}bps threshold")
        # ROI after gas
        roi_after_gas = 0.0
        if sim.amount_in > 0:
            roi_after_gas = (sim.amount_out - sim.amount_in - 0) / sim.amount_in  # compute net before gas
        roi_after_gas -= (sim.gas_cost_usd / max(1e-9, sim.amount_in))  # crude: assume $ value ~ amount_in units
        if roi_after_gas < MIN_ROI_AFTER_GAS:
            return ValidationResult(False, f"ROI {roi_after_gas*100:.3f}% < {MIN_ROI_AFTER_GAS*100:.2f}%")
        # Slippage per leg
        for i, leg in enumerate(sim.legs):
            if leg.slippage > MAX_SLIPPAGE_PER_LEG:
                return ValidationResult(False, f"Leg {i} slippage {leg.slippage*100:.3f}% > {MAX_SLIPPAGE_PER_LEG*100:.2f}%")
        return ValidationResult(True)

