# bots/bot_orchestrator.py
"""
ATOM Bot Orchestrator (production)
- Supervises all scanner bots as child processes (no signing here)
- Exponential backoff restarts with jitter and per-bot enable toggles
- Global kill switch + per-bot enable list (env)
- Optional health probes if metrics URLs provided
- Prometheus metrics + JSON logs
- Zero hardcoded secrets, all env-driven

IMPORTANT:
- Do not run individual bot systemd units if you're running the orchestrator.
- Orchestrator only supervises processes; bots remain headless scanners.
"""

import os
import sys
import asyncio
import signal
import time
import json
import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import aiohttp
import redis.asyncio as redis
from prometheus_client import Gauge, Counter, Histogram, start_http_server

# ---------------- Env helpers ----------------

def _env(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or str(v).strip() == ""):
        raise RuntimeError(f"Missing required env: {name}")
    return "" if v is None else str(v)

WORKDIR = _env("ATOM_WORKDIR", os.getcwd())
PYTHON_BIN = _env("ORCH_PYTHON_BIN", "/opt/atom-venv/bin/python")
ORCH_METRICS_PORT = int(_env("ORCH_METRICS_PORT", "9120"))
REDIS_URL = _env("REDIS_URL", "redis://127.0.0.1:6379/0")
KILL_SWITCH_KEY = _env("KILL_SWITCH_KEY", "atom:kill_switch")

# Enable only these bots (comma separated); default runs them all
DEFAULT_BOTS = "stablecoin,volatility,liquidation,triangular,cross_chain,mev,liquidity,stat_arb,nft"
ENABLED_BOTS = [b.strip() for b in _env("ORCH_ENABLED_BOTS", DEFAULT_BOTS).split(",") if b.strip()]

# Optional per-bot metrics URL overrides (http://host:port/metrics)
# You can set ORCH_<BOT>_METRICS_URL to enable readiness probe for that bot.

def _murl(name: str) -> Optional[str]:
    return os.getenv(f"ORCH_{name.upper()}_METRICS_URL", "").strip() or None

# ---------------- Logging ----------------

log = logging.getLogger("atom.orchestrator")
_hdlr = logging.StreamHandler(sys.stdout)
_hdlr.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(_hdlr)
log.setLevel(logging.INFO)

def jlog(level: str, **kw):
    getattr(log, level.lower())(json.dumps(kw, separators=(",", ":")))

# ---------------- Metrics ----------------

MET_ORCH_UP = Gauge("atom_orch_up", "Orchestrator process up (1/0)")
MET_KILL = Gauge("atom_orch_kill_switch", "Kill switch active (1/0)")
MET_BOT_UP = Gauge("atom_orch_bot_up", "Bot up (1/0)", ["bot"])
MET_BOT_RESTARTS = Counter("atom_orch_bot_restarts_total", "Bot restarts", ["bot"])
MET_BOT_LAST_START = Gauge("atom_orch_bot_last_start_ts", "Bot last start ts", ["bot"])
MET_BOT_LAST_EXIT = Gauge("atom_orch_bot_last_exit_ts", "Bot last exit ts", ["bot"])
MET_BOT_BACKOFF = Gauge("atom_orch_bot_backoff_seconds", "Backoff seconds", ["bot"])
MET_LOOP_LAT = Histogram("atom_orch_control_loop_seconds", "Control loop latency")

# ---------------- Bot spec ----------------

@dataclass
class BotSpec:
    name: str
    cmd: List[str]
    env_overrides: Dict[str, str] = field(default_factory=dict)
    metrics_url: Optional[str] = None
    enabled: bool = True
    backoff_initial: float = 2.0
    backoff_max: float = 60.0
    proc: Optional[asyncio.subprocess.Process] = None
    backoff: float = 0.0
    stopping: bool = False

# ---------------- Orchestrator ----------------

