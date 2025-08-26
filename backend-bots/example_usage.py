#!/usr/bin/env python3
"""
Example Usage Runner
⚠️ This is a diagnostic entrypoint, not production code.

Runs basic health checks on RPC, Redis, and core modules.
"""

import logging
from backend_bots.rpc_manager import RPCManager
from backend_bots.gas_liquidity import validate_trade
from backend_bots.price_utils import get_prices_usd
from config.secure_config import SecureConfig
from backend_bots.infra.redis_bus import Bus

logger = logging.getLogger("example_usage")
logging.basicConfig(level=logging.INFO)

def run():
    cfg = SecureConfig()
    rpc = RPCManager()

    # RPC test
    for chain in ["polygon", "ethereum", "base", "arbitrum"]:
        try:
            w3 = rpc.get_web3(chain)
            block = w3.eth.block_number
            logger.info(f"✅ {chain} connected, latest block {block}")
        except Exception as e:
            logger.error(f"❌ {chain} RPC failed: {e}")

    # Chainlink price test
    prices = get_prices_usd(["ETH", "MATIC", "USDC", "DAI", "USDT"])
    logger.info(f"Prices: {prices}")

    # Gas/liquidity test
    pair = "0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d"  # USDC/WETH QuickSwap
    result = validate_trade(pair, 1_000 * 10**6)
    logger.info(f"Gas/Liquidity validation: {result}")

    # Redis bus test
    try:
        bus = Bus()
        bus.publish("test.channel", {"hello": "world"})
        logger.info("✅ Redis publish test successful")
    except Exception as e:
        logger.error(f"❌ Redis test failed: {e}")

if __name__ == "__main__":
    run()
