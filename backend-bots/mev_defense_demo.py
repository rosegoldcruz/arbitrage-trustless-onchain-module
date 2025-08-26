#!/usr/bin/env python3
"""
MEV Defense Demo Runner
- Integrates mempool_sniper, gas_liquidity, price_utils
- Validates config and runs demo loops
- Exports Prometheus metrics on /metrics
"""

import argparse
import asyncio
import json
import logging
import signal
import sys
import time
from typing import Dict, Any

from prometheus_client import start_http_server
from config.secure_config import SecureConfig
from backend-bots import mempool_sniper, gas_liquidity, price_utils

logger = logging.getLogger("mev_defense_demo")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

_cfg = SecureConfig()

# ------------------------------------------------------------------------------
# Demo Components
# ------------------------------------------------------------------------------
async def run_mempool_sniper(duration: int):
    """
    Run mempool sniper for duration seconds.
    """
    logger.info("🚀 Starting mempool sniper demo...")
    start = time.time()
    async for _ in mempool_sniper.mempool_monitor():
        if duration and time.time() - start > duration:
            break

def run_gas_liquidity_test():
    """
    Run gas/liquidity validation on a known Polygon pool (USDC/WETH).
    """
    logger.info("🚀 Running gas/liquidity validation demo...")
    usdc_weth_pair = "0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d"
    result = gas_liquidity.validate_trade(usdc_weth_pair, 1_000 * 10**6)  # 1000 USDC
    logger.info(json.dumps(result, indent=2))
    return result

def run_price_feed_test():
    """
    Pull current Chainlink prices for core tokens.
    """
    logger.info("🚀 Running price feed demo...")
    symbols = ["ETH", "MATIC", "USDC", "DAI", "USDT"]
    if "CHAINLINK_GHO_USD" in _cfg.env:
        symbols.append("GHO")

    prices = price_utils.get_prices_usd(symbols)
    logger.info(json.dumps(prices, indent=2))
    return prices

# ------------------------------------------------------------------------------
# Main Demo
# ------------------------------------------------------------------------------
async def demo(duration: int, metrics_port: int):
    # Start Prometheus metrics server
    logger.info(f"📊 Starting Prometheus metrics server on port {metrics_port}")
    start_http_server(metrics_port)

    # Run price feeds and gas/liquidity once
    run_price_feed_test()
    run_gas_liquidity_test()

    # Kick off mempool monitor
    if duration:
        logger.info(f"⏱️ Running mempool sniper for {duration}s...")
        try:
            await asyncio.wait_for(run_mempool_sniper(duration), timeout=duration + 5)
        except asyncio.TimeoutError:
            logger.info("Mempool demo finished (timeout).")
    else:
        logger.info("⏱️ Running mempool sniper indefinitely (CTRL+C to stop)...")
        await run_mempool_sniper(0)

def parse_args():
    p = argparse.ArgumentParser(description="ATOM MEV Defense Demo")
    p.add_argument("--duration", type=int, default=30, help="Duration of mempool demo in seconds (0 = infinite)")
    p.add_argument("--metrics-port", type=int, default=9200, help="Port for Prometheus metrics server")
    return p.parse_args()

# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    args = parse_args()

    loop = asyncio.get_event_loop()

    def shutdown(sig, frame):
        logger.info("Received shutdown signal, stopping demo...")
        loop.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        loop.run_until_complete(demo(args.duration, args.metrics_port))
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    finally:
        loop.close()
