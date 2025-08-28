#!/usr/bin/env python3
"""
Triangular Arbitrage API Router
- Reads recent triangular arbitrage signals from Redis stream produced by bots/triangular_arbitrage.py
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

import redis.asyncio as redis

logger = logging.getLogger("api.triangular")
router = APIRouter(prefix="/triangular", tags=["triangular"]) 

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
STREAM = os.getenv("TRI_REDIS_STREAM", "atom:opps:triangular")

_redis_client: Optional[redis.Redis] = None

async def _redis() -> redis.Redis:
  global _redis_client
  if _redis_client is None:
    _redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
  return _redis_client

@router.get("/signals", response_class=JSONResponse)
async def signals(limit: int = Query(25, ge=1, le=200)):
  try:
    r = await _redis()
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
    return JSONResponse(content={"status": "success", "data": {"signals": out, "count": len(out)}})
  except Exception as e:
    logger.exception("tri signals error: %s", e)
    raise HTTPException(status_code=500, detail="failed to read tri signals")

@router.get("/status", response_class=JSONResponse)
async def status(limit: int = Query(200, ge=1, le=1000)):
  try:
    r = await _redis()
    entries = await r.xrevrange(STREAM, "+", "-", count=limit)
    best = 0.0
    total = 0
    last_ts = 0
    for _id, fields in entries:
      data = fields.get("data")
      if not data:
        continue
      try:
        obj = json.loads(data)
        total += 1
        best = max(best, float(obj.get("net_profit_usd", 0.0)))
        last_ts = max(last_ts, int(obj.get("ts", 0)))
      except Exception:
        continue
    return JSONResponse(content={
      "status": "ok",
      "total_recent": total,
      "best_net_profit_usd": best,
      "last_update": last_ts,
    })
  except Exception as e:
    logger.exception("tri status error: %s", e)
    raise HTTPException(status_code=500, detail="failed to compute tri status") 