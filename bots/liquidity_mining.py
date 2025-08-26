# bots/liquidity_mining.py
"""
ATOM Liquidity Mining & Incentive Farming Scanner (Polygon)
- Scans QuickSwap/Sushi farms on Polygon for APR, TVL, and IL risk
- Computes reward APR from MasterChef rates and pool allocPoints
- Prices rewards and LP components in USDC via router getAmountsOut
- Publishes ranked opportunities to Redis stream 'atom:opps:liquidity'
- Exposes Prometheus metrics on METRICS_PORT
- Headless: NO signing, NO private keys, NO tx building
- Production features: env-driven config, chain guard, circuit breakers, JSON logs
"""

import os
import time
import json
import asyncio
import logging
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3, HTTPProvider

# ---------------- Env helpers ----------------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

# Chain & RPC
LM_CHAIN = _env("LM_CHAIN", "polygon").lower()
if LM_CHAIN != "polygon":
    raise RuntimeError("LM_CHAIN must be 'polygon' for this scanner")

POLYGON_RPC_URL = _env("POLYGON_RPC_URL", required=True)
CHAIN_ID_EXPECTED = int(_env("LM_CHAIN_ID", "137"))

# Redis & ops
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
REDIS_STREAM = _env("LM_REDIS_STREAM", "atom:opps:liquidity")
REDIS_MAXLEN = int(_env("LM_REDIS_MAXLEN", "1000"))
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("LM_PAUSE_KEY", "atom:lm:paused")
METRICS_PORT = int(_env("METRICS_PORT", "9115"))
SCAN_INTERVAL_SEC = float(_env("LM_SCAN_INTERVAL_SEC", "600"))  # every 10 min
MAX_POOLS = int(_env("LM_MAX_POOLS", "80"))  # scan first N pools per protocol

# Economics & filters
MIN_TVL_USD = Decimal(_env("LM_MIN_TVL_USD", "20000"))
MIN_TOTAL_APR = Decimal(_env("LM_MIN_TOTAL_APR", "5"))       # %
STABLE_TOKENS = set([s.strip().upper() for s in _env("LM_STABLE_TOKENS", "USDC,USDT,DAI,GUSD,FRAX,TUSD,USDC.E").split(",")])
SECONDS_PER_YEAR = Decimal("31536000")
POLYGON_BLOCKS_PER_YEAR = Decimal(_env("LM_BLOCKS_PER_YEAR", "15768000"))  # ~2s blocks

# Protocol addresses (env-overridable)
QS_MASTERCHEF = Web3.to_checksum_address(_env("QUICKSWAP_MASTERCHEF", "0x68678CF174695fc2D27bd312DF67A3984364FFDd"))
QS_REWARD_TOKEN = Web3.to_checksum_address(_env("QUICKSWAP_REWARD_TOKEN", "0xf28164A485B0B2C90639E47b0f377b4a438a16B1"))  # QUICK
QS_ROUTER = Web3.to_checksum_address(_env("QUICKSWAP_V2_ROUTER", "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"))

SUSHI_MINICHEF = Web3.to_checksum_address(_env("SUSHI_MINICHEF", "0x0769fd68dFb93167989C6f7254cd0D766Fb2841F"))
SUSHI_REWARD_TOKEN = Web3.to_checksum_address(_env("SUSHI_REWARD_TOKEN", "0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a"))  # SUSHI
SUSHI_ROUTER = Web3.to_checksum_address(_env("SUSHI_V2_ROUTER", "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"))

