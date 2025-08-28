import statistics
from backend_bots.atom_core.rpc_pool import with_w3

async def dynamic_gas_cap(multiplier: float = 1.20) -> int:
    def _job(w3):
        latest = w3.eth.block_number
        basefees = []
        for i in range(0, 5):
            b = w3.eth.get_block(latest - i)
            basefees.append(b.get('baseFeePerGas', 0))
        cap = int(statistics.median(basefees) * multiplier)
        return cap
    return await with_w3(lambda w3: _job(w3)) 