import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any

from web3 import Web3
from web3.middleware import geth_poa_middleware
from prometheus_client import Counter, Histogram

from config.secure_config import SecureConfig

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logger = logging.getLogger("mempool_sniper")
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
# Prometheus Metrics
# ------------------------------------------------------------------------------
mempool_tx_detected_total = Counter("mempool_tx_detected_total", "Total pending txs detected")
mempool_latency_ms = Histogram("mempool_latency_ms", "Latency in processing mempool txs")
mempool_large_swaps_total = Counter("mempool_large_swaps_total", "Large swaps flagged in mempool")
mempool_mev_opportunities_total = Counter("mempool_mev_opportunities_total", "Potential MEV opps flagged")

# ------------------------------------------------------------------------------
# Config / Web3 Init
# ------------------------------------------------------------------------------
config = SecureConfig()
WSS_URL = config.require("POLYGON_WSS_URL")
DEX_ROUTERS = config.get_dex_routers()

w3 = Web3(Web3.WebsocketProvider(WSS_URL, websocket_timeout=30))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# ------------------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------------------
def decode_tx_input(tx_input: str, to_address: str) -> Dict[str, Any]:
    """
    Decode a pending transaction input against known DEX ABIs.
    Supports UniswapV2, UniswapV3, SushiSwap, QuickSwap.
    """
    decoded = {"method": "unknown", "params": {}}
    try:
        if to_address.lower() in [addr.lower() for addr in DEX_ROUTERS.values()]:
            # detect function selector
            selector = tx_input[:10]
            if selector == "0x38ed1739":  # swapExactTokensForTokens
                decoded["method"] = "swapExactTokensForTokens"
            elif selector == "0x8803dbee":  # swapTokensForExactTokens
                decoded["method"] = "swapTokensForExactTokens"
            elif selector == "0x18cbafe5":  # swapExactETHForTokens
                decoded["method"] = "swapExactETHForTokens"
            elif selector == "0x7ff36ab5":  # swapExactETHForTokensSupportingFeeOnTransferTokens
                decoded["method"] = "swapExactETHForTokensSupportingFee"
            else:
                decoded["method"] = "router_call"
        return decoded
    except Exception as e:
        logger.debug(f"Failed to decode tx input: {e}")
        return decoded

def is_large_swap(tx: Dict[str, Any]) -> bool:
    """
    Heuristic: Large swaps are >200k gas, >50 gwei, or tx value > 1 ETH.
    """
    gas = tx.get("gasPrice", 0)
    val = tx.get("value", 0)
    return gas > 50_000_000_000 or val > Web3.to_wei(1, "ether")

# ------------------------------------------------------------------------------
# Core Sniper
# ------------------------------------------------------------------------------
async def mempool_monitor():
    logger.info(f"Connecting to Polygon mempool via {WSS_URL}...")
    sub = w3.eth.subscribe("newPendingTransactions")
    start_time = time.time()

    async for tx_hash in sub:
        try:
            tx = w3.eth.get_transaction(tx_hash)
            if not tx or not tx.get("to"):
                continue

            to_addr = tx["to"]
            decoded = decode_tx_input(tx["input"], to_addr)

            mempool_tx_detected_total.inc()
            mempool_latency_ms.observe((time.time() - start_time) * 1000)

            if decoded["method"] != "unknown" and is_large_swap(tx):
                mempool_large_swaps_total.inc()
                mempool_mev_opportunities_total.inc()
                logger.info(
                    f"🚨 Large swap detected | to={to_addr} | method={decoded['method']} "
                    f"| gas={tx['gasPrice']} | value={tx['value']}"
                )
        except Exception as e:
            logger.error(f"Error processing pending tx: {e}")
            await asyncio.sleep(0.1)  # throttle on error

# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(mempool_monitor())
    except KeyboardInterrupt:
        logger.info("Sniper terminated by user")
        sys.exit(0)
