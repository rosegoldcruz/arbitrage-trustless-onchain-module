#!/usr/bin/env python3
"""
Main FastAPI entrypoint for ATOM backend API.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config.secure_config import SecureConfig
from api import metrics

logger = logging.getLogger("backend.main")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()

# ------------------------------------------------------------------------------
# Rate limiting config
# ------------------------------------------------------------------------------
limiter = Limiter(key_func=lambda request: request.client.host)

RATE_LIMIT = _cfg.env.get("API_RATE_LIMIT", "100/minute")

# ------------------------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------------------------
app = FastAPI(
    title="ATOM Arbitrage API",
    version="1.0.0",
    description="Production arbitrage backend for ATOM",
)

# CORS from env
allowed_origins = _cfg.env.get("CORS_ALLOW_ORIGINS", "https://smart4technology.com,https://www.smart4technology.com").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Hosts
trusted_hosts = _cfg.env.get("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

@app.get("/")
async def root():
    return {"status": "ok", "service": "atom-backend-api"}
