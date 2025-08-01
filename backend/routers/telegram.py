"""
🤖 Telegram Webhook Router
Handles interactive callbacks and manual approvals
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime
from typing import Dict, Any

from integrations.telegram_notifier import telegram_notifier, AlertType, Priority, TelegramAlert
from core.aeon_execution_mode import aeon_mode, AEONExecutionMode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])

# Store for approval responses
approval_responses: Dict[str, Dict[str, Any]] = {}

@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Telegram webhook callbacks"""
    try:
        data = await request.json()
        logger.debug(f"Telegram webhook data: {data}")
        
        # Handle callback queries (button presses)
        if "callback_query" in data:
            callback_query = data["callback_query"]
            callback_data = callback_query.get("data", "")
            user = callback_query.get("from", {})
            message_id = callback_query.get("message", {}).get("message_id")
            
            # Process approval callbacks
            if callback_data.startswith(("approve_", "reject_", "details_")):
                background_tasks.add_task(
                    handle_approval_callback,
                    callback_data,
                    user,
                    message_id
                )
        
        # Handle regular messages
        elif "message" in data:
            message = data["message"]
            text = message.get("text", "")
            user = message.get("from", {})
            
            # Handle commands
            if text.startswith("/"):
                background_tasks.add_task(
                    handle_command,
                    text,
                    user
                )
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

async def handle_approval_callback(callback_data: str, user: Dict, message_id: int):
    """Handle approval button callbacks"""
    try:
        action, approval_id = callback_data.split("_", 1)
        
        if approval_id not in telegram_notifier.pending_approvals:
            logger.warning(f"Approval {approval_id} not found or expired")
            return
        
        alert = telegram_notifier.pending_approvals[approval_id]
        user_id = user.get("id")
        username = user.get("username", "Unknown")
        
        if action == "approve":
            # Store approval for both approval_id and trade_id
            trade_id = alert.data.get('trade_id')

            approval_data = {
                "approved": True,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now().isoformat()
            }

            approval_responses[approval_id] = approval_data
            if trade_id:
                approval_responses[trade_id] = approval_data  # For trading engine

            # Send confirmation
            await telegram_notifier._send_message(
                f"✅ *APPROVED* by @{username}\n\n"
                f"Trade: {alert.title}\n"
                f"Estimated Profit: ${alert.data.get('estimated_profit_usd', 0):.2f}\n"
                f"Executing trade..."
            )

            logger.info(f"Trade approved by {username}: {approval_id} (trade_id: {trade_id})")

        elif action == "reject":
            # Store rejection for both approval_id and trade_id
            trade_id = alert.data.get('trade_id')

            approval_data = {
                "approved": False,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now().isoformat()
            }

            approval_responses[approval_id] = approval_data
            if trade_id:
                approval_responses[trade_id] = approval_data  # For trading engine

            # Send confirmation
            await telegram_notifier._send_message(
                f"❌ *REJECTED* by @{username}\n\n"
                f"Trade: {alert.title}\n"
                f"Trade cancelled."
            )

            logger.info(f"Trade rejected by {username}: {approval_id} (trade_id: {trade_id})")
            
        elif action == "details":
            # Send detailed information
            details_msg = f"📊 *Trade Details*\n\n"
            details_msg += f"*{alert.title}*\n\n"
            details_msg += f"{alert.message}\n\n"
            
            for key, value in alert.data.items():
                if isinstance(value, float):
                    if 'bps' in key.lower():
                        details_msg += f"• {key}: {value:.1f}bps\n"
                    elif 'usd' in key.lower():
                        details_msg += f"• {key}: ${value:.2f}\n"
                    else:
                        details_msg += f"• {key}: {value:.4f}\n"
                else:
                    details_msg += f"• {key}: {value}\n"
            
            await telegram_notifier._send_message(details_msg)
        
        # Clean up expired approval
        if approval_id in telegram_notifier.pending_approvals:
            del telegram_notifier.pending_approvals[approval_id]
            
    except Exception as e:
        logger.error(f"Error handling approval callback: {e}")

