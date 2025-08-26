# bots/triangular_arbitrage.py
"""
ATOM Triangular Arbitrage Scanner (Polygon mainnet)
- Discovers 3-token cycles across QuickSwap & Sushi
- Prices edges from on-chain reserves with proper decimals and DEX fees
- Estimates net PnL with Chainlink gas costing and Aave flash fee
- Publishes signals to Redis Stream 'atom:opps:triangular'
- Prometheus metrics on METRICS_PORT
- Strict: no private keys, no signing, no websockets required
- Hard fail if not on chain_id=137 (Polygon)
"""

import os
import asyncio
import json
import time
import logging
from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3, HTTPProvider

# ---------- Env ----------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

RPC_URL = _env("POLYGON_RPC_URL", required=True)
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")

# Scan cadence & discovery
SCAN_INTERVAL_SEC = float(_env("TRI_SCAN_INTERVAL_SEC", "3.0"))
DISCOVERY_INTERVAL_SEC = float(_env("TRI_DISCOVERY_INTERVAL_SEC", "900"))

# Economics
TRADE_SIZE_USD = Decimal(_env("TRI_TRADE_SIZE_USD", "25000"))
AAVE_FLASH_FEE_BPS = Decimal(_env("AAVE_FLASH_FEE_BPS", "9"))
MIN_NET_PROFIT_USD = Decimal(_env("TRI_MIN_NET_PROFIT_USD", "75"))
GAS_LIMIT_TRI = int(_env("TRI_GAS_LIMIT", "650000"))

# Streams/metrics/controls
METRICS_PORT = int(_env("METRICS_PORT", "9112"))
REDIS_STREAM = _env("TRI_REDIS_STREAM", "atom:opps:triangular")
REDIS_MAXLEN = int(_env("TRI_REDIS_MAXLEN", "1500"))
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("TRI_PAUSE_KEY", "atom:tri:paused")

# Chainlink MATIC/USD
CHAINLINK_MATIC_USD = Web3.to_checksum_address(
    _env("CHAINLINK_MATIC_USD", "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0")
)

# ---------- Polygon addresses (allowlist) ----------
USDC = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
USDT = Web3.to_checksum_address("0xc2132D05D31c914a87C6611C10748AEb04B58e8F")

TOKENS: Dict[str, str] = {
    # high-liquidity core set
    "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    "WETH"  : "0x7ceB23fD6b8C6f8D8252D06C5bC4b5d6B4C1d19E".lower().replace("b8c6f8d8252d06c5bc4b5d6b4c1d19e","b8c6f8d8252d06c5bc4b5d6b4c1d19e"),  # same
    "USDC"  : str(USDC),
    "USDT"  : str(USDT),
    "DAI"   : "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
    "WBTC"  : "0x1bfd67037b42cf73acF2047067bd4F2C47D9BfD6",
    "LINK"  : "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
    "AAVE"  : "0xD6DF932A45C0f255f85145f286eA0b292B21C90B",
    "CRV"   : "0x172370d5Cd63279eFa6d502DAB29171933a610AF",
}
# Normalize to checksum
TOKENS = {s: Web3.to_checksum_address(a) for s, a in TOKENS.items()}

DEXES = {
    "quickswap": {
        "factory": Web3.to_checksum_address("0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32"),
        "fee_bps": 30,  # 0.30%
    },
    "sushiswap": {
        "factory": Web3.to_checksum_address("0xc35DADB65012eC5796536bD9864eD8773aBc74C4"),
        "fee_bps": 30,  # 0.30%
    },
}

# ---------- Minimal ABIs ----------
FACTORY_ABI = json.loads('[{"constant":true,"inputs":[{"name":"tokenA","type":"address"},{"name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"name":"pair","type":"address"}],"stateMutability":"view","type":"function"}]')
PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"}]')
ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"stateMutability":"view","type":"function"}]')
CL_AGG_ABI = json.loads('[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"}]')

# ---------- Logging ----------
log = logging.getLogger("atom.tri")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

# ---------- Metrics ----------
MET_DISCOVER_LAT = Histogram("atom_tri_discovery_latency_seconds", "Discovery latency")
MET_SCAN_LAT     = Histogram("atom_tri_scan_latency_seconds", "Scan latency")
MET_ERRORS       = Counter("atom_tri_errors_total", "Errors")
MET_OPPS         = Counter("atom_tri_opportunities_total", "Opportunities")
MET_BEST_NET     = Gauge("atom_tri_best_net_profit_usd", "Best net profit last scan")
MET_TRIANGLES    = Gauge("atom_tri_triangles_scanned", "Triangles scanned per loop")

