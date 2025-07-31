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

import aiohttp
import json
from urllib.parse import quote

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

class Priority(Enum):
    LOW = "🟢"
    NORMAL = "🟡"
    HIGH = "🟠"
    CRITICAL = "🔴"

@dataclass
class TelegramAlert:
    alert_type: AlertType
    priority: Priority
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    requires_approval: bool = False
    approval_timeout: int = 300  # 5 minutes

class TelegramNotifier:
    """
    🚀 PRODUCTION TELEGRAM NOTIFIER
    Sends real-time alerts for ATOM arbitrage system
    """
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️ Telegram credentials not configured - notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Telegram notifier initialized")
        
        # Pending approvals
        self.pending_approvals: Dict[str, TelegramAlert] = {}
        
        # Rate limiting
        self.last_message_time = {}
        self.rate_limit_seconds = 2
        
    async def send_alert(self, alert: TelegramAlert) -> bool:
        """Send alert to Telegram"""
        if not self.enabled:
            logger.debug("Telegram notifications disabled")
            return False
            
        try:
            # Rate limiting
            now = datetime.now()
            key = f"{alert.alert_type.value}_{alert.title}"
            if key in self.last_message_time:
                time_diff = (now - self.last_message_time[key]).total_seconds()
                if time_diff < self.rate_limit_seconds:
                    logger.debug(f"Rate limited: {key}")
                    return False
            
            self.last_message_time[key] = now
            
            # Format message
            formatted_message = self._format_message(alert)
            
            # Send message
            success = await self._send_message(formatted_message)
            
            # Handle approval requests
            if alert.requires_approval and success:
                approval_id = f"approval_{int(now.timestamp())}"
                self.pending_approvals[approval_id] = alert
                await self._send_approval_keyboard(approval_id, alert)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def _format_message(self, alert: TelegramAlert) -> str:
        """Format alert message for Telegram"""
        timestamp = alert.timestamp.strftime("%H:%M:%S")
        
        # Header with priority and type
        header = f"{alert.priority.value} *ATOM ALERT* {alert.priority.value}\n"
        header += f"🕐 {timestamp} | {alert.alert_type.value.upper()}\n"
        header += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Title and message
        content = f"*{alert.title}*\n\n{alert.message}\n\n"
        
        # Data section
        if alert.data:
            content += "📊 *Details:*\n"
            for key, value in alert.data.items():
                if isinstance(value, float):
                    if 'bps' in key.lower():
                        content += f"• {key}: {value:.1f}bps\n"
                    elif 'usd' in key.lower() or 'profit' in key.lower():
                        content += f"• {key}: ${value:.2f}\n"
                    else:
                        content += f"• {key}: {value:.4f}\n"
                else:
                    content += f"• {key}: {value}\n"
            content += "\n"
        
        # Footer
        footer = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        footer += "🧬 *ATOM Arbitrage System* | Base Sepolia"
        
        return header + content + footer
    
    async def _send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.debug("✅ Telegram message sent successfully")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Telegram API error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def _send_approval_keyboard(self, approval_id: str, alert: TelegramAlert):
        """Send approval keyboard for manual trades"""
        try:
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Approve", "callback_data": f"approve_{approval_id}"},
                        {"text": "❌ Reject", "callback_data": f"reject_{approval_id}"}
                    ],
                    [
                        {"text": "📊 Details", "callback_data": f"details_{approval_id}"}
                    ]
                ]
            }
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": f"🤖 *Manual Approval Required*\n\n{alert.title}\n\nTimeout: {alert.approval_timeout}s",
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to send approval keyboard: {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to send approval keyboard: {e}")
    
    # Convenience methods for different alert types
    async def notify_arbitrage_opportunity(
        self, 
        token_a: str, 
        token_b: str, 
        spread_bps: float, 
        estimated_profit: float,
        dex_path: str
    ):
        """Notify about arbitrage opportunity"""
        alert = TelegramAlert(
            alert_type=AlertType.ARBITRAGE_OPPORTUNITY,
            priority=Priority.HIGH if spread_bps > 50 else Priority.NORMAL,
            title=f"Arbitrage Opportunity: {token_a}/{token_b}",
            message=f"Profitable spread detected on {dex_path}",
            data={
                "spread_bps": spread_bps,
                "estimated_profit_usd": estimated_profit,
                "token_pair": f"{token_a}/{token_b}",
                "dex_path": dex_path
            },
            timestamp=datetime.now()
        )
        return await self.send_alert(alert)
    
    async def notify_depeg_detected(
        self, 
        pool_address: str, 
        virtual_price: float, 
        deviation: float
    ):
        """Notify about Curve pool depeg"""
        alert = TelegramAlert(
            alert_type=AlertType.DEPEG_DETECTED,
            priority=Priority.HIGH,
            title="🌊 Curve Pool Depeg Detected",
            message=f"Virtual price deviation exceeds threshold",
            data={
                "pool_address": pool_address[:10] + "...",
                "virtual_price": virtual_price,
                "deviation_percent": deviation * 100,
                "threshold_percent": 2.0
            },
            timestamp=datetime.now()
        )
        return await self.send_alert(alert)
    
    async def notify_trade_executed(
        self, 
        trade_type: str, 
        profit_usd: float, 
        gas_used: int,
        tx_hash: str
    ):
        """Notify about successful trade execution"""
        alert = TelegramAlert(
            alert_type=AlertType.TRADE_EXECUTED,
            priority=Priority.NORMAL,
            title=f"✅ {trade_type} Executed",
            message="Trade completed successfully",
            data={
                "profit_usd": profit_usd,
                "gas_used": gas_used,
                "tx_hash": tx_hash[:10] + "...",
                "trade_type": trade_type
            },
            timestamp=datetime.now()
        )
        return await self.send_alert(alert)
    
    async def notify_trade_failed(
        self, 
        trade_type: str, 
        error_reason: str,
        estimated_loss: float = 0.0
    ):
        """Notify about failed trade"""
        alert = TelegramAlert(
            alert_type=AlertType.TRADE_FAILED,
            priority=Priority.HIGH,
            title=f"❌ {trade_type} Failed",
            message=f"Trade execution failed: {error_reason}",
            data={
                "trade_type": trade_type,
                "error_reason": error_reason,
                "estimated_loss_usd": estimated_loss
            },
            timestamp=datetime.now()
        )
        return await self.send_alert(alert)
    
    async def notify_bot_status(
        self, 
        bot_name: str, 
        status: str, 
        uptime: str,
        opportunities_found: int
    ):
        """Notify about bot status"""
        priority = Priority.CRITICAL if status == "stopped" else Priority.LOW
        
        alert = TelegramAlert(
            alert_type=AlertType.BOT_STATUS,
            priority=priority,
            title=f"🤖 {bot_name} Status: {status.upper()}",
            message=f"Bot status update",
            data={
                "bot_name": bot_name,
                "status": status,
                "uptime": uptime,
                "opportunities_found": opportunities_found
            },
            timestamp=datetime.now()
        )
        return await self.send_alert(alert)
    
    async def request_manual_approval(
        self, 
        trade_type: str, 
        estimated_profit: float,
        risk_level: str,
        timeout: int = 300
    ) -> str:
        """Request manual approval for high-value trades"""
        approval_id = f"approval_{int(datetime.now().timestamp())}"
        
        alert = TelegramAlert(
            alert_type=AlertType.MANUAL_APPROVAL,
            priority=Priority.HIGH,
            title=f"🔐 Manual Approval Required",
            message=f"High-value {trade_type} requires approval",
            data={
                "trade_type": trade_type,
                "estimated_profit_usd": estimated_profit,
                "risk_level": risk_level,
                "approval_id": approval_id
            },
            timestamp=datetime.now(),
            requires_approval=True,
            approval_timeout=timeout
        )
        
        await self.send_alert(alert)
        return approval_id
    
    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.enabled:
            return False
            
        try:
            url = f"{self.base_url}/getMe"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        bot_info = data.get("result", {})
                        logger.info(f"✅ Telegram bot connected: @{bot_info.get('username')}")
                        
                        # Send test message
                        test_alert = TelegramAlert(
                            alert_type=AlertType.SYSTEM_ERROR,
                            priority=Priority.LOW,
                            title="🧪 Connection Test",
                            message="ATOM Telegram notifier is working correctly!",
                            data={"test": True},
                            timestamp=datetime.now()
                        )
                        return await self.send_alert(test_alert)
                    else:
                        logger.error(f"Telegram bot connection failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False

# Global notifier instance
telegram_notifier = TelegramNotifier()
