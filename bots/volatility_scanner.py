# bots/volatility_scanner.py
"""
ATOM Volatility Scanner (Polygon mainnet)
- Tracks top volatile tokens from DEX subgraphs
- Builds minute-level price/volume history
- Detects pumps/dumps/oscillations using returns, stddev and volume spikes
- Publishes signals to Redis Stream 'atom:opps:volatility'
- Prometheus metrics on METRICS_PORT
- Strict: no secrets in code, no tx signing, no websockets required
- Hard fail if not on chain_id=137 (Polygon)
"""

import os
import asyncio
import json
import time
import logging
from collections import deque
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import aiohttp
import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3, HTTPProvider

# ---------- Env & Constants ----------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

# RPC/Redis
RPC_URL = _env("POLYGON_RPC_URL", required=True)
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")

# Subgraphs (require explicit config; defaults are safe to change at runtime)
QS_SUBGRAPH_URL = _env("QS_SUBGRAPH_URL", "https://api.thegraph.com/subgraphs/name/sameepsi/quickswap06")
SU_SUBGRAPH_URL = _env("SU_SUBGRAPH_URL", "https://api.thegraph.com/subgraphs/name/sushiswap/matic-exchange")

# Operational tuning
SCAN_INTERVAL_SEC = float(_env("VOL_SCAN_INTERVAL_SEC", "5.0"))
DISCOVERY_INTERVAL_SEC = float(_env("VOL_DISCOVERY_INTERVAL_SEC", "600"))
PRICE_WINDOW = int(_env("VOL_PRICE_WINDOW", "120"))  # minutes kept in memory
TOP_PAIRS = int(_env("VOL_TOP_PAIRS", "100"))        # pull top pairs by volume from subgraphs

# Detection thresholds
VOL_RET_STD_THRESHOLD = float(_env("VOL_RET_STD_THRESHOLD", "0.10"))  # stddev of 1m returns threshold
PUMP_5M_CHANGE = float(_env("VOL_PUMP_5M_CHANGE", "0.08"))            # +8% in 5m
DUMP_5M_CHANGE = float(_env("VOL_DUMP_5M_CHANGE", "-0.06"))           # -6% in 5m
VOL_SPIKE_MULTIPLE = float(_env("VOL_VOLUME_SPIKE_MULTIPLE", "3.0"))   # recent vs baseline
CONF_THRESHOLD = float(_env("VOL_CONF_THRESHOLD", "0.6"))

# Economic params
TRADE_SIZE_USD = Decimal(_env("VOL_TRADE_SIZE_USD", "25000"))
AAVE_FEE_BPS = Decimal(_env("AAVE_FLASH_FEE_BPS", "9"))  # 0.09%

# Metrics / Streams
METRICS_PORT = int(_env("METRICS_PORT", "9110"))
REDIS_STREAM = _env("VOL_REDIS_STREAM", "atom:opps:volatility")
REDIS_MAXLEN = int(_env("VOL_REDIS_MAXLEN", "1000"))

# Kill/pause keys
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("VOL_PAUSE_KEY", "atom:vol:paused")

# Chainlink MATIC/USD (Polygon mainnet)
CHAINLINK_MATIC_USD = Web3.to_checksum_address(_env(
    "CHAINLINK_MATIC_USD",
    "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0"
))

# DEX factories and USDC on Polygon
USDC = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
QS_FACTORY = Web3.to_checksum_address("0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32")
SU_FACTORY = Web3.to_checksum_address("0xc35DADB65012eC5796536bD9864eD8773aBc74C4")

PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"name":"","type":"address"}],"type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"name":"","type":"address"}],"type":"function"}]')
FACTORY_ABI = json.loads('[{"constant":true,"inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"name":"pair","type":"address"}],"type":"function"}]')
CL_AGG_ABI = json.loads('[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"}]')

# ---------- Logging ----------

log = logging.getLogger("atom.volatility")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

# ---------- Metrics ----------

MET_SCAN_LAT = Histogram("atom_vol_scan_latency_seconds", "Full scan latency")
MET_ERRORS   = Counter("atom_vol_errors_total", "Errors")
MET_SIGNALS  = Counter("atom_vol_signals_total", "Signals published")
MET_BEST_CONF= Gauge("atom_vol_best_confidence", "Best confidence last scan")
MET_BEST_PNL = Gauge("atom_vol_best_net_profit_usd", "Best net profit estimate last scan")

