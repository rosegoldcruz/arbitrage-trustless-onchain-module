#!/usr/bin/env python3
"""
Main FastAPI entrypoint for ATOM backend API.
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from api import metrics
from app.metrics_store import atom_api_requests_total, atom_arbitrage_opportunities_detected_total, atom_arbitrage_executions_total, atom_profit_usd_total, atom_gas_used_total, api_request_middleware, bootstrap_from_redis
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger("backend.main")
logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------------------------
# Rate limiting config
# ------------------------------------------------------------------------------
limiter = Limiter(key_func=lambda request: request.client.host)

RATE_LIMIT = os.getenv("API_RATE_LIMIT", "100/minute")

# ------------------------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------------------------
app = FastAPI(
    title="ATOM Arbitrage API",
    version="1.0.0",
    description="Production arbitrage backend for ATOM",
)

# CORS
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "https://dashboard.aeoninvestmentstechnologies.com")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
allow_credentials = False if origins == ["*"] else True
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Hosts
trusted_hosts_env = os.getenv("TRUSTED_HOSTS", "*")
trusted_hosts = [h.strip() for h in trusted_hosts_env.split(",") if h.strip()]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request metrics middleware
@app.middleware("http")
async def _metrics_middleware(request: Request, call_next):
    return await api_request_middleware(request, call_next)

# Bootstrap metrics from Redis on startup
@app.on_event("startup")
async def _bootstrap_metrics():
    try:
        await bootstrap_from_redis()
    except Exception:
        logger.info("metrics bootstrap skipped (redis unavailable)")

# Routers
app.include_router(metrics.router)
from api import addresses as addresses_router
app.include_router(addresses_router.router)
from api import stablecoin as stablecoin_router
app.include_router(stablecoin_router.router)
from api import volatility as volatility_router
app.include_router(volatility_router.router)
from api import triangular as triangular_router
app.include_router(triangular_router.router)
from api import mev as mev_router
app.include_router(mev_router.router)
from api import liquidity as liquidity_router
app.include_router(liquidity_router.router)
from api import stat_arb as stat_arb_router
app.include_router(stat_arb_router.router)
# Health router (v1)
try:
    from app.routers import health as health_router
    app.include_router(health_router.router)
except Exception:
    logger.info("health router not available; skipping")
# Admin router (protected)
try:
    from app.routers import admin as admin_router
    app.include_router(admin_router.router)
except Exception:
    logger.info("admin router not available; skipping")
# Protected API routers (/api/...)
try:
    from app.routers import trigger as trigger_router
    app.include_router(trigger_router.router)
except Exception:
    logger.info("trigger router not available; skipping")
try:
    from app.routers import dashboard as dashboard_router
    app.include_router(dashboard_router.router)
except Exception:
    logger.info("dashboard router not available; skipping")
try:
    from app.routers import internal_metrics as internal_metrics_router
    app.include_router(internal_metrics_router.router)
except Exception:
    logger.info("internal metrics router not available; skipping")

@app.get("/")
async def root():
    return {"status": "ok", "service": "atom-backend-api"}

@app.get("/health")
def health():
    return {"ok": True}

# Prometheus metrics endpoint
@app.get("/metrics")
async def prometheus_metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
