#!/usr/bin/env python3
"""
🧪 Test Balancer GraphQL Integration
Verify that all Balancer API queries work correctly with real data
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from integrations.balancer_client import balancer_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_balancer_integration():
    """Test all Balancer GraphQL queries"""
    
    print("🏊 Testing Balancer GraphQL Integration")
    print("=" * 50)
    
    async with balancer_client as client:
        
        # Test 1: Get high-TVL pools
        print("\n1️⃣ Testing High-TVL Pools Query...")
        try:
            pools = await client.get_high_tvl_pools(
                chains=["BASE"], 
                min_tvl=1000, 
                limit=10
            )
            print(f"✅ Found {len(pools)} high-TVL pools")
            
            if pools:
                sample_pool = pools[0]
                print(f"   Sample Pool: {sample_pool.name}")
                print(f"   TVL: ${sample_pool.total_liquidity:,.2f}")
                print(f"   Tokens: {len(sample_pool.tokens)}")
                print(f"   Type: {sample_pool.pool_type}")
            
        except Exception as e:
            print(f"❌ High-TVL pools test failed: {e}")
        
        # Test 2: Get pool details
        print("\n2️⃣ Testing Pool Details Query...")
        try:
            if pools:
                pool_detail = await client.get_pool_details(
                    pool_id=pools[0].id,
                    chain="BASE"
                )
                if pool_detail:
                    print(f"✅ Pool details retrieved successfully")
                    print(f"   Pool ID: {pool_detail.id[:20]}...")
                    print(f"   Swap Fee: {pool_detail.swap_fee * 100:.3f}%")
                    print(f"   Version: v{pool_detail.version}")
                else:
                    print("⚠️ No pool details found")
            else:
                print("⚠️ Skipping - no pools available")
                
        except Exception as e:
            print(f"❌ Pool details test failed: {e}")
        
        # Test 3: Smart Order Router
        print("\n3️⃣ Testing Smart Order Router...")
        try:
            # Test with common Base tokens (if available)
            swap_path = await client.get_smart_order_router_paths(
                token_in="0x4200000000000000000000000000000000000006",  # WETH on Base
                token_out="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC on Base
                amount="1000000000000000000",  # 1 ETH
                chain="BASE"
            )
            
            if swap_path:
                print(f"✅ SOR path found")
                print(f"   Amount In: {swap_path.swap_amount_raw}")
                print(f"   Amount Out: {swap_path.return_amount_raw}")
                print(f"   Price Impact: {swap_path.price_impact:.4f}%")
            else:
                print("⚠️ No SOR path found")
                
        except Exception as e:
            print(f"❌ SOR test failed: {e}")
        
        # Test 4: Find arbitrage opportunities
        print("\n4️⃣ Testing Arbitrage Opportunity Detection...")
        try:
            opportunities = await client.find_arbitrage_opportunities(
                chains=["BASE"],
                min_spread_bps=10  # Lower threshold for testing
            )
            
            print(f"✅ Found {len(opportunities)} arbitrage opportunities")
            
            if opportunities:
                top_opp = opportunities[0]
                print(f"   Top Opportunity:")
                print(f"   - Spread: {top_opp['spread_bps']} bps")
                print(f"   - Pool: {top_opp['pool_address'][:10]}...")
                print(f"   - TVL: ${top_opp['tvl']:,.2f}")
                
        except Exception as e:
            print(f"❌ Arbitrage opportunities test failed: {e}")
        
        # Test 5: High volume pools monitoring
        print("\n5️⃣ Testing High Volume Pool Monitoring...")
        try:
            high_volume_pools = await client.monitor_high_volume_pools(
                chains=["BASE"]
            )
            
            print(f"✅ Found {len(high_volume_pools)} high-volume pools")
            
            if high_volume_pools:
                top_pool = high_volume_pools[0]
                print(f"   Top Volume Pool:")
                print(f"   - Name: {top_pool['name']}")
                print(f"   - Recent Volume: ${top_pool['recent_volume']:,.2f}")
                print(f"   - Swap Count: {top_pool['swap_count']}")
                
        except Exception as e:
            print(f"❌ High volume pools test failed: {e}")
        
        # Test 6: Pool events
        print("\n6️⃣ Testing Pool Events Query...")
        try:
            if pools:
                events = await client.get_pool_events(
                    pool_ids=[pools[0].id],
                    event_types=["SWAP"],
                    limit=10
                )
                
                print(f"✅ Found {len(events)} recent events")
                
                if events:
                    recent_event = events[0]
                    print(f"   Recent Event:")
                    print(f"   - Type: {recent_event.event_type}")
                    print(f"   - Value: ${recent_event.value_usd:.2f}")
                    print(f"   - Pool: {recent_event.pool_id[:10]}...")
                    
            else:
                print("⚠️ Skipping - no pools available")
                
        except Exception as e:
            print(f"❌ Pool events test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Balancer Integration Test Complete!")
    print("\nNext Steps:")
    print("- Run the backend server: python backend/main.py")
    print("- Test endpoints: curl http://64.23.154.163:8000/api/arbitrage/balancer/pools")
    print("- Check ATOM bot: python backend/bots/working/ATOM.py")

async def test_api_endpoints():
    """Test the FastAPI endpoints"""
    import aiohttp
    
    print("\n🌐 Testing API Endpoints...")
    
    base_url = "http://64.23.154.163:8000/api/arbitrage"
    
    endpoints = [
        "/balancer/pools",
        "/balancer/opportunities",
        "/balancer/high-volume-pools"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint}: {response.status}")
                        
                        if "pools" in data:
                            print(f"   Found {len(data['pools'])} pools")
                        elif "opportunities" in data:
                            print(f"   Found {len(data['opportunities'])} opportunities")
                        elif "high_volume_pools" in data:
                            print(f"   Found {len(data['high_volume_pools'])} high-volume pools")
                            
                    else:
                        print(f"❌ {endpoint}: {response.status}")
                        
            except Exception as e:
                print(f"❌ {endpoint}: Connection failed - {e}")

if __name__ == "__main__":
    print("🚀 Starting Balancer Integration Tests...")
    
    # Test the client directly
    asyncio.run(test_balancer_integration())
    
    # Test API endpoints (if server is running)
    print("\n" + "=" * 50)
    try:
        asyncio.run(test_api_endpoints())
    except Exception as e:
        print(f"⚠️ API endpoint tests skipped - server may not be running: {e}")
        print("Start the server with: python backend/main.py")
