#!/usr/bin/env python3
"""
ATOM Arbitrage Orchestrator
Coordinates opportunity detection, execution, and system health.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict

from config.secure_config import SecureConfig
from backend_bots.infra.redis_bus import Bus
from bots.opportunity_detector import OpportunityDetector
from bots.trade_executor import TradeExecutor

logger = logging.getLogger("arbitrage_orchestrator")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()

class ArbitrageOrchestrator:
    def __init__(self):
        self.running = False
        self.detector = OpportunityDetector()
        self.executor = TradeExecutor()
        self.bus = Bus()
        self.stats = {
            "start_time": time.time(),
            "opportunities_detected": 0,
            "trades_executed": 0,
            "total_profit_usd": 0,
            "last_opportunity": None,
            "last_trade": None,
        }

        # Profit/loss thresholds from env
        self.daily_profit_target = float(_cfg.env.get("DAILY_PROFIT_TARGET_USD", "500"))
        self.max_daily_loss = float(_cfg.env.get("MAX_DAILY_LOSS_USD", "200"))
        self.health_check_interval = int(_cfg.env.get("HEALTH_CHECK_INTERVAL_SECONDS", "30"))

    async def opportunity_publisher(self):
        """Publish detected opportunities to Redis for executor"""
        logger.info("🔍 Starting opportunity publisher...")
        while self.running:
            try:
                opportunities = self.detector.get_best_opportunities(limit=5)
                for opp in opportunities:
                    self.bus.publish("arbitrage.opportunities", opp)
                    self.stats["opportunities_detected"] += 1
                    self.stats["last_opportunity"] = opp
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Publisher error: {e}")
                await asyncio.sleep(5)

    async def system_monitor(self):
        """Monitor system health and performance"""
        logger.info("📊 Starting system monitor...")
        while self.running:
            try:
                exec_stats = self.executor.get_stats()
                self.stats.update(
                    {
                        "trades_executed": exec_stats["total_trades"],
                        "total_profit_usd": exec_stats["total_profit_usd"],
                        "success_rate": exec_stats["success_rate"],
                    }
                )
                uptime = (time.time() - self.stats["start_time"]) / 3600
                current_stats = {
                    "timestamp": time.time(),
                    "uptime_hours": uptime,
                    "opportunities_detected": self.stats["opportunities_detected"],
                    "trades_executed": self.stats["trades_executed"],
                    "success_rate": exec_stats["success_rate"],
                    "total_profit_usd": self.stats["total_profit_usd"],
                }
                self.bus.publish("system.stats", current_stats)
                logger.info(json.dumps(current_stats))
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"System monitor error: {e}")
                await asyncio.sleep(30)

    async def start(self):
        """Start orchestrator"""
        self.running = True
        logger.info("🚀 Starting ATOM Arbitrage System...")
        tasks = [
            asyncio.create_task(self.detector.start(), name="detector"),
            asyncio.create_task(self.executor.start(), name="executor"),
            asyncio.create_task(self.opportunity_publisher(), name="publisher"),
            asyncio.create_task(self.system_monitor(), name="monitor"),
        ]
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.running = False
            for t in tasks:
                t.cancel()

    def get_system_stats(self) -> Dict:
        uptime = time.time() - self.stats["start_time"]
        return {
            "system": {
                "uptime_seconds": uptime,
                "status": "running" if self.running else "stopped",
            },
            "opportunities": {
                "total_detected": self.stats["opportunities_detected"],
                "last_opportunity": self.stats["last_opportunity"],
            },
            "trading": self.executor.get_stats(),
            "performance": {
                "daily_profit_target": self.daily_profit_target,
                "profit_actual": self.stats["total_profit_usd"],
            },
        }

if __name__ == "__main__":
    orchestrator = ArbitrageOrchestrator()
    asyncio.run(orchestrator.start())
