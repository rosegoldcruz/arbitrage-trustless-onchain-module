# backend-api/utils/stream_router.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Tuple
import os, json
from backend_api.deps.redis_pool import redis_client

def _coerce_messages(raw: List[Tuple[str, List[Tuple[str, Dict[str, str]]]]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for stream, msgs in raw:
        for msg_id, fields in msgs:
            try:
                payload = fields.get("data") or fields.get("payload") or fields
                if isinstance(payload, str):
                    payload = json.loads(payload)
            except Exception:
                payload = fields
            out.append({"id": msg_id, "stream": stream, "data": payload})
    return out

def _resolve_stream(env_key: str, fallback: str) -> str:
    # Each router can set a specific env var; otherwise fallback
    from backend_api.app.config import settings
    return getattr(settings, env_key, None) or fallback

def build_stream_router(
    name: str,
    env_key: str,
    fallback_stream: str,
) -> APIRouter:
    """
    Creates a deduplicated router exposing:
      GET /{name}/latest?count=50
      GET /{name}/range?start=-&end=+&count=100
    Reads from a Redis Stream whose key is resolved from env_key or fallback_stream.
    """
    router = APIRouter(prefix=f"/{name}", tags=[name.upper()])
    stream_key = _resolve_stream(env_key, fallback_stream)

    @router.get("/latest")
    async def latest(count: int = Query(50, ge=1, le=500)) -> List[Dict[str, Any]]:
        try:
            # XREVRANGE gets most recent entries first
            raw = await redis_client.xrevrange(stream_key, count=count)
            # Normalize shape to match _coerce_messages
            shaped = [(stream_key, [(mid, data) for mid, data in raw])]
            return _coerce_messages(shaped)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"redis latest error: {type(e).__name__}: {e}")

    @router.get("/range")
    async def range_read(
        start: str = Query("-", description="Start ID (inclusive), '-' for beginning"),
        end: str = Query("+", description="End ID (inclusive), '+' for latest"),
        count: int = Query(100, ge=1, le=1000),
    ) -> List[Dict[str, Any]]:
        try:
            raw = await redis_client.xrange(stream_key, min=start, max=end, count=count)
            shaped = [(stream_key, [(mid, data) for mid, data in raw])]
            return _coerce_messages(shaped)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"redis range error: {type(e).__name__}: {e}")

    return router