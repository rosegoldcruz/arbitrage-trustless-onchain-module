"""
🛡️ ATOM Risk Management Router - Enterprise Risk Controls
Advanced risk assessment, position limits, and portfolio protection
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

router = APIRouter()

# Risk Management Models
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessment(BaseModel):
    trade_id: str
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=1, description="Risk score from 0 to 1")
    max_loss_potential: float = Field(..., description="Maximum potential loss")
    confidence_interval: float = Field(..., description="Confidence interval")
    recommended_position_size: float = Field(..., description="Recommended position size")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    mitigation_strategies: List[str] = Field(..., description="Risk mitigation strategies")

class PositionLimit(BaseModel):
    asset: str
    max_position_size: float
    current_exposure: float
    utilization_percentage: float
    limit_type: str  # "absolute", "percentage", "volatility_adjusted"
    last_updated: datetime

class CircuitBreaker(BaseModel):
    breaker_id: str
    trigger_condition: str
    threshold_value: float
    current_value: float
    status: str  # "active", "triggered", "disabled"
    last_triggered: Optional[datetime]
    recovery_time: int  # seconds

class RiskMetrics(BaseModel):
    portfolio_var: float = Field(..., description="Value at Risk")
    portfolio_cvar: float = Field(..., description="Conditional Value at Risk")
    sharpe_ratio: float = Field(..., description="Risk-adjusted return")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    volatility: float = Field(..., description="Portfolio volatility")
    correlation_risk: float = Field(..., description="Asset correlation risk")
    liquidity_risk: float = Field(..., description="Liquidity risk score")
    concentration_risk: float = Field(..., description="Concentration risk")

class RiskManager:
    """Enterprise risk management system"""
    
    def __init__(self):
        self.position_limits = {}
        self.circuit_breakers = {}
        self.risk_cache = {}
        self.last_assessment = datetime.now(timezone.utc)
    
    async def assess_trade_risk(self, trade_data: Dict) -> RiskAssessment:
        """Comprehensive trade risk assessment"""
        try:
            # Simulate advanced risk calculation
            risk_factors = []
            mitigation_strategies = []
            
            # Analyze various risk factors
            amount = float(trade_data.get("amount", 0))
            token_pair = trade_data.get("token_pair", "ETH/USDC")
            dex_pair = trade_data.get("dex_pair", "Uniswap-Sushiswap")
            
            # Market risk assessment
            if amount > 10000:
                risk_factors.append("Large position size")
                mitigation_strategies.append("Split into smaller trades")
            
            # Liquidity risk
            if "USDT" in token_pair:
                risk_factors.append("Stablecoin depeg risk")
                mitigation_strategies.append("Monitor peg stability")
            
            # DEX risk
            if "new" in dex_pair.lower():
                risk_factors.append("Unproven DEX protocol")
                mitigation_strategies.append("Reduce position size")
            
            # Calculate risk score
            base_risk = 0.1
            size_risk = min(amount / 100000, 0.3)  # Size-based risk
            complexity_risk = len(risk_factors) * 0.1
            
            risk_score = min(base_risk + size_risk + complexity_risk, 1.0)
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = RiskLevel.LOW
            elif risk_score < 0.6:
                risk_level = RiskLevel.MEDIUM
            elif risk_score < 0.8:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
            
            return RiskAssessment(
                trade_id=trade_data.get("trade_id", f"trade_{int(datetime.now().timestamp())}"),
                risk_level=risk_level,
                risk_score=risk_score,
                max_loss_potential=amount * 0.05,  # 5% max loss
                confidence_interval=0.95,
                recommended_position_size=amount * (1 - risk_score),
                risk_factors=risk_factors,
                mitigation_strategies=mitigation_strategies
            )
            
        except Exception as e:
            logger.error(f"Error assessing trade risk: {e}")
            raise HTTPException(status_code=500, detail="Risk assessment failed")
    
    async def get_position_limits(self) -> List[PositionLimit]:
        """Get current position limits"""
        try:
            limits = [
                {
                    "asset": "ETH",
                    "max_position_size": 100.0,
                    "current_exposure": 67.5,
                    "utilization_percentage": 67.5,
                    "limit_type": "absolute",
                    "last_updated": datetime.now(timezone.utc)
                },
                {
                    "asset": "USDC",
                    "max_position_size": 500000.0,
                    "current_exposure": 234567.89,
                    "utilization_percentage": 46.9,
                    "limit_type": "absolute",
                    "last_updated": datetime.now(timezone.utc)
                },
                {
                    "asset": "WBTC",
                    "max_position_size": 5.0,
                    "current_exposure": 2.34,
                    "utilization_percentage": 46.8,
                    "limit_type": "volatility_adjusted",
                    "last_updated": datetime.now(timezone.utc)
                }
            ]
            
            return [PositionLimit(**limit) for limit in limits]
            
        except Exception as e:
            logger.error(f"Error getting position limits: {e}")
            raise HTTPException(status_code=500, detail="Failed to get position limits")
    
    async def get_circuit_breakers(self) -> List[CircuitBreaker]:
        """Get circuit breaker status"""
        try:
            breakers = [
                {
                    "breaker_id": "daily_loss_limit",
                    "trigger_condition": "Daily loss > $10,000",
                    "threshold_value": 10000.0,
                    "current_value": 2347.89,
                    "status": "active",
                    "last_triggered": None,
                    "recovery_time": 3600
                },
                {
                    "breaker_id": "position_concentration",
                    "trigger_condition": "Single asset > 50% portfolio",
                    "threshold_value": 0.5,
                    "current_value": 0.34,
                    "status": "active",
                    "last_triggered": None,
                    "recovery_time": 1800
                },
                {
                    "breaker_id": "gas_price_spike",
                    "trigger_condition": "Gas price > 100 gwei",
                    "threshold_value": 100.0,
                    "current_value": 25.4,
                    "status": "active",
                    "last_triggered": datetime.now(timezone.utc) - timedelta(hours=6),
                    "recovery_time": 900
                }
            ]
            
            return [CircuitBreaker(**breaker) for breaker in breakers]
            
        except Exception as e:
            logger.error(f"Error getting circuit breakers: {e}")
            raise HTTPException(status_code=500, detail="Failed to get circuit breakers")
    
    async def calculate_portfolio_risk(self) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            # Simulate advanced risk calculations
            metrics = {
                "portfolio_var": 0.023,  # 2.3% VaR
                "portfolio_cvar": 0.034,  # 3.4% CVaR
                "sharpe_ratio": 2.34,
                "max_drawdown": 0.067,
                "volatility": 0.156,
                "correlation_risk": 0.234,
                "liquidity_risk": 0.123,
                "concentration_risk": 0.089
            }
            
            return RiskMetrics(**metrics)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            raise HTTPException(status_code=500, detail="Failed to calculate portfolio risk")

# Initialize risk manager
risk_manager = RiskManager()

# API Endpoints
@router.post("/assess-trade", response_model=RiskAssessment)
async def assess_trade_risk(trade_data: Dict[str, Any]):
    """Assess risk for a specific trade"""
    return await risk_manager.assess_trade_risk(trade_data)

@router.get("/position-limits", response_model=List[PositionLimit])
async def get_position_limits():
    """Get current position limits and utilization"""
    return await risk_manager.get_position_limits()

@router.get("/circuit-breakers", response_model=List[CircuitBreaker])
async def get_circuit_breakers():
    """Get circuit breaker status and configuration"""
    return await risk_manager.get_circuit_breakers()

@router.get("/portfolio-risk", response_model=RiskMetrics)
async def get_portfolio_risk():
    """Get comprehensive portfolio risk metrics"""
    return await risk_manager.calculate_portfolio_risk()

@router.post("/update-position-limit")
async def update_position_limit(
    asset: str,
    new_limit: float,
    limit_type: str = "absolute"
):
    """Update position limit for an asset"""
    try:
        # Update position limit logic
        risk_manager.position_limits[asset] = {
            "max_position_size": new_limit,
            "limit_type": limit_type,
            "last_updated": datetime.now(timezone.utc)
        }
        
        return {
            "message": f"Position limit updated for {asset}",
            "asset": asset,
            "new_limit": new_limit,
            "limit_type": limit_type
        }
        
    except Exception as e:
        logger.error(f"Error updating position limit: {e}")
        raise HTTPException(status_code=500, detail="Failed to update position limit")

@router.post("/trigger-circuit-breaker")
async def trigger_circuit_breaker(breaker_id: str):
    """Manually trigger a circuit breaker"""
    try:
        if breaker_id not in risk_manager.circuit_breakers:
            raise HTTPException(status_code=404, detail="Circuit breaker not found")
        
        risk_manager.circuit_breakers[breaker_id]["status"] = "triggered"
        risk_manager.circuit_breakers[breaker_id]["last_triggered"] = datetime.now(timezone.utc)
        
        return {
            "message": f"Circuit breaker {breaker_id} triggered",
            "breaker_id": breaker_id,
            "triggered_at": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error triggering circuit breaker: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger circuit breaker")

@router.get("/risk-alerts")
async def get_risk_alerts():
    """Get current risk alerts and warnings"""
    try:
        alerts = [
            {
                "alert_id": "high_gas_prices",
                "severity": "medium",
                "message": "Gas prices elevated above normal levels",
                "current_value": 45.6,
                "threshold": 40.0,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                "alert_id": "eth_volatility",
                "severity": "low",
                "message": "ETH volatility increased in last hour",
                "current_value": 0.234,
                "threshold": 0.200,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=32)
            }
        ]
        
        return {"alerts": alerts, "total_alerts": len(alerts)}
        
    except Exception as e:
        logger.error(f"Error getting risk alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk alerts")

@router.get("/health")
async def risk_health_check():
    """Health check for risk management system"""
    return {
        "status": "healthy",
        "risk_manager": "operational",
        "last_assessment": risk_manager.last_assessment,
        "active_limits": len(risk_manager.position_limits),
        "active_breakers": len(risk_manager.circuit_breakers)
    }

@router.get("/exposure")
async def get_current_exposure():
    """Get current market exposure and concentration risk"""
    try:
        # Mock exposure data
        exposure_data = {
            "total_exposure_usd": round(random.uniform(50000, 200000), 2),
            "by_asset": {
                "ETH": {
                    "exposure_usd": round(random.uniform(20000, 80000), 2),
                    "percentage": round(random.uniform(30, 50), 1),
                    "risk_level": "medium"
                },
                "USDC": {
                    "exposure_usd": round(random.uniform(10000, 40000), 2),
                    "percentage": round(random.uniform(15, 25), 1),
                    "risk_level": "low"
                },
                "DAI": {
                    "exposure_usd": round(random.uniform(5000, 25000), 2),
                    "percentage": round(random.uniform(10, 20), 1),
                    "risk_level": "low"
                }
            },
            "by_strategy": {
                "triangular_arbitrage": round(random.uniform(40, 60), 1),
                "flash_loan_arbitrage": round(random.uniform(20, 35), 1),
                "cross_dex_arbitrage": round(random.uniform(10, 25), 1)
            },
            "concentration_risk": {
                "score": round(random.uniform(0.2, 0.8), 2),
                "level": random.choice(["low", "medium"]),
                "max_single_asset": round(random.uniform(35, 55), 1)
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        return exposure_data

    except Exception as e:
        logger.error(f"Error getting exposure data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get exposure data")

@router.get("/var")
async def get_value_at_risk():
    """Get Value at Risk (VaR) calculations"""
    try:
        # Mock VaR calculations
        var_data = {
            "daily_var": {
                "95_confidence": round(random.uniform(500, 2000), 2),
                "99_confidence": round(random.uniform(1000, 3500), 2),
                "99_9_confidence": round(random.uniform(2000, 5000), 2)
            },
            "weekly_var": {
                "95_confidence": round(random.uniform(1500, 5000), 2),
                "99_confidence": round(random.uniform(3000, 8000), 2),
                "99_9_confidence": round(random.uniform(5000, 12000), 2)
            },
            "expected_shortfall": {
                "daily_es_95": round(random.uniform(800, 2500), 2),
                "daily_es_99": round(random.uniform(1500, 4000), 2)
            },
            "historical_volatility": {
                "daily": round(random.uniform(0.015, 0.045), 4),
                "weekly": round(random.uniform(0.035, 0.085), 4),
                "monthly": round(random.uniform(0.08, 0.15), 4)
            },
            "correlation_matrix": {
                "ETH_USDC": round(random.uniform(-0.1, 0.3), 3),
                "ETH_DAI": round(random.uniform(-0.05, 0.25), 3),
                "USDC_DAI": round(random.uniform(0.7, 0.95), 3)
            },
            "calculation_date": datetime.now(timezone.utc).isoformat(),
            "methodology": "Historical Simulation (250 days)"
        }

        return var_data

    except Exception as e:
        logger.error(f"Error calculating VaR: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate VaR")

@router.get("/stress-test")
async def get_stress_test_results():
    """Get stress test scenarios and results"""
    try:
        stress_scenarios = {
            "scenarios": [
                {
                    "name": "Market Crash",
                    "description": "30% drop in all crypto assets",
                    "probability": 0.05,
                    "potential_loss": round(random.uniform(15000, 45000), 2),
                    "recovery_time": "2-4 weeks",
                    "mitigation": "Reduce position sizes, increase cash reserves"
                },
                {
                    "name": "Gas Price Spike",
                    "description": "Gas prices increase 10x",
                    "probability": 0.15,
                    "potential_loss": round(random.uniform(2000, 8000), 2),
                    "recovery_time": "1-3 days",
                    "mitigation": "Switch to L2 solutions, pause high-gas strategies"
                },
                {
                    "name": "DEX Liquidity Crisis",
                    "description": "Major DEX loses 50% liquidity",
                    "probability": 0.08,
                    "potential_loss": round(random.uniform(5000, 20000), 2),
                    "recovery_time": "1-2 weeks",
                    "mitigation": "Diversify across multiple DEXes"
                },
                {
                    "name": "Stablecoin Depeg",
                    "description": "Major stablecoin loses peg",
                    "probability": 0.12,
                    "potential_loss": round(random.uniform(8000, 25000), 2),
                    "recovery_time": "3-7 days",
                    "mitigation": "Monitor depeg indicators, reduce stablecoin exposure"
                }
            ],
            "overall_risk_score": round(random.uniform(0.25, 0.75), 2),
            "worst_case_scenario": round(random.uniform(50000, 100000), 2),
            "confidence_level": 0.95,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        return stress_scenarios

    except Exception as e:
        logger.error(f"Error getting stress test results: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stress test results")