# Stablecoin for pricing
USDC = Web3.to_checksum_address(_env("USDC_POLYGON", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"))

# Which protocols to scan
LM_PROTOCOLS = [p.strip().lower() for p in _env("LM_PROTOCOLS", "quickswap,sushiswap").split(",") if p.strip()]

# ---------------- Minimal ABIs ----------------

# MasterChef/MiniChef: we dynamically probe method names across variants
MC_ABI = json.loads("""[
  {"name":"poolLength","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"totalAllocPoint","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"poolInfo","outputs":[{"type":"tuple","components":[{"name":"lpToken","type":"address"},{"name":"allocPoint","type":"uint256"},{"name":"lastRewardBlock","type":"uint256"},{"name":"accRewardPerShare","type":"uint256"}]}],"inputs":[{"name":"pid","type":"uint256"}],"stateMutability":"view","type":"function"},
  {"name":"lpToken","outputs":[{"type":"address"}],"inputs":[{"type":"uint256"}],"stateMutability":"view","type":"function"},
  {"name":"rewardPerBlock","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"rewardsPerBlock","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"rewardPerSecond","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"rewardsPerSecond","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"sushiPerSecond","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"quickPerBlock","outputs":[{"type":"uint256"}],"inputs":[],"stateMutability":"view","type":"function"}
]""")

PAIR_ABI = json.loads("""[
  {"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"token0","outputs":[{"type":"address"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"token1","outputs":[{"name":"","type":"address"}],"inputs":[],"stateMutability":"view","type":"function"}
]""")

# Minimal ERC20
ERC20_ABI = json.loads("""[
  {"name":"decimals","outputs":[{"type":"uint8"}],"inputs":[],"stateMutability":"view","type":"function"},
  {"name":"symbol","outputs":[{"type":"string"}],"inputs":[],"stateMutability":"view","type":"function"}
]""")

# UniswapV2 Router:getAmountsOut
ROUTER_ABI = json.loads("""[
  {"name":"getAmountsOut","outputs":[{"type":"uint256[]"}],"inputs":[{"name":"amountIn","type":"uint256"},{"name":"path","type":"address[]"}],"stateMutability":"view","type":"function"}
]""")

# ---------------- Logging & Metrics ----------------

log = logging.getLogger("atom.liquidity")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

MET_SCAN_LAT     = Histogram("atom_lm_scan_latency_seconds", "End-to-end scan latency")
MET_ERRORS       = Counter("atom_lm_errors_total", "Errors")
MET_OPPS         = Counter("atom_lm_opportunities_total", "Published opportunities")
MET_POOLS_SCANNED= Gauge("atom_lm_pools_scanned", "Pools scanned in last run")
MET_BEST_APR     = Gauge("atom_lm_best_total_apr", "Best total APR seen (percent)")
MET_LAST_TS      = Gauge("atom_lm_last_scan_ts", "Unix ts of last successful scan")

# ---------------- Data models ----------------

@dataclass
class FarmingOpportunity:
    protocol: str
    pool_pid: int
    lp_token: str
    token0: str
    token1: str
    symbol0: str
    symbol1: str
    tvl_usd: float
    reward_token: str
    reward_token_symbol: str
    reward_price_usd: float
    reward_apr: float
    fee_apr: float
    total_apr: float
    il_risk: float
    compound_hours: int
    ts: int

# ---------------- Scanner ----------------

class LiquidityMiningScanner:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(POLYGON_RPC_URL, request_kwargs={"timeout": 12}))
        cid = self.w3.eth.chain_id
        if cid != CHAIN_ID_EXPECTED:
            raise RuntimeError(f"Wrong network: expected chain_id {CHAIN_ID_EXPECTED}, got {cid}")

        self.redis: Optional[redis.Redis] = None

        # Contracts
        self.qs_mc = self.w3.eth.contract(QS_MASTERCHEF, abi=MC_ABI)
        self.sushi_mc = self.w3.eth.contract(SUSHI_MINICHEF, abi=MC_ABI)
        self.qs_router = self.w3.eth.contract(QS_ROUTER, abi=ROUTER_ABI)
        self.sushi_router = self.w3.eth.contract(SUSHI_ROUTER, abi=ROUTER_ABI)

        # Caches
        self.decimals: Dict[str, int] = {}
        self.symbols: Dict[str, str] = {}

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        jlog("info", event="lm_init", chain=LM_CHAIN, rpc=POLYGON_RPC_URL, protocols=LM_PROTOCOLS)

    # ----- utils -----

    def _erc20(self, addr: str):
        return self.w3.eth.contract(addr, abi=ERC20_ABI)

    def _pair(self, addr: str):
        return self.w3.eth.contract(addr, abi=PAIR_ABI)

    def _dec(self, token: str) -> int:
        if token in self.decimals:
            return self.decimals[token]
        try:
            d = self._erc20(token).functions.decimals().call()
            self.decimals[token] = int(d)
        except Exception:
            self.decimals[token] = 18
        return self.decimals[token]

    def _sym(self, token: str) -> str:
        if token in self.symbols:
            return self.symbols[token]
        try:
            s = self._erc20(token).functions.symbol().call()
            self.symbols[token] = str(s)
        except Exception:
            self.symbols[token] = token[:6]
        return self.symbols[token]

    def _get_reward_rate(self, mc) -> Tuple[Decimal, str]:
        """
        Return (perSecond, unit) where unit is "second" or "block".
        We probe a handful of common function names.
        """
        candidates = [
            ("rewardPerSecond", "second"),
            ("rewardsPerSecond", "second"),
            ("sushiPerSecond", "second"),
            ("rewardPerBlock", "block"),
            ("rewardsPerBlock", "block"),
            ("quickPerBlock", "block"),
        ]
        for fn, unit in candidates:
            try:
                v = getattr(mc.functions, fn)().call()
                if v and int(v) > 0:
                    return (Decimal(int(v)), unit)
            except Exception:
                continue
        return (Decimal(0), "second")

    def _get_pool_length(self, mc) -> int:
        try:
            return int(mc.functions.poolLength().call())
        except Exception:
            return 0

    def _get_total_alloc(self, mc) -> int:
        try:
            return int(mc.functions.totalAllocPoint().call())
        except Exception:
            return 0

    def _get_lp_for_pid(self, mc, pid: int) -> Optional[str]:
        # Prefer explicit lpToken(pid)
        try:
            a = mc.functions.lpToken(pid).call()
            if a and int(a, 16) != 0:
                return Web3.to_checksum_address(a)
        except Exception:
            pass
        # Fallback: poolInfo(pid).lpToken or first tuple element if address
        try:
            info = mc.functions.poolInfo(pid).call()
            if isinstance(info, (list, tuple)):
                for v in info:
                    if isinstance(v, str) and v.startswith("0x") and len(v) == 42:
                        return Web3.to_checksum_address(v)
            if isinstance(info, dict) and "lpToken" in info:
                return Web3.to_checksum_address(info["lpToken"])
        except Exception:
            pass
        return None

    def _get_alloc_for_pid(self, mc, pid: int) -> int:
        try:
            info = mc.functions.poolInfo(pid).call()
            if isinstance(info, dict) and "allocPoint" in info:
                return int(info["allocPoint"])
            if isinstance(info, (list, tuple)):
                # try to find int field
                for v in info:
                    if isinstance(v, int):
                        return int(v)
        except Exception:
            pass
        return 0

    def _price_token_in_usdc(self, router, token: str, amount_in_wei: int) -> Optional[Decimal]:
        try:
            if token.lower() == USDC.lower():
                return Decimal(amount_in_wei) / Decimal(10**6)
            path = [Web3.to_checksum_address(token), USDC]
            amts = router.functions.getAmountsOut(amount_in_wei, path).call()
            out = int(amts[-1])
            return Decimal(out) / Decimal(10**6)
        except Exception:
            return None

    def _pair_tvl_usd(self, router, lp_addr: str) -> Optional[Decimal]:
        try:
            pair = self._pair(lp_addr)
            t0 = Web3.to_checksum_address(pair.functions.token0().call())
            t1 = Web3.to_checksum_address(pair.functions.token1().call())
            r0, r1, _ = pair.functions.getReserves().call()
            d0 = self._dec(t0)
            d1 = self._dec(t1)
            # price 1 full token of each side
            p0 = self._price_token_in_usdc(router, t0, 10**d0)
            p1 = self._price_token_in_usdc(router, t1, 10**d1)
            if p0 is None or p1 is None:
                return None
            v0 = (Decimal(r0) / Decimal(10**d0)) * p0
            v1 = (Decimal(r1) / Decimal(10**d1)) * p1
            return v0 + v1
        except Exception:
            return None

    def _is_stable_pair(self, sym0: str, sym1: str) -> bool:
        return sym0.upper() in STABLE_TOKENS and sym1.upper() in STABLE_TOKENS

    def _fee_apr_heuristic(self, tvl_usd: Decimal) -> Decimal:
        # Conservative heuristic fee APR; you can override via LM_FEE_APR_BPS
        bps = Decimal(_env("LM_FEE_APR_BPS", "300"))  # 3% default
        return bps / Decimal(100)

    def _compound_hours(self, total_apr: Decimal) -> int:
        # Higher APR -> compound more often; capped range
        if total_apr >= 50:
            return 12
        if total_apr >= 20:
            return 24
        return 48

    # ----- protocol scans -----

    def _scan_masterchef(
        self,
        name: str,
        mc,
        router,
        reward_token: str
    ) -> List[FarmingOpportunity]:
        opps: List[FarmingOpportunity] = []
        try:
            plen = self._get_pool_length(mc)
            total_alloc = self._get_total_alloc(mc)
            if plen == 0 or total_alloc == 0:
                return opps

            reward_rate, unit = self._get_reward_rate(mc)
            if reward_rate <= 0:
                return opps

            # annual reward units (token/year)
            if unit == "second":
                annual_reward_total = reward_rate * SECONDS_PER_YEAR
            else:
                annual_reward_total = reward_rate * POLYGON_BLOCKS_PER_YEAR

            # reward price in USDC
            reward_dec = self._dec(reward_token)
            reward_price_1 = self._price_token_in_usdc(router, reward_token, 10**reward_dec)
            if reward_price_1 is None or reward_price_1 <= 0:
                return opps

            scanned = 0
            for pid in range(plen):
                if scanned >= MAX_POOLS:
                    break
                alloc = self._get_alloc_for_pid(mc, pid)
                if alloc <= 0:
                    continue
                lp = self._get_lp_for_pid(mc, pid)
                if not lp:
                    continue

                tvl = self._pair_tvl_usd(router, lp)
                if tvl is None or tvl < MIN_TVL_USD:
                    continue

                # LP pair tokens and symbols
                pair = self._pair(lp)
                t0 = Web3.to_checksum_address(pair.functions.token0().call())
                t1 = Web3.to_checksum_address(pair.functions.token1().call())
                s0 = self._sym(t0)
                s1 = self._sym(t1)

                # pool's share of rewards
                pool_annual_reward = (annual_reward_total * Decimal(alloc)) / Decimal(total_alloc)
                pool_annual_reward_usd = pool_annual_reward * reward_price_1

                reward_apr = (pool_annual_reward_usd / tvl) * Decimal(100)  # %
                fee_apr = self._fee_apr_heuristic(tvl)
                total_apr = reward_apr + fee_apr

                if total_apr < MIN_TOTAL_APR:
                    scanned += 1
                    continue

                il = 0.05 if self._is_stable_pair(s0, s1) else 0.20
                opps.append(FarmingOpportunity(
                    protocol=name,
                    pool_pid=pid,
                    lp_token=lp,
                    token0=t0,
                    token1=t1,
                    symbol0=s0,
                    symbol1=s1,
                    tvl_usd=float(tvl),
                    reward_token=reward_token,
                    reward_token_symbol=self._sym(reward_token),
                    reward_price_usd=float(reward_price_1),
                    reward_apr=float(reward_apr),
                    fee_apr=float(fee_apr),
                    total_apr=float(total_apr),
                    il_risk=float(il),
                    compound_hours=self._compound_hours(total_apr),
                    ts=int(time.time()),
                ))
                scanned += 1

        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="scan_masterchef_error", protocol=name, err=str(e))
        return opps

    def scan_quickswap(self) -> List[FarmingOpportunity]:
        return self._scan_masterchef("quickswap", self.qs_mc, self.qs_router, QS_REWARD_TOKEN) if "quickswap" in LM_PROTOCOLS else []

    def scan_sushiswap(self) -> List[FarmingOpportunity]:
        return self._scan_masterchef("sushiswap", self.sushi_mc, self.sushi_router, SUSHI_REWARD_TOKEN) if "sushiswap" in LM_PROTOCOLS else []

    # ----- publishing & control -----

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

    async def publish(self, opps: List[FarmingOpportunity]):
        if not self.redis:
            return
        # rank by total APR then TVL
        opps.sort(key=lambda o: (o.total_apr, o.tvl_usd), reverse=True)
        for o in opps:
            payload = json.dumps(asdict(o), separators=(",", ":"))
            try:
                await self.redis.xadd(REDIS_STREAM, {"data": payload}, maxlen=REDIS_MAXLEN, approximate=True)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="redis_xadd_error", err=str(e))
        MET_OPPS.inc(len(opps))
        if opps:
            MET_BEST_APR.set(opps[0].total_apr)

    async def run_once(self):
        t0 = time.perf_counter()
        try:
            if await self.paused():
                await asyncio.sleep(1.0)
                return
            all_opps: List[FarmingOpportunity] = []
            if "quickswap" in LM_PROTOCOLS:
                all_opps.extend(self.scan_quickswap())
            if "sushiswap" in LM_PROTOCOLS:
                all_opps.extend(self.scan_sushiswap())

            MET_POOLS_SCANNED.set(len(all_opps))
            await self.publish(all_opps)
            MET_LAST_TS.set(int(time.time()))
            if all_opps:
                jlog("info", event="lm_opps", count=len(all_opps), best=asdict(sorted(all_opps, key=lambda x: (x.total_apr, x.tvl_usd), reverse=True)[0]))
            else:
                jlog("info", event="lm_opps", count=0)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="run_once_error", err=str(e))
        finally:
            MET_SCAN_LAT.observe(time.perf_counter() - t0)

    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="lm_started", protocols=LM_PROTOCOLS, min_tvl=float(MIN_TVL_USD), min_apr=float(MIN_TOTAL_APR))
        while True:
            await self.run_once()
            await asyncio.sleep(SCAN_INTERVAL_SEC)

# Entrypoint
if __name__ == "__main__":
    try:
        asyncio.run(LiquidityMiningScanner().run())
    except KeyboardInterrupt:
        pass 