# ---------- Models ----------
@dataclass
class TriSignal:
    a: str
    b: str
    c: str
    a_symbol: str
    b_symbol: str
    c_symbol: str
    # chosen dex per edge
    dex_ab: str
    dex_bc: str
    dex_ca: str
    # prices after fee (b per a, c per b, a per c)
    p_ab: float
    p_bc: float
    p_ca: float
    product: float
    gross_profit_usd: float
    gas_cost_usd: float
    flash_fee_usd: float
    net_profit_usd: float
    amount_usd: float
    ts: int

# ---------- Scanner ----------
class TriangularArbScanner:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
        self.redis: Optional[redis.Redis] = None
        self.factories = {name: self.w3.eth.contract(info["factory"], abi=FACTORY_ABI) for name, info in DEXES.items()}
        self.matic_usd = self.w3.eth.contract(CHAINLINK_MATIC_USD, abi=CL_AGG_ABI)

        # caches
        self.pairs: Dict[str, Dict[Tuple[str, str], str]] = {dex: {} for dex in DEXES.keys()}  # (a,b)->pair
        self.decimals: Dict[str, int] = {}
        self.symbols: Dict[str, str] = {}

        self._ensure_chain()

    def _ensure_chain(self):
        cid = self.w3.eth.chain_id
        if cid != 137:
            raise RuntimeError(f"Not on Polygon mainnet (137). chain_id={cid}")

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await self._discover_pairs()
        await self._prime_token_metadata()
        jlog("info", event="init", rpc=RPC_URL, redis=REDIS_URL,
             tokens=len(TOKENS), pairs=sum(len(v) for v in self.pairs.values()))

    # ---------- Discovery ----------
    async def _discover_pairs(self):
        t0 = time.perf_counter()
        tokens = list(TOKENS.values())
        async def get_pair_once(dex: str, a: str, b: str):
            try:
                fa = self.factories[dex]
                addr = await asyncio.to_thread(fa.functions.getPair(a, b).call)
                if addr and int(addr, 16) != 0:
                    self.pairs[dex][(a, b)] = Web3.to_checksum_address(addr)
                    self.pairs[dex][(b, a)] = Web3.to_checksum_address(addr)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="getPair_error", dex=dex, a=a, b=b, err=str(e))

        tasks = []
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                a, b = tokens[i], tokens[j]
                for dex in DEXES.keys():
                    tasks.append(get_pair_once(dex, a, b))
        await asyncio.gather(*tasks)

        # persist in Redis for visibility
        try:
            if self.redis:
                serial = {dex: {f"{k[0]}-{k[1]}": v for k, v in m.items()} for dex, m in self.pairs.items()}
                await self.redis.set("atom:tri:pairs", json.dumps(serial))
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="redis_set_pairs", err=str(e))

        MET_DISCOVER_LAT.observe(time.perf_counter() - t0)

    async def _prime_token_metadata(self):
        async def fetch_one(addr: str):
            if addr in self.decimals and addr in self.symbols:
                return
            try:
                erc = self.w3.eth.contract(addr, abi=ERC20_ABI)
                dec = await asyncio.to_thread(erc.functions.decimals().call)
                sym = await asyncio.to_thread(erc.functions.symbol().call)
                self.decimals[addr] = int(dec)
                self.symbols[addr] = str(sym)
            except Exception:
                # fallbacks
                self.decimals.setdefault(addr, 6 if addr in (USDC, USDT) else 18)
                self.symbols.setdefault(addr, next((s for s,a in TOKENS.items() if a == addr), addr[:6]))

        tasks = [fetch_one(a) for a in TOKENS.values()]
        await asyncio.gather(*tasks)

        # persist
        try:
            if self.redis:
                await self.redis.set("atom:tri:decimals", json.dumps(self.decimals))
                await self.redis.set("atom:tri:symbols", json.dumps(self.symbols))
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="redis_set_meta", err=str(e))

    # ---------- Pricing ----------
    def _edge_price_after_fee(self, pair_addr: str, src: str, dst: str, fee_bps: int) -> Optional[Decimal]:
        try:
            pair = self.w3.eth.contract(pair_addr, abi=PAIR_ABI)
            t0 = Web3.to_checksum_address(pair.functions.token0().call())
            t1 = Web3.to_checksum_address(pair.functions.token1().call())
            r0, r1, _ = pair.functions.getReserves().call()

            d0 = self.decimals.get(t0, 18)
            d1 = self.decimals.get(t1, 18)

            if t0 == src and t1 == dst and r0 > 0:
                price = (Decimal(r1) / Decimal(10**d1)) / (Decimal(r0) / Decimal(10**d0))
            elif t0 == dst and t1 == src and r1 > 0:
                price = (Decimal(r0) / Decimal(10**d0)) / (Decimal(r1) / Decimal(10**d1))
            else:
                return None

            return price * (Decimal(10000 - fee_bps) / Decimal(10000))
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="price_error", pair=pair_addr, src=src, dst=dst, err=str(e))
            return None

    async def _best_direct_price(self, src: str, dst: str) -> Tuple[Optional[Decimal], Optional[str]]:
        best: Optional[Decimal] = None
        best_dex: Optional[str] = None
        for dex, m in self.pairs.items():
            pair = m.get((src, dst))
            if not pair:
                continue
            fee = DEXES[dex]["fee_bps"]
            p = await asyncio.to_thread(self._edge_price_after_fee, pair, src, dst, fee)
            if p and p > 0 and (best is None or p > best):
                best = p
                best_dex = dex
        return best, best_dex

    async def _matic_usd(self) -> Decimal:
        try:
            rd = await asyncio.to_thread(self.matic_usd.functions.latestRoundData().call)
            return Decimal(rd[1]) / Decimal(10**8)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="chainlink_error", err=str(e))
            return Decimal("0")

    # ---------- Triangle search ----------
    async def scan_triangles(self) -> List[TriSignal]:
        tokens = list(TOKENS.values())
        triangles_scanned = 0
        signals: List[TriSignal] = []

        matic_usd = await self._matic_usd()
        gas_price = self.w3.eth.gas_price
        gas_cost_usd = (Decimal(gas_price) * Decimal(GAS_LIMIT_TRI) / Decimal(1e18)) * matic_usd
        flash_fee_usd = TRADE_SIZE_USD * (AAVE_FLASH_FEE_BPS / Decimal(10000))

        n = len(tokens)
        for i in range(n):
            for j in range(i+1, n):
                for k in range(j+1, n):
                    a, b, c = tokens[i], tokens[j], tokens[k]

                    # Try both orientations: a->b->c->a and a->c->b->a
                    for order in ((a,b,c), (a,c,b)):
                        x, y, z = order
                        p_xy, dex_xy = await self._best_direct_price(x, y)
                        p_yz, dex_yz = await self._best_direct_price(y, z)
                        p_zx, dex_zx = await self._best_direct_price(z, x)
                        triangles_scanned += 1

                        if not (p_xy and p_yz and p_zx):
                            continue

                        product = p_xy * p_yz * p_zx
                        profit_ratio = product - Decimal(1)

                        if profit_ratio <= Decimal(0):
                            continue

                        gross = TRADE_SIZE_USD * profit_ratio
                        net = gross - gas_cost_usd - flash_fee_usd
                        if net < MIN_NET_PROFIT_USD:
                            continue

                        sig = TriSignal(
                            a=x, b=y, c=z,
                            a_symbol=self.symbols.get(x, x[:6]),
                            b_symbol=self.symbols.get(y, y[:6]),
                            c_symbol=self.symbols.get(z, z[:6]),
                            dex_ab=dex_xy or "unknown",
                            dex_bc=dex_yz or "unknown",
                            dex_ca=dex_zx or "unknown",
                            p_ab=float(p_xy), p_bc=float(p_yz), p_ca=float(p_zx),
                            product=float(product),
                            gross_profit_usd=float(gross),
                            gas_cost_usd=float(gas_cost_usd),
                            flash_fee_usd=float(flash_fee_usd),
                            net_profit_usd=float(net),
                            amount_usd=float(TRADE_SIZE_USD),
                            ts=int(time.time()),
                        )
                        signals.append(sig)

        MET_TRIANGLES.set(triangles_scanned)
        signals.sort(key=lambda s: s.net_profit_usd, reverse=True)
        return signals

    # ---------- Publish ----------
    async def publish(self, signals: List[TriSignal]):
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
            MET_OPPS.inc(len(signals))
            MET_BEST_NET.set(signals[0].net_profit_usd)
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

    # ---------- Main ----------
    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="triangular_scanner_started",
             pairs=sum(len(v) for v in self.pairs.values()),
             min_net=float(MIN_NET_PROFIT_USD), trade_usd=float(TRADE_SIZE_USD))

        async def periodic_discovery():
            while True:
                try:
                    await self._discover_pairs()
                    await self._prime_token_metadata()
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
                signals = await self.scan_triangles()
                await self.publish(signals)
                if signals:
                    jlog("info", event="signals", count=len(signals), best=asdict(signals[0]))
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="main_loop_error", err=str(e))
                await asyncio.sleep(1.0)
            MET_SCAN_LAT.observe(time.perf_counter() - t0)
            await asyncio.sleep(max(0.0, SCAN_INTERVAL_SEC - (time.perf_counter() - t0)))


if __name__ == "__main__":
    try:
        asyncio.run(TriangularArbScanner().run())
    except KeyboardInterrupt:
        pass 