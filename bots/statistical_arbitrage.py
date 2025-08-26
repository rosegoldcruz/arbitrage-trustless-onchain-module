# bots/statistical_arbitrage.py
"""
ATOM Statistical Arbitrage Scanner (Polygon/Ethereum)
- Asynchronous data fetch from DEX subgraphs to build token price histories
- Three signal engines:
  1) Mean reversion (z-score)
  2) Pairs spread deviations (ratio z-score)
  3) ML short-horizon return prediction (RandomForest)
- Publishes ranked signals to Redis stream 'atom:opps:stat_arb'
- Exposes Prometheus metrics; JSON structured logs; circuit breakers
- Headless: NO signing, NO tx building, NO secrets in code
"""

import os
import asyncio
import time
import json
import logging
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from collections import deque

import aiohttp
import numpy as np

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from web3 import AsyncWeb3, AsyncHTTPProvider

# Optional ML
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

# ----------------------- ENV -----------------------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

CHAIN = _env("STAT_ARB_CHAIN", "polygon").lower()  # polygon | ethereum
if CHAIN not in ("polygon", "ethereum"):
    raise RuntimeError("STAT_ARB_CHAIN must be 'polygon' or 'ethereum'")

RPC_URL = _env("POLYGON_RPC_URL" if CHAIN == "polygon" else "ETHEREUM_RPC_URL", required=True)
CHAIN_ID_EXPECTED = 137 if CHAIN == "polygon" else 1

# Subgraph endpoints (override in env if desired)
SUBGRAPH_URL = _env(
    "STAT_ARB_SUBGRAPH",
    "https://api.thegraph.com/subgraphs/name/sameepsi/quickswap06" if CHAIN == "polygon"
    else "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
)

REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
REDIS_STREAM = _env("STAT_ARB_REDIS_STREAM", "atom:opps:stat_arb")
REDIS_MAXLEN = int(_env("STAT_ARB_REDIS_MAXLEN", "1500"))

KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("STAT_ARB_PAUSE_KEY", f"atom:stat_arb:{CHAIN}:paused")

METRICS_PORT = int(_env("METRICS_PORT", "9116"))
SCAN_INTERVAL_SEC = float(_env("STAT_ARB_SCAN_INTERVAL_SEC", "60"))

# Universe and pairs
DEFAULT_TOKENS_POLYGON = {
    "WETH":  "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
    "WMATIC":"0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    "USDC":  "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "USDT":  "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    "WBTC":  "0x1bfd67037b42cf73acF2047067bd4F2C47D9BfD6",
    "LINK":  "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
    "AAVE":  "0xD6DF932A45C0f255f85145f286eA0b292B21C90B",
    "UNI":   "0xb33EaAd8d922B1083446DC23f610c2567fB5180f",
}
DEFAULT_TOKENS_ETHEREUM = {
    "WETH":  "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "USDC":  "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT":  "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "WBTC":  "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "LINK":  "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "AAVE":  "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "UNI":   "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
}
TOKENS = json.loads(_env("STAT_ARB_TOKENS_JSON", json.dumps(DEFAULT_TOKENS_POLYGON if CHAIN == "polygon" else DEFAULT_TOKENS_ETHEREUM)))

# Pairs to model/predict (symbols)
DEFAULT_PAIRS = "WETH/USDC,WMATIC/USDC,WBTC/WETH" if CHAIN == "polygon" else "WETH/USDC,WBTC/WETH"
PAIRS = [p.strip() for p in _env("STAT_ARB_PAIRS", DEFAULT_PAIRS).split(",") if p.strip()]

# Model storage (optional)
PERSIST_MODELS = _env("STAT_ARB_PERSIST_MODELS", "false").lower() == "true"
MODEL_DIR = _env("STAT_ARB_MODEL_DIR", "artifacts/stat_arb")

# Economics
POSITION_SIZE_USD = Decimal(_env("STAT_ARB_POSITION_SIZE_USD", "25000"))
MIN_PROFIT_USD = Decimal(_env("STAT_ARB_MIN_PROFIT_USD", "100"))
MIN_CONFIDENCE = float(_env("STAT_ARB_MIN_CONFIDENCE", "0.65"))
LOOKBACK = int(_env("STAT_ARB_LOOKBACK_BARS", "180"))
MIN_ZSCORE = float(_env("STAT_ARB_MIN_ZSCORE", "2.0"))
EXIT_ZSCORE = float(_env("STAT_ARB_EXIT_ZSCORE", "0.5"))
MAX_OPEN_POSITIONS = int(_env("STAT_ARB_MAX_POSITIONS", "5"))

