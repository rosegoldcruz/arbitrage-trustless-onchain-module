import time, random
from infra.redis_bus import Bus
bus = Bus()
def run():
    t=0
    while True:
        base = 100000 + random.randint(0,25000)
        burst = 600000 + random.randint(0,100000) if t % 15 == 0 else 0
        usdc = base + burst; usdt = base // 2
        bus.publish("flows.univ3", {"t": int(time.time()), "usdc_weth_5m_usd": str(usdc), "usdt_weth_5m_usd": str(usdt)})
        t+=1; time.sleep(3)
if __name__ == "__main__": run()
