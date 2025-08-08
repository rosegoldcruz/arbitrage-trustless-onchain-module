"""
JSON-structured logging helpers for trade execution paths.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

_trade_logger = logging.getLogger("trade")
_trade_logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(message)s'))
if not any(isinstance(h, logging.StreamHandler) for h in _trade_logger.handlers):
    _trade_logger.addHandler(_handler)


def log_event(event: str, **fields: Any) -> None:
    payload: Dict[str, Any] = {"event": event, **fields}
    if "timestamp" not in payload:
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    _trade_logger.info(json.dumps(payload, default=str))

