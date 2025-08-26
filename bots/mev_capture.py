# bots/mev_capture.py
"""
ATOM MEV Scanner & Defense Signaler
- Watches DEX router txs (block-level; optional WSS mempool if provided)
- Identifies high-slippage, high-notional swaps that are backrun-sensitive
- Estimates conservative backrun gross using AMM math and costs gas in USD
- Publishes JSON signals to Redis stream 'atom:opps:mev'
- Exposes Prometheus metrics
- Headless: no signing, no bundle sending, no secrets in code
- Network guards; robust error handling; JSON logs

Supports:
- Polygon (QuickSwap, Sushi)
- Ethereum (Uniswap V2, Sushi)
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
from eth_abi import decode as abi_decode

# ---------------- Env helpers ----------------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

CHAIN = _env("MEV_CHAIN", "polygon").lower()  # polygon or ethereum
if CHAIN not in ("polygon", "ethereum"):
    raise RuntimeError("MEV_CHAIN must be 'polygon' or 'ethereum'")

# RPC / optional WSS for mempool subscribe (eth_subscribe)
RPC_URL = _env("POLYGON_RPC_URL" if CHAIN == "polygon" else "ETHEREUM_RPC_URL", required=True)
WSS_URL = _env("POLYGON_WSS_URL" if CHAIN == "polygon" else "ETHEREUM_WSS_URL", "")

REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")

# Stream/metrics/controls
REDIS_STREAM = _env("MEV_REDIS_STREAM", "atom:opps:mev")
REDIS_MAXLEN = int(_env("MEV_REDIS_MAXLEN", "1500"))
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")
PAUSE_KEY = _env("MEV_PAUSE_KEY", f"atom:mev:{CHAIN}:paused")
METRICS_PORT = int(_env("METRICS_PORT", "9114"))

# Tuning
BLOCK_POLL_SEC = float(_env("MEV_BLOCK_POLL_SEC", "1.5"))
MEMPOOL_ENABLED = _env("MEV_MEMPOOL_ENABLED", "false").lower() == "true" and bool(WSS_URL)
MIN_NOTIONAL_USD = Decimal(_env("MEV_MIN_NOTIONAL_USD", "20000"))
MIN_ALLOWED_SLIPPAGE_BPS = int(_env("MEV_MIN_ALLOWED_SLIPPAGE_BPS", "50"))  # 0.50% minOut discount threshold
BACKRUN_SIZE_FRACTION = Decimal(_env("MEV_BACKRUN_SIZE_FRACTION", "0.25"))   # we model backrun at 25% of target size
GAS_LIMIT_BACKRUN = int(_env("MEV_GAS_LIMIT", "450000"))
AAVE_FLASH_FEE_BPS = Decimal(_env("AAVE_FLASH_FEE_BPS", "9"))

# Chainlink native/USD (for gas costing)
CHAINLINK_NATIVE_USD = Web3.to_checksum_address(
    _env("CHAINLINK_MATIC_USD" if CHAIN == "polygon" else "CHAINLINK_ETH_USD",
         "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0" if CHAIN == "polygon"
         else "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419")
)

# Canonical USDC/USDT (for notional calc)
USDC = Web3.to_checksum_address(
    _env("USDC_POLYGON" if CHAIN == "polygon" else "USDC_ETHEREUM",
         "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174" if CHAIN == "polygon"
         else "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
)
USDT = Web3.to_checksum_address(
    _env("USDT_POLYGON" if CHAIN == "polygon" else "USDT_ETHEREUM",
         "0xc2132D05D31c914a87C6611C10748AEb04B58e8F" if CHAIN == "polygon"
         else "0xdAC17F958D2ee523a2206206994597C13D831ec7")
)

# Router allowlist (Uniswap V2-style)
ROUTERS: Dict[str, str] = {}
if CHAIN == "polygon":
    ROUTERS = {
        Web3.to_checksum_address(_env("QUICKSWAP_V2_ROUTER", "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff")): "QuickSwapV2",
        Web3.to_checksum_address(_env("SUSHI_V2_ROUTER",     "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506")): "SushiV2",
    }
else:
    ROUTERS = {
        Web3.to_checksum_address(_env("UNISWAP_V2_ROUTER",   "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")): "UniswapV2",
        Web3.to_checksum_address(_env("SUSHI_V2_ROUTER",     "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")): "SushiV2",
    }

# ---------------- ABIs & selectors ----------------

PAIR_ABI = json.loads('[{"inputs":[],"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token0","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token1","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"}]')
ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]')
ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"stateMutability":"view","type":"function"}]')
CL_AGG_ABI = json.loads('[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"}]')

# V2 function selectors we handle (swapExactTokensForTokens / ETH variants)
SEL_swapExactTokensForTokens = "0x38ed1739"
SEL_swapTokensForExactTokens = "0x8803dbee"
SEL_swapExactETHForTokens    = "0x7ff36ab5"
SEL_swapExactTokensForETH    = "0x18cbafe5"
SEL_swapETHForExactTokens    = "0xfb3bdb41"

# ---------------- Logging & Metrics ----------------

log = logging.getLogger("atom.mev")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

MET_SCAN_LAT   = Histogram("atom_mev_scan_latency_seconds", "Block scan latency")
MET_ERRORS     = Counter("atom_mev_errors_total", "Errors")
MET_SIGNALS    = Counter("atom_mev_signals_total", "Published signals")
MET_BEST_NET   = Gauge("atom_mev_best_net_profit_usd", "Best net last scan")
MET_LAST_BLOCK = Gauge("atom_mev_last_block", "Last processed block number")

# ---------------- Models ----------------

@dataclass
class MEVSignal:
    chain: str
    router: str
    router_name: str
    tx_hash: str
    from_addr: str
    path: List[str]
    amount_in: str           # raw uint
    min_out: str            # raw uint
    expected_out: str       # from getAmountsOut at observe time
    allowed_slippage_bps: int
    notional_usd: float
    est_gross_usd: float
    est_flash_fee_usd: float
    est_gas_usd: float
    est_net_usd: float
    ts: int
    block_number: int

# ---------------- Core scanner ----------------

class MEVCaptureScanner:
    def __init__(self):
        self.w3 = Web3(HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
        self.redis: Optional[redis.Redis] = None
        self.native_oracle = self.w3.eth.contract(CHAINLINK_NATIVE_USD, abi=CL_AGG_ABI)
        self.routers = {addr: self.w3.eth.contract(addr, abi=ROUTER_ABI) for addr in ROUTERS.keys()}

        # token caches
        self.decimals: Dict[str, int] = {}
        self.symbols: Dict[str, str] = {}

        # network guard
        cid = self.w3.eth.chain_id
        expect = 137 if CHAIN == "polygon" else 1
        if cid != expect:
            raise RuntimeError(f"Wrong network: expected chain_id={expect} for {CHAIN}, got {cid}")

    async def init(self):
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        jlog("info", event="mev_scanner_init", chain=CHAIN, rpc=RPC_URL, wss=bool(WSS_URL), mempool=MEMPOOL_ENABLED)

    # -------- helpers --------

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

    async def native_usd(self) -> Decimal:
        try:
            rd = await asyncio.to_thread(self.native_oracle.functions.latestRoundData().call)
            return Decimal(rd[1]) / Decimal(10**8)
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="chainlink_error", err=str(e))
            # conservative fallback if feed hiccups
            return Decimal("0.70") if CHAIN == "polygon" else Decimal("3000")

    def _decimals(self, token: str) -> int:
        if token in self.decimals:
            return self.decimals[token]
        try:
            erc = self.w3.eth.contract(token, abi=ERC20_ABI)
            d = erc.functions.decimals().call()
            self.decimals[token] = int(d)
            return self.decimals[token]
        except Exception:
            self.decimals[token] = 6 if token in (USDC, USDT) else 18
            return self.decimals[token]

    def _symbol(self, token: str) -> str:
        if token in self.symbols:
            return self.symbols[token]
        try:
            erc = self.w3.eth.contract(token, abi=ERC20_ABI)
            s = erc.functions.symbol().call()
            self.symbols[token] = str(s)
            return self.symbols[token]
        except Exception:
            return token[:6]

    async def _expected_out(self, router_addr: str, amount_in: int, path: List[str]) -> Optional[int]:
        try:
            router = self.routers[router_addr]
            amts = await asyncio.to_thread(router.functions.getAmountsOut(amount_in, path).call)
            if isinstance(amts, list) and len(amts) == len(path):
                return int(amts[-1])
        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="getAmountsOut_error", router=router_addr, err=str(e))
        return None

    async def _usd_notional(self, amount_in: int, path: List[str], router_addr: str) -> Optional[Decimal]:
        # Try to value by converting to USDC via the same router path if possible
        try:
            src = path[0]
            if src in (USDC, USDT):
                d = self._decimals(src)
                return Decimal(amount_in) / Decimal(10**d)
            # attempt to append USDC to path if not already present
            new_path = path + [USDC] if path[-1] != USDC else path
            amt = await asyncio.to_thread(self.routers[router_addr].functions.getAmountsOut(amount_in, new_path).call)
            d = self._decimals(USDC)
            return Decimal(amt[-1]) / Decimal(10**d)
        except Exception:
            return None

    def _allowed_slippage_bps(self, min_out: int, expected_out: int) -> int:
        if expected_out <= 0:
            return 0
        # how much the trader is willing to lose vs current quote
        slip = (Decimal(expected_out) - Decimal(min_out)) / Decimal(expected_out)
        return int((slip * Decimal(10000)).quantize(Decimal("1")))

    def _backrun_gross_conservative(self, amount_in: int, path: List[str], expected_out: int, min_out: int) -> Decimal:
        """
        Conservative gross estimate using allowed slippage and a fraction of target size.
        If trader allows S bps slippage, assume we can capture ~ S/2 of that on a trade that is F of target size.
        gross ≈ notional_usd * (S_bps/10000) * 0.5 * F
        """
        # notional is computed separately; here we return a multiplier in bps to apply later
        s_bps = self._allowed_slippage_bps(min_out, expected_out)
        # capture factor 50% of their allowance at configured backrun fraction
        return Decimal(max(s_bps, 0)) / Decimal(10000) * Decimal("0.5") * BACKRUN_SIZE_FRACTION

    # -------- decoders --------

    def _decode_swap(self, tx_input: str) -> Optional[Tuple[str, int, int, List[str]]]:
        """
        Return (selector, amount_in, amount_out_min, path)
        Only supports common V2 swap selectors.
        """
        if not tx_input or len(tx_input) < 10:
            return None
        sel = tx_input[:10]
        data = bytes.fromhex(tx_input[10:]) if tx_input.startswith("0x") else bytes.fromhex(tx_input)

        try:
            if sel == SEL_swapExactTokensForTokens:
                # (uint amountIn, uint amountOutMin, address[] path, address to, uint deadline)
                amount_in, min_out, path, _, _ = abi_decode(
                    ["uint256", "uint256", "address[]", "address", "uint256"], data
                )
                return sel, int(amount_in), int(min_out), [Web3.to_checksum_address(p) for p in path]
            elif sel == SEL_swapExactETHForTokens:
                # (uint amountOutMin, address[] path, address to, uint deadline)
                # amount_in is tx.value (we won't have it from input only), mark as 0 to skip notional
                min_out, path, _, _ = abi_decode(["uint256", "address[]", "address", "uint256"], data)
                return sel, 0, int(min_out), [Web3.to_checksum_address(p) for p in path]
            elif sel == SEL_swapExactTokensForETH:
                # (uint amountIn, uint amountOutMin, address[] path, address to, uint deadline)
                amount_in, min_out, path, _, _ = abi_decode(["uint256", "uint256", "address[]", "address", "uint256"], data)
                return sel, int(amount_in), int(min_out), [Web3.to_checksum_address(p) for p in path]
            elif sel == SEL_swapTokensForExactTokens:
                # we ignore exact-out for now (harder to model); return None
                return None
            elif sel == SEL_swapETHForExactTokens:
                return None
        except Exception:
            return None
        return None

    # -------- publishing --------

    async def _publish(self, signals: List[MEVSignal]):
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
            MET_BEST_NET.set(max(s.est_net_usd for s in signals))
        else:
            MET_BEST_NET.set(0.0)

    # -------- scanners --------

    async def scan_block(self, block_number: int):
        """
        Pull full transactions for the block; filter by router allowlist; decode; compute signals.
        """
        start = time.perf_counter()
        signals: List[MEVSignal] = []
        try:
            block = await asyncio.to_thread(self.w3.eth.get_block, block_number, True)
            txs = block["transactions"] or []
            MET_LAST_BLOCK.set(block_number)

            native_usd = await self.native_usd()
            gas_price = self.w3.eth.gas_price
            gas_usd = (Decimal(gas_price) * Decimal(GAS_LIMIT_BACKRUN) / Decimal(1e18)) * native_usd
            flash_fee_factor = AAVE_FLASH_FEE_BPS / Decimal(10000)

            for tx in txs:
                to = tx.get("to")
                if not to:
                    continue
                to = Web3.to_checksum_address(to)
                if to not in self.routers:
                    continue

                # decode
                sel_amount_path = self._decode_swap(tx.get("input", "0x"))
                if not sel_amount_path:
                    continue
                selector, amount_in, min_out, path = sel_amount_path

                # supply ETH amount if selector used value (exactETHForTokens)
                if selector == SEL_swapExactETHForTokens and amount_in == 0:
                    amount_in = int(tx.get("value", 0))

                if amount_in <= 0 or len(path) < 2:
                    continue

                # expectedOut now
                expected_out = await self._expected_out(to, amount_in, path)
                if not expected_out or expected_out <= 0:
                    continue

                slippage_bps = self._allowed_slippage_bps(min_out, expected_out)
                if slippage_bps < MIN_ALLOWED_SLIPPAGE_BPS:
                    continue

                # USD notional
                notional = await self._usd_notional(amount_in, path, to)
                if notional is None or notional < MIN_NOTIONAL_USD:
                    continue

                # conservative gross capture factor
                capture_factor = self._backrun_gross_conservative(amount_in, path, expected_out, min_out)
                est_gross = notional * capture_factor

                flash_fee_usd = notional * flash_fee_factor
                est_net = est_gross - flash_fee_usd - gas_usd

                if est_net < Decimal(0):
                    continue

                sig = MEVSignal(
                    chain=CHAIN,
                    router=to,
                    router_name=ROUTERS[to],
                    tx_hash=tx["hash"].hex(),
                    from_addr=tx.get("from", ""),
                    path=[Web3.to_checksum_address(p) for p in path],
                    amount_in=str(amount_in),
                    min_out=str(min_out),
                    expected_out=str(expected_out),
                    allowed_slippage_bps=int(slippage_bps),
                    notional_usd=float(notional),
                    est_gross_usd=float(est_gross),
                    est_flash_fee_usd=float(flash_fee_usd),
                    est_gas_usd=float(gas_usd),
                    est_net_usd=float(est_net),
                    ts=int(time.time()),
                    block_number=block_number,
                )
                signals.append(sig)

        except Exception as e:
            MET_ERRORS.inc()
            jlog("error", event="scan_block_error", block=block_number, err=str(e))
        finally:
            MET_SCAN_LAT.observe(time.perf_counter() - start)

        if signals:
            # Sort by net descending, publish
            signals.sort(key=lambda s: s.est_net_usd, reverse=True)
            await self._publish(signals)
            jlog("info", event="mev_signals", count=len(signals), best=asdict(signals[0]))

    async def block_loop(self):
        last = self.w3.eth.block_number
        while True:
            try:
                if await self.paused():
                    await asyncio.sleep(1.0)
                    continue
                cur = self.w3.eth.block_number
                if cur > last:
                    for b in range(last + 1, cur + 1):
                        await self.scan_block(b)
                    last = cur
                await asyncio.sleep(BLOCK_POLL_SEC)
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="block_loop_error", err=str(e))
                await asyncio.sleep(1.0)

    # Optional mempool monitor (best-effort). Many providers gate mempool access.
    async def mempool_loop(self):
        import websockets
        if not MEMPOOL_ENABLED:
            return
        subscribe = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["newPendingTransactions"]})
        while True:
            try:
                async with websockets.connect(WSS_URL, ping_interval=20, ping_timeout=20) as ws:
                    await ws.send(subscribe)
                    async for msg in ws:
                        # We intentionally do not act on mempool pending txs beyond enrichment:
                        # they can be fetched and cached for the next block-level confirmation step.
                        _ = msg  # placeholder for enrichment; avoid heavy logic here
            except Exception as e:
                MET_ERRORS.inc()
                jlog("error", event="mempool_loop_error", err=str(e))
                await asyncio.sleep(3.0)

    async def run(self):
        start_http_server(METRICS_PORT)
        await self.init()
        jlog("info", event="mev_scanner_started", chain=CHAIN, routers=len(self.routers), mempool=MEMPOOL_ENABLED)

        tasks = [asyncio.create_task(self.block_loop())]
        if MEMPOOL_ENABLED:
            tasks.append(asyncio.create_task(self.mempool_loop()))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(MEVCaptureScanner().run())
    except KeyboardInterrupt:
        pass 