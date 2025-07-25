"""
🚀 ATOM Trading Engine - Core Trading Algorithms
Advanced arbitrage detection and execution system
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import json
import time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OpportunityType(str, Enum):
    SIMPLE_ARBITRAGE = "simple_arbitrage"
    TRIANGULAR_ARBITRAGE = "triangular_arbitrage"
    FLASH_LOAN_ARBITRAGE = "flash_loan_arbitrage"
    MEV_ARBITRAGE = "mev_arbitrage"

@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity"""
    opportunity_id: str
    type: OpportunityType
    dex_a: str
    dex_b: str
    token_pair: str
    price_a: float
    price_b: float
    price_difference: float
    potential_profit: float
    gas_cost: float
    net_profit: float
    confidence_score: float
    liquidity_a: float
    liquidity_b: float
    slippage_estimate: float
    execution_window: float  # seconds
    detected_at: datetime
    expires_at: datetime

@dataclass
class TradeExecution:
    """Represents a trade execution"""
    trade_id: str
    opportunity_id: str
    amount_in: float
    amount_out: float
    actual_profit: float
    gas_used: int
    gas_price: float
    execution_time: float
    status: TradeStatus
    tx_hash: Optional[str]
    block_number: Optional[int]
    executed_at: datetime
    error_message: Optional[str] = None

