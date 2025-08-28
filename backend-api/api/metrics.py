#!/usr/bin/env python3
"""
Metrics API Router
- Serves JSON API metrics and Prometheus scrape endpoint.
"""

import logging
from fastapi import APIRouter, Depends
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response, JSONResponse

from config.secure_config import SecureConfig
# Removed side-effectful import from backend_bots.prometheus_metrics

logger = logging.getLogger("api.metrics")
router = APIRouter(prefix="/metrics", tags=["metrics"])

_cfg = SecureConfig()

@router.get("/health", response_class=JSONResponse)
async def health():
    """
    Basic health check.
    """
    return {"status": "ok"}

@router.get("/prometheus")
async def prometheus_metrics():
    """
    Prometheus metrics scrape endpoint.
    """
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@router.get("/status")
async def status():
    """
    Structured system status (expand with Redis/DB signals later).
    """
    return {
        "rpc_endpoints": {
            "polygon": _cfg.get_rpc_url("polygon"),
            "ethereum": _cfg.get_rpc_url("ethereum"),
            "base": _cfg.get_rpc_url("base"),
            "arbitrum": _cfg.get_rpc_url("arbitrum"),
        },
        "wallet_address": "hidden",  # do not expose private addresses here
    }
