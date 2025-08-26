#!/usr/bin/env python3
"""
Production Orchestrator - Coordinates all arbitrage system components.
Strict: no hardcoded RPCs, URLs, or keys. All via SecureConfig/.env.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict

import redis
import aiohttp

from config.secure_config import SecureConfig
from bots.production_opportunity_detector import ProductionOpportunityDetector
from bots.production_trade_executor import ProductionTradeExecutor
from bots.production_mev_protection import ProductionMEVProtection
from bots.profit_calculator import ProfitCalculator

logger = logging.getLogger("production_orchestrator")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()


class ProductionOrchestrator:
    def __init__(self):
        self.redis = redis.from_url(_cfg.require("REDIS_URL"), decode_responses=True)
        self.detector = ProductionOpportunityDetector()
        self.executor = ProductionTradeExecutor()
        self.profit_calc = ProfitCalculator()
        self.mev_protection = ProductionMEVProtection(self.executor.w3)

        self.running = False
        self.stats = {
            "start_time": time.time(),
            "opportunities_detected": 0,
            "trades_executed": 0,
            "total_profit_usd": 0.0,
            "last_trade_time": 0,
        }

        # Thresholds
        self.daily_profit_target = float(_cfg.env.get("DAILY_PROFIT_TARGET_USD", "500"))
        self.max_daily_loss = float(_cfg.env.get("MAX_DAILY_LOSS_USD", "200"))

        # Alert config
        self.discord_webhook = _cfg.env.get("DISCORD_WEBHOOK_URL")
        self.telegram_bot_token = _cfg.env.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = _cfg.env.get("TELEGRAM_CHAT_ID")

    async def send_alert(self, message: str, alert_type: str = "info"):
        color_map = {"info": 0x00ff00, "warning": 0xffff00, "error": 0xff0000, "success": 0x00ff00}
        logger.info(f"ALERT [{alert_type.upper()}]: {message}")

        if self.discord_webhook:
            try:
                embed = {
                    "title": "🤖 ATOM Production Alert",
                    "description": message,
                    "color": color_map.get(alert_type, 0x00ff00),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                async with aiohttp.ClientSession() as session:
                    await session.post(self.discord_webhook, json={"embeds": [embed]})
            except Exception as e:
                logger.error(f"Discord alert error: {e}")

    async def opportunity_processor(self):
        logger.info("🔍 Starting opportunity processor...")
        while self.running:
            try:
                opps = self.detector.get_best(limit=10)
                for opp in opps:
                    validation = self.profit_calc.validate_opportunity_realtime(opp)
                    if validation.get("profitable"):
                        # MEV risk
                        if not self.mev_protection.sandwich_detection_enabled:
                            self.redis.lpush("validated_opportunities", json.dumps(opp))
                            self.stats["opportunities_detected"] += 1
                            logger.info(f"✅ Validated opp: {opp['profit_bps']} bps")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Processor error: {e}")
                await asyncio.sleep(5)

    async def trade_monitor(self):
        logger.info("📊 Starting trade monitor...")
        while self.running:
            try:
                exec_stats = self.executor.get_stats()
                self.stats.update(
                    {
                        "trades_executed": exec_stats["total_trades"],
                        "total_profit_usd": exec_stats["total_profit_usd"],
                    }
                )
                if exec_stats["total_trades"] > 0:
                    self.stats["last_trade_time"] = time.time()

                snapshot = {
                    "timestamp": time.time(),
                    "uptime_hours": (time.time() - self.stats["start_time"]) / 3600,
                    "opportunities_detected": self.stats["opportunities_detected"],
                    "trades_executed": self.stats["trades_executed"],
                    "success_rate": exec_stats["success_rate"],
                    "total_profit_usd": self.stats["total_profit_usd"],
                    "current_wallet": exec_stats["current_wallet"],
                }
                self.redis.set("production_stats", json.dumps(snapshot))
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Trade monitor error: {e}")
                await asyncio.sleep(30)

    async def performance_analyzer(self):
        logger.info("📈 Starting performance analyzer...")
        last_alert = 0
        while self.running:
            try:
                profit = self._calculate_daily_profit()
                if profit >= self.daily_profit_target and time.time() - last_alert > 3600:
                    await self.send_alert(
                        f"🎉 Daily profit target reached: ${profit:.2f}", "success"
                    )
                    last_alert = time.time()
                if profit < -self.max_daily_loss:
                    await self.send_alert(f"🚨 Daily loss exceeded: ${profit:.2f}", "error")
                if time.time() - self.stats.get("last_trade_time", 0) > 3600:
                    await self.send_alert("⚠️ No trades executed in last hour", "warning")
                await asyncio.sleep(600)
            except Exception as e:
                logger.error(f"Performance analyzer error: {e}")
                await asyncio.sleep(600)

    def _calculate_daily_profit(self) -> float:
        cutoff = time.time() - 86400
        trades = self.redis.lrange("trade_history", 0, -1)
        total = 0.0
        for raw in trades:
            t = json.loads(raw)
            if t.get("timestamp", 0) > cutoff:
                total += t.get("net_profit_usd", 0)
        return total

    async def start(self):
        self.running = True
        await self.send_alert("🚀 ATOM Production System Starting", "info")
        logger.info("🚀 Starting orchestrator...")

        tasks = [
            asyncio.create_task(self.detector.scan(), name="detector"),
            asyncio.create_task(self.executor.start(), name="executor"),
            asyncio.create_task(self.opportunity_processor(), name="processor"),
            asyncio.create_task(self.trade_monitor(), name="monitor"),
            asyncio.create_task(self.performance_analyzer(), name="analyzer"),
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            self.running = False
            for t in tasks:
                t.cancel()

    def get_system_stats(self) -> Dict:
        uptime = time.time() - self.stats["start_time"]
        return {
            "system": {"uptime_hours": uptime / 3600, "status": "running" if self.running else "stopped"},
            "opportunities": {"total_detected": self.stats["opportunities_detected"]},
            "trading": self.executor.get_stats(),
            "performance": {
                "daily_profit_target": self.daily_profit_target,
                "daily_profit_actual": self._calculate_daily_profit(),
                "profit_per_hour": self.stats["total_profit_usd"] / (uptime / 3600) if uptime > 0 else 0,
            },
        }


if __name__ == "__main__":
    orch = ProductionOrchestrator()
    asyncio.run(orch.start())
