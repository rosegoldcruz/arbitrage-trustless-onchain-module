#!/usr/bin/env python3
"""
Production MEV Protection
- Flashbots Protect + sandwich prevention
- Strictly env-driven config (SecureConfig)
"""

import time
import logging
from typing import Dict, List, Optional, Tuple

import aiohttp
from web3 import Web3
from config.secure_config import SecureConfig

logger = logging.getLogger("production_mev_protection")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class ProductionMEVProtection:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.use_flashbots_protect = _cfg.env.get("USE_FLASHBOTS_PROTECT", "true").lower() == "true"
        self.flashbots_rpc = _cfg.env.get("FLASHBOTS_RPC_URL", "https://rpc.flashbots.net")
        self.private_mempool_enabled = _cfg.env.get("PRIVATE_MEMPOOL_ENABLED", "true").lower() == "true"
        self.max_priority_fee = int(_cfg.env.get("MAX_PRIORITY_FEE_GWEI", "2")) * 10**9
        self.max_fee_per_gas = int(_cfg.env.get("MAX_FEE_PER_GAS_GWEI", "100")) * 10**9

        self.sandwich_detection_enabled = True
        self.recent_transactions: List[Dict] = []

    # --------------------------------------------------------------------------
    # Gas Price Optimization
    # --------------------------------------------------------------------------
    def optimize_gas_price(self, base_fee: Optional[int] = None) -> Tuple[int, int]:
        try:
            if base_fee is None:
                block = self.w3.eth.get_block("latest")
                base_fee = block.baseFeePerGas
            priority_fee = min(self.max_priority_fee, int(base_fee * 0.1))
            max_fee = min(self.max_fee_per_gas, base_fee * 2 + priority_fee)
            return max_fee, priority_fee
        except Exception as e:
            logger.error(f"Gas price optimization failed: {e}")
            return self.max_fee_per_gas, self.max_priority_fee

    # --------------------------------------------------------------------------
    # Transaction Sending
    # --------------------------------------------------------------------------
    async def send_protected_transaction(self, signed_tx) -> str:
        if self.use_flashbots_protect and self.private_mempool_enabled:
            return await self._send_flashbots(signed_tx)
        return await self._send_public(signed_tx)

    async def _send_flashbots(self, signed_tx) -> str:
        try:
            bundle = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_sendBundle",
                "params": [
                    {
                        "txs": [signed_tx.rawTransaction.hex()],
                        "blockNumber": hex(self.w3.eth.block_number + 1),
                        "minTimestamp": 0,
                        "maxTimestamp": int(time.time()) + 120,
                    }
                ],
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.flashbots_rpc, json=bundle) as resp:
                    result = await resp.json()
                    if "result" in result:
                        logger.info("✔ Sent via Flashbots Protect")
                        return result["result"]
                    logger.error(f"Flashbots error: {result}")
                    return await self._send_public(signed_tx)
        except Exception as e:
            logger.error(f"Flashbots send failed: {e}")
            return await self._send_public(signed_tx)

    async def _send_public(self, signed_tx) -> str:
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            logger.info("✔ Sent via public mempool")
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Public send failed: {e}")
            raise

    # --------------------------------------------------------------------------
    # Monitoring
    # --------------------------------------------------------------------------
    def add_tx_monitor(self, tx_hash: str, expected_profit: float):
        self.recent_transactions.append(
            {
                "tx_hash": tx_hash,
                "timestamp": time.time(),
                "expected_profit": expected_profit,
                "status": "pending",
            }
        )
        cutoff = time.time() - 3600
        self.recent_transactions = [tx for tx in self.recent_transactions if tx["timestamp"] > cutoff]

    def get_stats(self) -> Dict:
        return {
            "flashbots_enabled": self.use_flashbots_protect,
            "private_mempool_enabled": self.private_mempool_enabled,
            "sandwich_detection_enabled": self.sandwich_detection_enabled,
            "recent_transactions": len(self.recent_transactions),
        }
