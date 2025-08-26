#!/usr/bin/env python3
"""
Enhanced Production Trade Executor (Polygon-optimized)
- Multi-wallet execution with nonce mgmt and circuit breaker
- Redis-backed opportunity queue (default: arbitrage_opportunities)
- MEV-aware send path (auto-disables Flashbots on Polygon)
- Chainlink-driven MATIC/USD pricing for gas cost accounting
- Prometheus metrics + graceful shutdown

Env highlights:
  ATOM_CHAIN=polygon
  POLYGON_RPC_URL=...
  REDIS_URL=redis://...
  ATOM_CONTRACT_ADDRESS=0x<your_polygon_flashloan_contract>
  ATOM_OPPORTUNITY_QUEUE=arbitrage_opportunities   (default here)
  CHAINLINK_MATIC_USD_FEED=0xab594600376ec9fd91f8e885dadf0ce036862de0
  DEFAULT_ROUTER=0xa5E0829CaCEd8fFDD4De3C43696c57F7D7A678ff  # QuickSwap
  UNISWAP_V3_ROUTER=0xE592427A0AEce92De3Edee1F18E0157C05861564
  UNISWAP_V3_ROUTER2=0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45
  SUSHISWAP_ROUTER=0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506
  QUICKSWAP_ROUTER=0xa5E0829CaCEd8fFDD4De3C43696c57F7D7A678ff
  BALANCER_VAULT=0xBA12222222228d8Ba445958a75a0704d566BF2C8
  CURVE_ROUTER=0x8e764bE4288B842791989DB5b8ec067279829809
  ZEROX_EXCHANGE_PROXY=0xDef1C0ded9bec7F1a1670819833240f027b25EfF
"""

import asyncio
import json
import logging
import os
import signal
import time
import traceback
from collections import deque
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

import redis
from eth_abi import encode
from eth_account import Account
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3
from web3.types import TxReceipt

from config.secure_config import SecureConfig
from backend_bots.rpc_manager import RPCManager
from bots.production_mev_protection import ProductionMEVProtection

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("enhanced_trade_executor")

# ------------------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------------------
trades_executed = Counter("trades_executed_total", "Total trades executed", ["status"])
trade_profit = Histogram("trade_profit_usd", "Trade profit distribution")
execution_time = Histogram("trade_execution_time_seconds", "Trade execution time")
gas_used = Histogram("trade_gas_used", "Gas used per trade")
wallet_balance_gauge = Gauge("wallet_balance_matic", "Wallet balance in MATIC", ["address"])

_cfg = SecureConfig()


class TradeStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    REVERTED = "reverted"
    TIMEOUT = "timeout"


# ------------------------------------------------------------------------------
# Chainlink price helper (Polygon MATIC/USD)
# ------------------------------------------------------------------------------
class ChainlinkMaticUsd:
    # Default Polygon MATIC/USD feed
    DEFAULT_FEED = Web3.to_checksum_address(
        os.environ.get(
            "CHAINLINK_MATIC_USD_FEED",
            "0xab594600376ec9fd91f8e885dadf0ce036862de0",  # Polygon mainnet MATIC/USD
        )
    )
    ABI = [
        {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
         "stateMutability": "view", "type": "function"},
        {"inputs": [], "name": "latestRoundData", "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"},
        ], "stateMutability": "view", "type": "function"},
    ]

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.contract = w3.eth.contract(address=self.DEFAULT_FEED, abi=self.ABI)
        self._cache_price = 0.0
        self._cache_ts = 0.0
        self._ttl = float(os.environ.get("MATIC_USD_TTL_SEC", "15"))

    def get_price_usd(self) -> float:
        now = time.time()
        if now - self._cache_ts < self._ttl and self._cache_price > 0:
            return self._cache_price
        try:
            decimals = self.contract.functions.decimals().call()
            _, answer, _, updated_at, _ = self.contract.functions.latestRoundData().call()
            if int(updated_at) == 0 or int(answer) <= 0:
                raise RuntimeError("stale or invalid Chainlink price")
            price = float(answer) / (10 ** decimals)
            self._cache_price = price
            self._cache_ts = now
            return price
        except Exception as e:
            # Hard fallback if Chainlink is temporarily unreachable; do NOT rely on this long-term.
            fallback = float(os.environ.get("MATIC_USD_FALLBACK", "0.55"))
            logger.error(f"Chainlink price fetch failed: {e}. Using fallback {fallback}")
            return fallback


