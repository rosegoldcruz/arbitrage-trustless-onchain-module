#!/usr/bin/env python3
"""
Execution helpers for ATOM arbitrage engine.
Handles profitability validation and dry-run vs live execution.
"""

import os
import logging
from decimal import Decimal
from config.secure_config import SecureConfig

logger = logging.getLogger("engine.exec")
logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
_cfg = SecureConfig()
DRY_RUN = _cfg.env.get("DRY_RUN", "true").lower() == "true"
MIN_PROFIT_BPS = Decimal(_cfg.env.get("ATOM_MIN_PROFIT_THRESHOLD_BPS", "23"))

# ------------------------------------------------------------------------------
# Profitability Validation
# ------------------------------------------------------------------------------
def validate_dual_leg(usdc_in: Decimal, usdc_out: Decimal) -> (bool, Decimal):
    """
    Check profitability between input and output in basis points.
    """
    try:
        net_bps = (usdc_out - usdc_in) / usdc_in * Decimal(10000)
        profitable = net_bps >= MIN_PROFIT_BPS
        return profitable, net_bps
    except Exception as e:
        logger.error(f"Profitability validation failed: {e}")
        return False, Decimal(0)

# ------------------------------------------------------------------------------
# Trade Execution
# ------------------------------------------------------------------------------
def try_dual_leg(usd_amount: int) -> (bool, Decimal):
    """
    Execute or simulate a dual-leg arbitrage trade.
    """
    usdc_in = Decimal(usd_amount)

    # In production this would be the real output after routing.
    # For now we just pass through to validation until routers are wired.
    usdc_out = usdc_in  # placeholder, must be updated with actual execution path

    profitable, net_bps = validate_dual_leg(usdc_in, usdc_out)

    if DRY_RUN:
        logger.info(f"[dry-run] {usd_amount} USDC -> {usdc_out} USDC (net={net_bps:.2f} bps)")
        return profitable, net_bps

    if profitable:
        logger.info(f"[EXEC] Executing trade {usd_amount} USDC -> {usdc_out} USDC (net={net_bps:.2f} bps)")
        # TODO: integrate with trade_executor.execute_trade()
        return True, net_bps

    logger.info(f"[SKIP] Trade not profitable ({net_bps:.2f} bps < {MIN_PROFIT_BPS})")
    return False, net_bps
