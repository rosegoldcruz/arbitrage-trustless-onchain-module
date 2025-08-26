# bots/stablecoin_monitor.py
"""
ATOM Stablecoin Peg Monitor (Polygon mainnet)
- Scans Quickswap/Sushiswap stable-stable pools for depegs
- Publishes opportunities to Redis Stream 'atom:opps:stablecoin'
- Exposes Prometheus metrics on METRICS_PORT
- Strict: no secrets in code, no tx signing, no websockets required
- Hard fail if not on chain_id=137 (Polygon)
"""

import os
import asyncio
import json
import time
import logging
import math
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3, HTTPProvider

# ---------- Config ----------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    val = os.getenv(name, default)
    if required and (val is None or str(val).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return str(val) if val is not None else ""

RPC_URL = _env("POLYGON_RPC_URL", required=True)
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
SCAN_INTERVAL_SEC = float(_env("STABLESCAN_INTERVAL_SEC", "1.0"))
MAX_WORKERS = int(_env("STABLESCAN_MAX_WORKERS", "16"))
SPREAD_BPS_THRESHOLD = int(_env("STABLESCAN_SPREAD_BPS", "35"))  # 0.35%
MIN_PROFIT_USD = Decimal(_env("STABLESCAN_MIN_PROFIT_USD", "100"))
TRADE_SIZE_USD = Decimal(_env("STABLESCAN_TRADE_SIZE_USD", "25000"))
AAVE_FEE_BPS = Decimal(_env("AAVE_FLASH_FEE_BPS", "9"))  # 0.09%
GAS_LIMIT_ARB = int(_env("STABLESCAN_GAS_LIMIT", "400000"))
METRICS_PORT = int(_env("METRICS_PORT", "9109"))
REDIS_STREAM = _env("STABLESCAN_REDIS_STREAM", "atom:opps:stablecoin")
REDIS_MAXLEN = int(_env("STABLESCAN_REDIS_MAXLEN", "1000"))
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("STABLESCAN_PAUSE_KEY", "atom:stablecoin:paused")

# Chainlink MATIC/USD aggregator on Polygon
CHAINLINK_MATIC_USD = Web3.to_checksum_address(
    _env("CHAINLINK_MATIC_USD", "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0")
)

# DEX factories/routers (Polygon mainnet)
QS_FACTORY = Web3.to_checksum_address("0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32")
QS_ROUTER  = Web3.to_checksum_address("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff")
SU_FACTORY = Web3.to_checksum_address("0xc35DADB65012eC5796536bD9864eD8773aBc74C4")
SU_ROUTER  = Web3.to_checksum_address("0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506")

DEXES = {
    "quickswap": {"factory": QS_FACTORY, "router": QS_ROUTER},
    "sushiswap": {"factory": SU_FACTORY, "router": SU_ROUTER},
}

# Stablecoins (Polygon) with decimals
STABLES = {
    "USDC": {"addr": Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"), "dec": 6},
    "USDT": {"addr": Web3.to_checksum_address("0xc2132D05D31c914a87C6611C10748AEb04B58e8F"), "dec": 6},
    "DAI":  {"addr": Web3.to_checksum_address("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063"), "dec": 18},
    "FRAX": {"addr": Web3.to_checksum_address("0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89"), "dec": 18},
    "TUSD": {"addr": Web3.to_checksum_address("0x2e1AD108fF1fB6C94968b8B5EC3B9aD83c2fa9E9"), "dec": 18},
    "BUSD": {"addr": Web3.to_checksum_address("0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39"), "dec": 18},
    "MAI":  {"addr": Web3.to_checksum_address("0xa3Fa99A148fA48D14Ed51d610c367C61876997F1"), "dec": 18},
}

PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"name":"","type":"address"}],"type":"function"}]')
FACTORY_ABI = json.loads('[{"constant":true,"inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"name":"pair","type":"address"}],"type":"function"}]')
CL_AGG_ABI = json.loads('[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"}]')

# ---------- Logging ----------

log = logging.getLogger("atom.stables")
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(_handler)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    msg = json.dumps(kw, separators=(",", ":"))
    getattr(log, level.lower())(msg)

# ---------- Metrics ----------

MET_SCAN_LAT = Histogram("atom_stables_scan_latency_seconds", "Full scan latency")
MET_ERRORS   = Counter("atom_stables_errors_total", "Errors")
MET_OPPS     = Counter("atom_stables_opportunities_total", "Detected opportunities")
MET_BEST_NET = Gauge("atom_stables_best_net_profit_usd", "Best net profit (USD) last scan")
MET_SPREAD   = Gauge("atom_stables_best_spread_bps", "Best spread bps last scan")