class TradingEngine:
    """Core trading engine for arbitrage execution"""
    
    def __init__(self):
        self.opportunities = {}
        self.active_trades = {}
        self.completed_trades = {}
        self.performance_metrics = {
            "total_trades": 0,
            "successful_trades": 0,
            "total_profit": 0.0,
            "total_volume": 0.0,
            "avg_execution_time": 0.0,
            "success_rate": 0.0
        }
        self.is_running = False
        self.last_scan = datetime.now(timezone.utc)
    
    async def start_engine(self):
        """Start the trading engine"""
        logger.info("🚀 Starting ATOM Trading Engine")
        self.is_running = True
        
        # Start background tasks
        asyncio.create_task(self.opportunity_scanner())
        asyncio.create_task(self.trade_executor())
        asyncio.create_task(self.performance_monitor())
        
        logger.info("✅ Trading Engine started successfully")
    
    async def stop_engine(self):
        """Stop the trading engine"""
        logger.info("🛑 Stopping ATOM Trading Engine")
        self.is_running = False
        
        # Cancel pending trades
        for trade_id, trade in self.active_trades.items():
            if trade.status == TradeStatus.PENDING:
                trade.status = TradeStatus.CANCELLED
                logger.info(f"Cancelled pending trade: {trade_id}")
        
        logger.info("✅ Trading Engine stopped")
    
    async def opportunity_scanner(self):
        """Continuously scan for arbitrage opportunities"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Scan different DEX pairs
                dex_pairs = [
                    ("Uniswap", "Sushiswap"),
                    ("Curve", "Balancer"),
                    ("1inch", "0x"),
                    ("Pancakeswap", "Biswap"),
                    ("Quickswap", "Dfyn")
                ]
                
                token_pairs = [
                    "ETH/USDC", "WBTC/ETH", "USDT/USDC", 
                    "DAI/USDC", "LINK/ETH", "UNI/ETH"
                ]
                
                opportunities_found = 0
                
                for dex_a, dex_b in dex_pairs:
                    for token_pair in token_pairs:
                        opportunity = await self.detect_arbitrage_opportunity(
                            dex_a, dex_b, token_pair
                        )
                        
                        if opportunity and opportunity.net_profit > 10.0:  # Min $10 profit
                            self.opportunities[opportunity.opportunity_id] = opportunity
                            opportunities_found += 1
                            
                            logger.info(
                                f"💰 Opportunity found: {opportunity.dex_a}-{opportunity.dex_b} "
                                f"{opportunity.token_pair} - Profit: ${opportunity.net_profit:.2f}"
                            )
                
                scan_time = time.time() - start_time
                self.last_scan = datetime.now(timezone.utc)
                
                logger.debug(f"Scan completed: {opportunities_found} opportunities in {scan_time:.3f}s")
                
                # Clean expired opportunities
                await self.cleanup_expired_opportunities()
                
                # Wait before next scan
                await asyncio.sleep(0.5)  # 500ms scan interval
                
            except Exception as e:
                logger.error(f"Error in opportunity scanner: {e}")
                await asyncio.sleep(1.0)
    
    async def detect_arbitrage_opportunity(
        self, dex_a: str, dex_b: str, token_pair: str
    ) -> Optional[ArbitrageOpportunity]:
        """Detect arbitrage opportunity between two DEXes"""
        try:
            # Simulate price fetching (replace with real DEX API calls)
            base_price = 2000.0 + (hash(token_pair) % 1000)  # Simulate ETH price
            
            # Add some randomness to simulate real price differences
            price_a = base_price * (1 + (hash(dex_a + token_pair) % 100) / 10000)
            price_b = base_price * (1 + (hash(dex_b + token_pair) % 100) / 10000)
            
            # Ensure there's a meaningful difference
            if abs(price_a - price_b) < base_price * 0.001:  # Less than 0.1%
                return None
            
            # Calculate arbitrage metrics
            price_difference = abs(price_a - price_b)
            trade_amount = 1.0  # 1 ETH equivalent
            
            if price_a > price_b:
                # Buy on dex_b, sell on dex_a
                potential_profit = (price_a - price_b) * trade_amount
                buy_dex, sell_dex = dex_b, dex_a
            else:
                # Buy on dex_a, sell on dex_b
                potential_profit = (price_b - price_a) * trade_amount
                buy_dex, sell_dex = dex_a, dex_b
            
            # Estimate gas cost
            gas_cost = 0.01 * base_price  # ~$20 gas cost
            net_profit = potential_profit - gas_cost
            
            # Calculate confidence score
            liquidity_a = 100000.0 + (hash(dex_a) % 50000)  # Simulate liquidity
            liquidity_b = 100000.0 + (hash(dex_b) % 50000)
            
            min_liquidity = min(liquidity_a, liquidity_b)
            confidence_score = min(0.95, min_liquidity / 150000.0)
            
            # Only return profitable opportunities
            if net_profit <= 0:
                return None
            
            opportunity_id = f"arb_{int(time.time())}_{hash(f'{dex_a}{dex_b}{token_pair}') % 10000}"
            
            return ArbitrageOpportunity(
                opportunity_id=opportunity_id,
                type=OpportunityType.SIMPLE_ARBITRAGE,
                dex_a=dex_a,
                dex_b=dex_b,
                token_pair=token_pair,
                price_a=price_a,
                price_b=price_b,
                price_difference=price_difference,
                potential_profit=potential_profit,
                gas_cost=gas_cost,
                net_profit=net_profit,
                confidence_score=confidence_score,
                liquidity_a=liquidity_a,
                liquidity_b=liquidity_b,
                slippage_estimate=0.005,  # 0.5% slippage
                execution_window=30.0,  # 30 seconds
                detected_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=30)
            )
            
        except Exception as e:
            logger.error(f"Error detecting arbitrage opportunity: {e}")
            return None
    
    async def trade_executor(self):
        """Execute profitable trades"""
        while self.is_running:
            try:
                # Get best opportunities
                profitable_opportunities = [
                    opp for opp in self.opportunities.values()
                    if opp.net_profit > 10.0 and opp.confidence_score > 0.8
                ]
                
                # Sort by profit potential
                profitable_opportunities.sort(key=lambda x: x.net_profit, reverse=True)
                
                # Execute top opportunities
                for opportunity in profitable_opportunities[:5]:  # Max 5 concurrent trades
                    if opportunity.opportunity_id not in self.active_trades:
                        await self.execute_arbitrage_trade(opportunity)
                
                await asyncio.sleep(0.1)  # 100ms execution interval
                
            except Exception as e:
                logger.error(f"Error in trade executor: {e}")
                await asyncio.sleep(1.0)
    
    async def execute_arbitrage_trade(self, opportunity: ArbitrageOpportunity) -> TradeExecution:
        """Execute an arbitrage trade"""
        try:
            trade_id = f"trade_{int(time.time())}_{hash(opportunity.opportunity_id) % 10000}"
            
            # Create trade execution record
            trade = TradeExecution(
                trade_id=trade_id,
                opportunity_id=opportunity.opportunity_id,
                amount_in=1.0,  # 1 ETH
                amount_out=0.0,
                actual_profit=0.0,
                gas_used=0,
                gas_price=25.0,  # 25 gwei
                execution_time=0.0,
                status=TradeStatus.PENDING,
                tx_hash=None,
                block_number=None,
                executed_at=datetime.now(timezone.utc)
            )
            
            self.active_trades[trade_id] = trade
            
            logger.info(f"🔄 Executing trade: {trade_id} for opportunity {opportunity.opportunity_id}")
            
            # Simulate trade execution
            start_time = time.time()
            trade.status = TradeStatus.EXECUTING
            
            # Simulate execution delay
            await asyncio.sleep(0.05 + (hash(trade_id) % 100) / 2000)  # 50-100ms
            
            # Simulate success/failure (95% success rate)
            success = (hash(trade_id) % 100) < 95
            
            if success:
                # Successful execution
                execution_time = time.time() - start_time
                slippage_factor = 1 - opportunity.slippage_estimate
                
                trade.amount_out = opportunity.potential_profit * slippage_factor
                trade.actual_profit = trade.amount_out - opportunity.gas_cost
                trade.gas_used = 180000 + (hash(trade_id) % 50000)
                trade.execution_time = execution_time
                trade.status = TradeStatus.COMPLETED
                trade.tx_hash = f"0x{hash(trade_id):064x}"
                trade.block_number = 18000000 + (int(time.time()) % 100000)
                
                # Update performance metrics
                self.performance_metrics["total_trades"] += 1
                self.performance_metrics["successful_trades"] += 1
                self.performance_metrics["total_profit"] += trade.actual_profit
                self.performance_metrics["total_volume"] += trade.amount_in * opportunity.price_a
                
                logger.info(
                    f"✅ Trade completed: {trade_id} - "
                    f"Profit: ${trade.actual_profit:.2f} - "
                    f"Time: {execution_time:.3f}s"
                )
                
            else:
                # Failed execution
                trade.status = TradeStatus.FAILED
                trade.error_message = "Insufficient liquidity"
                
                self.performance_metrics["total_trades"] += 1
                
                logger.warning(f"❌ Trade failed: {trade_id} - {trade.error_message}")
            
            # Move to completed trades
            self.completed_trades[trade_id] = trade
            del self.active_trades[trade_id]
            
            # Remove executed opportunity
            if opportunity.opportunity_id in self.opportunities:
                del self.opportunities[opportunity.opportunity_id]
            
            return trade
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            trade.status = TradeStatus.FAILED
            trade.error_message = str(e)
            return trade
    
    async def cleanup_expired_opportunities(self):
        """Remove expired opportunities"""
        current_time = datetime.now(timezone.utc)
        expired_ids = [
            opp_id for opp_id, opp in self.opportunities.items()
            if opp.expires_at < current_time
        ]
        
        for opp_id in expired_ids:
            del self.opportunities[opp_id]
        
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired opportunities")
    
    async def performance_monitor(self):
        """Monitor and update performance metrics"""
        while self.is_running:
            try:
                # Update success rate
                if self.performance_metrics["total_trades"] > 0:
                    self.performance_metrics["success_rate"] = (
                        self.performance_metrics["successful_trades"] / 
                        self.performance_metrics["total_trades"]
                    )
                
                # Update average execution time
                if self.completed_trades:
                    execution_times = [
                        trade.execution_time for trade in self.completed_trades.values()
                        if trade.status == TradeStatus.COMPLETED
                    ]
                    if execution_times:
                        self.performance_metrics["avg_execution_time"] = sum(execution_times) / len(execution_times)
                
                await asyncio.sleep(5.0)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(5.0)
    
    def get_current_opportunities(self) -> List[ArbitrageOpportunity]:
        """Get current arbitrage opportunities"""
        return list(self.opportunities.values())
    
    def get_active_trades(self) -> List[TradeExecution]:
        """Get currently active trades"""
        return list(self.active_trades.values())
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    def get_trade_history(self, limit: int = 100) -> List[TradeExecution]:
        """Get recent trade history"""
        trades = list(self.completed_trades.values())
        trades.sort(key=lambda x: x.executed_at, reverse=True)
        return trades[:limit]

# Global trading engine instance
trading_engine = TradingEngine()
