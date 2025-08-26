#!/usr/bin/env python3
"""
Rotation Consumer
⚠️ This is a diagnostic subscriber only — not part of core execution.

Listens to Redis channels and logs structured messages.
Useful for debugging bus events without interfering with production bots.
"""

import json
import logging
from backend_bots.infra.redis_bus import Bus

logger = logging.getLogger("orchestrator.rotation_consumer")
logging.basicConfig(level=logging.INFO)

CHANNEL = "flows.univ3"  # example, adjust to your production bus channel

def handle_message(msg: dict):
    try:
        logger.info(f"[rotation_consumer] {json.dumps(msg)}")
    except Exception as e:
        logger.error(f"Failed to log message: {e}")

def run():
    bus = Bus()
    bus.subscribe(CHANNEL, handle_message)

if __name__ == "__main__":
    run()
