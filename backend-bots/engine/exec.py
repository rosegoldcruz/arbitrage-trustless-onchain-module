import os
from decimal import Decimal
DRY = os.getenv("DRY_RUN","true").lower() == "true"
def try_dual_leg(usd_amount):
    usdc_in = Decimal(usd_amount)
    usdc_out = usdc_in * Decimal("1.0035")
    net_bps = (usdc_out - usdc_in) / usdc_in * Decimal(10000)
    if DRY:
        print(f"[dryrun] would trade {usd_amount} USDC -> net_bps={net_bps:.2f}")
        return (True, net_bps)
    return (False, Decimal(0))
