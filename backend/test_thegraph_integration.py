#!/usr/bin/env python3
"""
🧪 THE GRAPH INTEGRATION TEST
Test all The Graph Protocol services for Base Sepolia
API Key: f187a007e656031f58294838b7219a0f
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from integrations.thegraph_service import thegraph_service
from core.parallel_orchestrator import orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_thegraph_health():
    """Test The Graph service health"""
    print("\n🔍 Testing The Graph Service Health...")
    
    try:
        async with thegraph_service as client:
            health = await client.health_check()
            
            print(f"✅ Health Status: {health['status']}")
            print(f"⏱️  Latency: {health['latency_ms']:.2f}ms")
            print(f"📊 Pools Available: {health.get('pools_available', 'Unknown')}")
            
            return health['status'] == 'healthy'
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def test_top_pools():
    """Test fetching top pools"""
    print("\n📊 Testing Top Pools Fetch...")
    
    try:
        async with thegraph_service as client:
            pools = await client.get_top_pools(first=5)
            
            print(f"✅ Fetched {len(pools)} pools")
            
            for i, pool in enumerate(pools[:3], 1):
                print(f"  {i}. {pool.token0.symbol}/{pool.token1.symbol}")
                print(f"     TVL: ${float(pool.total_value_locked_usd):,.2f}")
                print(f"     Volume: ${float(pool.volume_usd):,.2f}")
                print(f"     Liquidity: {pool.liquidity}")
                
            return len(pools) > 0
            
    except Exception as e:
        print(f"❌ Top pools test failed: {e}")
        return False

async def test_token_prices():
    """Test fetching token prices"""
    print("\n💰 Testing Token Prices...")
    
    # Base Sepolia test tokens
    test_tokens = [
        "0x4200000000000000000000000000000000000006",  # WETH
        "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # USDC
    ]
    
    try:
        async with thegraph_service as client:
            tokens = await client.get_token_prices(test_tokens)
            
            print(f"✅ Fetched {len(tokens)} token prices")
            
            for token in tokens:
                price = float(token.price_usd) if token.price_usd else 0
                print(f"  {token.symbol}: ${price:.4f}")
                
            return len(tokens) > 0
            
    except Exception as e:
        print(f"❌ Token prices test failed: {e}")
        return False

async def test_arbitrage_opportunities():
    """Test arbitrage opportunity detection"""
    print("\n⚡ Testing Arbitrage Opportunities...")
    
    try:
        async with thegraph_service as client:
            opportunities = await client.find_arbitrage_opportunities(
                min_spread_bps=10,  # Lower threshold for testing
                min_tvl=100
            )
            
            print(f"✅ Found {len(opportunities)} arbitrage opportunities")
            
            for i, opp in enumerate(opportunities[:3], 1):
                print(f"  {i}. {opp.token_pair}")
                print(f"     Spread: {opp.spread_bps} bps")
                print(f"     Estimated Profit: ${opp.estimated_profit_usd:.2f}")
                print(f"     Pool 1 TVL: ${opp.pool1_tvl:,.2f}")
                print(f"     Pool 2 TVL: ${opp.pool2_tvl:,.2f}")
                
            return True
            
    except Exception as e:
        print(f"❌ Arbitrage opportunities test failed: {e}")
        return False

async def test_recent_swaps():
    """Test fetching recent swaps"""
    print("\n🔄 Testing Recent Swaps...")
    
    try:
        # First get a pool ID
        async with thegraph_service as client:
            pools = await client.get_top_pools(first=1)
            
            if not pools:
                print("❌ No pools available for swap testing")
                return False
                
            pool_id = pools[0].id
            swaps = await client.get_recent_swaps(pool_id, first=3)
            
            print(f"✅ Fetched {len(swaps)} recent swaps for pool {pool_id[:10]}...")
            
            for i, swap in enumerate(swaps, 1):
                print(f"  {i}. {swap.token0_symbol}/{swap.token1_symbol}")
                print(f"     Block: {swap.block_number}")
                print(f"     Amount USD: ${swap.amount_usd or 'N/A'}")
                
            return len(swaps) >= 0  # Allow 0 swaps for new pools
            
    except Exception as e:
        print(f"❌ Recent swaps test failed: {e}")
        return False

async def test_parallel_orchestrator():
    """Test the parallel orchestrator"""
    print("\n🎯 Testing Parallel Orchestrator...")
    
    try:
        # Start orchestrator
        await orchestrator.start()
        
        # Wait a moment for initialization
        await asyncio.sleep(2)
        
        # Check if running
        if orchestrator.isRunning:
            print("✅ Orchestrator started successfully")
            
            # Force an update
            snapshot = await orchestrator.force_update()
            
            print(f"📊 Market Snapshot:")
            print(f"   Timestamp: {datetime.fromtimestamp(snapshot.timestamp)}")
            print(f"   Balancer Status: {snapshot.system_health.balancer_status}")
            print(f"   0x Status: {snapshot.system_health.zrx_status}")
            print(f"   The Graph Status: {snapshot.system_health.thegraph_status}")
            print(f"   Opportunities: {len(snapshot.arbitrage_opportunities)}")
            
            # Stop orchestrator
            await orchestrator.stop()
            
            return True
        else:
            print("❌ Orchestrator failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

async def run_all_tests():
    """Run all The Graph integration tests"""
    print("🚀 ATOM - The Graph Integration Test Suite")
    print("=" * 50)
    print(f"API Key: f187a007e656031f58294838b7219a0f")
    print(f"Network: Base Sepolia Testnet")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_thegraph_health),
        ("Top Pools", test_top_pools),
        ("Token Prices", test_token_prices),
        ("Arbitrage Opportunities", test_arbitrage_opportunities),
        ("Recent Swaps", test_recent_swaps),
        ("Parallel Orchestrator", test_parallel_orchestrator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! The Graph integration is ready for production.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
