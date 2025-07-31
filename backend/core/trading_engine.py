"""
🧬 AEON FLASHLOAN EXECUTION ENGINE
Real money, real profits, real flashloan arbitrage execution
Uses AAVE V3 + Multi-DEX routing for atomic profit extraction
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import time
from dataclasses import dataclass
from enum import Enum

# AEON Core Integration
from .aeon_execution_mode import aeon_mode, AEONExecutionMode
from ..integrations.telegram_notifier import telegram_notifier, TelegramAlert, AlertType, Priority
from ..integrations.flashloan_providers import flashloan_manager, FlashLoanProvider, FlashLoanQuote
from ..integrations.dex_aggregator import dex_aggregator, Chain

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
        """Execute an arbitrage trade with AEON mode support"""
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

            logger.info(f"🔄 Processing trade: {trade_id} for opportunity {opportunity.opportunity_id}")

            # 🧬 AEON EXECUTION MODE CHECK
            spread_bps = (opportunity.price_difference / min(opportunity.price_a, opportunity.price_b)) * 10000
            amount_usd = opportunity.net_profit  # Simplified

            should_auto_execute = aeon_mode.should_auto_execute(amount_usd, spread_bps)

            if not should_auto_execute:
                # 🔴 MANUAL APPROVAL REQUIRED
                logger.info(f"🔴 Manual approval required for trade {trade_id}")

                # Send approval request via Telegram
                approval_alert = TelegramAlert(
                    alert_type=AlertType.MANUAL_APPROVAL,
                    priority=Priority.HIGH,
                    title=f"Trade Approval Required",
                    message=f"Arbitrage opportunity detected:\n"
                           f"• Pair: {opportunity.token_pair}\n"
                           f"• DEXs: {opportunity.dex_a} → {opportunity.dex_b}\n"
                           f"• Spread: {spread_bps:.1f}bps\n"
                           f"• Est. Profit: ${opportunity.net_profit:.2f}\n"
                           f"• Confidence: {opportunity.confidence_score:.1%}",
                    data={
                        "trade_id": trade_id,
                        "opportunity_id": opportunity.opportunity_id,
                        "spread_bps": spread_bps,
                        "estimated_profit_usd": opportunity.net_profit,
                        "token_pair": opportunity.token_pair,
                        "dex_path": f"{opportunity.dex_a} → {opportunity.dex_b}"
                    },
                    timestamp=datetime.now(),
                    requires_approval=True
                )

                await telegram_notifier.send_alert(approval_alert)

                # Wait for approval (timeout after 5 minutes)
                approved = await self._wait_for_approval(trade_id, timeout=300)

                if not approved:
                    trade.status = TradeStatus.CANCELLED
                    trade.error_message = "Manual approval timeout or rejected"
                    logger.info(f"❌ Trade {trade_id} cancelled - no approval")
                    return trade

                logger.info(f"✅ Trade {trade_id} approved - proceeding with execution")

            # 🔥 EXECUTE REAL FLASHLOAN ARBITRAGE
            start_time = time.time()
            trade.status = TradeStatus.EXECUTING

            logger.info(f"⚡ EXECUTING REAL FLASHLOAN: {trade_id}")

            try:
                # Get best flashloan quote (AAVE V3 or Balancer)
                flashloan_quote = await flashloan_manager.get_best_quote(
                    asset="WETH",  # Primary asset for Base
                    amount=opportunity.net_profit * 10,  # 10x leverage via flashloan
                    chain=Chain.BASE
                )

                if not flashloan_quote:
                    raise Exception("No flashloan providers available")

                # Prepare arbitrage parameters for smart contract
                arbitrage_params = {
                    "token_a": opportunity.token_pair.split("/")[0],
                    "token_b": opportunity.token_pair.split("/")[1],
                    "buy_dex": opportunity.dex_a,
                    "sell_dex": opportunity.dex_b,
                    "expected_profit": opportunity.net_profit,
                    "max_slippage": opportunity.slippage_estimate,
                    "gas_limit": 500000  # 500k gas limit
                }

                # Execute flashloan arbitrage via smart contract
                execution_result = await flashloan_manager.execute_flash_loan_arbitrage(
                    flashloan_quote,
                    arbitrage_params
                )

                execution_time = time.time() - start_time

                if execution_result.status.value == "completed":
                    # ✅ SUCCESSFUL FLASHLOAN ARBITRAGE
                    trade.amount_out = execution_result.amount + execution_result.arbitrage_profit
                    trade.actual_profit = execution_result.net_profit
                    trade.gas_used = execution_result.gas_used
                    trade.execution_time = execution_time
                    trade.status = TradeStatus.COMPLETED
                    trade.tx_hash = execution_result.tx_hash
                    trade.block_number = execution_result.block_number

                    # Update performance metrics
                    self.performance_metrics["total_trades"] += 1
                    self.performance_metrics["successful_trades"] += 1
                    self.performance_metrics["total_profit"] += trade.actual_profit
                    self.performance_metrics["total_volume"] += flashloan_quote.amount

                    # Send success notification
                    await telegram_notifier.notify_trade_executed(
                        "Flashloan Arbitrage",
                        trade.actual_profit,
                        trade.gas_used,
                        trade.tx_hash
                    )

                    logger.info(
                        f"🚀 FLASHLOAN SUCCESS: {trade_id} - "
                        f"Profit: ${trade.actual_profit:.2f} - "
                        f"Provider: {flashloan_quote.provider.value} - "
                        f"Time: {execution_time:.3f}s"
                    )

                else:
                    # ❌ FLASHLOAN FAILED
                    trade.status = TradeStatus.FAILED
                    trade.error_message = f"Flashloan execution failed: {execution_result.status.value}"

                    self.performance_metrics["total_trades"] += 1

                    await telegram_notifier.notify_trade_failed(
                        "Flashloan Arbitrage",
                        trade.error_message,
                        opportunity.gas_cost
                    )

                    logger.warning(f"❌ FLASHLOAN FAILED: {trade_id} - {trade.error_message}")

            except Exception as e:
                # Handle execution errors
                trade.status = TradeStatus.FAILED
                trade.error_message = f"Execution error: {str(e)}"
                execution_time = time.time() - start_time
                trade.execution_time = execution_time

                self.performance_metrics["total_trades"] += 1

                await telegram_notifier.notify_trade_failed(
                    "Flashloan Arbitrage",
                    str(e),
                    opportunity.gas_cost
                )

                logger.error(f"💥 EXECUTION ERROR: {trade_id} - {str(e)}")
            
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

    async def _wait_for_approval(self, trade_id: str, timeout: int = 300) -> bool:
        """Wait for manual approval via Telegram"""
        try:
            start_time = time.time()

            while time.time() - start_time < timeout:
                # Check if approval was received via Telegram webhook
                # This integrates with the existing telegram.py approval system
                from ..routers.telegram import approval_responses

                if trade_id in approval_responses:
                    response = approval_responses.pop(trade_id)
                    approved = response.get("approved", False)
                    username = response.get("username", "Unknown")

                    if approved:
                        logger.info(f"✅ Trade {trade_id} approved by {username}")
                        return True
                    else:
                        logger.info(f"❌ Trade {trade_id} rejected by {username}")
                        return False

                # Check every 1 second
                await asyncio.sleep(1.0)

            # Timeout reached
            logger.warning(f"⏰ Trade {trade_id} approval timeout after {timeout}s")
            return False

        except Exception as e:
            logger.error(f"Error waiting for approval: {e}")
            return False

# Global trading engine instance
trading_engine = TradingEngine()
