#!/usr/bin/env python3
"""
Stablecoin Monitor API Router
- Serves opportunities and status from Redis stream produced by bots/stablecoin_monitor.py
"""

import json
import logging
import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

import redis.asyncio as redis

logger = logging.getLogger("api.stablecoin")
router = APIRouter(prefix="/stablecoin", tags=["stablecoin"])

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
STREAM = os.getenv("STABLESCAN_REDIS_STREAM", "atom:opps:stablecoin")

async def _redis() -> redis.Redis:
    return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

@router.get("/opportunities", response_class=JSONResponse)
async def opportunities(limit: int = Query(50, ge=1, le=500)):
    try:
        r = await _redis()
        # XREVRANGE stream from + to - with count
        entries = await r.xrevrange(STREAM, "+", "-", count=limit)
        out: List[Dict[str, Any]] = []
        for _id, fields in entries:
            data = fields.get("data")
            if not data:
                continue
            try:
                obj = json.loads(data)
                out.append(obj)
            except Exception as e:
                logger.exception("bad payload in stream: %s", e)
        return JSONResponse(content={"status": "success", "data": {"opportunities": out, "count": len(out)}})
    except Exception as e:
        logger.exception("opportunities error: %s", e)
        raise HTTPException(status_code=500, detail="failed to read opportunities")

@router.get("/status", response_class=JSONResponse)
async def status(limit: int = Query(100, ge=1, le=1000)):
    try:
        r = await _redis()
        entries = await r.xrevrange(STREAM, "+", "-", count=limit)
        best_net = 0.0
        best_spread = 0
        last_ts = 0
        total = 0
        for _id, fields in entries:
            data = fields.get("data")
            if not data:
                continue
            try:
                obj = json.loads(data)
                total += 1
                best_net = max(best_net, float(obj.get("net_profit_usd", 0.0)))
                best_spread = max(best_spread, int(obj.get("spread_bps", 0)))
                last_ts = max(last_ts, int(obj.get("ts", 0)))
            except Exception:
                continue
        return JSONResponse(content={
            "status": "ok",
            "total_recent": total,
            "best_net_profit_usd": best_net,
            "best_spread_bps": best_spread,
            "last_update": last_ts,
        })
    except Exception as e:
        logger.exception("status error: %s", e)
        raise HTTPException(status_code=500, detail="failed to compute status") 