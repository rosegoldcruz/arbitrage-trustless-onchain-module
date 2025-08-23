#!/usr/bin/env python3
"""
Real-time Monitoring & Analytics System
Comprehensive monitoring for live profit tracking, success rates, and system health
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis
import aiohttp
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MonitoringSystem:
    def __init__(self):
        self.load_config()
        self.setup_redis()
        self.metrics = {
            'system_start_time': time.time(),
            'total_opportunities': 0,
            'total_trades': 0,
            'successful_trades': 0,
            'total_profit_usd': 0.0,
            'total_gas_cost_usd': 0.0,
            'last_trade_time': 0,
            'last_opportunity_time': 0
        }
        self.performance_history = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        self.alert_history = deque(maxlen=1000)
        self.running = False
        
    def load_config(self):
        """Load monitoring configuration"""
        self.update_interval = int(os.getenv('MONITORING_UPDATE_INTERVAL', '60'))  # seconds
        self.alert_thresholds = {
            'min_success_rate': float(os.getenv('ALERT_MIN_SUCCESS_RATE', '0.5')),
            'max_daily_loss': float(os.getenv('MAX_DAILY_LOSS_USD', '200')),
            'min_hourly_opportunities': int(os.getenv('ALERT_MIN_HOURLY_OPPORTUNITIES', '5')),
            'max_gas_cost_ratio': float(os.getenv('ALERT_MAX_GAS_COST_RATIO', '0.3'))
        }
        
        # Dashboard configuration
        self.dashboard_port = int(os.getenv('DASHBOARD_PORT', '8080'))
        self.enable_web_dashboard = os.getenv('ENABLE_WEB_DASHBOARD', 'true').lower() == 'true'
        
    def setup_redis(self):
        """Initialize Redis connection"""
        redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    async def start_monitoring(self):
        """Start the monitoring system"""
        self.running = True
        logger.info("🔍 Starting monitoring system...")
        
        tasks = [
            asyncio.create_task(self._collect_metrics()),
            asyncio.create_task(self._analyze_performance()),
            asyncio.create_task(self._check_alerts()),
            asyncio.create_task(self._update_dashboard_data())
        ]
        
        if self.enable_web_dashboard:
            tasks.append(asyncio.create_task(self._run_web_dashboard()))
            
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in monitoring system: {e}")
        finally:
            self.running = False
            
    async def _collect_metrics(self):
        """Collect system metrics from Redis"""
        while self.running:
            try:
                # Get trade history
                trade_history_raw = self.redis_client.lrange('trade_history', 0, -1)
                trade_history = [json.loads(t) for t in trade_history_raw]
                
                # Get opportunity count
                opportunity_count = self.redis_client.llen('arbitrage_opportunities')
                
                # Update metrics
                self.metrics['total_trades'] = len(trade_history)
                self.metrics['successful_trades'] = sum(1 for t in trade_history if t.get('success', False))
                self.metrics['total_profit_usd'] = sum(t.get('net_profit_usd', 0) for t in trade_history)
                self.metrics['total_gas_cost_usd'] = sum(t.get('gas_cost_usd', 0) for t in trade_history)
                
                if trade_history:
                    self.metrics['last_trade_time'] = max(t.get('timestamp', 0) for t in trade_history)
                    
                # Calculate derived metrics
                self.metrics['success_rate'] = (
                    self.metrics['successful_trades'] / self.metrics['total_trades'] 
                    if self.metrics['total_trades'] > 0 else 0
                )
                
                self.metrics['net_profit_usd'] = (
                    self.metrics['total_profit_usd'] - self.metrics['total_gas_cost_usd']
                )
                
                self.metrics['uptime_hours'] = (time.time() - self.metrics['system_start_time']) / 3600
                
                self.metrics['profit_per_hour'] = (
                    self.metrics['net_profit_usd'] / self.metrics['uptime_hours']
                    if self.metrics['uptime_hours'] > 0 else 0
                )
                
                # Store current metrics in Redis
                self.redis_client.set('monitoring_metrics', json.dumps(self.metrics))
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(30)
                
    async def _analyze_performance(self):
        """Analyze system performance and trends"""
        while self.running:
            try:
                current_time = time.time()
                
                # Calculate hourly metrics
                hourly_metrics = self._calculate_hourly_metrics()
                
                # Store performance snapshot
                performance_snapshot = {
                    'timestamp': current_time,
                    'metrics': self.metrics.copy(),
                    'hourly': hourly_metrics,
                    'trends': self._calculate_trends()
                }
                
                self.performance_history.append(performance_snapshot)
                
                # Store in Redis for dashboard
                self.redis_client.set('performance_history', json.dumps(list(self.performance_history)))
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error analyzing performance: {e}")
                await asyncio.sleep(60)
                
    def _calculate_hourly_metrics(self) -> Dict:
        """Calculate metrics for the last hour"""
        try:
            cutoff_time = time.time() - 3600  # 1 hour ago
            
            # Get recent trades
            trade_history_raw = self.redis_client.lrange('trade_history', 0, -1)
            recent_trades = []
            
            for trade_raw in trade_history_raw:
                trade = json.loads(trade_raw)
                if trade.get('timestamp', 0) > cutoff_time:
                    recent_trades.append(trade)
                    
            # Calculate hourly metrics
            hourly_trades = len(recent_trades)
            hourly_successful = sum(1 for t in recent_trades if t.get('success', False))
            hourly_profit = sum(t.get('net_profit_usd', 0) for t in recent_trades)
            hourly_gas_cost = sum(t.get('gas_cost_usd', 0) for t in recent_trades)
            
            return {
                'trades': hourly_trades,
                'successful_trades': hourly_successful,
                'success_rate': hourly_successful / hourly_trades if hourly_trades > 0 else 0,
                'profit_usd': hourly_profit,
                'gas_cost_usd': hourly_gas_cost,
                'net_profit_usd': hourly_profit - hourly_gas_cost,
                'avg_profit_per_trade': hourly_profit / hourly_trades if hourly_trades > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating hourly metrics: {e}")
            return {}
            
    def _calculate_trends(self) -> Dict:
        """Calculate performance trends"""
        try:
            if len(self.performance_history) < 10:
                return {}
                
            # Get last 10 data points
            recent_data = list(self.performance_history)[-10:]
            
            # Calculate trends
            profits = [d['metrics']['net_profit_usd'] for d in recent_data]
            success_rates = [d['metrics']['success_rate'] for d in recent_data]
            
            profit_trend = 'increasing' if profits[-1] > profits[0] else 'decreasing'
            success_trend = 'improving' if success_rates[-1] > success_rates[0] else 'declining'
            
            return {
                'profit_trend': profit_trend,
                'success_rate_trend': success_trend,
                'profit_change_1h': profits[-1] - profits[-6] if len(profits) >= 6 else 0,
                'success_rate_change_1h': success_rates[-1] - success_rates[-6] if len(success_rates) >= 6 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
            
    async def _check_alerts(self):
        """Check for alert conditions"""
        while self.running:
            try:
                alerts = []
                
                # Check success rate
                if (self.metrics['total_trades'] > 10 and 
                    self.metrics['success_rate'] < self.alert_thresholds['min_success_rate']):
                    alerts.append({
                        'type': 'low_success_rate',
                        'severity': 'warning',
                        'message': f"Success rate is {self.metrics['success_rate']:.1%}, below threshold of {self.alert_thresholds['min_success_rate']:.1%}",
                        'timestamp': time.time()
                    })
                    
                # Check daily loss
                daily_profit = self._calculate_daily_profit()
                if daily_profit < -self.alert_thresholds['max_daily_loss']:
                    alerts.append({
                        'type': 'daily_loss_exceeded',
                        'severity': 'critical',
                        'message': f"Daily loss of ${abs(daily_profit):.2f} exceeds limit of ${self.alert_thresholds['max_daily_loss']:.2f}",
                        'timestamp': time.time()
                    })
                    
                # Check opportunity detection rate
                hourly_opportunities = self._calculate_hourly_opportunities()
                if hourly_opportunities < self.alert_thresholds['min_hourly_opportunities']:
                    alerts.append({
                        'type': 'low_opportunity_rate',
                        'severity': 'warning',
                        'message': f"Only {hourly_opportunities} opportunities detected in last hour, below threshold of {self.alert_thresholds['min_hourly_opportunities']}",
                        'timestamp': time.time()
                    })
                    
                # Check gas cost ratio
                if self.metrics['total_profit_usd'] > 0:
                    gas_ratio = self.metrics['total_gas_cost_usd'] / self.metrics['total_profit_usd']
                    if gas_ratio > self.alert_thresholds['max_gas_cost_ratio']:
                        alerts.append({
                            'type': 'high_gas_cost_ratio',
                            'severity': 'warning',
                            'message': f"Gas costs are {gas_ratio:.1%} of profits, above threshold of {self.alert_thresholds['max_gas_cost_ratio']:.1%}",
                            'timestamp': time.time()
                        })
                        
                # Process alerts
                for alert in alerts:
                    await self._process_alert(alert)
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(300)
                
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
            
    def _calculate_hourly_opportunities(self) -> int:
        """Calculate opportunities detected in the last hour"""
        try:
            # This would need to be tracked separately in the opportunity detector
            # Return current system metrics
            return self.redis_client.llen('arbitrage_opportunities')
        except:
            return 0
            
    async def _process_alert(self, alert: Dict):
        """Process and send alert"""
        try:
            # Add to alert history
            self.alert_history.append(alert)
            
            # Store in Redis
            self.redis_client.lpush('system_alerts', json.dumps(alert))
            self.redis_client.ltrim('system_alerts', 0, 99)  # Keep last 100 alerts
            
            # Log alert
            severity_emoji = {'info': 'ℹ️', 'warning': '⚠️', 'critical': '🚨'}
            emoji = severity_emoji.get(alert['severity'], '📢')
            
            logger.warning(f"{emoji} ALERT [{alert['type']}]: {alert['message']}")
            
            # Send to external alert systems (Discord, Telegram, etc.)
            await self._send_external_alert(alert)
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            
    async def _send_external_alert(self, alert: Dict):
        """Send alert to external systems"""
        try:
            # This would integrate with the alert system from arbitrage_orchestrator.py
            # For now, just log
            logger.info(f"External alert would be sent: {alert['message']}")
        except Exception as e:
            logger.error(f"Error sending external alert: {e}")
            
    async def _update_dashboard_data(self):
        """Update dashboard data in Redis"""
        while self.running:
            try:
                dashboard_data = {
                    'metrics': self.metrics,
                    'performance_history': list(self.performance_history)[-60:],  # Last hour
                    'alerts': list(self.alert_history)[-20:],  # Last 20 alerts
                    'system_status': self._get_system_status(),
                    'last_updated': time.time()
                }
                
                self.redis_client.set('dashboard_data', json.dumps(dashboard_data))
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error updating dashboard data: {e}")
                await asyncio.sleep(30)
                
    def _get_system_status(self) -> Dict:
        """Get overall system status"""
        try:
            status = 'healthy'
            issues = []
            
            # Check recent activity
            if time.time() - self.metrics.get('last_trade_time', 0) > 3600:  # No trades in 1 hour
                status = 'warning'
                issues.append('No recent trades')
                
            # Check success rate
            if self.metrics['success_rate'] < 0.5 and self.metrics['total_trades'] > 10:
                status = 'warning'
                issues.append('Low success rate')
                
            # Check daily profit
            daily_profit = self._calculate_daily_profit()
            if daily_profit < -100:  # More than $100 loss
                status = 'critical'
                issues.append('Significant daily loss')
                
            return {
                'status': status,
                'issues': issues,
                'uptime_hours': self.metrics['uptime_hours'],
                'last_check': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'status': 'unknown', 'issues': ['Status check failed']}
            
    async def _run_web_dashboard(self):
        """Run simple web dashboard for monitoring"""
        # This would implement a simple web server for the dashboard
        # For now, just log that it would be running
        logger.info(f"Web dashboard would be running on port {self.dashboard_port}")
        
        while self.running:
            await asyncio.sleep(60)
            
    def get_comprehensive_report(self) -> Dict:
        """Get comprehensive system report"""
        return {
            'summary': {
                'uptime_hours': self.metrics['uptime_hours'],
                'total_trades': self.metrics['total_trades'],
                'success_rate': self.metrics['success_rate'],
                'net_profit_usd': self.metrics['net_profit_usd'],
                'profit_per_hour': self.metrics['profit_per_hour']
            },
            'performance': {
                'hourly_metrics': self._calculate_hourly_metrics(),
                'daily_profit': self._calculate_daily_profit(),
                'trends': self._calculate_trends()
            },
            'system_health': self._get_system_status(),
            'recent_alerts': list(self.alert_history)[-10:],
            'generated_at': time.time()
        }