async def handle_command(text: str, user: Dict):
    """Handle Telegram commands"""
    try:
        command = text.split()[0].lower()
        username = user.get("username", "Unknown")
        
        if command == "/start":
            welcome_msg = (
                "🧬 *Welcome to ATOM Arbitrage System*\n\n"
                "I'll notify you about:\n"
                "• 🎯 Arbitrage opportunities\n"
                "• 🌊 Curve pool depegs\n"
                "• ✅ Successful trades\n"
                "• ❌ Failed trades\n"
                "• 🤖 Bot status updates\n"
                "• 🔐 Manual approval requests\n\n"
                "*Available Commands:*\n"
                "/status - Bot status\n"
                "/stats - Trading statistics\n"
                "/test - Test notification\n"
                "/help - Show this help"
            )
            await telegram_notifier._send_message(welcome_msg)
            
        elif command == "/status":
            # Get bot status with AEON mode
            current_status = aeon_mode.get_status()
            status_msg = (
                "🧬 *AEON SYSTEM STATUS*\n\n"
                f"**Execution Mode:** {current_status['mode'].upper()} {current_status['emoji']}\n"
                f"_{current_status['description']}_\n\n"
                "**System Status:**\n"
                "• ATOM Bot: 🟢 Running\n"
                "• ADOM Bot: 🟢 Running\n"
                "• Telegram Notifier: 🟢 Active\n"
                "• Base Sepolia: 🟢 Connected\n"
                f"• Execution Mode: {current_status['emoji']} {current_status['mode'].title()}\n\n"
                f"Last update: {datetime.now().strftime('%H:%M:%S')}\n\n"
                "Use `/auto` to change execution mode"
            )
            await telegram_notifier._send_message(status_msg)
            
        elif command == "/stats":
            # Trading statistics (would integrate with actual data)
            stats_msg = (
                "📊 *Trading Statistics (24h)*\n\n"
                "• Opportunities Found: 47\n"
                "• Trades Executed: 12\n"
                "• Success Rate: 85.7%\n"
                "• Total Profit: $234.56\n"
                "• Average Spread: 31.2bps\n"
                "• Gas Spent: $18.90\n\n"
                f"Updated: {datetime.now().strftime('%H:%M:%S')}"
            )
            await telegram_notifier._send_message(stats_msg)
            
        elif command == "/test":
            # Send test notification
            test_alert = TelegramAlert(
                alert_type=AlertType.ARBITRAGE_OPPORTUNITY,
                priority=Priority.NORMAL,
                title="🧪 Test Notification",
                message=f"Test message requested by @{username}",
                data={
                    "test": True,
                    "spread_bps": 45.2,
                    "estimated_profit_usd": 123.45,
                    "token_pair": "DAI/USDC"
                },
                timestamp=datetime.now()
            )
            await telegram_notifier.send_alert(test_alert)
            
        elif command == "/auto":
            # Show auto-trade control menu with current mode
            current_status = aeon_mode.get_status()
            auto_msg = (
                "🧬 *AEON EXECUTION CONTROL*\n\n"
                f"**Current Mode:** {current_status['mode'].upper()} {current_status['emoji']}\n"
                f"_{current_status['description']}_\n\n"
                "Choose your execution mode:\n\n"
                "🔴 `/manual` - All trades require approval\n"
                "🟡 `/hybrid` - Small auto, large manual\n"
                "🟢 `/autonomous` - Fully autonomous\n\n"
                "⚡ **AEON** = Advanced Efficient Optimized Network"
            )
            await telegram_notifier._send_message(auto_msg)

        elif command == "/manual":
            # Set manual mode
            success = aeon_mode.set_mode(AEONExecutionMode.MANUAL)
            if success:
                await telegram_notifier._send_message(
                    "🔴 *MANUAL MODE ACTIVATED*\n\n"
                    "✅ All trades require your approval\n"
                    "✅ Maximum safety and control\n"
                    "✅ Approval buttons for every trade\n\n"
                    "🧬 **AEON is now in MANUAL mode**"
                )
            else:
                await telegram_notifier._send_message("❌ Failed to set manual mode")

        elif command == "/hybrid":
            # Set hybrid mode
            success = aeon_mode.set_mode(AEONExecutionMode.HYBRID)
            if success:
                await telegram_notifier._send_message(
                    "🟡 *HYBRID MODE ACTIVATED*\n\n"
                    "✅ Small trades (<$100): Auto-execute\n"
                    "✅ Large trades (>$100): Manual approval\n"
                    "✅ High spreads (>75bps): Manual approval\n\n"
                    "🧬 **AEON is now in HYBRID mode**"
                )
            else:
                await telegram_notifier._send_message("❌ Failed to set hybrid mode")

        elif command == "/autonomous":
            # Set autonomous mode
            success = aeon_mode.set_mode(AEONExecutionMode.AUTONOMOUS)
            if success:
                await telegram_notifier._send_message(
                    "🟢 *AUTONOMOUS MODE ACTIVATED*\n\n"
                    "⚡ All profitable trades execute automatically\n"
                    "⚡ 23bps minimum threshold enforced\n"
                    "⚡ Circuit breakers protect against losses\n\n"
                    "⚠️ **WARNING:** AEON will trade without approval!\n"
                    "Use `/manual` to regain control anytime.\n\n"
                    "🧬 **AEON is now FULLY AUTONOMOUS**"
                )
            else:
                await telegram_notifier._send_message("❌ Failed to set autonomous mode")

        elif command == "/help":
            help_msg = (
                "🧬 *AEON TELEGRAM CONTROL*\n\n"
                "**🤖 EXECUTION CONTROL:**\n"
                "/auto - Choose execution mode\n"
                "/manual - Manual approval mode 🔴\n"
                "/hybrid - Hybrid auto/manual mode 🟡\n"
                "/autonomous - Full auto mode 🟢\n\n"
                "**📊 MONITORING:**\n"
                "/start - Welcome message\n"
                "/status - Current bot status\n"
                "/stats - Trading statistics\n"
                "/test - Send test notification\n\n"
                "**🔔 NOTIFICATIONS:**\n"
                "🎯 Arbitrage opportunities\n"
                "🌊 Depeg alerts\n"
                "✅ Trade confirmations\n"
                "❌ Error alerts\n"
                "🔐 Manual approvals\n\n"
                "🧬 **AEON** = Advanced Efficient Optimized Network"
            )
            await telegram_notifier._send_message(help_msg)
            
        else:
            await telegram_notifier._send_message(
                f"Unknown command: {command}\n"
                "Type /help for available commands."
            )
            
    except Exception as e:
        logger.error(f"Error handling command: {e}")

