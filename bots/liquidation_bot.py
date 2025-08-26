# bots/liquidation_bot.py
"""
ATOM Liquidation Scanner (Polygon mainnet)
- Finds liquidatable accounts on Aave v3 (Polygon) via subgraph, confirms on-chain
- Optional Compound v3 support via subgraph (disabled by default)
- Publishes opportunities to Redis Stream 'atom:opps:liquidations'
- Prometheus metrics on METRICS_PORT
- Strict: no private keys, no tx signing, no websockets required
- Hard fail if not on chain_id=137 (Polygon)
"""

import os
import asyncio
import json
import time
import logging
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional

import aiohttp
import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3, HTTPProvider

# ---------------- Env ----------------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

# Core infra
RPC_URL = _env("POLYGON_RPC_URL", required=True)
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")

# Aave v3 (Polygon) subgraph + pool
AAVE_V3_SUBGRAPH_URL = _env("AAVE_V3_SUBGRAPH_URL", "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-polygon")
AAVE_V3_POOL_ADDR = Web3.to_checksum_address(_env("AAVE_V3_POOL_ADDR", "0x794a61358D6845594F94dc1DB02A252b5b4814aD"))

# Optional Compound v3 subgraph (set to enable)
COMPOUND_V3_SUBGRAPH_URL = _env("COMPOUND_V3_SUBGRAPH_URL", "")

# Economics and thresholds
MIN_NET_PROFIT_USD = Decimal(_env("LIQ_MIN_NET_PROFIT_USD", "100"))
AAVE_CLOSE_FACTOR_BPS = int(_env("AAVE_CLOSE_FACTOR_BPS", "5000"))           # 50%
AAVE_LIQ_BONUS_BPS_DEFAULT = int(_env("AAVE_LIQ_BONUS_BPS_DEFAULT", "500"))  # 5% default if per-reserve bonus unavailable
AAVE_FLASH_FEE_BPS = Decimal(_env("AAVE_FLASH_FEE_BPS", "9"))                # 0.09%
LIQ_MAX_REPAY_USD = Decimal(_env("LIQ_MAX_REPAY_USD", "100000"))
GAS_LIMIT_ESTIMATE = int(_env("LIQ_GAS_LIMIT", "850000"))                    # liquidation+flash overhead

# Candidate discovery
AAVE_HF_QUERY_LT = _env("AAVE_HF_QUERY_LT", "1.00")  # pull HF < this to reduce on-chain calls
DISCOVERY_PAGE_SIZE = int(_env("LIQ_DISCOVERY_PAGE", "250"))
DISCOVERY_INTERVAL_SEC = float(_env("LIQ_DISCOVERY_INTERVAL_SEC", "30"))
SCAN_INTERVAL_SEC = float(_env("LIQ_SCAN_INTERVAL_SEC", "5.0"))

# Chainlink MATIC/USD on Polygon
CHAINLINK_MATIC_USD = Web3.to_checksum_address(
    _env("CHAINLINK_MATIC_USD", "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0")
)

# Streams/metrics/controls
REDIS_STREAM = _env("LIQ_REDIS_STREAM", "atom:opps:liquidations")
REDIS_MAXLEN = int(_env("LIQ_REDIS_MAXLEN", "2000"))
METRICS_PORT = int(_env("METRICS_PORT", "9111"))
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("LIQ_PAUSE_KEY", "atom:liq:paused")

# ---------------- Logging ----------------

log = logging.getLogger("atom.liquidations")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

# ---------------- Metrics ----------------

MET_DISCOVER_LAT = Histogram("atom_liq_discovery_latency_seconds", "Discovery latency")
MET_SCAN_LAT     = Histogram("atom_liq_scan_latency_seconds", "On-chain confirmation latency")
MET_ERRORS       = Counter("atom_liq_errors_total", "Errors")
MET_OPPS         = Counter("atom_liq_opportunities_total", "Opportunities published")
MET_BEST_NET     = Gauge("atom_liq_best_net_profit_usd", "Best net profit last publish")
MET_CANDIDATES   = Gauge("atom_liq_candidates", "Candidates per discovery")

# ---------------- Minimal ABIs ----------------

AAVE_POOL_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserAccountData","outputs":[{"internalType":"uint256","name":"totalCollateralBase","type":"uint256"},{"internalType":"uint256","name":"totalDebtBase","type":"uint256"},{"internalType":"uint256","name":"availableBorrowsBase","type":"uint256"},{"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},{"internalType":"uint256","name":"ltv","type":"uint256"},{"internalType":"uint256","name":"healthFactor","type":"uint256"}],"stateMutability":"view","type":"function"}]')
CL_AGG_ABI = json.loads('[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"}]')

