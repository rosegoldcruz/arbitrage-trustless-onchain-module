#!/usr/bin/env python3
"""
ATOM Monitoring System
- Tracks profit, trades, success rates
- Pushes metrics into Redis for dashboard & Prometheus
- Raises alerts on thresholds
"""

import asyncio
import json
import logging
import time
from collections import deque
from typing import Dict, List

import redis
from config.secure_config import SecureConfig

logger = logging.getLogger("monitoring_system")
logging.basicConfig(level=logging.INFO)

_cfg = SecureConfig()
REDIS_URL = _cfg.require("REDIS_URL")


class MonitoringSystem:
    def __init__(self):
        self.r = redis.from_url(REDIS_URL, decode_responses=True)
        self.update_interval = int(_cfg.env.get("MONITORING_UPDATE_INTERVAL", "60"))
        self.alert_thresholds = {
            "min_success_rate": float(_cfg.env.get("ALERT_MIN_SUCCESS_RATE", "0.5")),
            "max_daily_loss": float(_cfg.env.get("MAX_DAILY_LOSS_USD", "200")),
            "min_hourly_opportunities": int(_cfg.env.get("ALERT_MIN_HOURLY_OPPORTUNITIES", "5")),
            "max_gas_cost_ratio": float(_cfg.env.get("ALERT_MAX_GAS_COST_RATIO", "0.3")),
        }

        self.metrics = {
            "system_start_time": time.time(),
            "total_trades": 0,
            "successful_trades": 0,
            "total_profit_usd": 0.0,
            "total_gas_cost_usd": 0.0,
            "last_trade_time": 0,
        }
        self.performance_history = deque(maxlen=1440)
        self.alert_history = deque(maxlen=200)
        self.running = False

    async def start(self):
        self.running = True
        logger.info("📊 Monitoring system starting...")
        tasks = [
            asyncio.create_task(self._collect_metrics()),
            asyncio.create_task(self._check_alerts()),
        ]
        await asyncio.gather(*tasks)

    async def _collect_metrics(self):
        while self.running:
            try:
                trade_history_raw = self.r.lrange("trade_history", 0, -1)
                trades = [json.loads(t) for t in trade_history_raw]

                self.metrics["total_trades"] = len(trades)
                self.metrics["successful_trades"] = sum(1 for t in trades if t.get("success"))
                self.metrics["total_profit_usd"] = sum(t.get("net_profit_usd", 0) for t in trades)
                self.metrics["total_gas_cost_usd"] = sum(t.get("gas_cost_usd", 0) for t in trades)
                self.metrics["last_trade_time"] = max((t.get("timestamp", 0) for t in trades), default=0)

                self.metrics["success_rate"] = (
                    self.metrics["successful_trades"] / self.metrics["total_trades"]
                    if self.metrics["total_trades"] > 0
                    else 0
                )
                self.metrics["net_profit_usd"] = (
                    self.metrics["total_profit_usd"] - self.metrics["total_gas_cost_usd"]
                )
                self.metrics["uptime_hours"] = (time.time() - self.metrics["system_start_time"]) / 3600

                self.r.set("monitoring_metrics", json.dumps(self.metrics))
                self.performance_history.append(
                    {"t": time.time(), "profit": self.metrics["net_profit_usd"]}
                )
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)

    async def _check_alerts(self):
        while self.running:
            try:
                alerts = []

                if (
                    self.metrics["total_trades"] > 10
                    and self.metrics["success_rate"] < self.alert_thresholds["min_success_rate"]
                ):
                    alerts.append("Low success rate")

                if self.metrics["net_profit_usd"] < -self.alert_thresholds["max_daily_loss"]:
                    alerts.append("Daily loss exceeded")

                gas_ratio = (
                    self.metrics["total_gas_cost_usd"] / self.metrics["total_profit_usd"]
                    if self.metrics["total_profit_usd"] > 0
                    else 0
                )
                if gas_ratio > self.alert_thresholds["max_gas_cost_ratio"]:
                    alerts.append("High gas cost ratio")

                for a in alerts:
                    alert = {"t": time.time(), "msg": a}
                    self.alert_history.append(alert)
                    self.r.lpush("system_alerts", json.dumps(alert))
                    self.r.ltrim("system_alerts", 0, 99)
                    logger.warning(f"⚠️ ALERT: {a}")

                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Alert check error: {e}")
                await asyncio.sleep(300)

    def get_report(self) -> Dict:
        return {
            "summary": self.metrics,
            "alerts": list(self.alert_history)[-10:],
            "generated_at": time.time(),
        }


if __name__ == "__main__":
    ms = MonitoringSystem()
    asyncio.run(ms.start())