@router.get("/test")
async def test_telegram():
    """Test Telegram connection"""
    try:
        success = await telegram_notifier.test_connection()
        if success:
            return {"status": "success", "message": "Telegram bot is working"}
        else:
            return {"status": "error", "message": "Telegram bot connection failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notify/arbitrage")
async def notify_arbitrage(
    token_a: str,
    token_b: str,
    spread_bps: float,
    estimated_profit: float,
    dex_path: str
):
    """Send arbitrage opportunity notification"""
    try:
        success = await telegram_notifier.notify_arbitrage_opportunity(
            token_a, token_b, spread_bps, estimated_profit, dex_path
        )
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notify/depeg")
async def notify_depeg(
    pool_address: str,
    virtual_price: float,
    deviation: float
):
    """Send depeg notification"""
    try:
        success = await telegram_notifier.notify_depeg_detected(
            pool_address, virtual_price, deviation
        )
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notify/trade")
async def notify_trade(
    trade_type: str,
    success: bool,
    profit_usd: float = 0.0,
    gas_used: int = 0,
    tx_hash: str = "",
    error_reason: str = ""
):
    """Send trade execution notification"""
    try:
        if success:
            result = await telegram_notifier.notify_trade_executed(
                trade_type, profit_usd, gas_used, tx_hash
            )
        else:
            result = await telegram_notifier.notify_trade_failed(
                trade_type, error_reason, abs(profit_usd)
            )
        return {"status": "success" if result else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approvals/{approval_id}")
async def get_approval_status(approval_id: str):
    """Get approval status"""
    if approval_id in approval_responses:
        return approval_responses[approval_id]
    elif approval_id in telegram_notifier.pending_approvals:
        return {"status": "pending", "expires_at": "300s"}
    else:
        raise HTTPException(status_code=404, detail="Approval not found")

@router.post("/setup-webhook")
async def setup_webhook(webhook_url: str):
    """Setup Telegram webhook for interactive features"""
    try:
        if not telegram_notifier.enabled:
            raise HTTPException(status_code=400, detail="Telegram not configured")

        url = f"{telegram_notifier.base_url}/setWebhook"
        payload = {"url": webhook_url}

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"status": "success", "result": result}
                else:
                    error = await response.text()
                    raise HTTPException(status_code=400, detail=f"Webhook setup failed: {error}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/webhook")
async def remove_webhook():
    """Remove Telegram webhook"""
    try:
        if not telegram_notifier.enabled:
            raise HTTPException(status_code=400, detail="Telegram not configured")

        url = f"{telegram_notifier.base_url}/deleteWebhook"

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"status": "success", "result": result}
                else:
                    error = await response.text()
                    raise HTTPException(status_code=400, detail=f"Webhook removal failed: {error}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aeon/mode")
async def get_aeon_mode():
    """Get current AEON execution mode"""
    try:
        status = aeon_mode.get_status()
        return {
            "status": "success",
            "aeon_mode": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/aeon/mode/{mode}")
async def set_aeon_mode(mode: str):
    """Set AEON execution mode"""
    try:
        mode_map = {
            "manual": AEONExecutionMode.MANUAL,
            "hybrid": AEONExecutionMode.HYBRID,
            "autonomous": AEONExecutionMode.AUTONOMOUS
        }

        if mode.lower() not in mode_map:
            raise HTTPException(status_code=400, detail="Invalid mode. Use: manual, hybrid, or autonomous")

        success = aeon_mode.set_mode(mode_map[mode.lower()])
        if success:
            status = aeon_mode.get_status()
            return {
                "status": "success",
                "message": f"AEON mode set to {mode.upper()}",
                "aeon_mode": status
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set mode")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def telegram_health():
    """Health check for Telegram integration"""
    return {
        "status": "healthy" if telegram_notifier.enabled else "disabled",
        "bot_token_configured": bool(telegram_notifier.bot_token),
        "chat_id_configured": bool(telegram_notifier.chat_id),
        "pending_approvals": len(telegram_notifier.pending_approvals),
        "aeon_mode": aeon_mode.get_status()
    }
