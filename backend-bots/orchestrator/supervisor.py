import os
import asyncio
import logging
from typing import Any, Dict, List, Tuple

from prometheus_client import Counter, Gauge

from backend_bots.atom_core import get_redis
from backend_bots.atom_core.rpc_pool import with_w3
from backend_bots.atom_core.safe_async import guard, CircuitBreaker
from backend_bots.atom_core.gas import dynamic_gas_cap

log = logging.getLogger("atom.supervisor")
logging.basicConfig(level=logging.INFO)

STREAMS: List[Tuple[str, str]] = [
    (os.getenv("ARB_STREAM", "atom:signals"), "arb"),
    (os.getenv("MEV_STREAM", "atom:opps:mev"), "mev"),
]
BREAKER = CircuitBreaker(fail_max=5, reset_after=30)

signals_total = Counter("atom_signals_total", "Total signals consumed", ["stream"])
signals_fail_total = Counter("atom_signals_fail_total", "Total failed signal processing", ["stream"])
last_signal_ts = Gauge("atom_last_signal_ts", "Unix ts of last signal", ["stream"])
current_gas_cap = Gauge("atom_gas_cap_wei", "Current dynamic gas cap in wei")

async def handle_signal(kind: str, sig: Dict[str, Any]):
    cap = await dynamic_gas_cap()
    current_gas_cap.set(cap)
    async def _job(w3):
        # TODO: validate route using w3, slippage, profit checks
        _ = w3.eth.chain_id
        return True
    return await guard(with_w3(_job), timeout=15, retries=2, breaker=BREAKER)

async def main():
    r = get_redis()
    last_ids = {name: "$" for name, _ in STREAMS}
    while True:
        await asyncio.sleep(0)  # yield
        for stream, label in STREAMS:
            resp = await r.xread({stream: last_ids[stream]}, count=10, block=100)
            if not resp:
                continue
            _, entries = resp[0]
            for entry_id, fields in entries:
                try:
                    await handle_signal(label, fields)
                    signals_total.labels(stream=label).inc()
                    last_signal_ts.labels(stream=label).set(float(entry_id.split("-")[0]) / 1000.0)
                    last_ids[stream] = entry_id
                except Exception as e:
                    signals_fail_total.labels(stream=label).inc()
                    log.exception("signal %s/%s failed: %s", label, entry_id, e)

if __name__ == "__main__":
    asyncio.run(main()) 