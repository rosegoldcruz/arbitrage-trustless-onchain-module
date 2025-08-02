"""
🤖 ATOM Telegram Notification System
Real-time alerts for arbitrage opportunities, depegs, and system events
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from urllib.parse import quote
import aiohttp
import json

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class AlertType(Enum):
    ARBITRAGE_OPPORTUNITY = "arbitrage_opportunity"
    HIGH_PROFIT = "high_profit"
    DEPEG_DETECTED = "depeg_detected"
    TRADE_EXECUTED = "trade_executed"
    TRADE_FAILED = "trade_failed"
    SYSTEM_ERROR = "system_error"
    BOT_STATUS = "bot_status"
    SECURITY_ALERT = "security_alert"
    MANUAL_APPROVAL = "manual_approval"

@dataclass
class TelegramAlert:
    message: str
    alert_type: AlertType = AlertType.BOT_STATUS
    timestamp: Optional[datetime] = None

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️ Telegram credentials not configured - notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Telegram notifier active")

        self.pending_approvals: Dict[str, TelegramAlert] = {}
        self.last_message_time = {}
        self.rate_limit_seconds = 2

    async def send_alert(self, alert: TelegramAlert) -> bool:
        """Send alert to Telegram"""
        if not self.enabled:
            logger.debug("Telegram notifications disabled")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": f"📢 {alert.alert_type.name.replace('_', ' ').title()}:\n\n{alert.message}",
            "parse_mode": "HTML"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/sendMessage", data=payload) as resp:
                    if resp.status != 200:
                        logger.warning(f"Telegram send failed: {resp.status}")
                        return False
                    logger.info("✅ Telegram alert sent")
                    return True
        except Exception as e:
            logger.error(f"Telegram send exception: {str(e)}")
            return False

# Exported singleton
telegram_notifier = TelegramNotifier()