class Orchestrator:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.stopping = False
        self.specs: Dict[str, BotSpec] = self._build_specs()

    def _build_specs(self) -> Dict[str, BotSpec]:
        """
        Map bot keys to subprocess commands. Relative paths are from WORKDIR.
        Override PYTHON_BIN via ORCH_PYTHON_BIN if needed.
        """
        bots: Dict[str, BotSpec] = {}

        def mk(name: str, script: str):
            return BotSpec(
                name=name,
                cmd=[PYTHON_BIN, "-u", os.path.join(WORKDIR, script)],
                env_overrides={},  # inherit full env; bots read their own vars
                metrics_url=_murl(name),
                enabled=(name in ENABLED_BOTS)
            )

        bots["stablecoin"]  = mk("stablecoin",  "bots/stablecoin_monitor.py")
        bots["volatility"]  = mk("volatility",  "bots/volatility_scanner.py")
        bots["liquidation"] = mk("liquidation", "bots/liquidation_bot.py")
        bots["triangular"]  = mk("triangular",  "bots/triangular_arbitrage.py")
        bots["cross_chain"] = mk("cross_chain", "bots/cross_chain_arbitrage.py")
        bots["mev"]         = mk("mev",         "bots/mev_capture.py")
        bots["liquidity"]   = mk("liquidity",   "bots/liquidity_mining.py")
        bots["stat_arb"]    = mk("stat_arb",    "bots/statistical_arbitrage.py")
        bots["nft"]         = mk("nft",         "bots/nft_arbitrage.py")

        # mark disabled ones (not in ORCH_ENABLED_BOTS)
        for n, s in bots.items():
            MET_BOT_UP.labels(n).set(0)
            MET_BOT_BACKOFF.labels(n).set(0)
            MET_BOT_LAST_START.labels(n).set(0)
            MET_BOT_LAST_EXIT.labels(n).set(0)
            if not s.enabled:
                jlog("info", event="bot_disabled", bot=n)
        return bots

    async def init(self):
        start_http_server(ORCH_METRICS_PORT)
        MET_ORCH_UP.set(1)
        self.redis = await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        jlog("info", event="orchestrator_init", workdir=WORKDIR, python=PYTHON_BIN, bots=list(self.specs.keys()))

    async def close(self):
        if self.session:
            try:
                await self.session.close()
            except Exception:
                pass
        if self.redis:
            try:
                await self.redis.close()
            except Exception:
                pass
        MET_ORCH_UP.set(0)

    async def kill_switch_active(self) -> bool:
        try:
            if not self.redis:
                return False
            v = await self.redis.get(KILL_SWITCH_KEY)
            active = v == "1"
            MET_KILL.set(1 if active else 0)
            return active
        except Exception:
            MET_KILL.set(0)
            return False

    async def _start_bot(self, spec: BotSpec):
        if spec.proc or not spec.enabled:
            return
        try:
            env = os.environ.copy()
            env.update(spec.env_overrides)
            spec.proc = await asyncio.create_subprocess_exec(
                *spec.cmd,
                cwd=WORKDIR,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            spec.backoff = 0.0
            MET_BOT_UP.labels(spec.name).set(1)
            MET_BOT_LAST_START.labels(spec.name).set(time.time())
            jlog("info", event="bot_start", bot=spec.name, pid=spec.proc.pid, cmd=" ".join(spec.cmd))
            asyncio.create_task(self._pump_output(spec))
            # optional readiness probe
            if spec.metrics_url:
                asyncio.create_task(self._probe_ready(spec))
        except Exception as e:
            jlog("error", event="bot_start_error", bot=spec.name, err=str(e))
            await self._schedule_restart(spec)

    async def _pump_output(self, spec: BotSpec):
        # Stream child stdout/stderr as JSON-wrapped lines
        async def _reader(stream, stream_name):
            try:
                while not self.stopping and spec.proc and stream:
                    line = await stream.readline()
                    if not line:
                        break
                    try:
                        s = line.decode(errors="ignore").rstrip("\n")
                        jlog("info", bot=spec.name, stream=stream_name, msg=s)
                    except Exception:
                        pass
            except Exception as e:
                jlog("error", event="pump_error", bot=spec.name, err=str(e))
        if spec.proc:
            asyncio.create_task(_reader(spec.proc.stdout, "stdout"))
            asyncio.create_task(_reader(spec.proc.stderr, "stderr"))

    async def _probe_ready(self, spec: BotSpec):
        # Poll metrics endpoint a few times to log readiness
        if not self.session or not spec.metrics_url:
            return
        for _ in range(5):
            if not spec.proc:
                return
            try:
                async with self.session.get(spec.metrics_url) as r:
                    if r.status == 200:
                        jlog("info", event="bot_ready", bot=spec.name, metrics=spec.metrics_url)
                        return
            except Exception:
                await asyncio.sleep(1.0)
        jlog("info", event="bot_ready_unknown", bot=spec.name)

    async def _schedule_restart(self, spec: BotSpec):
        # Exponential backoff with jitter
        if spec.backoff == 0.0:
            spec.backoff = spec.backoff_initial
        else:
            spec.backoff = min(spec.backoff * 2.0, spec.backoff_max)
        delay = spec.backoff + random.uniform(0, min(1.0, spec.backoff))
        MET_BOT_BACKOFF.labels(spec.name).set(delay)
        jlog("info", event="bot_backoff", bot=spec.name, delay=round(delay, 2))
        await asyncio.sleep(delay)
        await self._start_bot(spec)

    async def _stop_bot(self, spec: BotSpec, reason: str = "stop"):
        # Graceful terminate
        if not spec.proc:
            return
        try:
            spec.stopping = True
            jlog("info", event="bot_stop", bot=spec.name, reason=reason)
            spec.proc.terminate()
            try:
                await asyncio.wait_for(spec.proc.wait(), timeout=15)
            except asyncio.TimeoutError:
                jlog("info", event="bot_kill", bot=spec.name)
                spec.proc.kill()
                await spec.proc.wait()
        finally:
            MET_BOT_UP.labels(spec.name).set(0)
            MET_BOT_LAST_EXIT.labels(spec.name).set(time.time())
            spec.proc = None
            spec.stopping = False

    async def _watch_bot(self, spec: BotSpec):
        # Wait for process exit and schedule restart
        if not spec.proc:
            return
        rc = await spec.proc.wait()
        MET_BOT_UP.labels(spec.name).set(0)
        MET_BOT_LAST_EXIT.labels(spec.name).set(time.time())
        jlog("info", event="bot_exit", bot=spec.name, returncode=rc)
        spec.proc = None
        if not self.stopping and spec.enabled:
            MET_BOT_RESTARTS.labels(spec.name).inc()
            await self._schedule_restart(spec)

    async def control_loop(self):
        await self.init()

        loop = asyncio.get_event_loop()

        # graceful shutdown
        def _sig_handler():
            self.stopping = True
            jlog("info", event="orchestrator_shutdown_signal")
        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(s, _sig_handler)
            except NotImplementedError:
                # Windows fallback
                pass

        # initial starts
        for spec in self.specs.values():
            if spec.enabled:
                await self._start_bot(spec)
                asyncio.create_task(self._watch_bot(spec))

        # supervise
        while not self.stopping:
            t0 = time.perf_counter()
            try:
                # Kill switch: stop all if active, resume when cleared
                if await self.kill_switch_active():
                    for spec in self.specs.values():
                        if spec.proc:
                            await self._stop_bot(spec, reason="kill_switch")
                else:
                    # ensure enabled bots are running
                    for spec in self.specs.values():
                        if not spec.enabled:
                            if spec.proc:
                                await self._stop_bot(spec, reason="disabled")
                            continue
                        if not spec.proc:
                            await self._start_bot(spec)
                            asyncio.create_task(self._watch_bot(spec))
                await asyncio.sleep(2.0)
            except Exception as e:
                jlog("error", event="control_loop_error", err=str(e))
                await asyncio.sleep(2.0)
            finally:
                MET_LOOP_LAT.observe(time.perf_counter() - t0)

        # shutdown
        for spec in self.specs.values():
            try:
                await self._stop_bot(spec, reason="shutdown")
            except Exception:
                pass
        await self.close()

# Entrypoint
if __name__ == "__main__":
    try:
        asyncio.run(Orchestrator().control_loop())
    except KeyboardInterrupt:
        pass 