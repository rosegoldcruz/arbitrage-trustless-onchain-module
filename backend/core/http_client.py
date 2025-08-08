"""
Shared aiohttp client session for HTTP requests.
Ensures a single session is reused across the app lifetime.
"""
from __future__ import annotations
import asyncio
from typing import Optional

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None  # type: ignore

_session: Optional["aiohttp.ClientSession"] = None
_lock = asyncio.Lock()

async def get_session() -> "aiohttp.ClientSession":
    if aiohttp is None:
        raise RuntimeError("aiohttp is not installed")
    global _session
    if _session and not _session.closed:
        return _session
    async with _lock:
        if _session is None or _session.closed:
            _session = aiohttp.ClientSession()
    return _session

async def close_session():
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None