# ----------------------- LOGGING/metrics -----------------------

log = logging.getLogger("atom.stat_arb")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

MET_SCAN_LAT      = Histogram("atom_stat_arb_scan_latency_seconds", "Full scan latency seconds")
MET_ERRORS        = Counter("atom_stat_arb_errors_total", "Errors total")
MET_SIGNALS       = Counter("atom_stat_arb_signals_total", "Signals published")
MET_BEST_EXP_PROF = Gauge("atom_stat_arb_best_expected_profit_usd", "Best expected profit USD")
MET_LAST_TS       = Gauge("atom_stat_arb_last_ts", "Last successful loop ts")
MET_MODELS        = Gauge("atom_stat_arb_models_trained", "Models trained count")

# ----------------------- data models -----------------------

@dataclass
class StatArbSignal:
    engine: str                 # "mean_reversion" | "pairs" | "ml"
    pair: str                   # "WETH/USDC"
    base: str
    quote: str
    zscore: float
    predicted_return: float     # fractional return of base vs quote
    confidence: float
    entry_ref: float            # price ratio or normalized ref
    target_ref: float
    stop_ref: float
    position_size_usd: float
    expected_profit_usd: float
    ts: int

# ----------------------- core scanner -----------------------

class StatisticalArbScanner:
    def __init__(self):
        self.w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL, request_kwargs={"timeout": 12}))
        self.redis: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None

        # histories keyed by token address, values are deque of floats (USD price)
        self.price_history: Dict[str, deque] = {addr: deque(maxlen=LOOKBACK * 2) for addr in TOKENS.values()}

        # ML models per pair
        self.models: Dict[str, RandomForestRegressor] = {}
        self.scalers: Dict[str, StandardScaler] = {}

        # positions tracking (headless signaler; no real positions placed here)
        self.open_positions: Dict[str, dict] = {}

    async def init(self):
        # chain guard
        net = await self.w3.eth.chain_id
        if net != CHAIN_ID_EXPECTED:
            raise RuntimeError(f"Wrong network: expected chain_id={CHAIN_ID_EXPECTED} for {CHAIN}, got {net}")

        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20))
        jlog("info", event="stat_arb_init", chain=CHAIN, rpc=RPC_URL, subgraph=SUBGRAPH_URL, pairs=PAIRS)

        await self._bootstrap_history()
        await self._train_models()

    async def close(self):
        try:
            if self.session:
                await self.session.close()
        except Exception:
            pass

    # ---------------- control ----------------

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

    # ---------------- data fetch ----------------

    async def _bootstrap_history(self):
        tasks = [self._fetch_historical_prices(addr) for addr in TOKENS.values()]
        await asyncio.gather(*tasks)

    async def _fetch_historical_prices(self, token_address: str):
        # tokenDayDatas; newest first
        q = {
            "query": f"""
            {{
              tokenDayDatas(
                first: 120,
                orderBy: date,
                orderDirection: desc,
                where: {{ token: "{token_address.lower()}" }}
              ) {{
                date
                priceUSD
              }}
            }}
            """
        }
        try:
            assert self.session is not None
            async with self.session.post(SUBGRAPH_URL, json=q) as r:
                data = await r.json()
                arr = data.get("data", {}).get("tokenDayDatas", [])
                for row in reversed(arr):
                    p = float(row.get("priceUSD") or 0) or 0.0
                    if p > 0:
                        self.price_history[token_address].append(p)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="subgraph_bootstrap_error", token=token_address, err=str(e))

    async def _fetch_latest_price(self, token_address: str) -> Optional[float]:
        q = {
            "query": f"""
            {{
              tokenDayDatas(
                first: 1,
                orderBy: date,
                orderDirection: desc,
                where: {{ token: "{token_address.lower()}" }}
              ) {{
                date
                priceUSD
              }}
            }}
            """
        }
        try:
            assert self.session is not None
            async with self.session.post(SUBGRAPH_URL, json=q) as r:
                data = await r.json()
                arr = data.get("data", {}).get("tokenDayDatas", [])
                if not arr:
                    return None
                p = float(arr[0].get("priceUSD") or 0) or 0.0
                return p if p > 0 else None
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="subgraph_latest_error", token=token_address, err=str(e))
            return None

    async def refresh_prices(self):
        tasks = []
        for addr in TOKENS.values():
            tasks.append(self._refresh_one(addr))
        await asyncio.gather(*tasks)

    async def _refresh_one(self, token_address: str):
        p = await self._fetch_latest_price(token_address)
        if p is not None:
            dq = self.price_history[token_address]
            if len(dq) == 0 or abs(dq[-1] - p) > 1e-9:
                dq.append(p)

    # ---------------- feature helpers ----------------

    @staticmethod
    def _zscore(series: np.ndarray) -> float:
        if series.size < 20:
            return 0.0
        mu = float(series.mean())
        sigma = float(series.std(ddof=1))
        if sigma <= 0:
            return 0.0
        return float((series[-1] - mu) / sigma)

    @staticmethod
    def _ratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        n = min(a.size, b.size)
        if n == 0:
            return np.array([])
        ra = a[-n:]
        rb = b[-n:]
        with np.errstate(divide='ignore', invalid='ignore'):
            r = np.where(rb > 0, ra / rb, np.nan)
        r = np.nan_to_num(r, nan=0.0, posinf=0.0, neginf=0.0)
        return r

    # ---------------- engines ----------------

    def _engine_mean_reversion(self, pair: str) -> Optional[StatArbSignal]:
        base, quote = pair.split("/")
        ba = TOKENS.get(base)
        qa = TOKENS.get(quote)
        if not ba or not qa:
            return None
        a = np.array(self.price_history[ba], dtype=float)
        b = np.array(self.price_history[qa], dtype=float)
        if a.size < 30 or b.size < 30:
            return None
        ratio = self._ratio(a, b)
        if ratio.size < 30:
            return None
        z = self._zscore(ratio[-LOOKBACK:])
        if abs(z) < MIN_ZSCORE:
            return None
        # mean reversion: expect revert toward mean (z -> 0)
        entry = float(ratio[-1])
        target = float(ratio[-1] - z * float(ratio[-LOOKBACK:].std(ddof=1)))
        stop = float(ratio[-1] + np.sign(z) * float(ratio[-LOOKBACK:].std(ddof=1)) * EXIT_ZSCORE)
        # expected move magnitude
        expected_move = abs(entry - target) / max(target, 1e-9)
        exp_profit = float(POSITION_SIZE_USD * Decimal(expected_move))
        if exp_profit < float(MIN_PROFIT_USD):
            return None
        return StatArbSignal(
            engine="mean_reversion",
            pair=pair,
            base=base,
            quote=quote,
            zscore=float(z),
            predicted_return=float(-np.sign(z) * expected_move),
            confidence=min(0.95, 0.55 + min(0.4, abs(z) / 6.0)),
            entry_ref=entry,
            target_ref=target,
            stop_ref=stop,
            position_size_usd=float(POSITION_SIZE_USD),
            expected_profit_usd=exp_profit,
            ts=int(time.time()),
        )

    def _engine_pairs_spread(self, pair: str) -> Optional[StatArbSignal]:
        # same ratio engine but different thresholding and risk
        base, quote = pair.split("/")
        ba = TOKENS.get(base)
        qa = TOKENS.get(quote)
        if not ba or not qa:
            return None
        a = np.array(self.price_history[ba], dtype=float)
        b = np.array(self.price_history[qa], dtype=float)
        if a.size < 40 or b.size < 40:
            return None
        ratio = self._ratio(a, b)
        if ratio.size < 40:
            return None
        recent = ratio[-60:] if ratio.size >= 60 else ratio
        z = self._zscore(recent)
        if abs(z) < (MIN_ZSCORE + 0.5):
            return None
        entry = float(ratio[-1])
        mu = float(recent.mean())
        sd = float(recent.std(ddof=1) or 1.0)
        target = mu
        stop = float(entry + np.sign(z) * sd * EXIT_ZSCORE)
        expected_move = abs(entry - target) / max(target, 1e-9)
        exp_profit = float(POSITION_SIZE_USD * Decimal(expected_move))
        if exp_profit < float(MIN_PROFIT_USD):
            return None
        return StatArbSignal(
            engine="pairs",
            pair=pair,
            base=base,
            quote=quote,
            zscore=float(z),
            predicted_return=float(-np.sign(z) * expected_move),
            confidence=min(0.95, 0.50 + min(0.45, abs(z) / 5.0)),
            entry_ref=entry,
            target_ref=target,
            stop_ref=stop,
            position_size_usd=float(POSITION_SIZE_USD),
            expected_profit_usd=exp_profit,
            ts=int(time.time()),
        )

    async def _train_models(self):
        if not SKLEARN_AVAILABLE:
            MET_MODELS.set(0)
            return
        os.makedirs(MODEL_DIR, exist_ok=True)
        trained = 0
        for pair in PAIRS:
            base, quote = pair.split("/")
            ba = TOKENS.get(base)
            qa = TOKENS.get(quote)
            if not ba or not qa:
                continue
            a = np.array(self.price_history[ba], dtype=float)
            b = np.array(self.price_history[qa], dtype=float)
            n = min(a.size, b.size)
            if n < 80:
                continue
            ra = np.diff(np.log(a[-n:]))
            rb = np.diff(np.log(b[-n:]))
            X = np.stack([
                ra[-LOOKBACK:][-60:],
                rb[-LOOKBACK:][-60:],
            ], axis=1)
            y = ra[-LOOKBACK:][-60:]
            if X.shape[0] < 40:
                continue
            scaler = StandardScaler()
            Xs = scaler.fit_transform(X)
            model = RandomForestRegressor(n_estimators=128, max_depth=6, random_state=42)
            model.fit(Xs, y)
            self.models[pair] = model
            self.scalers[pair] = scaler
            trained += 1
        MET_MODELS.set(trained)

    def _engine_ml(self, pair: str) -> Optional[StatArbSignal]:
        if not SKLEARN_AVAILABLE or pair not in self.models:
            return None
        base, quote = pair.split("/")
        ba = TOKENS.get(base)
        qa = TOKENS.get(quote)
        a = np.array(self.price_history[ba], dtype=float)
        b = np.array(self.price_history[qa], dtype=float)
        n = min(a.size, b.size)
        if n < 70:
            return None
        ra = np.diff(np.log(a[-n:]))
        rb = np.diff(np.log(b[-n:]))
        X = np.array([[ra[-1], rb[-1]]])
        scaler = self.scalers[pair]
        model = self.models[pair]
        pred = float(model.predict(scaler.transform(X))[0])
        conf = min(0.95, 0.50 + min(0.45, abs(pred) * 20))
        if conf < MIN_CONFIDENCE:
            return None
        entry = float(a[-1] / b[-1])
        target = entry * (1.0 + pred)
        stop = entry * (1.0 - abs(pred) * 0.5)
        exp_profit = float(POSITION_SIZE_USD * Decimal(abs(pred)))
        if exp_profit < float(MIN_PROFIT_USD):
            return None
        return StatArbSignal(
            engine="ml",
            pair=pair,
            base=base,
            quote=quote,
            zscore=0.0,
            predicted_return=float(pred),
            confidence=conf,
            entry_ref=entry,
            target_ref=target,
            stop_ref=stop,
            position_size_usd=float(POSITION_SIZE_USD),
            expected_profit_usd=exp_profit,
            ts=int(time.time()),
        )

    # ---------------- publish ----------------

    async def publish(self, signals: List[StatArbSignal]):
        if not self.redis:
            return
        # rank by expected profit then confidence
        signals.sort(key=lambda s: (s.expected_profit_usd, s.confidence), reverse=True)
        for s in signals:
            payload = json.dumps(asdict(s), separators=(",", ":"))
            try:
                await self.redis.xadd(REDIS_STREAM, {"data": payload}, maxlen=REDIS_MAXLEN, approximate=True)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="redis_xadd_error", err=str(e))
        if signals:
            MET_SIGNALS.inc(len(signals))
            MET_BEST_EXP_PROF.set(signals[0].expected_profit_usd)

    # ---------------- main loop ----------------

    async def run_once(self):
        t0 = time.perf_counter()
        try:
            if await self.paused():
                await asyncio.sleep(1.0)
                return
            await self.refresh_prices()
            out: List[StatArbSignal] = []
            for pair in PAIRS:
                sig1 = self._engine_mean_reversion(pair)
                if sig1:
                    out.append(sig1)
                sig2 = self._engine_pairs_spread(pair)
                if sig2:
                    out.append(sig2)
                sig3 = self._engine_ml(pair)
                if sig3:
                    out.append(sig3)
            await self.publish(out)
            MET_LAST_TS.set(int(time.time()))
            jlog("info", event="stat_arb_signals", count=len(out), best=asdict(out[0]) if out else None)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="run_once_error", err=str(e))
        finally:
            MET_SCAN_LAT.observe(time.perf_counter() - t0)

    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        while True:
            await self.run_once()
            await asyncio.sleep(SCAN_INTERVAL_SEC)

# Entrypoint
if __name__ == "__main__":
    try:
        asyncio.run(StatisticalArbScanner().run())
    except KeyboardInterrupt:
        pass 