# ---------- Models ----------

@dataclass
class VolSignal:
    token: str
    symbol: str
    source_dex: str
    price_usd: float
    ret_5m: float
    ret_15m: float
    vol_std: float
    vol_spike: float
    pattern: str  # pump | dump | oscillating | neutral
    confidence: float
    gas_cost_usd: float
    flash_fee_usd: float
    net_profit_usd: float
    amount_usd: float
    ts: int

# ---------- Scanner ----------

class VolatilityScanner:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
        self.redis: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.factories = {
            "quickswap": self.w3.eth.contract(QS_FACTORY, abi=FACTORY_ABI),
            "sushiswap": self.w3.eth.contract(SU_FACTORY, abi=FACTORY_ABI),
        }
        self.matic_usd = self.w3.eth.contract(CHAINLINK_MATIC_USD, abi=CL_AGG_ABI)

        # token_addr -> symbol, pair cache per dex
        self.tracked_tokens: Dict[str, Dict] = {}
        self.pairs: Dict[str, Dict[str, str]] = {"quickswap": {}, "sushiswap": {}}
        self.price_history: Dict[str, deque] = {}   # token -> deque[(ts, price_usd)]
        self.volume_history: Dict[str, deque] = {}  # token -> deque[(ts, volume_24h_usd)]

        self._ensure_chain()

    def _ensure_chain(self):
        cid = self.w3.eth.chain_id
        if cid != 137:
            raise RuntimeError(f"Not on Polygon mainnet (137). chain_id={cid}")

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        self.session = aiohttp.ClientSession()
        await self.discover_tokens()
        await self.build_pairs_cache()
        jlog("info", event="init", tokens=len(self.tracked_tokens), rpc=RPC_URL, redis=REDIS_URL)

    async def close(self):
        try:
            if self.session:
                await self.session.close()
        finally:
            self.session = None

    # ---------- Discovery ----------

    async def _fetch_top_pairs(self, url: str, first: int) -> List[Dict]:
        q = """
        query($first:Int!){
          pairs(first: $first, orderBy: volumeUSD, orderDirection: desc){
            id
            token0{ id symbol name }
            token1{ id symbol name }
            volumeUSD
            txCount
          }
        }"""
        try:
            assert self.session is not None
            async with self.session.post(url, json={"query": q, "variables": {"first": first}}, timeout=20) as r:
                data = await r.json()
                return data.get("data", {}).get("pairs", []) or []
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="subgraph_error", url=url, err=str(e))
            return []

    @staticmethod
    def _is_stable_or_base(sym: str) -> bool:
        s = (sym or "").upper()
        return s in {"USDC", "USDT", "DAI", "WETH", "WMATIC", "WBTC"}

    async def discover_tokens(self):
        """Pull top pairs from both QS and SU, collect non-stable token addresses."""
        qs = await self._fetch_top_pairs(QS_SUBGRAPH_URL, TOP_PAIRS)
        su = await self._fetch_top_pairs(SU_SUBGRAPH_URL, TOP_PAIRS)
        seen = {}
        for pair in qs + su:
            for side in ("token0", "token1"):
                tok = pair[side]
                sym = tok.get("symbol", "")
                if self._is_stable_or_base(sym):
                    continue
                addr = Web3.to_checksum_address(tok["id"])
                seen.setdefault(addr, {"symbol": sym or "UNK", "name": tok.get("name") or "UNK"})
        self.tracked_tokens = seen
        # init deques
        for addr in self.tracked_tokens:
            self.price_history.setdefault(addr, deque(maxlen=PRICE_WINDOW))
            self.volume_history.setdefault(addr, deque(maxlen=PRICE_WINDOW))

        await self._persist_discovery()

    async def _persist_discovery(self):
        try:
            if self.redis:
                await self.redis.set("atom:vol:tokens", json.dumps(self.tracked_tokens))
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="redis_set_error", key="atom:vol:tokens", err=str(e))

    async def build_pairs_cache(self):
        """Cache token/USDC pair addresses for both dexes."""
        async def get_pair(dex: str, token: str) -> Optional[str]:
            try:
                fa = self.factories[dex]
                pair_addr = await asyncio.to_thread(fa.functions.getPair(token, USDC).call)
                if pair_addr and int(pair_addr, 16) != 0:
                    self.pairs[dex][token] = Web3.to_checksum_address(pair_addr)
                    return self.pairs[dex][token]
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="getPair_error", dex=dex, token=token, err=str(e))
            return None

        tasks = []
        for token in self.tracked_tokens.keys():
            tasks += [get_pair("quickswap", token), get_pair("sushiswap", token)]
        await asyncio.gather(*tasks)

        try:
            if self.redis:
                await self.redis.set("atom:vol:pairs", json.dumps(self.pairs))
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="redis_set_error", key="atom:vol:pairs", err=str(e))

    # ---------- Price/Volume ----------

    def _price_from_reserves(self, pair_addr: str, token: str) -> Optional[Decimal]:
        try:
            pair = self.w3.eth.contract(pair_addr, abi=PAIR_ABI)
            t0 = Web3.to_checksum_address(pair.functions.token0().call())
            t1 = Web3.to_checksum_address(pair.functions.token1().call())
            r0, r1, _ = pair.functions.getReserves().call()
            # USDC has 6 decimals
            if t0 == token and t1 == USDC and r0 > 0:
                return Decimal(r1) / Decimal(10**6) / (Decimal(r0) / Decimal(10**18))
            if t0 == USDC and t1 == token and r1 > 0:
                return (Decimal(r0) / Decimal(10**6)) / (Decimal(r1) / Decimal(10**18))
            return None
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="price_reserve_error", pair=pair_addr, token=token, err=str(e))
            return None

    async def _price_token_usd(self, token: str) -> Optional[Decimal]:
        """Try QS first then SU for token/USDc spot via reserves."""
        for dex in ("quickswap", "sushiswap"):
            pair = self.pairs[dex].get(token)
            if not pair:
                continue
            p = await asyncio.to_thread(self._price_from_reserves, pair, token)
            if p and p > 0:
                return p
        return None

    async def _token_volume_24h(self, url: str, token: str) -> Optional[Decimal]:
        q = f'{{ token(id: "{token.lower()}") {{ volumeUSD }} }}'
        try:
            assert self.session is not None
            async with self.session.post(url, json={"query": q}, timeout=20) as r:
                data = await r.json()
                v = data.get("data", {}).get("token", {}).get("volumeUSD")
                return Decimal(v) if v is not None else None
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="subgraph_token_error", url=url, token=token, err=str(e))
            return None

    async def _matic_usd_price(self) -> Decimal:
        try:
            roundData = await asyncio.to_thread(self.matic_usd.functions.latestRoundData().call)
            return Decimal(roundData[1]) / Decimal(10**8)  # 8 decimals
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="chainlink_error", err=str(e))
            return Decimal("0")

    async def update_feeds(self):
        """Minute-level price/volume updates."""
        while True:
            try:
                for token in self.tracked_tokens.keys():
                    price = await self._price_token_usd(token)
                    if price:
                        self.price_history[token].append((int(time.time()), float(price)))
                    # alternate subgraph sources to reduce load
                    vol = await self._token_volume_24h(QS_SUBGRAPH_URL, token)
                    if vol is None:
                        vol = await self._token_volume_24h(SU_SUBGRAPH_URL, token)
                    if vol is not None:
                        self.volume_history[token].append((int(time.time()), float(vol)))
                await asyncio.sleep(60)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="update_feeds_error", err=str(e))
                await asyncio.sleep(60)

    # ---------- Detection ----------

    @staticmethod
    def _returns(series: List[float]) -> List[float]:
        out = []
        for i in range(1, len(series)):
            a, b = series[i-1], series[i]
            if a > 0:
                out.append((b - a) / a)
        return out

    def _vol_std(self, prices: List[float]) -> float:
        rets = self._returns(prices[-30:])  # last ~30 minutes
        if not rets:
            return 0.0
        # simple stddev
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / len(rets)
        return var ** 0.5

    def _change(self, prices: List[float], wnd: int) -> float:
        if len(prices) < wnd + 1:
            return 0.0
        a = prices[-wnd-1]
        b = prices[-1]
        return (b - a) / a if a > 0 else 0.0

    def _vol_spike(self, vols: List[float]) -> float:
        if len(vols) < 20:
            return 1.0
        recent = sum(vols[-5:]) / 5.0
        base = sum(vols[-20:-5]) / 15.0 if sum(vols[-20:-5]) > 0 else 0.0
        if base <= 0.0:
            return 1.0
        return recent / base

    async def detect(self) -> List[VolSignal]:
        signals: List[VolSignal] = []
        matic_usd = await self._matic_usd_price()
        gas_price = self.w3.eth.gas_price
        # assume 450k budget for a quick two-hop execution
        gas_cost_usd = (Decimal(gas_price) * Decimal(450000) / Decimal(1e18)) * matic_usd
        flash_fee_usd = TRADE_SIZE_USD * (AAVE_FEE_BPS / Decimal(10000))

        for token, meta in self.tracked_tokens.items():
            ph = [p for _, p in self.price_history.get(token, [])]
            vh = [v for _, v in self.volume_history.get(token, [])]
            if len(ph) < 20:
                continue

            ret5 = self._change(ph, 5)
            ret15 = self._change(ph, 15)
            vstd = self._vol_std(ph)
            vspike = self._vol_spike(vh)

            pattern = "neutral"
            if ret5 >= PUMP_5M_CHANGE and vspike >= VOL_SPIKE_MULTIPLE:
                pattern = "pump"
            elif ret5 <= DUMP_5M_CHANGE and vspike >= 2.0:
                pattern = "dump"
            elif abs(ret5) >= 0.04 and vstd >= VOL_RET_STD_THRESHOLD:
                pattern = "oscillating"

            if pattern == "neutral" and vstd < VOL_RET_STD_THRESHOLD:
                continue

            conf = min(0.95, max(0.0, (abs(ret5) * 4) + (vstd * 2) + (max(0.0, vspike - 1) * 0.1)))
            if conf < CONF_THRESHOLD:
                continue

            price = Decimal(str(ph[-1]))
            # crude expected pnl from a 1-leg move size
            gross = TRADE_SIZE_USD * Decimal(abs(ret5))
            net = gross - gas_cost_usd - flash_fee_usd

            sig = VolSignal(
                token=token,
                symbol=meta["symbol"],
                source_dex="quickswap" if token in self.pairs["quickswap"] else "sushiswap" if token in self.pairs["sushiswap"] else "unknown",
                price_usd=float(price),
                ret_5m=float(ret5),
                ret_15m=float(ret15),
                vol_std=float(vstd),
                vol_spike=float(vspike),
                pattern=pattern,
                confidence=float(conf),
                gas_cost_usd=float(gas_cost_usd),
                flash_fee_usd=float(flash_fee_usd),
                net_profit_usd=float(net),
                amount_usd=float(TRADE_SIZE_USD),
                ts=int(time.time()),
            )
            signals.append(sig)

        # best first
        signals.sort(key=lambda s: s.confidence * max(0.0, s.net_profit_usd), reverse=True)
        return signals

    async def publish(self, signals: List[VolSignal]):
        if not self.redis:
            return
        for s in signals:
            payload = json.dumps(asdict(s), separators=(",", ":"))
            try:
                await self.redis.xadd(REDIS_STREAM, {"data": payload}, maxlen=REDIS_MAXLEN, approximate=True)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="redis_xadd_error", err=str(e))
        if signals:
            MET_SIGNALS.inc(len(signals))
            MET_BEST_CONF.set(signals[0].confidence)
            MET_BEST_PNL.set(max(0.0, signals[0].net_profit_usd))
        else:
            MET_BEST_CONF.set(0.0)
            MET_BEST_PNL.set(0.0)

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

    # ---------- Main loop ----------

    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="volatility_scanner_started",
             interval=SCAN_INTERVAL_SEC, top_pairs=TOP_PAIRS,
             thresholds=dict(std=VOL_RET_STD_THRESHOLD, pump=PUMP_5M_CHANGE, dump=DUMP_5M_CHANGE))

        # background updaters
        asyncio.create_task(self.update_feeds())

        # periodic rediscovery
        async def periodic_discovery():
            while True:
                try:
                    await self.discover_tokens()
                    await self.build_pairs_cache()
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
                signals = await self.detect()
                await self.publish(signals)
                if signals:
                    jlog("info", event="signals", count=len(signals), best=asdict(signals[0]))
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="main_loop_error", err=str(e))
                await asyncio.sleep(1.0)
            dur = time.perf_counter() - t0
            MET_SCAN_LAT.observe(dur)
            await asyncio.sleep(max(0.0, SCAN_INTERVAL_SEC - dur))

if __name__ == "__main__":
    try:
        asyncio.run(VolatilityScanner().run())
    except KeyboardInterrupt:
        pass 