# ------------------------------------------------------------------------------
# Wallet Manager
# ------------------------------------------------------------------------------
class WalletManager:
    """Manages multiple wallets for load distribution and risk management"""

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.wallets: List[Dict] = []
        self.wallet_stats: Dict[str, Dict] = {}

        primary_key = _cfg.require("PRIVATE_KEY")
        self._add_wallet(primary_key, is_primary=True)

        for i in range(1, 6):
            key_name = f"EXECUTOR_WALLET_{i}"
            if key_name in _cfg.env and _cfg.env[key_name].strip():
                self._add_wallet(_cfg.env[key_name].strip(), is_primary=False)

    def _add_wallet(self, private_key: str, is_primary: bool = False) -> None:
        account = Account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        wallet = {
            "account": account,
            "address": account.address,
            "nonce": nonce,
            "is_primary": is_primary,
            "last_used": 0.0,
            "trades_executed": 0,
            "total_profit": 0.0,
            "consecutive_failures": 0,
        }
        self.wallets.append(wallet)
        self.wallet_stats[account.address] = {
            "trades": 0,
            "successes": 0,
            "failures": 0,
            "total_profit": 0.0,
        }

        balance = self.w3.eth.get_balance(account.address)
        wallet_balance_gauge.labels(address=account.address).set(balance / 1e18)
        logger.info(f"✅ Wallet added: {account.address} (Primary: {is_primary})")

    def get_best_wallet(self) -> Dict:
        min_balance_wei = int(float(_cfg.env.get("WALLET_MIN_BALANCE_MATIC", "0.02")) * 1e18)
        candidates: List[Dict] = []
        for w in self.wallets:
            bal = self.w3.eth.get_balance(w["address"])
            wallet_balance_gauge.labels(address=w["address"]).set(bal / 1e18)
            if bal >= min_balance_wei and w["consecutive_failures"] < 3:
                candidates.append(w)

        if not candidates:
            return self.wallets[0]

        candidates.sort(key=lambda x: (x["consecutive_failures"], x["last_used"]))
        return candidates[0]

    def update_wallet_stats(self, wallet_address: str, success: bool, profit: float = 0.0) -> None:
        for w in self.wallets:
            if w["address"] == wallet_address:
                w["last_used"] = time.time()
                w["trades_executed"] += 1
                if success:
                    w["consecutive_failures"] = 0
                    w["total_profit"] += float(profit)
                    self.wallet_stats[wallet_address]["successes"] += 1
                else:
                    w["consecutive_failures"] += 1
                    self.wallet_stats[wallet_address]["failures"] += 1
                self.wallet_stats[wallet_address]["trades"] += 1
                self.wallet_stats[wallet_address]["total_profit"] += float(profit)
                break

    def refresh_nonces(self) -> None:
        for w in self.wallets:
            try:
                w["nonce"] = self.w3.eth.get_transaction_count(w["address"])
            except Exception as e:
                logger.error(f"Nonce refresh failed for {w['address']}: {e}")