# ---------------- Models ----------------

@dataclass
class LiqOpp:
    protocol: str
    user: str
    health_factor: float
    total_debt_usd: float
    close_factor_bps: int
    liquidation_bonus_bps: int
    repay_usd: float
    bonus_usd: float
    flash_fee_usd: float
    gas_cost_usd: float
    net_profit_usd: float
    ts: int

# ---------------- Scanner ----------------

class LiquidationScanner:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
        self.redis: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None

        self.aave_pool = self.w3.eth.contract(AAVE_V3_POOL_ADDR, abi=AAVE_POOL_ABI)
        self.chainlink_matic = self.w3.eth.contract(CHAINLINK_MATIC_USD, abi=CL_AGG_ABI)

        self.candidates: List[str] = []  # set of addresses detected by discovery
        self._ensure_chain()

    def _ensure_chain(self):
        cid = self.w3.eth.chain_id
        if cid != 137:
            raise RuntimeError(f"Not on Polygon mainnet (137). chain_id={cid}")

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        self.session = aiohttp.ClientSession()
        await self.discover_aave_candidates()

    async def close(self):
        try:
            if self.session:
                await self.session.close()
        finally:
            self.session = None

    # -------- Aave discovery via subgraph --------

    async def discover_aave_candidates(self):
        """Pull users with HF below threshold from subgraph; cheap prefilter."""
        if not AAVE_V3_SUBGRAPH_URL:
            self.candidates = []
            return
        users: List[str] = []
        skip = 0
        more = True
        t0 = time.perf_counter()
        try:
            assert self.session is not None
            while more:
                q = """
                query($first:Int!,$skip:Int!,$hf:String!){
                  users(first:$first, skip:$skip, where:{healthFactor_lt:$hf}) { id healthFactor }
                }"""
                payload = {"query": q, "variables": {"first": DISCOVERY_PAGE_SIZE, "skip": skip, "hf": AAVE_HF_QUERY_LT}}
                async with self.session.post(AAVE_V3_SUBGRAPH_URL, json=payload, timeout=20) as r:
                    data = await r.json()
                    arr = data.get("data", {}).get("users", []) or []
                    users.extend(u.get("id") for u in arr if u.get("id"))
                    more = len(arr) == DISCOVERY_PAGE_SIZE
                    skip += DISCOVERY_PAGE_SIZE
                    # be polite
                    await asyncio.sleep(0.25)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="aave_discovery_error", err=str(e))
        finally:
            dur = time.perf_counter() - t0
            MET_DISCOVER_LAT.observe(dur)

        # dedupe and cap
        users = list(dict.fromkeys(users))
        self.candidates = users
        MET_CANDIDATES.set(len(users))
        jlog("info", event="aave_discovery", candidates=len(users))

    # -------- Optional Compound v3 discovery (subgraph) --------

    async def discover_compound_candidates(self) -> List[str]:
        if not COMPOUND_V3_SUBGRAPH_URL:
            return []
        try:
            assert self.session is not None
            q = """{ accounts(first: 500, where:{ isLiquidatable: true }) { id } }"""
            async with self.session.post(COMPOUND_V3_SUBGRAPH_URL, json={"query": q}, timeout=20) as r:
                data = await r.json()
                return [a["id"] for a in data.get("data", {}).get("accounts", []) if a.get("id")]
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="compound_discovery_error", err=str(e))
            return []

    # -------- Chainlink price --------

    async def matic_usd(self) -> Decimal:
        try:
            rd = await asyncio.to_thread(self.chainlink_matic.functions.latestRoundData().call)
            return Decimal(rd[1]) / Decimal(10**8)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="chainlink_error", err=str(e))
            return Decimal("0")

    # -------- On-chain confirm + economics --------

    def _confirm_aave(self, user: str) -> Optional[LiqOpp]:
        """Confirm liquidation on-chain and compute economics."""
        try:
            data = self.aave_pool.functions.getUserAccountData(Web3.to_checksum_address(user)).call()
            total_debt_base = Decimal(data[1])          # base currency 1e8
            health_factor = Decimal(data[5]) / Decimal(10**18)
            if total_debt_base <= 0 or health_factor >= 1:
                return None

            # Convert base to USD (Aave v3 Polygon uses USD base 1e8)
            total_debt_usd = total_debt_base / Decimal(10**8)

            close_factor = Decimal(AAVE_CLOSE_FACTOR_BPS) / Decimal(10000)
            repay_usd = min(total_debt_usd * close_factor, LIQ_MAX_REPAY_USD)

            bonus_bps = Decimal(AAVE_LIQ_BONUS_BPS_DEFAULT)
            bonus_usd = repay_usd * (bonus_bps / Decimal(10000))

            # Costs
            gas_price = self.w3.eth.gas_price
            matic_price = asyncio.run(self.matic_usd())  # safe short call here
            gas_cost_usd = (Decimal(gas_price) * Decimal(GAS_LIMIT_ESTIMATE) / Decimal(1e18)) * matic_price
            flash_fee_usd = repay_usd * (AAVE_FLASH_FEE_BPS / Decimal(10000))

            net = bonus_usd - gas_cost_usd - flash_fee_usd
            if net < MIN_NET_PROFIT_USD:
                return None

            return LiqOpp(
                protocol="aave_v3",
                user=Web3.to_checksum_address(user),
                health_factor=float(health_factor),
                total_debt_usd=float(total_debt_usd),
                close_factor_bps=int(AAVE_CLOSE_FACTOR_BPS),
                liquidation_bonus_bps=int(bonus_bps),
                repay_usd=float(repay_usd),
                bonus_usd=float(bonus_usd),
                flash_fee_usd=float(flash_fee_usd),
                gas_cost_usd=float(gas_cost_usd),
                net_profit_usd=float(net),
                ts=int(time.time())
            )
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="aave_confirm_error", user=user, err=str(e))
            return None

    # -------- Publish --------

    async def publish(self, opps: List[LiqOpp]):
        if not self.redis:
            return
        for o in opps:
            payload = json.dumps(asdict(o), separators=(",", ":"))
            try:
                await self.redis.xadd(REDIS_STREAM, {"data": payload}, maxlen=REDIS_MAXLEN, approximate=True)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="redis_xadd_error", err=str(e))
        if opps:
            MET_OPPS.inc(len(opps))
            MET_BEST_NET.set(max(o.net_profit_usd for o in opps))
        else:
            MET_BEST_NET.set(0.0)

    async def paused(self) -> bool:
        try:
            if not self.redis:
                return False
            if await self.redis.get(KILL_SWITCH_KEY) == "1":
                return True
            if await self.redis.get(PAUSE_KEY) == "1":
                return True
        except Exception:
            pass
        return False

    # -------- Main loop --------

    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="liquidation_scanner_started",
             aave_subgraph=AAVE_V3_SUBGRAPH_URL, compound_subgraph=bool(COMPOUND_V3_SUBGRAPH_URL),
             min_net=float(MIN_NET_PROFIT_USD))

        # periodic discovery
        async def periodic_discovery():
            while True:
                try:
                    await self.discover_aave_candidates()
                    # compound optional enrichment (not required)
                    # comp = await self.discover_compound_candidates()
                    # self.candidates.extend(comp)
                    # self.candidates = list(dict.fromkeys(self.candidates))
                except Exception as e:
                    MET_ERRORS.inc()
                    jlog("error", event="periodic_discovery_error", err=str(e))
                await asyncio.sleep(DISCOVERY_INTERVAL_SEC)

        asyncio.create_task(periodic_discovery())

        while True:
            t0 = time.perf_counter()
            try:
                if await self.paused():
                    await asyncio.sleep(1.0)
                    continue

                # confirm on-chain for current candidates
                opps: List[LiqOpp] = []
                for user in self.candidates[:1000]:  # sanity cap
                    o = await asyncio.to_thread(self._confirm_aave, user)
                    if o:
                        opps.append(o)

                # publish
                await self.publish(opps)
                if opps:
                    jlog("info", event="opps", count=len(opps), best=asdict(sorted(opps, key=lambda x: x.net_profit_usd, reverse=True)[0]))
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="main_loop_error", err=str(e))
                await asyncio.sleep(1.0)

            dur = time.perf_counter() - t0
            MET_SCAN_LAT.observe(dur)
            await asyncio.sleep(max(0.0, SCAN_INTERVAL_SEC - dur))

if __name__ == "__main__":
    try:
        asyncio.run(LiquidationScanner().run())
    except KeyboardInterrupt:
        pass 