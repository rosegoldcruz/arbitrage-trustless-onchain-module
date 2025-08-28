#!/usr/bin/env python3
"""
Volatility Scanner API Router
- Exposes recent volatility signals and aggregate status from Redis stream produced by bots/volatility_scanner.py
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

import redis.asyncio as redis

logger = logging.getLogger("api.volatility")
router = APIRouter(prefix="/volatility", tags=["volatility"])

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
STREAM = os.getenv("VOL_REDIS_STREAM", "atom:opps:volatility")

_redis_client: Optional[redis.Redis] = None

async def _redis() -> redis.Redis:
  global _redis_client
  if _redis_client is None:
    _redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
  return _redis_client

@router.get("/signals", response_class=JSONResponse)
async def signals(limit: int = Query(50, ge=1, le=500)):
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
    logger.exception("signals error: %s", e)
    raise HTTPException(status_code=500, detail="failed to read signals")

@router.get("/status", response_class=JSONResponse)
async def status(limit: int = Query(200, ge=1, le=1000)):
  try:
    r = await _redis()
    entries = await r.xrevrange(STREAM, "+", "-", count=limit)
    best_conf = 0.0
    best_pnl = 0.0
    total = 0
    last_ts = 0
    for _id, fields in entries:
      data = fields.get("data")
      if not data:
        continue
      try:
        obj = json.loads(data)
        total += 1
        best_conf = max(best_conf, float(obj.get("confidence", 0.0)))
        best_pnl = max(best_pnl, float(obj.get("net_profit_usd", 0.0)))
        last_ts = max(last_ts, int(obj.get("ts", 0)))
      except Exception:
        continue
    return JSONResponse(content={
      "status": "ok",
      "total_recent": total,
      "best_confidence": best_conf,
      "best_net_profit_usd": best_pnl,
      "last_update": last_ts,
    })
  except Exception as e:
    logger.exception("status error: %s", e)
    raise HTTPException(status_code=500, detail="failed to compute status") 