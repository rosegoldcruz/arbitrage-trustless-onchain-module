import logging
import math
import time
from typing import Dict, Optional, List

from web3 import Web3
from prometheus_client import Gauge, Counter

from config.secure_config import SecureConfig
from backend-bots.rpc_manager import RPCManager

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logger = logging.getLogger("price_utils")
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
# Prometheus metrics
# ------------------------------------------------------------------------------
chainlink_price_usd = Gauge(
    "chainlink_price_usd",
    "Latest Chainlink price in USD",
    ["symbol"]
)
chainlink_feed_healthy = Gauge(
    "chainlink_feed_healthy",
    "1 if feed fresh and sane, 0 otherwise",
    ["symbol"]
)
chainlink_price_age_seconds = Gauge(
    "chainlink_price_age_seconds",
    "Age of the latest Chainlink price update",
    ["symbol"]
)
chainlink_request_failures = Counter(
    "chainlink_request_failures_total",
    "Total Chainlink read failures",
    ["symbol"]
)

# ------------------------------------------------------------------------------
# Minimal AggregatorV3Interface ABI
# ------------------------------------------------------------------------------
AGGREGATOR_V3_ABI = [
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "description",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

# ------------------------------------------------------------------------------
# Config & RPC
# ------------------------------------------------------------------------------
_cfg = SecureConfig()
_rpc = RPCManager()

# Required Polygon feeds (you already set these in .env.production)
_FEED_ADDRS: Dict[str, str] = {
    "ETH": _cfg.require("CHAINLINK_ETH_USD"),
    "MATIC": _cfg.require("CHAINLINK_MATIC_USD"),
    "USDC": _cfg.require("CHAINLINK_USDC_USD"),
    "DAI": _cfg.require("CHAINLINK_DAI_USD"),
    "USDT": _cfg.require("CHAINLINK_USDT_USD"),
}

# Optional: GHO (if you add CHAINLINK_GHO_USD later)
_gho_env_key = "CHAINLINK_GHO_USD"
if _gho_env_key in _cfg.env and _cfg.env.get(_gho_env_key):
    _FEED_ADDRS["GHO"] = _cfg.env.get(_gho_env_key)

# Freshness / sanity
_MAX_AGE_SECONDS = 60 * 60  # 1 hour max staleness
_MIN_POSITIVE_PRICE = 0.0001  # basically > 0
_MAX_REASONABLE_PRICE = 10_000_000  # USD sanity cap, we're not pricing planets

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def _get_w3_polygon() -> Web3:
    # Use RPCManager so failover/latency logic applies
    return _rpc.get_web3("polygon")

def _read_latest_price(w3: Web3, feed_address: str) -> Optional[Dict[str, float]]:
    """
    Read latest price from Chainlink aggregator.
    Returns dict with price, decimals, updated_at.
    """
    try:
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(feed_address),
            abi=AGGREGATOR_V3_ABI
        )
        decimals = contract.functions.decimals().call()
        round_id, answer, started_at, updated_at, answered_in_round = contract.functions.latestRoundData().call()
        if answer is None:
            return None
        price = float(answer) / (10 ** decimals)
        return {"price": price, "decimals": decimals, "updated_at": float(updated_at)}
    except Exception as e:
        logger.error(f"Chainlink read failed for {feed_address}: {e}")
        return None

def _retry_price(symbol: str, feed_address: str, attempts: int = 3, backoff_sec: float = 0.4) -> Optional[Dict[str, float]]:
    """
    Retry wrapper with simple backoff, using RPC failover if needed.
    """
    for i in range(attempts):
        try:
            w3 = _get_w3_polygon()
            data = _read_latest_price(w3, feed_address)
            if data:
                return data
        except Exception as e:
            logger.warning(f"[{symbol}] RPC/price read attempt {i+1}/{attempts} failed: {e}")
        time.sleep(backoff_sec * (2 ** i))
    chainlink_request_failures.labels(symbol=symbol).inc()
    return None

def _is_fresh(updated_at: float) -> bool:
    return (time.time() - updated_at) <= _MAX_AGE_SECONDS

def _is_sane(price: float) -> bool:
    return _MIN_POSITIVE_PRICE <= price <= _MAX_REASONABLE_PRICE

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------
def get_token_price_usd(symbol: str) -> Optional[float]:
    """
    Return latest USD price for a token symbol using Chainlink feeds on Polygon.
    Supported out of the box: ETH, MATIC, USDC, USDT, DAI (and GHO if env set).
    """
    sym = symbol.upper()
    feed = _FEED_ADDRS.get(sym)
    if not feed:
        logger.warning(f"No Chainlink feed configured for symbol {sym}")
        chainlink_feed_healthy.labels(symbol=sym).set(0)
        return None

    data = _retry_price(sym, feed)
    if not data:
        chainlink_feed_healthy.labels(symbol=sym).set(0)
        return None

    price = data["price"]
    updated_at = data["updated_at"]

    age = max(0.0, time.time() - updated_at)
    chainlink_price_age_seconds.labels(symbol=sym).set(age)

    fresh = _is_fresh(updated_at)
    sane = _is_sane(price)

    if not fresh or not sane:
        logger.warning(f"[{sym}] feed unhealthy | fresh={fresh} sane={sane} price={price} age={age:.0f}s")
        chainlink_feed_healthy.labels(symbol=sym).set(0)
        return None

    # metrics
    chainlink_feed_healthy.labels(symbol=sym).set(1)
    chainlink_price_usd.labels(symbol=sym).set(price)
    return price

def get_prices_usd(symbols: List[str]) -> Dict[str, Optional[float]]:
    """
    Batch read convenience wrapper.
    """
    results: Dict[str, Optional[float]] = {}
    for s in symbols:
        try:
            results[s.upper()] = get_token_price_usd(s)
        except Exception as e:
            logger.error(f"Failed to get price for {s}: {e}")
            results[s.upper()] = None
    return results

def usd_value_of(amount: float, symbol: str, decimals: int) -> Optional[float]:
    """
    Convert an on-chain token amount to USD using Chainlink.
    amount: integer amount (wei-like), pass as float or int
    decimals: token decimals (e.g. 6 for USDC, 18 for WETH/WMATIC)
    """
    px = get_token_price_usd(symbol)
    if px is None:
        return None
    return (float(amount) / (10 ** decimals)) * px

# ------------------------------------------------------------------------------
# CLI / Quick test
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Quick sanity check without spamming logs
    logging.basicConfig(level=logging.INFO)
    symbols = ["ETH", "MATIC", "USDC", "DAI", "USDT"]
    # Include GHO if you’ve set CHAINLINK_GHO_USD
    if "GHO" in _FEED_ADDRS:
        symbols.append("GHO")

    prices = get_prices_usd(symbols)
    for sym, px in prices.items():
        if px is None:
            print(f"{sym}: unavailable")
        else:
            print(f"{sym}: ${px:,.6f}")