# ------------------------------------------------------------------------------
# Transaction Builder
# ------------------------------------------------------------------------------
class TransactionBuilder:
    """Builds optimized transactions for flash loan arbitrage"""

    def __init__(self, w3: Web3, flashloan_address: str):
        self.w3 = w3
        self.flashloan_address = Web3.to_checksum_address(flashloan_address)
        self.flashloan_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "asset", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "bytes", "name": "params", "type": "bytes"},
                ],
                "name": "executeArbitrage",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ]
        self.contract = w3.eth.contract(address=self.flashloan_address, abi=self.flashloan_abi)

    def encode_arbitrage_params(self, opp: Dict) -> bytes:
        try:
            def router_for_name(name: Optional[str]) -> str:
                if not name:
                    return _cfg.require("DEFAULT_ROUTER")
                key_map = {
                    "uniswap_v3": "UNISWAP_V3_ROUTER",
                    "sushiswap": "SUSHISWAP_ROUTER",
                    "quickswap": "QUICKSWAP_ROUTER",
                    "balancer": "BALANCER_VAULT",
                    "curve": "CURVE_ROUTER",
                    "zero_x": "ZEROX_EXCHANGE_PROXY",
                }
                env_key = key_map.get(name.lower(), "DEFAULT_ROUTER")
                return _cfg.require(env_key)

            router_addresses = [
                router_for_name(opp.get("dex_a")),
                router_for_name(opp.get("dex_b")),
                router_for_name(opp.get("dex_c")),
            ]

            slippage_bps = int(_cfg.env.get("SLIPPAGE_BPS", "50"))
            def apply_slippage(x: int) -> int:
                return (x * (10_000 - slippage_bps)) // 10_000

            min_amount_ab = apply_slippage(int(opp.get("amount_ab", 0)))
            min_amount_bc = apply_slippage(int(opp.get("amount_bc", 0)))
            min_amount_ca = apply_slippage(int(opp.get("amount_out", 0)))

            min_profit_wei = int(Decimal(str(opp.get("net_profit", 0))) * Decimal("0.8"))

            params = encode(
                [
                    "address[]",  # routers
                    "address[]",  # tokens (intermediates)
                    "uint24[]",   # fees
                    "uint256[]",  # minAmountsOut
                    "bytes[]",    # routerCalldata
                    "uint256",    # minProfit
                    "uint256",    # deadline
                    "bool",       # useCommitReveal
                    "bytes32",    # commitHash
                ],
                [
                    router_addresses,
                    [opp.get("token_b"), opp.get("token_c")],
                    [3000, 3000, 3000],
                    [min_amount_ab, min_amount_bc, min_amount_ca],
                    [b"", b"", b""],
                    min_profit_wei,
                    int(time.time()) + int(_cfg.env.get("TX_DEADLINE_SECONDS", "120")),
                    False,
                    bytes(32),
                ],
            )
            return params
        except Exception as e:
            logger.error(f"Failed to encode params: {e}")
            raise

    def build_transaction(self, wallet: Dict, opp: Dict, gas_price: int) -> Dict:
        try:
            params = self.encode_arbitrage_params(opp)
            tx = self.contract.functions.executeArbitrage(
                Web3.to_checksum_address(opp["token_a"]),
                int(opp["amount_in"]),
                params,
            ).build_transaction(
                {
                    "from": wallet["address"],
                    "gas": int(_cfg.env.get("MAX_GAS_LIMIT", "600000")),
                    "gasPrice": int(gas_price),
                    "nonce": int(wallet["nonce"]),
                }
            )
            return tx
        except Exception as e:
            logger.error(f"Failed to build tx: {e}")
            raise