# ---------- Data Models ----------

@dataclass
class Opportunity:
    token_a: str
    token_b: str
    dex_buy: str
    dex_sell: str
    price_buy: float
    price_sell: float
    spread_bps: int
    gross_profit_usd: float
    gas_cost_usd: float
    flash_fee_usd: float
    net_profit_usd: float
    amount_usd: float
    ts: int

# ---------- Monitor ----------

class StablecoinPegMonitor:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
        self.redis: Optional[redis.Redis] = None
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.factories = {name: self.w3.eth.contract(addr["factory"], abi=FACTORY_ABI) for name, addr in DEXES.items()}
        self.matic_usd = self.w3.eth.contract(CHAINLINK_MATIC_USD, abi=CL_AGG_ABI)
        self.pairs: Dict[str, Dict[str, Dict[str, str]]] = {}  # pairs[dex][key] -> {pair, t0, t1}
        self._ensure_chain()

    def _ensure_chain(self):
        chain_id = self.w3.eth.chain_id
        if chain_id != 137:
            raise RuntimeError(f"Not on Polygon mainnet (137). chain_id={chain_id}")

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await self.discover_pairs()
        jlog("info", event="init", pairs=sum(len(x) for x in self.pairs.values()), rpc=RPC_URL, redis=REDIS_URL)

    async def discover_pairs(self):
        # build stable pairs like (USDC,USDT), (USDC,DAI), ...
        tokens = list(STABLES.keys())
        combos: List[Tuple[str, str]] = []
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                combos.append((tokens[i], tokens[j]))

        self.pairs = {dex: {} for dex in DEXES.keys()}

        async def get_one(dex: str, a: str, b: str):
            fa = self.factories[dex]
            a_addr = STABLES[a]["addr"]
            b_addr = STABLES[b]["addr"]
            try:
                pair_addr = await asyncio.to_thread(fa.functions.getPair(a_addr, b_addr).call)
                if pair_addr and int(pair_addr, 16) != 0:
                    # confirm token order to compute price correctly
                    pair = self.w3.eth.contract(pair_addr, abi=PAIR_ABI)
                    t0 = await asyncio.to_thread(pair.functions.token0().call)
                    t1 = await asyncio.to_thread(pair.functions.token1().call)
                    key = f"{a}-{b}"
                    self.pairs[dex][key] = {"pair": pair_addr, "t0": t0, "t1": t1}
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="discover_error", dex=dex, a=a, b=b, err=str(e))

        tasks = []
        for dex in DEXES.keys():
            for a, b in combos:
                tasks.append(get_one(dex, a, b))
        await asyncio.gather(*tasks)

        # persist to Redis for other services
        if self.redis:
            await self.redis.set("atom:stablecoin:pairs", json.dumps(self.pairs))

    @staticmethod
    def _adj(reserve: int, decimals: int) -> Decimal:
        return Decimal(reserve) / Decimal(10 ** decimals)

    async def _pair_price(self, dex: str, pair_info: Dict, a: str, b: str) -> Optional[Decimal]:
        """Price as token_b per token_a (i.e., how many b for 1 a)"""
        try:
            pair = self.w3.eth.contract(pair_info["pair"], abi=PAIR_ABI)
            reserves = await asyncio.to_thread(pair.functions.getReserves().call)
            # map token0/token1 to a/b order
            t0 = pair_info["t0"]
            t1 = pair_info["t1"]
            a_addr = STABLES[a]["addr"]
            b_addr = STABLES[b]["addr"]
            dec_a = STABLES[a]["dec"]
            dec_b = STABLES[b]["dec"]
            if Web3.to_checksum_address(t0) == a_addr and Web3.to_checksum_address(t1) == b_addr:
                r0 = self._adj(reserves[0], dec_a)
                r1 = self._adj(reserves[1], dec_b)
                if r0 > 0:
                    return r1 / r0
            elif Web3.to_checksum_address(t0) == b_addr and Web3.to_checksum_address(t1) == a_addr:
                r0 = self._adj(reserves[0], dec_b)
                r1 = self._adj(reserves[1], dec_a)
                if r1 > 0:
                    return r0 / r1
            return None
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="price_error", dex=dex, pair=pair_info.get("pair"), err=str(e))
            return None

    async def scan_prices(self) -> Dict[str, Dict[str, Decimal]]:
        """Returns prices[dex][a-b] = price_b_per_a"""
        out: Dict[str, Dict[str, Decimal]] = {dex: {}} for dex in DEXES.keys()
        tasks = []
        for dex, m in self.pairs.items():
            for key, info in m.items():
                a, b = key.split("-")
                tasks.append(self._fill_price(out, dex, key, info, a, b))
        await asyncio.gather(*tasks)
        return out

    async def _fill_price(self, out, dex, key, info, a, b):
        p = await self._pair_price(dex, info, a, b)
        if p is not None:
            out[dex][key] = p

    async def _matic_usd_price(self) -> Decimal:
        try:
            roundData = await asyncio.to_thread(self.matic_usd.functions.latestRoundData().call)
            # Chainlink price with 8 decimals
            return Decimal(roundData[1]) / Decimal(10 ** 8)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="chainlink_error", err=str(e))
            return Decimal("0")

    async def detect_opps(self, prices: Dict[str, Dict[str, Decimal]]) -> List[Opportunity]:
        opps: List[Opportunity] = []
        tokens = list(STABLES.keys())
        matic_usd = await self._matic_usd_price()
        gas_price_wei = self.w3.eth.gas_price
        gas_cost_usd = (Decimal(gas_price_wei) * GAS_LIMIT_ARB / Decimal(1e18)) * matic_usd
        flash_fee_usd = TRADE_SIZE_USD * (AAVE_FEE_BPS / Decimal(10000))

        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                a, b = tokens[i], tokens[j]
                key = f"{a}-{b}"
                # collect available dex quotes
                dex_quotes: List[Tuple[str, Decimal]] = []
                for dex in DEXES.keys():
                    p = prices.get(dex, {}).get(key)
                    if p is not None and p > 0:
                        dex_quotes.append((dex, p))

                # need at least two dex quotes
                for i1 in range(len(dex_quotes)):
                    for i2 in range(i1 + 1, len(dex_quotes)):
                        (dex_a, pa) = dex_quotes[i1]
                        (dex_b, pb) = dex_quotes[i2]
                        # two directions: buy on lower, sell on higher
                        for buy_dex, sell_dex, buy_p, sell_p in [
                            (dex_a, dex_b, pa, pb),
                            (dex_b, dex_a, pb, pa),
                        ]:
                            spread = abs(sell_p - buy_p)
                            avg = (sell_p + buy_p) / 2
                            spread_bps = int((spread / avg) * 10000)
                            if spread_bps < SPREAD_BPS_THRESHOLD:
                                continue

                            gross = TRADE_SIZE_USD * (spread / avg)
                            net = gross - gas_cost_usd - flash_fee_usd
                            if net >= MIN_PROFIT_USD:
                                opps.append(
                                    Opportunity(
                                        token_a=a,
                                        token_b=b,
                                        dex_buy=buy_dex,
                                        dex_sell=sell_dex,
                                        price_buy=float(buy_p),
                                        price_sell=float(sell_p),
                                        spread_bps=spread_bps,
                                        gross_profit_usd=float(gross),
                                        gas_cost_usd=float(gas_cost_usd),
                                        flash_fee_usd=float(flash_fee_usd),
                                        net_profit_usd=float(net),
                                        amount_usd=float(TRADE_SIZE_USD),
                                        ts=int(time.time()),
                                    )
                                )

        opps.sort(key=lambda o: o.net_profit_usd, reverse=True)
        return opps

    async def publish(self, opps: List[Opportunity]):
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
            MET_BEST_NET.set(opps[0].net_profit_usd)
            MET_SPREAD.set(opps[0].spread_bps)

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

    async def run(self):
        # metrics
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="stablecoin_monitor_started", interval=SCAN_INTERVAL_SEC, spread_bps=SPREAD_BPS_THRESHOLD)

        while True:
            t0 = time.perf_counter()
            try:
                if await self.paused():
                    await asyncio.sleep(1.0)
                    continue

                prices = await self.scan_prices()
                opps = await self.detect_opps(prices)
                await self.publish(opps)

                if opps:
                    jlog("info", event="opps", count=len(opps), best=asdict(opps[0]))
                else:
                    MET_BEST_NET.set(0.0)
                    MET_SPREAD.set(0)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="main_loop_error", err=str(e))
                await asyncio.sleep(1.0)

            dur = time.perf_counter() - t0
            MET_SCAN_LAT.observe(dur)
            # keep loop pacing stable
            sleep_left = max(0.0, SCAN_INTERVAL_SEC - dur)
            await asyncio.sleep(sleep_left)


if __name__ == "__main__":
    asyncio.run(StablecoinPegMonitor().run()) 