import os
from decimal import Decimal
from infra.redis_bus import Bus
BUS = Bus()
FLOW_MIN = Decimal(os.getenv("ROTATION_FLOW_USD_MIN","500000"))
SLIP_MIN = Decimal(os.getenv("ROTATION_SLIPPAGE_BPS_MIN","15"))
SIM = os.getenv("ROTATION_SIMULATE","true").lower() == "true"
def on_flow(msg):
    usdc5 = Decimal(msg.get("usdc_weth_5m_usd","0")); usdt5 = Decimal(msg.get("usdt_weth_5m_usd","0"))
    flow = usdc5 + usdt5
    if flow < FLOW_MIN: return
    slip_bps = Decimal(20 if SIM else 0)
    if slip_bps >= SLIP_MIN:
        BUS.publish("signals.rotation", {"t": int(time.time()), "flow_5m_usd": str(flow), "slippage_bps": str(slip_bps)})
def run(): BUS.subscribe("flows.univ3", on_flow)
if __name__ == "__main__": run()