# ------------------------------------------------------------------------------
# Executor
# ------------------------------------------------------------------------------
class EnhancedTradeExecutor:
    def __init__(self):
        # Network: default Polygon
        chain_name = _cfg.env.get("ATOM_CHAIN", "polygon").strip().lower()
        expected_chain_id = {"sepolia": 11155111, "mainnet": 1, "polygon": 137}.get(chain_name, 137)

        self.rpc_manager = RPCManager()
        self.w3 = self.rpc_manager.get_web3(chain_name)
        if self.w3.eth.chain_id != expected_chain_id:
            raise RuntimeError(
                f"Connected chain_id {self.w3.eth.chain_id} != expected {expected_chain_id} for {chain_name}"
            )

        # Redis
        self.redis = redis.from_url(_cfg.require("REDIS_URL"), decode_responses=True)

        # Config
        self.min_profit_bps = Decimal(_cfg.env.get("MIN_PROFIT_THRESHOLD_BPS", "35"))
        self.min_trade_size_usd = float(_cfg.env.get("MIN_TRADE_SIZE_USD", "25000"))
        self.target_net_profit = float(_cfg.env.get("TARGET_NET_PROFIT_PER_TRADE", "100"))
        self.max_gas_limit = int(_cfg.env.get("MAX_GAS_LIMIT", "600000"))
        self.gas_price_multiplier = float(_cfg.env.get("GAS_PRICE_MULTIPLIER", "1.2"))
        self.execution_timeout = int(_cfg.env.get("ATOM_EXECUTION_TIMEOUT", "8000")) / 1000.0

        # Queue / keys (default aligned to detector)
        self.opp_queue = _cfg.env.get("ATOM_OPPORTUNITY_QUEUE", "arbitrage_opportunities")
        self.killswitch_key = _cfg.env.get("ATOM_KILL_SWITCH_KEY", "atom:killswitch")
        self.lock_ttl = int(_cfg.env.get("ATOM_TRADE_LOCK_TTL_SEC", "30"))

        # Components
        self.wallet_manager = WalletManager(self.w3)
        self.mev_protection = ProductionMEVProtection(self.w3)

        # Auto-disable Flashbots Protect on Polygon
        if chain_name == "polygon":
            try:
                # If the class supports a flag, flip it; otherwise we just won't call the protected path.
                setattr(self.mev_protection, "use_flashbots_protect", False)
            except Exception:
                pass

        # Contract
        flashloan_addr = _cfg.env.get("ATOM_CONTRACT_ADDRESS", _cfg.env.get("FLASHLOAN_ARB_ADDR", ""))
        if not flashloan_addr:
            raise ValueError("Flash loan contract address not configured (ATOM_CONTRACT_ADDRESS or FLASHLOAN_ARB_ADDR)")
        self.flashloan_addr = Web3.to_checksum_address(flashloan_addr)
        self.tx_builder = TransactionBuilder(self.w3, self.flashloan_addr)

        # Price oracle
        self.price_oracle = ChainlinkMaticUsd(self.w3)

        # State
        self.active_trades: Dict[str, Dict] = {}
        self.trade_history: deque = deque(maxlen=1000)
        self.pending_confirmations: Dict[str, Dict] = {}
        self.running: bool = False

        # Stats
        self.stats = {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "reverted_trades": 0,
            "timeout_trades": 0,
            "total_profit_usd": 0.0,
            "total_gas_cost_usd": 0.0,
            "avg_execution_time": 0.0,
            "success_rate": 0.0,
        }

        # Circuit breaker
        self.failure_window = deque(maxlen=20)
        self.fail_threshold = int(_cfg.env.get("ATOM_FAILURE_BREAKER", "8"))
        self.cooldown_seconds = int(_cfg.env.get("ATOM_BREAKER_COOLDOWN_SEC", "60"))
        self._cooldown_until = 0.0

        # Metrics server
        metrics_port = int(_cfg.env.get("PROMETHEUS_PORT", "9100"))
        start_http_server(metrics_port)
        logger.info(f"📈 Prometheus metrics exposed on :{metrics_port}")

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------
    async def execute(self, opp: Dict) -> bool:
        trade_id = opp.get("id", f"trade_{int(time.time()*1000)}")
        started_at = time.time()

        lock_key = f"atom:trade:lock:{trade_id}"
        if not self.redis.set(lock_key, "1", nx=True, ex=self.lock_ttl):
            logger.info(f"🔒 Skipping duplicate trade: {trade_id}")
            return False

        try:
            if not self._validate_opportunity(opp):
                logger.warning(f"[{trade_id}] Validation failed")
                return False

            if self._breaker_active():
                logger.warning(f"[{trade_id}] Breaker active, skipping")
                return False

            if self.redis.get(self.killswitch_key) in ("1", "true", "TRUE", "on", "ON"):
                logger.warning(f"[{trade_id}] Kill switch enabled, skipping")
                return False

            if trade_id in self.active_trades:
                logger.warning(f"[{trade_id}] Already active")
                return False

            self.active_trades[trade_id] = {"opportunity": opp, "status": TradeStatus.PENDING, "start_time": started_at}

            wallet = self.wallet_manager.get_best_wallet()
            logger.info(f"🔄 Executing {trade_id} via {wallet['address']}")

            gas_price = await self._get_optimized_gas_price(opp)
            tx = self.tx_builder.build_transaction(wallet, opp, gas_price)

            signed = self.w3.eth.account.sign_transaction(tx, wallet["account"].key)
            self.active_trades[trade_id]["status"] = TradeStatus.EXECUTING

            # MEV path (disabled on Polygon via flag)
            use_protect = bool(getattr(self.mev_protection, "use_flashbots_protect", False))
            if opp.get("mev_risk", 0) > 0.5 and use_protect:
                tx_hash = await self.mev_protection.send_protected_transaction(signed)
            else:
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction).hex()

            logger.info(f"[{trade_id}] 📤 Sent: {tx_hash}")
            wallet["nonce"] += 1

            self.pending_confirmations[tx_hash] = {
                "trade_id": trade_id,
                "wallet": wallet["address"],
                "opportunity": opp,
                "sent_time": time.time(),
            }

            receipt = await self._wait_for_confirmation(tx_hash, timeout=self.execution_timeout)
            if receipt:
                return await self._finalize_receipt(trade_id, tx_hash, receipt, started_at, wallet, opp)
            else:
                self.stats["timeout_trades"] += 1
                self.wallet_manager.update_wallet_stats(wallet["address"], False)
                trades_executed.labels(status="timeout").inc()
                self._register_failure()
                logger.error(f"[{trade_id}] ⏱️ Timeout waiting for receipt")
                return False

        except Exception as e:
            logger.error(f"[{trade_id}] Execution error: {e}")
            logger.error(traceback.format_exc())
            self.stats["failed_trades"] += 1
            trades_executed.labels(status="failed").inc()
            self._register_failure()
            self.redis.lpush(
                "trade_failures",
                json.dumps(
                    {
                        "trade_id": trade_id,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "opportunity": opp,
                        "timestamp": time.time(),
                    }
                ),
            )
            self.redis.ltrim("trade_failures", 0, 99)
            return False
        finally:
            self.active_trades.pop(trade_id, None)
            self.stats["total_trades"] += 1
            self._update_success_rate()
            try:
                self.redis.delete(lock_key)
            except Exception:
                pass

    # --------------------------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------------------------
    def _validate_opportunity(self, opp: Dict) -> bool:
        try:
            if time.time() - float(opp.get("timestamp", 0)) > float(_cfg.env.get("OPP_MAX_AGE_SEC", "10")):
                logger.warning("Opportunity too old")
                return False

            if Decimal(str(opp.get("profit_bps", 0))) < self.min_profit_bps:
                logger.warning("Profit below threshold")
                return False

            if float(opp.get("net_profit_usd", 0.0)) < self.target_net_profit:
                logger.warning("USD profit below target")
                return False

            if float(opp.get("trade_size_usd", 0.0)) < self.min_trade_size_usd:
                logger.warning("Trade size too small")
                return False

            for t in ("token_a", "token_b", "token_c"):
                addr = opp.get(t)
                if not addr or not Web3.is_address(addr):
                    logger.warning(f"Invalid token address: {t}={addr}")
                    return False

            if int(opp.get("amount_in", 0)) <= 0:
                logger.warning("Invalid amount_in")
                return False

            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    async def _get_optimized_gas_price(self, opp: Dict) -> int:
        try:
            base = self.w3.eth.gas_price
            mev_price, _prio = self.mev_protection.optimize_gas_price(base)
            profit_bps = float(opp.get("profit_bps", 0))
            if profit_bps > 100:
                multiplier = self.gas_price_multiplier * 1.2
            elif profit_bps > 50:
                multiplier = self.gas_price_multiplier
            else:
                multiplier = self.gas_price_multiplier * 0.9
            optimized = int(max(base, mev_price) * multiplier)
            max_gwei = int(_cfg.env.get("ATOM_MAX_GAS_PRICE", "200"))
            final_price = min(optimized, int(max_gwei * 1e9))
            logger.debug(f"Gas price base={base/1e9:.2f} gwei optimized={final_price/1e9:.2f} gwei")
            return final_price
        except Exception as e:
            logger.error(f"Gas price optimization error: {e}")
            return int(100 * 1e9)

    async def _wait_for_confirmation(self, tx_hash: str, timeout: float) -> Optional[TxReceipt]:
        start = time.time()
        interval = 1.0
        while time.time() - start < timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    self.pending_confirmations.pop(tx_hash, None)
                    return receipt
            except Exception:
                pass
            await asyncio.sleep(interval)
            interval = min(interval * 1.2, 3.0)

        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                self.pending_confirmations.pop(tx_hash, None)
                return receipt
        except Exception:
            pass
        return None

    async def _finalize_receipt(
        self,
        trade_id: str,
        tx_hash: str,
        receipt: TxReceipt,
        started_at: float,
        wallet: Dict,
        opp: Dict,
    ) -> bool:
        success = (receipt.status == 1)

        # Gas cost in USD using Chainlink MATIC/USD
        matic_usd = self.price_oracle.get_price_usd()
        gas_price = getattr(receipt, "effectiveGasPrice", None)
        if gas_price is None:
            try:
                tx = self.w3.eth.get_transaction(tx_hash)
                gas_price = tx.get("gasPrice", self.w3.eth.gas_price)
            except Exception:
                gas_price = self.w3.eth.gas_price
        gas_cost_wei = int(receipt.gasUsed) * int(gas_price)
        gas_cost_usd = (gas_cost_wei / 1e18) * matic_usd

        if success:
            profit_usd = float(opp.get("net_profit_usd", 0.0))
            self.stats["successful_trades"] += 1
            self.stats["total_profit_usd"] += profit_usd
            self.stats["total_gas_cost_usd"] += gas_cost_usd
            self.wallet_manager.update_wallet_stats(wallet["address"], True, profit_usd)
            trades_executed.labels(status="success").inc()
            trade_profit.observe(profit_usd)
            gas_used.observe(int(receipt.gasUsed))

            rec = {
                "trade_id": trade_id,
                "tx_hash": tx_hash,
                "status": "success",
                "wallet": wallet["address"],
                "opportunity": opp,
                "profit_usd": profit_usd,
                "gas_cost_usd": gas_cost_usd,
                "net_profit_usd": profit_usd - gas_cost_usd,
                "execution_time": time.time() - started_at,
                "timestamp": time.time(),
            }
            self.trade_history.append(rec)
            self.redis.lpush("trade_history", json.dumps(rec))
            self.redis.ltrim("trade_history", 0, 999)
            logger.info(
                f"[{trade_id}] ✅ Success | Profit ${profit_usd:.2f} | Gas ${gas_cost_usd:.2f} "
                f"| Net ${profit_usd - gas_cost_usd:.2f} | Hash {tx_hash}"
            )
        else:
            self.stats["reverted_trades"] += 1
            self.wallet_manager.update_wallet_stats(wallet["address"], False)
            trades_executed.labels(status="reverted").inc()
            self._register_failure()
            logger.error(f"[{trade_id}] ❌ Reverted | Hash {tx_hash}")
            await self._analyze_revert(tx_hash, receipt)

        execution_time.observe(time.time() - started_at)
        return success

    async def _analyze_revert(self, tx_hash: str, receipt: TxReceipt) -> None:
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            try:
                self.w3.eth.call({"to": tx["to"], "data": tx["input"], "from": tx["from"]}, receipt.blockNumber - 1)
            except Exception as e:
                reason = str(e)
                logger.error(f"Revert reason: {reason}")
                if any(x in reason for x in ("InsufficientProfit", "MinProfitNotMet")):
                    logger.info("Revert → profit vanished pre-exec")
                elif "SlippageTooHigh" in reason:
                    logger.info("Revert → slippage exceeded limit")
                elif "BadPoolCaller" in reason:
                    logger.error("Revert → contract configuration issue")
                self.redis.lpush(
                    "revert_analysis",
                    json.dumps({"tx_hash": tx_hash, "reason": reason, "timestamp": time.time()}),
                )
                self.redis.ltrim("revert_analysis", 0, 99)
        except Exception as e:
            logger.error(f"Revert analysis failed: {e}")

    # Background monitors
    async def monitor_pending_transactions(self) -> None:
        while self.running:
            try:
                now = time.time()
                for tx_hash, details in list(self.pending_confirmations.items()):
                    if now - details["sent_time"] > 180:
                        logger.warning(f"Tx stuck >180s: {tx_hash}")
                        self.pending_confirmations.pop(tx_hash, None)
                        continue
                    try:
                        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                        if receipt:
                            await self._process_confirmation(tx_hash, receipt, details)
                            self.pending_confirmations.pop(tx_hash, None)
                    except Exception:
                        pass
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Pending monitor error: {e}")
                await asyncio.sleep(5)

    async def _process_confirmation(self, tx_hash: str, receipt: TxReceipt, details: Dict) -> None:
        if receipt.status == 1:
            logger.info(f"✅ Late confirmation: {tx_hash}")
        else:
            logger.warning(f"❌ Late revert: {tx_hash}")
            await self._analyze_revert(tx_hash, receipt)

    async def emergency_cancel_pending(self) -> None:
        logger.warning("🚨 Emergency cancel of pending txs")
        for w in self.wallet_manager.wallets:
            try:
                cancel_tx = {
                    "from": w["address"],
                    "to": w["address"],
                    "value": 0,
                    "gas": 21000,
                    "gasPrice": int(self.w3.eth.gas_price * 1.5),
                    "nonce": int(w["nonce"]),
                }
                signed = self.w3.eth.account.sign_transaction(cancel_tx, w["account"].key)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction).hex()
                logger.info(f"Sent cancel tx: {tx_hash}")
                w["nonce"] += 1
            except Exception as e:
                logger.error(f"Cancel failed for {w['address']}: {e}")

    # --------------------------------------------------------------------------
    # Queue consumer & lifecycle
    # --------------------------------------------------------------------------
    async def _consume_queue(self) -> None:
        logger.info(f"🧵 Consuming queue: {self.opp_queue}")
        while self.running:
            try:
                if self.redis.get(self.killswitch_key) in ("1", "true", "TRUE", "on", "ON"):
                    await asyncio.sleep(1.5)
                    continue

                item = self.redis.brpop(self.opp_queue, timeout=2)
                if not item:
                    continue
                _key, payload = item
                try:
                    opp = json.loads(payload)
                except Exception:
                    logger.error("Malformed opportunity JSON; dropping")
                    continue

                await self.execute(opp)
            except Exception as e:
                logger.error(f"Queue consume error: {e}")
                await asyncio.sleep(1)

    async def start(self) -> None:
        self.running = True
        logger.info("🚀 Enhanced Trade Executor started")
        asyncio.create_task(self.monitor_pending_transactions())

        async def refresh_nonces_loop():
            while self.running:
                self.wallet_manager.refresh_nonces()
                await asyncio.sleep(60)

        asyncio.create_task(refresh_nonces_loop())
        await self._consume_queue()

    async def stop(self) -> None:
        logger.info("🛑 Stopping executor...")
        self.running = False
        await asyncio.sleep(0.3)

    # --------------------------------------------------------------------------
    # Circuit breaker, stats
    # --------------------------------------------------------------------------
    def _register_failure(self) -> None:
        now = time.time()
        self.failure_window.append(now)
        horizon = now - 120
        while self.failure_window and self.failure_window[0] < horizon:
            self.failure_window.popleft()
        if len(self.failure_window) >= self.fail_threshold:
            self._cooldown_until = now + self.cooldown_seconds
            logger.warning(f"⚠️ Circuit breaker tripped for {self.cooldown_seconds}s")

    def _breaker_active(self) -> bool:
        return time.time() < self._cooldown_until

    def _update_success_rate(self) -> None:
        if self.stats["total_trades"] > 0:
            self.stats["success_rate"] = self.stats["successful_trades"] / self.stats["total_trades"]

    # --------------------------------------------------------------------------
    # Introspection
    # --------------------------------------------------------------------------
    def get_stats(self) -> Dict:
        return {
            "total_trades": self.stats["total_trades"],
            "successful_trades": self.stats["successful_trades"],
            "failed_trades": self.stats["failed_trades"],
            "reverted_trades": self.stats["reverted_trades"],
            "timeout_trades": self.stats["timeout_trades"],
            "success_rate_pct": round(self.stats["success_rate"] * 100, 2),
            "total_profit_usd": self.stats["total_profit_usd"],
            "total_gas_cost_usd": self.stats["total_gas_cost_usd"],
            "net_profit_usd": self.stats["total_profit_usd"] - self.stats["total_gas_cost_usd"],
            "active_trades": len(self.active_trades),
            "pending_confirmations": len(self.pending_confirmations),
            "wallets": [
                {
                    "address": w["address"],
                    "balance": self.w3.eth.get_balance(w["address"]) / 1e18,
                    "trades": w["trades_executed"],
                    "profit": w["total_profit"],
                    "failures": w["consecutive_failures"],
                }
                for w in self.wallet_manager.wallets
            ],
            "current_wallet": self.wallet_manager.get_best_wallet()["address"],
        }

    async def build_transaction(self, opp: Dict) -> Dict:
        wallet = self.wallet_manager.get_best_wallet()
        gas_price = await self._get_optimized_gas_price(opp)
        return self.tx_builder.build_transaction(wallet, opp, gas_price)

    @property
    def wallet(self) -> Dict:
        return self.wallet_manager.get_best_wallet()


# ------------------------------------------------------------------------------
# Entrypoint with graceful shutdown
# ------------------------------------------------------------------------------
async def _amain() -> None:
    executor = EnhancedTradeExecutor()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler():
        loop.create_task(executor.stop())
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    runner = asyncio.create_task(executor.start())
    await stop_event.wait()
    try:
        await asyncio.wait_for(runner, timeout=2.0)
    except asyncio.TimeoutError:
        pass


if __name__ == "__main__":
    asyncio.run(_amain())
