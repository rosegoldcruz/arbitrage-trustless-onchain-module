#!/usr/bin/env python3
"""
Security & Failsafe System for ATOM
- Emergency controls
- Automatic fund protection
- System health monitoring
STRICT: No hardcoded values. All from .env via SecureConfig.
"""

import asyncio
import json
import logging
import time
from decimal import Decimal
from typing import Dict, List, Callable

import redis
import aiohttp
from web3 import Web3

from config.secure_config import SecureConfig

logger = logging.getLogger("security_system")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class SecuritySystem:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.redis = redis.from_url(_cfg.require("REDIS_URL"), decode_responses=True)

        # Thresholds
        self.max_daily_loss = Decimal(_cfg.env.get("MAX_DAILY_LOSS_USD", "200"))
        self.max_single_trade_loss = Decimal(_cfg.env.get("MAX_SINGLE_TRADE_LOSS_USD", "50"))
        self.max_consecutive_failures = int(_cfg.env.get("MAX_CONSECUTIVE_FAILURES", "5"))
        self.wallet_balance_threshold = Decimal(_cfg.env.get("WALLET_BALANCE_THRESHOLD_USD", "10000"))

        # Emergency settings
        self.contract = _cfg.require("ATOM_CONTRACT_ADDRESS")
        self.emergency_webhook = _cfg.env.get("EMERGENCY_WEBHOOK_URL")

        # State
        self.running = False
        self.system_paused = False
        self.security_violations: List[Dict] = []
        self.callbacks: List[Callable] = []

    async def start(self):
        self.running = True
        logger.info("🛡️ Security system starting...")
        tasks = [
            asyncio.create_task(self._monitor_health()),
            asyncio.create_task(self._monitor_trading()),
            asyncio.create_task(self._check_emergencies()),
        ]
        await asyncio.gather(*tasks)

    async def _monitor_health(self):
        while self.running:
            try:
                status = {"rpc": self._check_rpc(), "redis": self._check_redis()}
                failed = [k for k, v in status.items() if not v["healthy"]]
                health = "healthy" if not failed else "critical"
                self.redis.set("system_health", json.dumps({"status": health, "checks": status, "t": time.time()}))
                if health == "critical":
                    await self._trigger("system_health", {"failed": failed})
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)

    async def _monitor_trading(self):
        while self.running:
            try:
                trades = self.redis.lrange("trade_history", 0, -1)
                total = len(trades)
                if not trades:
                    await asyncio.sleep(180)
                    continue
                daily_profit = sum(json.loads(t).get("net_profit_usd", 0) for t in trades if json.loads(t).get("timestamp", 0) > time.time() - 86400)
                if daily_profit < -float(self.max_daily_loss):
                    await self._trigger("daily_loss_exceeded", {"daily_profit": daily_profit})
                await asyncio.sleep(180)
            except Exception as e:
                logger.error(f"Trading monitor error: {e}")
                await asyncio.sleep(180)

    async def _check_emergencies(self):
        while self.running:
            try:
                for v in [v for v in self.security_violations if v.get("severity") == "critical"]:
                    await self._pause_system(f"Critical violation: {v['type']}")
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Emergency check error: {e}")
                await asyncio.sleep(60)

    def _check_rpc(self) -> Dict:
        try:
            bn = self.w3.eth.block_number
            return {"healthy": True, "block": bn}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    def _check_redis(self) -> Dict:
        try:
            self.redis.ping()
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _trigger(self, event: str, details: Dict):
        logger.critical(f"🚨 Emergency triggered: {event} {details}")
        violation = {"type": event, "details": details, "t": time.time(), "severity": "critical"}
        self.security_violations.append(violation)
        self.redis.lpush("security_violations", json.dumps(violation))
        self.redis.ltrim("security_violations", 0, 99)
        for cb in self.callbacks:
            await cb(event, details)
        await self._alert(event, details)

    async def _pause_system(self, reason: str):
        if self.system_paused:
            return
        self.system_paused = True
        self.redis.set("system_paused", json.dumps({"paused": True, "reason": reason, "t": time.time()}))
        await self._alert("SYSTEM PAUSED", {"reason": reason})

    async def _alert(self, title: str, details: Dict):
        if not self.emergency_webhook:
            return
        try:
            async with aiohttp.ClientSession() as s:
                await s.post(self.emergency_webhook, json={"embeds": [{"title": title, "description": json.dumps(details), "color": 0xFF0000}]})
        except Exception as e:
            logger.error(f"Alert send error: {e}")
