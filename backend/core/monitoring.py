"""
ATOM Monitoring & Alerting System
Real-time monitoring for arbitrage execution with dashboard integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class TradeMetrics:
    trade_id: str
    timestamp: datetime
    token_pair: str
    dex_path: List[str]
    amount_in: float
    amount_out: float
    profit_usd: float
    gas_used: int
    gas_cost_usd: float
    execution_time: float
    success: bool
    tx_hash: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SystemAlert:
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    component: str
    resolved: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class PerformanceMetrics:
    total_trades: int
    successful_trades: int
    failed_trades: int
    total_profit_usd: float
    total_volume_usd: float
    average_execution_time: float
    success_rate: float
    uptime_percentage: float
    last_trade_timestamp: Optional[datetime] = None

class MonitoringSystem:
    """
    Comprehensive monitoring system for ATOM arbitrage execution
    """
    
    def __init__(self):
        self.trade_history: List[TradeMetrics] = []
        self.active_alerts: List[SystemAlert] = []
        self.performance_metrics = PerformanceMetrics(
            total_trades=0,
            successful_trades=0,
            failed_trades=0,
            total_profit_usd=0.0,
            total_volume_usd=0.0,
            average_execution_time=0.0,
            success_rate=0.0,
            uptime_percentage=100.0
        )
        self.system_start_time = datetime.now(timezone.utc)
        self.last_health_check = None
        self.dashboard_subscribers = []
    
    async def log_trade_execution(
        self,
        trade_id: str,
        token_pair: str,
        dex_path: List[str],
        amount_in: float,
        amount_out: float,
        profit_usd: float,
        gas_used: int,
        gas_cost_usd: float,
        execution_time: float,
        success: bool,
        tx_hash: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log trade execution with comprehensive metrics"""
        
        trade_metrics = TradeMetrics(
            trade_id=trade_id,
            timestamp=datetime.now(timezone.utc),
            token_pair=token_pair,
            dex_path=dex_path,
            amount_in=amount_in,
            amount_out=amount_out,
            profit_usd=profit_usd,
            gas_used=gas_used,
            gas_cost_usd=gas_cost_usd,
            execution_time=execution_time,
            success=success,
            tx_hash=tx_hash,
            error_message=error_message
        )
        
        # Add to trade history
        self.trade_history.append(trade_metrics)
        
        # Update performance metrics
        self._update_performance_metrics(trade_metrics)
        
        # Log to Supabase
        await self._log_to_supabase(trade_metrics)
        
        # Check for alerts
        await self._check_trade_alerts(trade_metrics)
        
        # Notify dashboard subscribers
        await self._notify_dashboard(trade_metrics)
        
        logger.info(f"📊 Trade logged: {trade_id} - Success: {success} - Profit: ${profit_usd:.2f}")
    
    def _update_performance_metrics(self, trade: TradeMetrics):
        """Update system performance metrics"""
        self.performance_metrics.total_trades += 1
        self.performance_metrics.total_volume_usd += trade.amount_in
        self.performance_metrics.last_trade_timestamp = trade.timestamp
        
        if trade.success:
            self.performance_metrics.successful_trades += 1
            self.performance_metrics.total_profit_usd += trade.profit_usd
        else:
            self.performance_metrics.failed_trades += 1
        
        # Calculate success rate
        if self.performance_metrics.total_trades > 0:
            self.performance_metrics.success_rate = (
                self.performance_metrics.successful_trades / self.performance_metrics.total_trades
            ) * 100
        
        # Calculate average execution time
        if self.trade_history:
            total_time = sum(t.execution_time for t in self.trade_history)
            self.performance_metrics.average_execution_time = total_time / len(self.trade_history)
        
        # Calculate uptime
        uptime_seconds = (datetime.now(timezone.utc) - self.system_start_time).total_seconds()
        self.performance_metrics.uptime_percentage = min(100.0, (uptime_seconds / (24 * 3600)) * 100)
    
    async def _log_to_supabase(self, trade: TradeMetrics):
        """Log trade to Supabase database"""
        try:
            from backend.real_orchestrator import _async_db
            
            if not _async_db or not _async_db.pool:
                logger.warning("⚠️ Supabase connection not available")
                return
            
            async with _async_db.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO trade_executions (
                        trade_id, timestamp, token_pair, dex_path, amount_in, amount_out,
                        profit_usd, gas_used, gas_cost_usd, execution_time, success,
                        tx_hash, error_message, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ''',
                trade.trade_id,
                trade.timestamp,
                trade.token_pair,
                json.dumps(trade.dex_path),
                trade.amount_in,
                trade.amount_out,
                trade.profit_usd,
                trade.gas_used,
                trade.gas_cost_usd,
                trade.execution_time,
                trade.success,
                trade.tx_hash,
                trade.error_message,
                json.dumps({"component": "atom_arbitrage"})
                )
                
            logger.info(f"✅ Trade {trade.trade_id} logged to Supabase")
            
        except Exception as e:
            logger.error(f"❌ Failed to log trade to Supabase: {e}")
    
    async def _check_trade_alerts(self, trade: TradeMetrics):
        """Check for alert conditions based on trade execution"""
        
        # Alert on failed trades
        if not trade.success:
            await self.create_alert(
                level=AlertLevel.ERROR,
                title="Trade Execution Failed",
                message=f"Trade {trade.trade_id} failed: {trade.error_message}",
                component="trading_engine",
                metadata={"trade_id": trade.trade_id, "token_pair": trade.token_pair}
            )
        
        # Alert on low profit
        if trade.success and trade.profit_usd < 1.0:
            await self.create_alert(
                level=AlertLevel.WARNING,
                title="Low Profit Trade",
                message=f"Trade {trade.trade_id} profit ${trade.profit_usd:.2f} below $1.00",
                component="trading_engine",
                metadata={"trade_id": trade.trade_id, "profit": trade.profit_usd}
            )
        
        # Alert on high gas costs
        if trade.gas_cost_usd > trade.profit_usd * 0.5:
            await self.create_alert(
                level=AlertLevel.WARNING,
                title="High Gas Cost",
                message=f"Trade {trade.trade_id} gas cost ${trade.gas_cost_usd:.2f} is {(trade.gas_cost_usd/trade.profit_usd)*100:.1f}% of profit",
                component="trading_engine",
                metadata={"trade_id": trade.trade_id, "gas_cost": trade.gas_cost_usd}
            )
        
        # Alert on slow execution
        if trade.execution_time > 30.0:
            await self.create_alert(
                level=AlertLevel.WARNING,
                title="Slow Trade Execution",
                message=f"Trade {trade.trade_id} took {trade.execution_time:.1f}s to execute",
                component="trading_engine",
                metadata={"trade_id": trade.trade_id, "execution_time": trade.execution_time}
            )
    
    async def create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        component: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create a system alert"""
        
        alert = SystemAlert(
            alert_id=f"alert_{int(datetime.now(timezone.utc).timestamp())}_{len(self.active_alerts)}",
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(timezone.utc),
            component=component,
            metadata=metadata or {}
        )
        
        self.active_alerts.append(alert)
        
        # Log alert
        logger.log(
            logging.ERROR if level in [AlertLevel.ERROR, AlertLevel.CRITICAL] else logging.WARNING,
            f"🚨 {level.value.upper()} ALERT: {title} - {message}"
        )
        
        # Notify dashboard
        await self._notify_dashboard_alert(alert)
    
    async def _notify_dashboard(self, trade: TradeMetrics):
        """Notify dashboard of new trade execution"""
        notification = {
            "type": "trade_execution",
            "data": asdict(trade),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # In a real implementation, this would use WebSocket or Server-Sent Events
        # For now, we'll store it for dashboard polling
        logger.info(f"📡 Dashboard notification: Trade {trade.trade_id}")
    
    async def _notify_dashboard_alert(self, alert: SystemAlert):
        """Notify dashboard of new alert"""
        notification = {
            "type": "system_alert",
            "data": asdict(alert),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"📡 Dashboard alert: {alert.title}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary for dashboard"""
        return {
            "metrics": asdict(self.performance_metrics),
            "recent_trades": [
                asdict(trade) for trade in self.trade_history[-10:]
            ],
            "active_alerts": [
                asdict(alert) for alert in self.active_alerts if not alert.resolved
            ],
            "system_uptime": (datetime.now(timezone.utc) - self.system_start_time).total_seconds(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def get_trade_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trade history"""
        recent_trades = self.trade_history[-limit:] if limit else self.trade_history
        return [asdict(trade) for trade in recent_trades]
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"✅ Alert resolved: {alert.title}")
                return True
        return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        recent_failures = sum(
            1 for trade in self.trade_history[-20:] if not trade.success
        )
        
        critical_alerts = sum(
            1 for alert in self.active_alerts 
            if alert.level == AlertLevel.CRITICAL and not alert.resolved
        )
        
        health_status = "healthy"
        if critical_alerts > 0:
            health_status = "critical"
        elif recent_failures > 5:
            health_status = "degraded"
        elif recent_failures > 2:
            health_status = "warning"
        
        return {
            "status": health_status,
            "uptime_seconds": (datetime.now(timezone.utc) - self.system_start_time).total_seconds(),
            "recent_failures": recent_failures,
            "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
            "critical_alerts": critical_alerts,
            "last_trade": self.performance_metrics.last_trade_timestamp.isoformat() if self.performance_metrics.last_trade_timestamp else None
        }

# Global monitoring system instance
monitoring_system = MonitoringSystem()
