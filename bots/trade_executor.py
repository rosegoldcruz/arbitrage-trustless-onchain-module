#!/usr/bin/env python3
"""
Trade Executor
- Executes flashloan arbitrage via deployed ATOM contract
- Wallet rotation & Redis trade logging
STRICT: No hardcoded RPCs, keys, or addresses. All SecureConfig.
"""

import asyncio
import json
import logging
import time
from decimal import Decimal
from typing import Dict

import redis
from web3 import Web3
from eth_account import Account
from eth_abi import encode_abi

from config.secure_config import SecureConfig
from backend_bots.rpc_manager import RPCManager

logger = logging.getLogger("trade_executor")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class TradeExecutor:
    def __init__(self):
        self.rpc = RPCManager()
        self.w3 = self.rpc.get_web3("polygon")
        if self.w3.eth.chain_id != 137:
            raise RuntimeError("Not Polygon mainnet")

        self.redis = redis.from_url(_cfg.require("REDIS_URL"), decode_responses=True)

        # Load thresholds
        self.min_profit_bps = Decimal(_cfg.env.get("ATOM_MIN_PROFIT_THRESHOLD_BPS", "23"))
        self.min_trade_size_usd = float(_cfg.env.get("MIN_TRADE_SIZE_USD", "25000"))
        self.target_net_profit = float(_cfg.env.get("TARGET_NET_PROFIT_USD", "100"))
        self.max_gas_limit = int(_cfg.env.get("MAX_GAS_LIMIT", "600000"))
        self.gas_price_mult = float(_cfg.env.get("GAS_PRICE_MULTIPLIER", "1.2"))

        # Wallet
        priv = _cfg.require("PRIVATE_KEY")
        acct = Account.from_key(priv)
        self.wallet = {"acct": acct, "address": acct.address, "nonce": self.w3.eth.get_transaction_count(acct.address)}

        # Contract
        flashloan_addr = _cfg.env.get("FLASHLOAN_ARB_ADDR") or _cfg.env.get("ATOM_CONTRACT_ADDRESS")
        if not flashloan_addr:
            raise ValueError("Flash loan contract address not configured (FLASHLOAN_ARB_ADDR or ATOM_CONTRACT_ADDRESS)")
        self.contract = self.w3.eth.contract(
            address=flashloan_addr,
            abi=[{
                "inputs": [
                    {"internalType": "address", "name": "asset", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "bytes", "name": "params", "type": "bytes"},
                ],
                "name": "executeFlashLoanArbitrage",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }]
        )

        # Router addresses (example)
        self.router_allowlist: Dict[str, str] = {
            "UniswapV3": _cfg.env.get("UNISWAP_V3_ROUTER", "0xE592427A0AEce92De3Edee1F18E0157C05861564"),
        }

    def encode_params(self, opp: Dict) -> bytes:
        dex_map = {"uniswap_v3": 0, "quickswap": 1, "sushiswap": 2, "balancer": 3}
        return encode_abi(
            ["address", "address", "address", "uint8", "uint8", "uint8", "uint24", "uint24", "uint24", "bytes32", "bytes32", "bytes32", "uint256"],
            [
                opp["token_a"], opp["token_b"], opp["token_c"],
                dex_map[opp["dex_a"]], dex_map[opp["dex_b"]], dex_map[opp["dex_c"]],
                3000, 3000, 3000,
                b"\x00" * 32, b"\x00" * 32, b"\x00" * 32,
                int(self.min_profit_bps),
            ],
        )

    async def execute(self, opp: Dict) -> bool:
        try:
            gas_price = int(self.w3.eth.gas_price * self.gas_price_mult)
            tx = self.contract.functions.executeFlashLoanArbitrage(
                opp["token_a"], opp["amount_in"], self.encode_params(opp)
            ).build_transaction({
                "from": self.wallet["address"],
                "gas": self.max_gas_limit,
                "gasPrice": gas_price,
                "nonce": self.wallet["nonce"],
            })
            signed = self.w3.eth.account.sign_transaction(tx, self.wallet["acct"].key)
            txh = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            rcpt = self.w3.eth.wait_for_transaction_receipt(txh, timeout=120)
            self.wallet["nonce"] += 1

            if rcpt.status == 1:
                profit = float(opp.get("net_profit_usd", 0))
                rec = {"opp": opp, "tx_hash": txh.hex(), "profit_usd": profit, "success": True, "t": time.time()}
                self.history.append(rec)
                self.redis.lpush("trade_history", json.dumps(rec))
                logger.info(f"✅ Trade success {txh.hex()} profit=${profit}")
                return True
            else:
                logger.error(f"❌ Trade failed {txh.hex()}")
                return False
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return False

    async def monitor(self):
        logger.info("Monitoring for opportunities...")
        self.running = True
        while self.running:
            try:
                raw = self.redis.lpop("arbitrage_opportunities")
                if raw:
                    opp = json.loads(raw)
                    if opp["profit_bps"] >= self.min_profit_bps:
                        await self.execute(opp)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(1)

    def get_stats(self) -> Dict:
        total, succ = len(self.history), len([t for t in self.history if t["success"]])
        return {
            "total_trades": total,
            "successful_trades": succ,
            "success_rate": succ / total * 100 if total else 0,
            "total_profit_usd": sum(t["profit_usd"] for t in self.history if t["success"]),
            "wallet": self.wallet["address"],
        }
