#!/usr/bin/env python3
"""
DASHBOARD API ROUTER
Real-time dashboard endpoints for ATOM frontend
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
import asyncio
from typing import Dict, List, Any

# Import your existing modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from backend.bots.working.config import get_atom_config
except ImportError:
    from backend.bots.working_config import get_atom_config

try:
    from backend.integrations.dex_aggregator import DEXAggregator
except ImportError:
    # Fallback if DEXAggregator doesn't exist
    DEXAggregator = None

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

# Initialize services
dex_aggregator = DEXAggregator() if DEXAggregator else None
config = get_atom_config()

# Mock data for now - replace with real data from your bots
app_state = {
    "system_status": "healthy",
    "agents": {
        "ATOM": {"status": "active", "profit": 125.50, "trades": 15, "type": "spot"},
        "ADOM": {"status": "active", "profit": 89.25, "trades": 8, "type": "flashloan"},
        "ARCHANGEL": {"status": "standby", "profit": 0.0, "trades": 0, "type": "emergency"}
    },
    "total_profit": 214.75,
    "active_agents": 2,
    "opportunities": [],
    "trades": [],
    "dex_connections": {
        "0x": "healthy",
        "balancer": "healthy", 
        "curve": "healthy",
        "uniswap": "healthy"
    },
    "real_time_data": {
        "gas_price": 25.5,
        "eth_price": 2450.75,
        "spread_opportunities": 3,
        "profitable_paths": 12
    }
}

@router.get("/status")
async def get_dashboard_status():
    """Get real-time dashboard status"""
    try:
        return {
            "status": "success",
            "data": {
                "system_status": app_state["system_status"],
                "agents": app_state["agents"],
                "total_profit": app_state["total_profit"],
                "active_agents": app_state["active_agents"],
                "last_update": datetime.utcnow().isoformat(),
                "dex_connections": app_state["dex_connections"],
                "real_time_data": app_state["real_time_data"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/opportunities")
async def get_opportunities():
    """Get real-time arbitrage opportunities"""
    try:
        # Get real opportunities from DEX aggregator
        opportunities = []
        
        # Sample opportunity data - replace with real DEX data
        sample_opportunities = [
            {
                "id": "opp_001",
                "path": "WETH → USDC → DAI → WETH",
                "spread_bps": 45,
                "profit_usd": 12.50,
                "dex_route": "Balancer → Curve → Uniswap",
                "confidence": 0.85,
                "detected_at": datetime.utcnow().isoformat()
            },
            {
                "id": "opp_002", 
                "path": "USDC → GHO → DAI → USDC",
                "spread_bps": 32,
                "profit_usd": 8.75,
                "dex_route": "0x → Curve → Balancer",
                "confidence": 0.78,
                "detected_at": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "status": "success",
            "data": {
                "opportunities": sample_opportunities,
                "total_opportunities": len(sample_opportunities),
                "profitable_count": len([o for o in sample_opportunities if o["profit_usd"] > 5]),
                "last_update": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dex-status")
async def get_dex_status():
    """Get DEX connection status"""
    try:
        return {
            "status": "success",
            "data": {
                "connections": app_state["dex_connections"],
                "healthy_connections": len([c for c in app_state["dex_connections"].values() if c == "healthy"]),
                "total_connections": len(app_state["dex_connections"]),
                "last_check": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting DEX status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-opportunity")
async def execute_opportunity(request: Dict[str, Any]):
    """Execute an arbitrage opportunity"""
    try:
        opportunity_id = request.get("opportunity_id")
        if not opportunity_id:
            raise HTTPException(status_code=400, detail="opportunity_id required")
        
        # Mock execution - replace with real execution logic
        result = {
            "opportunity_id": opportunity_id,
            "status": "executed",
            "profit_realized": 12.50,
            "gas_used": 150000,
            "tx_hash": "0x1234567890abcdef1234567890abcdef12345678",
            "executed_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error executing opportunity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bot-logs")
async def get_bot_logs():
    """Get bot logs and activity"""
    try:
        # Mock logs - replace with real log data
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "bot": "ATOM",
                "level": "INFO",
                "message": "Scanning for arbitrage opportunities..."
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "bot": "ADOM", 
                "level": "SUCCESS",
                "message": "Flash loan executed successfully, profit: $12.50"
            }
        ]
        
        return {
            "status": "success",
            "data": {
                "logs": logs,
                "total_logs": len(logs)
            }
        }
    except Exception as e:
        logger.error(f"Error getting bot logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data")
async def get_market_data():
    """Get real-time market data"""
    try:
        return {
            "status": "success",
            "data": {
                "gas_price": app_state["real_time_data"]["gas_price"],
                "eth_price": app_state["real_time_data"]["eth_price"],
                "base_fee": 20.5,
                "network_congestion": "low"
            }
        }
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
async def get_system_health():
    """Get system health check"""
    try:
        return {
            "status": "success",
            "data": {
                "overall_status": "healthy",
                "components": {
                    "api": {"status": "healthy", "last_check": datetime.utcnow().isoformat()},
                    "bots": {"status": "healthy", "last_check": datetime.utcnow().isoformat()},
                    "dex_connections": {"status": "healthy", "last_check": datetime.utcnow().isoformat()},
                    "database": {"status": "healthy", "last_check": datetime.utcnow().isoformat()}
                },
                "uptime": 3600  # seconds
            }
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading-history")
async def get_trading_history(limit: int = 50):
    """Get trading history"""
    try:
        # Mock trading history - replace with real data
        trades = [
            {
                "id": "trade_001",
                "timestamp": datetime.utcnow().isoformat(),
                "bot": "ATOM",
                "type": "triangular_arbitrage",
                "profit": 12.50,
                "gas_used": 150000,
                "tx_hash": "0x1234567890abcdef1234567890abcdef12345678",
                "status": "completed"
            }
        ]
        
        return {
            "status": "success",
            "data": {
                "trades": trades[:limit],
                "total_trades": len(trades),
                "total_profit": sum(t["profit"] for t in trades)
            }
        }
    except Exception as e:
        logger.error(f"Error getting trading history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-dex-connections")
async def test_dex_connections():
    """Test DEX connections manually"""
    try:
        # Mock test results - replace with real connection tests
        test_results = {
            "0x": {"status": "healthy", "response_time": 150},
            "balancer": {"status": "healthy", "response_time": 200},
            "curve": {"status": "healthy", "response_time": 180},
            "uniswap": {"status": "healthy", "response_time": 120}
        }
        
        return {
            "status": "success",
            "data": {
                "test_results": test_results,
                "overall_health": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Error testing DEX connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))
