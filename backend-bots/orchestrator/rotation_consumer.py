import os
from decimal import Decimal
from infra.redis_bus import Bus
from engine.exec import try_dual_leg
BUS = Bus()
MIN_BPS = Decimal(os.getenv("ATOM_MIN_PROFIT_THRESHOLD_BPS","23"))
def on_signal(msg):
    for usd in [5000, 10000, 20000]:
        ok, net_bps = try_dual_leg(usd)
        print(f"[orchestrator] attempt {usd} -> ok={ok} net_bps={net_bps}")
        if ok and net_bps >= MIN_BPS: break
def run(): BUS.subscribe("signals.rotation", on_signal)
if __name__ == "__main__": run()
