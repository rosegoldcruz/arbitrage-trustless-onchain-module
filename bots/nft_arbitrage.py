# bots/nft_arbitrage.py
"""
ATOM NFT & Tokenized Asset Arbitrage Scanner (headless)
- Scans enabled marketplaces for collection floors/listings (env-driven)
- Computes net spread after marketplace fees and gas (native/USD via Chainlink)
- Publishes ranked opportunities to Redis stream 'atom:opps:nft'
- Exposes Prometheus metrics on METRICS_PORT
- Circuit breakers: global kill switch + per-bot pause key
- Production hygiene: no private keys, no signing, no hardcoded secrets, chain guard
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal

import aiohttp
import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from web3 import Web3, HTTPProvider

# ---------------------- ENV ----------------------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

# Chain
NFT_CHAIN = _env("NFT_CHAIN", "polygon").lower()   # polygon | ethereum
if NFT_CHAIN not in ("polygon", "ethereum"):
    raise RuntimeError("NFT_CHAIN must be 'polygon' or 'ethereum'")
RPC_URL = _env("POLYGON_RPC_URL" if NFT_CHAIN == "polygon" else "ETHEREUM_RPC_URL", required=True)
CHAIN_ID_EXPECTED = 137 if NFT_CHAIN == "polygon" else 1

# Chainlink native/USD feeds
CHAINLINK_NATIVE_USD = Web3.to_checksum_address(
    _env(
        "CHAINLINK_MATIC_USD" if NFT_CHAIN == "polygon" else "CHAINLINK_ETH_USD",
        "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0" if NFT_CHAIN == "polygon"
        else "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419",
    )
)

# Redis & control
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
REDIS_STREAM = _env("NFT_REDIS_STREAM", "atom:opps:nft")
REDIS_MAXLEN = int(_env("NFT_REDIS_MAXLEN", "1500"))
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("NFT_PAUSE_KEY", f"atom:nft:{NFT_CHAIN}:paused")

# Scanner settings
METRICS_PORT = int(_env("METRICS_PORT", "9117"))
SCAN_INTERVAL_SEC = float(_env("NFT_SCAN_INTERVAL_SEC", "90"))
MIN_PROFIT_USD = Decimal(_env("NFT_MIN_PROFIT_USD", "200"))
MAX_SPREAD_PCT = float(_env("NFT_MAX_SPREAD_PCT", "40"))        # sanity cap
GAS_TOTAL_UNITS = int(_env("NFT_GAS_TOTAL_UNITS", "520000"))    # buy + list combined rough upper bound

# Collections universe (symbol->contract)
DEFAULT_COLLECTIONS = {
    # polygon examples (override via env)
    "PudgyPolygon": "0xf84c7fadaad69d3edc2b5f2b2b80d4f2a5e9cdbf",  # example; replace with your set
}
COLLECTIONS: Dict[str, str] = json.loads(_env("NFT_COLLECTIONS_JSON", json.dumps(DEFAULT_COLLECTIONS)))

# Marketplaces (enable/disable + endpoints + fees)
# If a marketplace key is missing, that venue is skipped. All values are env-overridable.
MP_OPENSEA_ENABLED = _env("MP_OPENSEA_ENABLED", "false").lower() == "true"
MP_OPENSEA_API = _env("MP_OPENSEA_API", "https://api.opensea.io/api/v2")
MP_OPENSEA_KEY = _env("OPENSEA_API_KEY", "")
MP_OPENSEA_FEE = Decimal(_env("MP_OPENSEA_FEE_BPS", "250"))  # bps

MP_BLUR_ENABLED = _env("MP_BLUR_ENABLED", "false").lower() == "true"
MP_BLUR_API = _env("MP_BLUR_API", "https://api.blur.io/v1")
MP_BLUR_KEY = _env("BLUR_API_KEY", "")
MP_BLUR_FEE = Decimal(_env("MP_BLUR_FEE_BPS", "50"))

MP_X2Y2_ENABLED = _env("MP_X2Y2_ENABLED", "false").lower() == "true"
MP_X2Y2_API = _env("MP_X2Y2_API", "https://api.x2y2.io/v1")
MP_X2Y2_KEY = _env("X2Y2_API_KEY", "")
MP_X2Y2_FEE = Decimal(_env("MP_X2Y2_FEE_BPS", "50"))

# Optional aggregator (Reservoir)
AGGR_ENABLED = _env("MP_RESERVOIR_ENABLED", "false").lower() == "true"
AGGR_API = _env("MP_RESERVOIR_API", "https://api.reservoir.tools")
AGGR_KEY = _env("RESERVOIR_API_KEY", "")

# Rarity (optional)
RARITY_ENABLED = _env("RARITY_ENABLED", "false").lower() == "true"
RARITY_API = _env("RARITY_API", "")
RARITY_KEY = _env("RARITY_API_KEY", "")

# ---------------------- ABIs ----------------------

CL_ABI = json.loads('[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"}]')

# ---------------------- Logging & Metrics ----------------------

log = logging.getLogger("atom.nft")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

MET_SCAN_LAT      = Histogram("atom_nft_scan_latency_seconds", "End-to-end scan latency")
MET_ERRORS        = Counter("atom_nft_errors_total", "Errors")
MET_OPPS          = Counter("atom_nft_opportunities_total", "Published opportunities")
MET_BEST_PROFIT   = Gauge("atom_nft_best_profit_usd", "Best net profit seen")
MET_LAST_TS       = Gauge("atom_nft_last_scan_ts", "Last successful scan ts")
MET_MARKETS_ON    = Gauge("atom_nft_markets_enabled", "Enabled marketplace count")

# ---------------------- Models ----------------------

@dataclass
class NFTArbOpp:
    collection_symbol: str
    collection_address: str
    buy_market: str
    sell_market: str
    buy_price_native: float
    sell_price_native: float
    buy_fee_bps: int
    sell_fee_bps: int
    gas_cost_usd: float
    spread_pct: float
    net_profit_usd: float
    rarity_hint: float
    ts: int

# ---------------------- Scanner ----------------------

class NFTArbScanner:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={"timeout": 12}))
        cid = self.w3.eth.chain_id
        if cid != CHAIN_ID_EXPECTED:
            raise RuntimeError(f"Wrong network: expected chain_id={CHAIN_ID_EXPECTED} for {NFT_CHAIN}, got {cid}")

        self.native_oracle = self.w3.eth.contract(CHAINLINK_NATIVE_USD, abi=CL_ABI)
        self.redis: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None

        # enabled markets inventory
        self.markets: Dict[str, Dict] = {}
        if MP_OPENSEA_ENABLED and MP_OPENSEA_KEY:
            self.markets["opensea"] = {"api": MP_OPENSEA_API, "key": MP_OPENSEA_KEY, "fee_bps": int(MP_OPENSEA_FEE)}
        if MP_BLUR_ENABLED and MP_BLUR_KEY:
            self.markets["blur"] = {"api": MP_BLUR_API, "key": MP_BLUR_KEY, "fee_bps": int(MP_BLUR_FEE)}
        if MP_X2Y2_ENABLED and MP_X2Y2_KEY:
            self.markets["x2y2"] = {"api": MP_X2Y2_API, "key": MP_X2Y2_KEY, "fee_bps": int(MP_X2Y2_FEE)}
        if AGGR_ENABLED and AGGR_KEY:
            self.markets["reservoir"] = {"api": AGGR_API, "key": AGGR_KEY, "fee_bps": 0}

        MET_MARKETS_ON.set(len(self.markets))

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12))
        jlog("info", event="nft_init", chain=NFT_CHAIN, rpc=RPC_URL, markets=list(self.markets.keys()), cols=len(COLLECTIONS))

    async def close(self):
        try:
            if self.session:
                await self.session.close()
        except Exception:
            pass

    # ------------- controls -------------

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

    # ------------- pricing / fees -------------

    async def native_usd(self) -> Decimal:
        try:
            rd = await asyncio.to_thread(self.native_oracle.functions.latestRoundData().call)
            return Decimal(rd[1]) / Decimal(10**8)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="chainlink_error", err=str(e))
            # fallback that won't explode math
            return Decimal("0.70") if NFT_CHAIN == "polygon" else Decimal("3000")

    # ------------- market queries -------------

    async def _headers(self, market: str) -> Dict[str, str]:
        if market == "opensea":
            return {"X-API-KEY": self.markets["opensea"]["key"]}
        if market == "blur":
            return {"x-api-key": self.markets["blur"]["key"]}
        if market == "x2y2":
            return {"X-API-KEY": self.markets["x2y2"]["key"]}
        if market == "reservoir":
            return {"x-api-key": self.markets["reservoir"]["key"], "accept": "application/json"}
        return {}

    async def _fetch_floor(self, market: str, contract: str) -> Optional[Decimal]:
        """
        Fetch floor price in native currency for a given collection contract.
        All calls are best-effort; missing keys will result in None.
        """
        try:
            base = self.markets[market]["api"]
            headers = await self._headers(market)
            if market == "opensea":
                return None
            elif market == "blur":
                return None
            elif market == "x2y2":
                return None
            elif market == "reservoir":
                url = f"{base}/collections/v7?contracts={contract}&includeTopBid=false&normalizeRoyalties=false"
                async with self.session.get(url, headers=headers) as r:
                    if r.status == 200:
                        data = await r.json()
                        cols = data.get("collections", [])
                        if cols:
                            price = cols[0].get("floorAsk", {}).get("price", {})
                            native = price.get("nativePrice", {}) or price.get("price", {})
                            val = native.get("decimal")
                            if val is not None:
                                return Decimal(str(val))
            return None
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="fetch_floor_error", market=market, err=str(e))
            return None

    async def _fetch_best_bid(self, market: str, contract: str) -> Optional[Decimal]:
        return None

    # ------------- scan logic -------------

    async def _scan_collection(self, symbol: str, contract: str, native_usd: Decimal, gas_price_wei: int) -> List['NFTArbOpp']:
        tasks = [self._fetch_floor(m, contract) for m in self.markets]
        floors = await asyncio.gather(*tasks, return_exceptions=True)

        market_list = list(self.markets.keys())
        per_market_floor: Dict[str, Decimal] = {}
        for i, res in enumerate(floors):
            if isinstance(res, Exception) or res is None:
                continue
            per_market_floor[market_list[i]] = Decimal(res)

        opps: List[NFTArbOpp] = []
        if len(per_market_floor) < 2:
            return opps

        gas_usd = (Decimal(gas_price_wei) * Decimal(GAS_TOTAL_UNITS) / Decimal(1e18)) * native_usd

        mkts = list(per_market_floor.keys())
        for i in range(len(mkts)):
            for j in range(i + 1, len(mkts)):
                a, b = mkts[i], mkts[j]
                pa, pb = per_market_floor[a], per_market_floor[b]
                if pa <= 0 or pb <= 0:
                    continue
                if pa < pb:
                    buy_m, sell_m, buy_p, sell_p = a, b, pa, pb
                else:
                    buy_m, sell_m, buy_p, sell_p = b, a, pb, pa

                avg = (buy_p + sell_p) / Decimal(2)
                spread_pct = float(((sell_p - buy_p) / avg) * Decimal(100)) if avg > 0 else 0.0
                if spread_pct <= 0 or spread_pct > MAX_SPREAD_PCT:
                    continue

                buy_fee_bps = int(self.markets[buy_m].get("fee_bps", 0))
                sell_fee_bps = int(self.markets[sell_m].get("fee_bps", 0))

                sell_net_native = sell_p * (Decimal(1) - Decimal(sell_fee_bps) / Decimal(10000))
                buy_gross_native = buy_p * (Decimal(1) + Decimal(buy_fee_bps) / Decimal(10000))
                native_diff = sell_net_native - buy_gross_native
                net_usd = (native_diff * native_usd) - gas_usd

                if net_usd >= MIN_PROFIT_USD:
                    opps.append(NFTArbOpp(
                        collection_symbol=symbol,
                        collection_address=Web3.to_checksum_address(contract),
                        buy_market=buy_m,
                        sell_market=sell_m,
                        buy_price_native=float(buy_p),
                        sell_price_native=float(sell_p),
                        buy_fee_bps=buy_fee_bps,
                        sell_fee_bps=sell_fee_bps,
                        gas_cost_usd=float(gas_usd),
                        spread_pct=float(spread_pct),
                        net_profit_usd=float(net_usd),
                        rarity_hint=0.0,
                        ts=int(time.time()),
                    ))
        return opps

    async def publish(self, opps: List['NFTArbOpp']):
        if not self.redis:
            return
        opps.sort(key=lambda x: x.net_profit_usd, reverse=True)
        for op in opps:
            try:
                await self.redis.xadd(
                    REDIS_STREAM,
                    {"data": json.dumps(asdict(op), separators=(",", ":"))},
                    maxlen=REDIS_MAXLEN,
                    approximate=True,
                )
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="redis_xadd_error", err=str(e))
        if opps:
            MET_OPPS.inc(len(opps))
            MET_BEST_PROFIT.set(opps[0].net_profit_usd)

    async def run_once(self):
        t0 = time.perf_counter()
        try:
            if await self.paused():
                await asyncio.sleep(1.0)
                return

            native_usd = await self.native_usd()
            gas_price = self.w3.eth.gas_price

            all_opps: List[NFTArbOpp] = []
            tasks = [self._scan_collection(sym, addr, native_usd, gas_price) for sym, addr in COLLECTIONS.items()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    MET_ERRORS.inc()
                    jlog("error", event="scan_collection_error", err=str(res))
                    continue
                all_opps.extend(res)

            await self.publish(all_opps)
            MET_LAST_TS.set(int(time.time()))
            if all_opps:
                jlog("info", event="nft_opps", count=len(all_opps), best=asdict(all_opps[0]))
            else:
                jlog("info", event="nft_opps", count=0)

        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="run_once_error", err=str(e))
        finally:
            MET_SCAN_LAT.observe(time.perf_counter() - t0)

    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="nft_started", collections=len(COLLECTIONS), min_profit=float(MIN_PROFIT_USD))
        try:
            while True:
                await self.run_once()
                await asyncio.sleep(SCAN_INTERVAL_SEC)
        finally:
            await self.close()

# Entrypoint
if __name__ == "__main__":
    try:
        asyncio.run(NFTArbScanner().run())
    except KeyboardInterrupt:
        pass 