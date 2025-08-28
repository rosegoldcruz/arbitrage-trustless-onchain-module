import asyncio
from typing import Dict
from prometheus_client import Counter, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
from backend_bots.atom_core import get_redis

# Prometheus metrics
atom_api_requests_total = Counter("atom_api_requests_total", "API requests", ["method", "endpoint", "status"])
atom_arbitrage_opportunities_detected_total = Counter("atom_arbitrage_opportunities_detected_total", "Opportunities detected")
atom_arbitrage_executions_total = Counter("atom_arbitrage_executions_total", "Executions", ["status"])
atom_profit_usd_total = Counter("atom_profit_usd_total", "Cumulative profit in USD")
atom_gas_used_total = Counter("atom_gas_used_total", "Cumulative gas used (wei)")

# Redis keys for persistence
KEYS = {
    "opps": "metrics:atom:opps_total",
    "exec_ok": "metrics:atom:exec_ok_total",
    "exec_fail": "metrics:atom:exec_fail_total",
    "profit": "metrics:atom:profit_usd_total",
    "gas": "metrics:atom:gas_used_total",
}

async def bootstrap_from_redis():
    r = get_redis()
    async def _inc(counter, key: str, labels: Dict = None):
        val = await r.get(key)
        if val:
            amt = float(val)
            if labels:
                counter.labels(**labels).inc(amt)
            else:
                counter.inc(amt)
    await _inc(atom_arbitrage_opportunities_detected_total, KEYS["opps"])
    await _inc(atom_arbitrage_executions_total, KEYS["exec_ok"], labels={"status": "success"})
    await _inc(atom_arbitrage_executions_total, KEYS["exec_fail"], labels={"status": "failed"})
    await _inc(atom_profit_usd_total, KEYS["profit"])
    await _inc(atom_gas_used_total, KEYS["gas"])

async def persist_delta(kind: str, amount: float):
    r = get_redis()
    await r.incrbyfloat(KEYS[kind], amount)

async def api_request_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        endpoint = request.url.path
        method = request.method
        status = str(response.status_code)
        atom_api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    except Exception:
        pass
    return response 