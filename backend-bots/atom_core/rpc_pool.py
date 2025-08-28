import os
import random
import asyncio
from typing import List, Callable, Awaitable, Any
from web3 import Web3, HTTPProvider

# Comma-separated list of HTTP RPC URLs
_RPCs: List[str] = [x.strip() for x in os.environ.get("ETH_RPC_URLS", "").split(",") if x.strip()]
if not _RPCs:
    # Fallback to individual chain RPC if provided
    for k in ["POLYGON_RPC_URL", "ETHEREUM_RPC_URL", "BASE_RPC_URL", "ARBITRUM_RPC_URL"]:
        v = os.environ.get(k)
        if v:
            _RPCs.append(v)

_PROVIDERS: List[Web3] = [Web3(HTTPProvider(u, request_kwargs={"timeout": 10})) for u in _RPCs]

async def choose_web3() -> Web3:
    """Pick a healthy provider by sampling the pool and verifying block access."""
    if not _PROVIDERS:
        raise RuntimeError("ETH_RPC_URLS not configured")
    for _ in range(len(_PROVIDERS)):
        w3 = random.choice(_PROVIDERS)
        try:
            # web3 is blocking; run in thread
            _ = await asyncio.to_thread(lambda: w3.eth.block_number)
            return w3
        except Exception:
            await asyncio.sleep(0.05)
            continue
    raise RuntimeError("All RPC endpoints failed")

async def with_w3(fn: Callable[[Web3], Awaitable[Any]]):
    """Run a coroutine factory with failover retries over the provider pool."""
    last_err: Exception | None = None
    if not _PROVIDERS:
        raise RuntimeError("ETH_RPC_URLS not configured")
    for _ in range(len(_PROVIDERS)):
        w3 = await choose_web3()
        try:
            return await fn(w3)
        except Exception as e:
            last_err = e
            await asyncio.sleep(0.5)
    if last_err:
        raise last_err
    raise RuntimeError("with_w3: unexpected failure") 