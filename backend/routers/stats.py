"""
Statistics and analytics router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
from datetime import datetime, timedelta, timezone

router = APIRouter()

class DailyStats(BaseModel):
    date: str
    profit: float
    trades: int
    success_rate: float
    gas_cost: float

class TokenStats(BaseModel):
    symbol: str
    profit: float
    trades: int
    success_rate: float
    volume: float

class NetworkStats(BaseModel):
    network: str
    profit: float
    trades: int
    avg_gas_cost: float
    success_rate: float

class OverallStats(BaseModel):
    total_profit: float
    total_trades: int
    successful_trades: int
    success_rate: float
    avg_profit_per_trade: float
    total_gas_spent: float
    uptime_hours: int
    active_agents: int

class ChartDataPoint(BaseModel):
    timestamp: str
    value: float
    label: Optional[str] = None

@router.get("/overview", response_model=OverallStats)
async def get_overview_stats():
    """Get overall platform statistics"""
    try:
        # Mock data - in production, this would query the database
        total_trades = random.randint(800, 1200)
        successful_trades = int(total_trades * random.uniform(0.92, 0.98))
        total_profit = random.uniform(8000, 15000)
        
        return OverallStats(
            total_profit=round(total_profit, 2),
            total_trades=total_trades,
            successful_trades=successful_trades,
            success_rate=round((successful_trades / total_trades) * 100, 2),
            avg_profit_per_trade=round(total_profit / successful_trades, 2),
            total_gas_spent=round(random.uniform(50, 150), 3),
            uptime_hours=random.randint(720, 744),  # ~30 days
            active_agents=3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(days: int = 7):
    """Get daily statistics for the last N days"""
    try:
        stats = []
        base_date = datetime.now() - timedelta(days=days-1)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            daily_trades = random.randint(15, 45)
            success_rate = random.uniform(0.90, 0.98)
            daily_profit = random.uniform(50, 300)
            gas_cost = random.uniform(0.5, 2.5)
            
            stats.append(DailyStats(
                date=current_date.strftime("%Y-%m-%d"),
                profit=round(daily_profit, 2),
                trades=daily_trades,
                success_rate=round(success_rate * 100, 2),
                gas_cost=round(gas_cost, 3)
            ))
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tokens", response_model=List[TokenStats])
async def get_token_stats():
    """Get statistics by token"""
    try:
        tokens = ["ETH", "USDC", "WBTC", "DAI", "USDT"]
        stats = []
        
        for token in tokens:
            trades = random.randint(50, 200)
            success_rate = random.uniform(0.88, 0.96)
            profit = random.uniform(500, 3000)
            volume = random.uniform(10000, 100000)
            
            stats.append(TokenStats(
                symbol=token,
                profit=round(profit, 2),
                trades=trades,
                success_rate=round(success_rate * 100, 2),
                volume=round(volume, 2)
            ))
        
        return sorted(stats, key=lambda x: x.profit, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/networks", response_model=List[NetworkStats])
async def get_network_stats():
    """Get statistics by network"""
    try:
        networks = ["ethereum", "base", "arbitrum", "polygon"]
        stats = []
        
        for network in networks:
            trades = random.randint(100, 400)
            success_rate = random.uniform(0.85, 0.95)
            profit = random.uniform(1000, 5000)
            avg_gas = random.uniform(0.001, 0.05) if network != "ethereum" else random.uniform(0.01, 0.1)
            
            stats.append(NetworkStats(
                network=network,
                profit=round(profit, 2),
                trades=trades,
                avg_gas_cost=round(avg_gas, 4),
                success_rate=round(success_rate * 100, 2)
            ))
        
        return sorted(stats, key=lambda x: x.profit, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/profit", response_model=List[ChartDataPoint])
async def get_profit_chart_data(period: str = "7d"):
    """Get profit chart data for different time periods"""
    try:
        data_points = []
        
        if period == "24h":
            # Hourly data for last 24 hours
            base_time = datetime.now() - timedelta(hours=23)
            for i in range(24):
                timestamp = base_time + timedelta(hours=i)
                value = random.uniform(5, 50)
                data_points.append(ChartDataPoint(
                    timestamp=timestamp.isoformat(),
                    value=round(value, 2),
                    label=timestamp.strftime("%H:00")
                ))
        elif period == "7d":
            # Daily data for last 7 days
            base_date = datetime.now() - timedelta(days=6)
            for i in range(7):
                date = base_date + timedelta(days=i)
                value = random.uniform(100, 500)
                data_points.append(ChartDataPoint(
                    timestamp=date.isoformat(),
                    value=round(value, 2),
                    label=date.strftime("%m/%d")
                ))
        elif period == "30d":
            # Daily data for last 30 days
            base_date = datetime.now() - timedelta(days=29)
            for i in range(30):
                date = base_date + timedelta(days=i)
                value = random.uniform(80, 600)
                data_points.append(ChartDataPoint(
                    timestamp=date.isoformat(),
                    value=round(value, 2),
                    label=date.strftime("%m/%d")
                ))
        
        return data_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/volume", response_model=List[ChartDataPoint])
async def get_volume_chart_data(period: str = "7d"):
    """Get trading volume chart data"""
    try:
        data_points = []
        
        if period == "24h":
            base_time = datetime.now() - timedelta(hours=23)
            for i in range(24):
                timestamp = base_time + timedelta(hours=i)
                value = random.uniform(1000, 10000)
                data_points.append(ChartDataPoint(
                    timestamp=timestamp.isoformat(),
                    value=round(value, 2),
                    label=timestamp.strftime("%H:00")
                ))
        else:
            # Daily data
            days = 7 if period == "7d" else 30
            base_date = datetime.now() - timedelta(days=days-1)
            for i in range(days):
                date = base_date + timedelta(days=i)
                value = random.uniform(10000, 100000)
                data_points.append(ChartDataPoint(
                    timestamp=date.isoformat(),
                    value=round(value, 2),
                    label=date.strftime("%m/%d")
                ))
        
        return data_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        return {
            "system": {
                "cpu_usage": round(random.uniform(15, 45), 1),
                "memory_usage": round(random.uniform(30, 70), 1),
                "disk_usage": round(random.uniform(20, 50), 1),
                "network_latency": round(random.uniform(10, 50), 1)
            },
            "trading": {
                "avg_execution_time": round(random.uniform(0.5, 2.5), 2),
                "success_rate_24h": round(random.uniform(92, 98), 2),
                "opportunities_detected": random.randint(150, 300),
                "opportunities_executed": random.randint(50, 120)
            },
            "blockchain": {
                "ethereum_gas_price": random.randint(15, 45),
                "base_gas_price": random.randint(1, 5),
                "arbitrum_gas_price": random.randint(1, 3),
                "polygon_gas_price": random.randint(20, 80)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SystemSummary(BaseModel):
    total_profit: float
    total_trades: int
    success_rate: float
    active_bots: int
    system_uptime: str
    last_trade: Optional[str]
    current_opportunities: int
    gas_efficiency: float

@router.get("/summary", response_model=SystemSummary)
async def get_system_summary():
    """Get comprehensive system summary statistics"""
    try:
        total_trades = random.randint(1500, 3000)
        successful_trades = int(total_trades * random.uniform(0.88, 0.96))
        total_profit = random.uniform(25000, 75000)

        # Calculate uptime
        uptime_hours = random.randint(720, 8760)  # 30 days to 1 year
        uptime_days = uptime_hours // 24
        uptime_str = f"{uptime_days} days, {uptime_hours % 24} hours"

        return SystemSummary(
            total_profit=round(total_profit, 2),
            total_trades=total_trades,
            success_rate=round((successful_trades / total_trades) * 100, 2),
            active_bots=random.randint(2, 5),
            system_uptime=uptime_str,
            last_trade=(datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 30))).isoformat(),
            current_opportunities=random.randint(5, 25),
            gas_efficiency=round(random.uniform(85, 98), 1)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")

class BotStats(BaseModel):
    name: str
    status: str
    uptime: str
    trades_today: int
    profit_today: float
    success_rate: float
    avg_execution_time: float
    last_activity: str
    current_strategy: str
    risk_level: str

@router.get("/bots", response_model=List[BotStats])
async def get_bot_statistics():
    """Get statistics for all trading bots"""
    try:
        bots_data = [
            {
                "name": "ATOM",
                "status": "active",
                "uptime": f"{random.randint(12, 72)} hours",
                "trades_today": random.randint(15, 45),
                "profit_today": round(random.uniform(150, 800), 2),
                "success_rate": round(random.uniform(88, 96), 1),
                "avg_execution_time": round(random.uniform(18, 35), 1),
                "last_activity": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 15))).isoformat(),
                "current_strategy": "triangular_arbitrage",
                "risk_level": "medium"
            },
            {
                "name": "ADOM",
                "status": "active",
                "uptime": f"{random.randint(24, 96)} hours",
                "trades_today": random.randint(8, 25),
                "profit_today": round(random.uniform(200, 1200), 2),
                "success_rate": round(random.uniform(90, 98), 1),
                "avg_execution_time": round(random.uniform(12, 28), 1),
                "last_activity": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(2, 20))).isoformat(),
                "current_strategy": "flash_loan_arbitrage",
                "risk_level": "low"
            },
            {
                "name": "MEV_SENTINEL",
                "status": random.choice(["active", "paused"]),
                "uptime": f"{random.randint(6, 48)} hours",
                "trades_today": random.randint(3, 12),
                "profit_today": round(random.uniform(50, 400), 2),
                "success_rate": round(random.uniform(85, 95), 1),
                "avg_execution_time": round(random.uniform(8, 20), 1),
                "last_activity": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(5, 45))).isoformat(),
                "current_strategy": "mev_protection",
                "risk_level": "high"
            },
            {
                "name": "SPECTRE",
                "status": random.choice(["active", "idle"]),
                "uptime": f"{random.randint(1, 24)} hours",
                "trades_today": random.randint(0, 8),
                "profit_today": round(random.uniform(0, 200), 2),
                "success_rate": round(random.uniform(80, 92), 1),
                "avg_execution_time": round(random.uniform(25, 45), 1),
                "last_activity": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 6))).isoformat(),
                "current_strategy": "cross_dex_arbitrage",
                "risk_level": "medium"
            }
        ]

        return [BotStats(**bot) for bot in bots_data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bot stats error: {str(e)}")

@router.get("/realtime")
async def get_realtime_stats():
    """Get real-time system statistics"""
    try:
        return {
            "current_time": datetime.now(timezone.utc).isoformat(),
            "active_trades": random.randint(0, 5),
            "pending_opportunities": random.randint(8, 35),
            "system_load": round(random.uniform(0.2, 0.8), 2),
            "memory_usage": round(random.uniform(45, 85), 1),
            "network_status": "healthy",
            "gas_tracker": {
                "ethereum": {
                    "fast": random.randint(25, 45),
                    "standard": random.randint(20, 35),
                    "safe": random.randint(15, 25)
                },
                "base": {
                    "fast": random.randint(1, 3),
                    "standard": random.randint(1, 2),
                    "safe": 1
                }
            },
            "profit_tracker": {
                "last_hour": round(random.uniform(10, 150), 2),
                "last_24h": round(random.uniform(200, 800), 2),
                "this_week": round(random.uniform(1500, 5000), 2)
            },
            "bot_activity": {
                "atom_last_scan": (datetime.now(timezone.utc) - timedelta(seconds=random.randint(10, 60))).isoformat(),
                "adom_last_execution": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 15))).isoformat(),
                "mev_sentinel_alerts": random.randint(0, 3)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Realtime stats error: {str(e)}")

@router.get("/leaderboard")
async def get_trading_leaderboard():
    """Get trading performance leaderboard"""
    try:
        # Generate mock leaderboard data
        strategies = [
            "Triangular Arbitrage",
            "Flash Loan Arbitrage",
            "Cross-DEX Arbitrage",
            "MEV Arbitrage",
            "Stable Coin Arbitrage"
        ]

        leaderboard = []
        for i, strategy in enumerate(strategies):
            profit = random.uniform(1000, 10000)
            trades = random.randint(50, 300)

            leaderboard.append({
                "rank": i + 1,
                "strategy": strategy,
                "total_profit": round(profit, 2),
                "total_trades": trades,
                "success_rate": round(random.uniform(85, 98), 1),
                "avg_profit_per_trade": round(profit / trades, 2),
                "roi_percentage": round(random.uniform(15, 45), 1),
                "last_active": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24))).isoformat()
            })

        # Sort by profit
        leaderboard.sort(key=lambda x: x["total_profit"], reverse=True)

        # Update ranks
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1

        return {
            "leaderboard": leaderboard,
            "period": "30 days",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leaderboard error: {str(e)}")
