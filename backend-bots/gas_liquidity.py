import logging
import time
from typing import Dict, Any, Optional

from web3 import Web3
from prometheus_client import Counter, Gauge
from config.secure_config import SecureConfig
from abi.uniswap_v2_pair_abi import UNISWAP_V2_PAIR_ABI
from abi.uniswap_v3_pool_abi import UNISWAP_V3_POOL_ABI
from abi.balancer_vault_abi import BALANCER_VAULT_ABI

# ------------------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------------------
logger = logging.getLogger("gas_liquidity")
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
# Prometheus metrics
# ------------------------------------------------------------------------------
gas_predictions_total = Counter("gas_predictions_total", "Number of gas predictions made")
liquidity_checks_total = Counter("liquidity_checks_total", "Number of liquidity checks run")
trades_aborted_gas_total = Counter("trades_aborted_gas_total", "Trades aborted due to gas concerns")
trades_aborted_slippage_total = Counter("trades_aborted_slippage_total", "Trades aborted due to slippage")
slippage_pct_gauge = Gauge("slippage_pct", "Calculated trade slippage percent")
gas_estimate_gwei = Gauge("gas_estimate_gwei", "Estimated gas price in gwei")

# ------------------------------------------------------------------------------
# Config load
# ------------------------------------------------------------------------------
config = SecureConfig()
w3 = Web3(Web3.HTTPProvider(config.get_rpc_url("polygon")))  # default Polygon RPC

# ------------------------------------------------------------------------------
# Gas Estimation (EIP-1559)
# ------------------------------------------------------------------------------
def get_dynamic_gas_estimate() -> Dict[str, Any]:
    """
    Fetch dynamic gas prediction using recent blocks.
    """
    block = w3.eth.get_block("latest")
    base_fee = block.get("baseFeePerGas", 0)
    if base_fee == 0:
        base_fee = w3.eth.gas_price

    # Add simple percentiles for priority fee
    low = int(base_fee * 1.05)
    standard = int(base_fee * 1.15)
    fast = int(base_fee * 1.25)
    urgent = int(base_fee * 1.35)

    gas_predictions_total.inc()
    gas_estimate_gwei.set(base_fee / 1e9)

    return {
        "low": low,
        "standard": standard,
        "fast": fast,
        "urgent": urgent,
        "baseFee": base_fee,
    }

# ------------------------------------------------------------------------------
# Pool Utilities
# ------------------------------------------------------------------------------
def get_uniswap_v2_reserves(pair_address: str) -> Optional[tuple]:
    try:
        pair = w3.eth.contract(address=Web3.to_checksum_address(pair_address), abi=UNISWAP_V2_PAIR_ABI)
        reserves = pair.functions.getReserves().call()
        return reserves  # (reserve0, reserve1, timestamp)
    except Exception as e:
        logger.error(f"Failed to fetch V2 reserves for {pair_address}: {e}")
        return None

def get_uniswap_v3_liquidity(pool_address: str) -> Optional[int]:
    try:
        pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=UNISWAP_V3_POOL_ABI)
        liquidity = pool.functions.liquidity().call()
        return liquidity
    except Exception as e:
        logger.error(f"Failed to fetch V3 liquidity for {pool_address}: {e}")
        return None

def get_balancer_pool_info(vault_address: str, pool_id: str) -> Optional[Dict[str, Any]]:
    try:
        vault = w3.eth.contract(address=Web3.to_checksum_address(vault_address), abi=BALANCER_VAULT_ABI)
        pool_tokens = vault.functions.getPoolTokens(pool_id).call()
        return {
            "tokens": pool_tokens[0],
            "balances": pool_tokens[1],
        }
    except Exception as e:
        logger.error(f"Failed to fetch Balancer pool info {vault_address}:{pool_id}: {e}")
        return None

# ------------------------------------------------------------------------------
# Slippage Calculation
# ------------------------------------------------------------------------------
def calculate_slippage(amount_in: float, reserve_in: float, reserve_out: float) -> float:
    """
    AMM formula: x*y=k
    """
    amount_out = (reserve_out * amount_in) / (reserve_in + amount_in)
    ideal_out = (reserve_out / reserve_in) * amount_in
    slippage = ((ideal_out - amount_out) / ideal_out) * 100
    return slippage

# ------------------------------------------------------------------------------
# Main Validation Logic
# ------------------------------------------------------------------------------
def validate_trade(pair_address: str, amount_in: float, min_spread_bps: int = 23) -> Dict[str, Any]:
    """
    Validates a trade based on gas and liquidity conditions.
    """
    gas_est = get_dynamic_gas_estimate()
    reserves = get_uniswap_v2_reserves(pair_address)

    if reserves is None:
        return {"ok": False, "reason": "No reserves"}

    reserve0, reserve1, _ = reserves
    slippage = calculate_slippage(amount_in, reserve0, reserve1)

    liquidity_checks_total.inc()
    slippage_pct_gauge.set(slippage)

    if slippage > 0.5:
        trades_aborted_slippage_total.inc()
        return {"ok": False, "reason": f"Slippage too high ({slippage:.2f}%)"}

    # Approx profit check
    spread_bps = 30  # mock, in practice compare on-chain vs oracle
    if spread_bps < min_spread_bps:
        return {"ok": False, "reason": f"Spread too low ({spread_bps}bps)"}

    return {
        "ok": True,
        "gas": gas_est,
        "slippage": slippage,
        "spread_bps": spread_bps,
    }

# ------------------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Example: USDC/WETH QuickSwap pair
    usdc_weth_pair = "0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d"
    logger.info("Running gas/liquidity validation test...")
    result = validate_trade(usdc_weth_pair, 1_000 * 10**6)  # 1000 USDC
    logger.info(result)
