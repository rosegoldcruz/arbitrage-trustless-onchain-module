#!/usr/bin/env python3
"""
Polygon Arbitrage System Orchestrator
Coordinates opportunity detection and trade execution bots
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List
import redis
import aiohttp
from opportunity_detector import OpportunityDetector
from trade_executor import TradeExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArbitrageOrchestrator:
    def __init__(self):
        self.load_config()
        self.setup_redis()
        self.detector = OpportunityDetector()
        self.executor = TradeExecutor()
        self.running = False
        self.stats = {
            'start_time': time.time(),
            'opportunities_detected': 0,
            'trades_executed': 0,
            'total_profit_usd': 0,
            'last_opportunity': None,
            'last_trade': None
        }
        
    def load_config(self):
        """Load configuration"""
        self.daily_profit_target = float(os.getenv('DAILY_PROFIT_TARGET_USD', '500'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS_USD', '200'))
        self.health_check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL_SECONDS', '30'))
        
        # Alert configuration
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def setup_redis(self):
        """Initialize Redis connection"""
        redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    async def send_discord_alert(self, message: str, color: int = 0x00ff00):
        """Send alert to Discord webhook"""
        if not self.discord_webhook:
            return
            
        try:
            embed = {
                "title": "🤖 ATOM Arbitrage Bot Alert",
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "ATOM Arbitrage System"}
            }
            
            payload = {"embeds": [embed]}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook, json=payload) as response:
                    if response.status == 204:
                        logger.info("Discord alert sent successfully")
                    else:
                        logger.error(f"Failed to send Discord alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending Discord alert: {e}")
            
    async def send_telegram_alert(self, message: str):
        """Send alert to Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": f"🤖 ATOM Bot: {message}",
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram alert sent successfully")
                    else:
                        logger.error(f"Failed to send Telegram alert: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
            
    async def send_alert(self, message: str, alert_type: str = "info"):
        """Send alert via all configured channels"""
        color_map = {
            "info": 0x00ff00,    # Green
            "warning": 0xffff00,  # Yellow
            "error": 0xff0000,    # Red
            "success": 0x00ff00   # Green
        }
        
        logger.info(f"ALERT [{alert_type.upper()}]: {message}")
        
        # Send to Discord
        await self.send_discord_alert(message, color_map.get(alert_type, 0x00ff00))
        
        # Send to Telegram
        await self.send_telegram_alert(message)
        
    async def opportunity_publisher(self):
        """Publish detected opportunities to Redis for executor"""
        logger.info("🔍 Starting opportunity publisher...")
        
        while self.running:
            try:
                # Get best opportunities from detector
                opportunities = self.detector.get_best_opportunities(limit=5)
                
                for opportunity in opportunities:
                    # Publish to Redis for executor
                    self.redis_client.lpush('arbitrage_opportunities', json.dumps(opportunity))
                    self.stats['opportunities_detected'] += 1
                    self.stats['last_opportunity'] = opportunity
                    
                    # Alert on high-profit opportunities
                    if opportunity['profit_bps'] > 100:  # > 1% profit
                        profit_usd = opportunity['profit'] / 10**18
                        await self.send_alert(
                            f"🚀 HIGH PROFIT OPPORTUNITY: {opportunity['token_a_name']}->{opportunity['token_b_name']}->{opportunity['token_c_name']} "
                            f"Profit: {opportunity['profit_bps']} bps (${profit_usd:.2f})",
                            "success"
                        )
                
                await asyncio.sleep(1)  # Publish every second
                
            except Exception as e:
                logger.error(f"Error in opportunity publisher: {e}")
                await asyncio.sleep(5)
                
    async def system_monitor(self):
        """Monitor system health and performance"""
        logger.info("📊 Starting system monitor...")
        
        last_alert_time = 0
        
        while self.running:
            try:
                # Get current stats
                detector_opportunities = len(self.detector.opportunities)
                executor_stats = self.executor.get_stats()
                
                # Update overall stats
                self.stats.update({
                    'trades_executed': executor_stats['total_trades'],
                    'total_profit_usd': executor_stats['total_profit_usd'],
                    'success_rate': executor_stats['success_rate']
                })
                
                # Store stats in Redis
                current_stats = {
                    'timestamp': time.time(),
                    'uptime_hours': (time.time() - self.stats['start_time']) / 3600,
                    'opportunities_detected': self.stats['opportunities_detected'],
                    'current_opportunities': detector_opportunities,
                    'trades_executed': self.stats['trades_executed'],
                    'successful_trades': executor_stats['successful_trades'],
                    'success_rate': executor_stats['success_rate'],
                    'total_profit_usd': self.stats['total_profit_usd'],
                    'active_wallets': executor_stats['active_wallets'],
                    'current_wallet': executor_stats['current_wallet']
                }
                
                self.redis_client.set('system_stats', json.dumps(current_stats))
                
                # Log periodic status
                logger.info(f"📊 Status: {detector_opportunities} opportunities, "
                          f"{self.stats['trades_executed']} trades, "
                          f"${self.stats['total_profit_usd']:.2f} profit, "
                          f"{executor_stats['success_rate']:.1f}% success rate")
                
                # Check daily profit target
                daily_profit = self.stats['total_profit_usd']
                if daily_profit >= self.daily_profit_target:
                    if time.time() - last_alert_time > 3600:  # Alert once per hour
                        await self.send_alert(
                            f"🎉 DAILY TARGET REACHED: ${daily_profit:.2f} / ${self.daily_profit_target:.2f}",
                            "success"
                        )
                        last_alert_time = time.time()
                
                # Check for losses
                if daily_profit < -self.max_daily_loss:
                    await self.send_alert(
                        f"🚨 DAILY LOSS LIMIT EXCEEDED: ${daily_profit:.2f}",
                        "error"
                    )
                    # Consider pausing system
                    
                # Health checks
                if detector_opportunities == 0:
                    logger.warning("⚠️ No opportunities detected - check price feeds")
                    
                if executor_stats['success_rate'] < 50 and executor_stats['total_trades'] > 10:
                    await self.send_alert(
                        f"⚠️ LOW SUCCESS RATE: {executor_stats['success_rate']:.1f}%",
                        "warning"
                    )
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in system monitor: {e}")
                await asyncio.sleep(30)
                
    async def start_system(self):
        """Start the complete arbitrage system"""
        self.running = True
        
        logger.info("🚀 Starting ATOM Arbitrage System...")
        await self.send_alert("🚀 ATOM Arbitrage System Starting Up", "info")
        
        # Start all components
        tasks = [
            asyncio.create_task(self.detector.start(), name="detector"),
            asyncio.create_task(self.executor.start(), name="executor"),
            asyncio.create_task(self.opportunity_publisher(), name="publisher"),
            asyncio.create_task(self.system_monitor(), name="monitor")
        ]
        
        try:
            # Wait for all tasks
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down system...")
            await self.send_alert("🛑 ATOM Arbitrage System Shutting Down", "warning")
            
            self.running = False
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
                
            # Wait for tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'system': {
                'uptime_seconds': uptime,
                'uptime_hours': uptime / 3600,
                'start_time': datetime.fromtimestamp(self.stats['start_time']).isoformat(),
                'status': 'running' if self.running else 'stopped'
            },
            'opportunities': {
                'total_detected': self.stats['opportunities_detected'],
                'current_count': len(self.detector.opportunities),
                'detection_rate_per_hour': self.stats['opportunities_detected'] / (uptime / 3600) if uptime > 0 else 0,
                'last_opportunity': self.stats['last_opportunity']
            },
            'trading': self.executor.get_stats(),
            'performance': {
                'daily_profit_target': self.daily_profit_target,
                'daily_profit_actual': self.stats['total_profit_usd'],
                'target_progress': (self.stats['total_profit_usd'] / self.daily_profit_target * 100) if self.daily_profit_target > 0 else 0,
                'profit_per_hour': self.stats['total_profit_usd'] / (uptime / 3600) if uptime > 0 else 0
            }
        }

if __name__ == "__main__":
    orchestrator = ArbitrageOrchestrator()
    asyncio.run(orchestrator.start_system())
