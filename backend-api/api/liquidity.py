#!/usr/bin/env python3
"""
Liquidity Mining API Router
- Serves ranked LP farming opportunities from Redis stream produced by bots/liquidity_mining.py
"""

import json
import logging
import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

import redis.asyncio as redis

logger = logging.getLogger("api.liquidity")
router = APIRouter(prefix="/liquidity", tags=["liquidity"]) 

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
STREAM = os.getenv("LM_REDIS_STREAM", "atom:opps:liquidity")

async def _redis() -> redis.Redis:
  return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

@router.get("/opportunities", response_class=JSONResponse)
async def opportunities(limit: int = Query(25, ge=1, le=200)):
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
    return JSONResponse(content={"status": "success", "data": {"opportunities": out, "count": len(out)}})
  except Exception as e:
    logger.exception("liquidity opportunities error: %s", e)
    raise HTTPException(status_code=500, detail="failed to read opportunities")

@router.get("/status", response_class=JSONResponse)
async def status(limit: int = Query(200, ge=1, le=1000)):
  try:
    r = await _redis()
    entries = await r.xrevrange(STREAM, "+", "-", count=limit)
    best_apr = 0.0
    total = 0
    last_ts = 0
    for _id, fields in entries:
      data = fields.get("data")
      if not data:
        continue
      try:
        obj = json.loads(data)
        total += 1
        best_apr = max(best_apr, float(obj.get("total_apr", 0.0)))
        last_ts = max(last_ts, int(obj.get("ts", 0)))
      except Exception:
        continue
    return JSONResponse(content={
      "status": "ok",
      "total_recent": total,
      "best_total_apr": best_apr,
      "last_update": last_ts,
    })
  except Exception as e:
    logger.exception("liquidity status error: %s", e)
    raise HTTPException(status_code=500, detail="failed to compute status") 