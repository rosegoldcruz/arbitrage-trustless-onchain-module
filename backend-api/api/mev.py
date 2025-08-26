#!/usr/bin/env python3
"""
MEV Signals API Router
- Serves recent MEV signals produced by bots/mev_capture.py from Redis stream
"""

import json
import logging
import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

import redis.asyncio as redis

logger = logging.getLogger("api.mev")
router = APIRouter(prefix="/mev", tags=["mev"]) 

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
STREAM = os.getenv("MEV_REDIS_STREAM", "atom:opps:mev")

async def _redis() -> redis.Redis:
  return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

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
    logger.exception("mev signals error: %s", e)
    raise HTTPException(status_code=500, detail="failed to read mev signals")

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
        best = max(best, float(obj.get("est_net_usd", 0.0)))
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
    logger.exception("mev status error: %s", e)
    raise HTTPException(status_code=500, detail="failed to compute mev status") 