#!/usr/bin/env python3
"""
🧪 Test AEON Integration
Test the manual approval and autonomous execution modes
"""

import asyncio
import logging
from datetime import datetime, timezone

from core.trading_engine import trading_engine, ArbitrageOpportunity, OpportunityType
from core.aeon_execution_mode import aeon_mode, AEONExecutionMode

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_manual_mode():
    """Test manual approval mode"""
    logger.info("🔴 Testing MANUAL mode")
    
    # Set to manual mode
    aeon_mode.set_mode(AEONExecutionMode.MANUAL)
    
    # Create a test opportunity
    opportunity = ArbitrageOpportunity(
        opportunity_id="test_manual_001",
        type=OpportunityType.SIMPLE_ARBITRAGE,
        dex_a="Uniswap",
        dex_b="Sushiswap",
        token_pair="ETH/USDC",
        price_a=2000.0,
        price_b=2050.0,
        price_difference=50.0,
        potential_profit=45.0,
        gas_cost=5.0,
        net_profit=40.0,
        confidence_score=0.85,
        liquidity_a=100000.0,
        liquidity_b=120000.0,
        slippage_estimate=0.005,
        execution_window=30.0,
        detected_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
    )
    
    logger.info(f"📊 Created test opportunity: {opportunity.net_profit:.2f} USD profit")
    
    # This should trigger manual approval request
    trade = await trading_engine.execute_arbitrage_trade(opportunity)
    
    logger.info(f"🔄 Trade result: {trade.status} - {trade.error_message}")

async def test_autonomous_mode():
    """Test autonomous execution mode"""
    logger.info("🟢 Testing AUTONOMOUS mode")
    
    # Set to autonomous mode
    aeon_mode.set_mode(AEONExecutionMode.AUTONOMOUS)
    
    # Create a test opportunity
    opportunity = ArbitrageOpportunity(
        opportunity_id="test_auto_001",
        type=OpportunityType.SIMPLE_ARBITRAGE,
        dex_a="Curve",
        dex_b="Balancer",
        token_pair="DAI/USDC",
        price_a=1.0,
        price_b=1.002,
        price_difference=0.002,
        potential_profit=15.0,
        gas_cost=3.0,
        net_profit=12.0,
        confidence_score=0.90,
        liquidity_a=200000.0,
        liquidity_b=180000.0,
        slippage_estimate=0.003,
        execution_window=45.0,
        detected_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
    )
    
    logger.info(f"📊 Created test opportunity: {opportunity.net_profit:.2f} USD profit")
    
    # This should execute automatically
    trade = await trading_engine.execute_arbitrage_trade(opportunity)
    
    logger.info(f"🔄 Trade result: {trade.status} - Profit: ${trade.actual_profit:.2f}")

async def test_hybrid_mode():
    """Test hybrid mode"""
    logger.info("🟡 Testing HYBRID mode")
    
    # Set to hybrid mode
    aeon_mode.set_mode(AEONExecutionMode.HYBRID)
    
    # Test small trade (should auto-execute)
    small_opportunity = ArbitrageOpportunity(
        opportunity_id="test_hybrid_small",
        type=OpportunityType.SIMPLE_ARBITRAGE,
        dex_a="1inch",
        dex_b="0x",
        token_pair="USDT/USDC",
        price_a=1.0,
        price_b=1.001,
        price_difference=0.001,
        potential_profit=8.0,
        gas_cost=3.0,
        net_profit=5.0,  # Small profit - should auto-execute
        confidence_score=0.88,
        liquidity_a=150000.0,
        liquidity_b=140000.0,
        slippage_estimate=0.002,
        execution_window=20.0,
        detected_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
    )
    
    logger.info(f"📊 Small trade: {small_opportunity.net_profit:.2f} USD profit (should auto-execute)")
    small_trade = await trading_engine.execute_arbitrage_trade(small_opportunity)
    logger.info(f"🔄 Small trade result: {small_trade.status}")
    
    # Test large trade (should require approval)
    large_opportunity = ArbitrageOpportunity(
        opportunity_id="test_hybrid_large",
        type=OpportunityType.FLASH_LOAN_ARBITRAGE,
        dex_a="Uniswap",
        dex_b="Curve",
        token_pair="WBTC/ETH",
        price_a=15.0,
        price_b=15.2,
        price_difference=0.2,
        potential_profit=150.0,
        gas_cost=10.0,
        net_profit=140.0,  # Large profit - should require approval
        confidence_score=0.92,
        liquidity_a=500000.0,
        liquidity_b=480000.0,
        slippage_estimate=0.004,
        execution_window=60.0,
        detected_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
    )
    
    logger.info(f"📊 Large trade: {large_opportunity.net_profit:.2f} USD profit (should require approval)")
    large_trade = await trading_engine.execute_arbitrage_trade(large_opportunity)
    logger.info(f"🔄 Large trade result: {large_trade.status}")

async def main():
    """Run all tests"""
    logger.info("🧬 Starting AEON Integration Tests")
    
    # Test current mode
    current_status = aeon_mode.get_status()
    logger.info(f"Current AEON mode: {current_status['mode']} {current_status['emoji']}")
    
    try:
        # Test autonomous mode first (no waiting)
        await test_autonomous_mode()
        await asyncio.sleep(1)
        
        # Test hybrid mode
        await test_hybrid_mode()
        await asyncio.sleep(1)
        
        # Test manual mode (will timeout after 5 seconds for demo)
        logger.info("⚠️ Manual mode test will timeout after 5 seconds (no approval)")
        await test_manual_mode()
        
    except Exception as e:
        logger.error(f"Test error: {e}")
    
    logger.info("✅ AEON Integration Tests completed")

if __name__ == "__main__":
    asyncio.run(main())
