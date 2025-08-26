#!/usr/bin/env python3
"""
Prometheus metrics exporter for ATOM.
- Serves /metrics (Prometheus text) and /health (JSON).
- Optional HTTP Basic Auth via env:
    METRICS_BASIC_AUTH_USER
    METRICS_BASIC_AUTH_PASS
- Host/port via CLI flags (defaults: 127.0.0.1:9090).
- No global singletons; other modules just import prometheus_client and update metrics.
"""

import argparse
import base64
import json
import logging
import os
import signal
import sys
import threading
import time
from typing import Callable

from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
from prometheus_client import make_wsgi_app, Gauge, Counter

from config.secure_config import SecureConfig

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logger = logging.getLogger("prometheus_metrics")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

# ------------------------------------------------------------------------------
# Config (strict env loader available if you set creds)
# ------------------------------------------------------------------------------
_cfg = SecureConfig()  # does fail-fast validation for core env; safe to instantiate

_METRICS_USER = _cfg.env.get("METRICS_BASIC_AUTH_USER")  # optional
_METRICS_PASS = _cfg.env.get("METRICS_BASIC_AUTH_PASS")  # optional

if (_METRICS_USER and not _METRICS_PASS) or (_METRICS_PASS and not _METRICS_USER):
    logger.critical("Both METRICS_BASIC_AUTH_USER and METRICS_BASIC_AUTH_PASS must be set together if using auth.")
    sys.exit(1)

# ------------------------------------------------------------------------------
# Minimal built-in metrics (modules define their own elsewhere)
# ------------------------------------------------------------------------------
exporter_uptime_seconds = Gauge("exporter_uptime_seconds", "Uptime of the metrics exporter in seconds")
exporter_scrapes_total = Counter("exporter_scrapes_total", "Total scrapes served by this exporter")

# Background thread to bump uptime
def _uptime_loop(stop_evt: threading.Event):
    start = time.time()
    while not stop_evt.is_set():
        exporter_uptime_seconds.set(time.time() - start)
        stop_evt.wait(1.0)

# ------------------------------------------------------------------------------
# WSGI app with routing and optional basic auth
# ------------------------------------------------------------------------------
_metrics_app = make_wsgi_app()  # prometheus_client WSGI

def _basic_auth_ok(environ) -> bool:
    if not _METRICS_USER:
        # No auth configured; allow (typical for localhost-only scrape).
        return True
    header = environ.get("HTTP_AUTHORIZATION")
    if not header or not header.startswith("Basic "):
        return False
    try:
        userpass = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
        user, pwd = userpass.split(":", 1)
        return user == _METRICS_USER and pwd == _METRICS_PASS
    except Exception:
        return False

def _unauthorized(start_response: Callable):
    start_response("401 Unauthorized", [("Content-Type", "text/plain"), ("WWW-Authenticate", 'Basic realm="metrics"')])
    return [b"Unauthorized"]

def _json(start_response: Callable, status: str, obj: dict):
    body = json.dumps(obj).encode("utf-8")
    headers = [("Content-Type", "application/json"), ("Content-Length", str(len(body)))]
    start_response(status, headers)
    return [body]

def _not_found(start_response: Callable):
    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]

def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path == "/metrics":
        if not _basic_auth_ok(environ):
            return _unauthorized(start_response)
        exporter_scrapes_total.inc()
        return _metrics_app(environ, start_response)

    if path == "/health":
        if not _basic_auth_ok(environ):
            return _unauthorized(start_response)
        # You can extend this later to include deeper component health
        return _json(start_response, "200 OK", {"status": "ok", "ts": int(time.time())})

    return _not_found(start_response)

# ------------------------------------------------------------------------------
# Runner
# ------------------------------------------------------------------------------
class QuietHandler(WSGIRequestHandler):
    # Keep logs clean
    def log_message(self, format, *args):
        logger.info("%s - - %s", self.address_string(), format % args)

def run_server(host: str, port: int):
    with make_server(host, port, application, handler_class=QuietHandler) as httpd:
        logger.info("Serving Prometheus metrics on http://%s:%d/metrics", host, port)
        if _METRICS_USER:
            logger.info("Basic Auth enabled for /metrics and /health")
        stop_evt = threading.Event()
        t = threading.Thread(target=_uptime_loop, args=(stop_evt,), daemon=True)
        t.start()

        def _graceful_shutdown(signum, frame):
            logger.info("Shutting down metrics server...")
            stop_evt.set()
            httpd.shutdown()

        signal.signal(signal.SIGINT, _graceful_shutdown)
        signal.signal(signal.SIGTERM, _graceful_shutdown)

        httpd.serve_forever()

def parse_args():
    p = argparse.ArgumentParser(description="ATOM Prometheus metrics exporter")
    p.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=9090, help="Bind port (default: 9090)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        run_server(args.host, args.port)
    except Exception as e:
        logger.exception("Metrics server crashed: %s", e)
        sys.exit(1)
