#!/usr/bin/env python3
"""
Production Orchestrator - Coordinates all arbitrage system components
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict
import redis
import aiohttp
from production_opportunity_detector import ProductionOpportunityDetector
from production_trade_executor import ProductionTradeExecutor
from production_mev_protection import ProductionMEVProtection
from profit_calculator import ProfitCalculator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionOrchestrator:
    def __init__(self):
        self.load_config()
        self.setup_redis()
        self.detector = ProductionOpportunityDetector()
        self.executor = ProductionTradeExecutor()
        self.profit_calc = ProfitCalculator()
        self.mev_protection = ProductionMEVProtection(self.executor.w3)
        self.running = False
        self.stats = {
            'start_time': time.time(),
            'opportunities_detected': 0,
            'trades_executed': 0,
            'total_profit_usd': 0.0,
            'last_trade_time': 0
        }
        
    def load_config(self):
        """Load configuration"""
        self.daily_profit_target = float(os.getenv('DAILY_PROFIT_TARGET_USD', '500'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS_USD', '200'))
        
        # Alert configuration
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def setup_redis(self):
        """Initialize Redis connection"""
        redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    async def send_alert(self, message: str, alert_type: str = "info"):
        """Send alert via configured channels"""
        color_map = {
            "info": 0x00ff00,
            "warning": 0xffff00,
            "error": 0xff0000,
            "success": 0x00ff00
        }
        
        logger.info(f"ALERT [{alert_type.upper()}]: {message}")
        
        # Send to Discord
        if self.discord_webhook:
            try:
                embed = {
                    "title": "🤖 ATOM Production Alert",
                    "description": message,
                    "color": color_map.get(alert_type, 0x00ff00),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.discord_webhook, 
                        json={"embeds": [embed]}
                    ) as response:
                        if response.status != 204:
                            logger.error(f"Discord alert failed: {response.status}")
            except Exception as e:
                logger.error(f"Discord alert error: {e}")
                
    async def opportunity_processor(self):
        """Process and validate opportunities"""
        logger.info("🔍 Starting opportunity processor...")
        
        while self.running:
            try:
                # Get opportunities from detector
                opportunities = self.detector.get_best_opportunities(limit=10)
                
                for opportunity in opportunities:
                    # Validate with real-time quotes
                    validation = self.profit_calc.validate_opportunity_realtime(opportunity)
                    
                    if validation.get('profitable'):
                        # Check MEV risk
                        if not self.mev_protection.should_delay_transaction(
                            opportunity['token_a'],
                            opportunity['token_b'], 
                            opportunity['amount_in']
                        ):
                            # Queue for execution
                            self.redis_client.lpush('validated_opportunities', json.dumps(opportunity))
                            self.stats['opportunities_detected'] += 1
                            
                            logger.info(f"✅ Validated opportunity: {opportunity['profit_bps']} bps profit")
                        else:
                            logger.warning("⚠️ Opportunity delayed due to MEV risk")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in opportunity processor: {e}")
                await asyncio.sleep(5)
                
    async def trade_monitor(self):
        """Monitor trade execution and results"""
        logger.info("📊 Starting trade monitor...")
        
        while self.running:
            try:
                # Get executor stats
                executor_stats = self.executor.get_stats()
                
                # Update overall stats
                self.stats.update({
                    'trades_executed': executor_stats['total_trades'],
                    'total_profit_usd': executor_stats['total_profit_usd']
                })
                
                # Check for new trades
                if executor_stats['total_trades'] > 0:
                    self.stats['last_trade_time'] = time.time()
                    
                # Store stats in Redis
                current_stats = {
                    'timestamp': time.time(),
                    'uptime_hours': (time.time() - self.stats['start_time']) / 3600,
                    'opportunities_detected': self.stats['opportunities_detected'],
                    'trades_executed': self.stats['trades_executed'],
                    'success_rate': executor_stats['success_rate'],
                    'total_profit_usd': self.stats['total_profit_usd'],
                    'current_wallet': executor_stats['current_wallet']
                }
                
                self.redis_client.set('production_stats', json.dumps(current_stats))
                
                # Log periodic status
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    logger.info(f"📊 Status: {self.stats['opportunities_detected']} opportunities, "
                              f"{self.stats['trades_executed']} trades, "
                              f"${self.stats['total_profit_usd']:.2f} profit")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in trade monitor: {e}")
                await asyncio.sleep(30)
                
    async def performance_analyzer(self):
        """Analyze system performance and send alerts"""
        logger.info("📈 Starting performance analyzer...")
        
        last_alert_time = 0
        
        while self.running:
            try:
                # Calculate daily profit
                daily_profit = self._calculate_daily_profit()
                
                # Check daily target
                if daily_profit >= self.daily_profit_target:
                    if time.time() - last_alert_time > 3600:  # Once per hour
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
                    
                # Check system health
                if time.time() - self.stats.get('last_trade_time', 0) > 3600:  # No trades in 1 hour
                    await self.send_alert(
                        "⚠️ No trades executed in the last hour - checking system health",
                        "warning"
                    )
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in performance analyzer: {e}")
                await asyncio.sleep(600)
                
    def _calculate_daily_profit(self) -> float:
        """Calculate profit for the last 24 hours"""
        try:
            cutoff_time = time.time() - 86400  # 24 hours ago
            trade_history_raw = self.redis_client.lrange('trade_history', 0, -1)
            
            daily_profit = 0.0
            for trade_raw in trade_history_raw:
                trade = json.loads(trade_raw)
                if trade.get('timestamp', 0) > cutoff_time:
                    daily_profit += trade.get('net_profit_usd', 0)
                    
            return daily_profit
            
        except Exception as e:
            logger.error(f"Error calculating daily profit: {e}")
            return 0.0
            
    async def start_production_system(self):
        """Start the complete production arbitrage system"""
        self.running = True
        
        logger.info("🚀 ATOM PRODUCTION SYSTEM STARTING...")
        await self.send_alert("🚀 ATOM Production System Starting Up", "info")
        
        # Start all components
        tasks = [
            asyncio.create_task(self.detector.start(), name="detector"),
            asyncio.create_task(self.executor.start(), name="executor"),
            asyncio.create_task(self.opportunity_processor(), name="processor"),
            asyncio.create_task(self.trade_monitor(), name="monitor"),
            asyncio.create_task(self.performance_analyzer(), name="analyzer")
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down production system...")
            await self.send_alert("🛑 ATOM Production System Shutting Down", "warning")
            
            self.running = False
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
                
            await asyncio.gather(*tasks, return_exceptions=True)
            
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'system': {
                'uptime_hours': uptime / 3600,
                'start_time': datetime.fromtimestamp(self.stats['start_time']).isoformat(),
                'status': 'running' if self.running else 'stopped'
            },
            'opportunities': {
                'total_detected': self.stats['opportunities_detected'],
                'detection_rate_per_hour': self.stats['opportunities_detected'] / (uptime / 3600) if uptime > 0 else 0
            },
            'trading': self.executor.get_stats(),
            'performance': {
                'daily_profit_target': self.daily_profit_target,
                'daily_profit_actual': self._calculate_daily_profit(),
                'profit_per_hour': self.stats['total_profit_usd'] / (uptime / 3600) if uptime > 0 else 0
            },
            'mev_protection': self.mev_protection.get_protection_stats()
        }

if __name__ == "__main__":
    orchestrator = ProductionOrchestrator()
    asyncio.run(orchestrator.start_production_system())
