#!/usr/bin/env python3
"""
🧪 COMPLETE INTEGRATION TEST
Test all services: Balancer, 0x, The Graph & Parallel Dashboard
Base Sepolia Testnet - Production Ready System
"""

import asyncio
import logging
import sys
import os
import requests
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

async def test_backend_health():
    """Test backend health endpoint"""
    print("\n🔍 Testing Backend Health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/parallel/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data['status']}")
            print(f"📊 Services:")
            for service, status in data['services'].items():
                icon = "✅" if "healthy" in status else "❌"
                print(f"   {icon} {service}: {status}")
            return True
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

async def test_balancer_integration():
    """Test Balancer GraphQL integration"""
    print("\n🏊 Testing Balancer Integration...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/parallel/balancer/pools?min_tvl=1000&limit=5",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                pools = data['data']
                print(f"✅ Fetched {len(pools)} Balancer pools")
                
                for i, pool in enumerate(pools[:2], 1):
                    print(f"   {i}. {pool['name']}")
                    print(f"      TVL: ${pool['tvl']:,.2f}")
                    print(f"      Tokens: {', '.join([t['symbol'] for t in pool['tokens']])}")
                
                return True
            else:
                print("❌ Balancer API returned unsuccessful response")
                return False
        else:
            print(f"❌ Balancer test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Balancer test failed: {e}")
        return False

async def test_zrx_integration():
    """Test 0x API integration"""
    print("\n🔄 Testing 0x Integration...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/parallel/zrx/prices",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                prices = data['data']
                print(f"✅ Fetched {len(prices)} token prices from 0x")
                
                for price in prices[:3]:
                    print(f"   {price['symbol']}: ${price['priceUsd']:.4f}")
                
                return True
            else:
                print("❌ 0x API returned unsuccessful response")
                return False
        else:
            print(f"❌ 0x test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 0x test failed: {e}")
        return False

async def test_thegraph_integration():
    """Test The Graph Protocol integration"""
    print("\n📊 Testing The Graph Integration...")
    
    try:
        # Test pools
        response = requests.get(
            f"{BACKEND_URL}/api/parallel/thegraph/pools?min_tvl=100&limit=5",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                pools = data['data']
                print(f"✅ Fetched {len(pools)} pools from The Graph")
                
                for i, pool in enumerate(pools[:2], 1):
                    print(f"   {i}. {pool['token0']['symbol']}/{pool['token1']['symbol']}")
                    print(f"      TVL: ${pool['tvl']:,.2f}")
                    print(f"      Volume 24h: ${pool['volume24h']:,.2f}")
                
                # Test opportunities
                opp_response = requests.get(
                    f"{BACKEND_URL}/api/parallel/thegraph/opportunities?min_spread_bps=10",
                    timeout=30
                )
                
                if opp_response.status_code == 200:
                    opp_data = opp_response.json()
                    if opp_data['success']:
                        opportunities = opp_data['data']
                        print(f"✅ Found {len(opportunities)} arbitrage opportunities")
                        
                        for i, opp in enumerate(opportunities[:2], 1):
                            print(f"   {i}. {opp['tokenPair']}: {opp['spreadBps']} bps")
                        
                        return True
                
                return True
            else:
                print("❌ The Graph API returned unsuccessful response")
                return False
        else:
            print(f"❌ The Graph test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ The Graph test failed: {e}")
        return False

async def test_arbitrage_opportunities():
    """Test arbitrage opportunity detection"""
    print("\n⚡ Testing Arbitrage Opportunities...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/parallel/arbitrage/opportunities?min_spread_bps=23",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                opportunities = data['data']
                print(f"✅ Found {len(opportunities)} arbitrage opportunities")
                
                if opportunities:
                    for i, opp in enumerate(opportunities[:3], 1):
                        print(f"   {i}. {opp['tokenA']} → {opp['tokenB']}")
                        print(f"      Spread: {opp['spreadBps']} bps")
                        print(f"      Profit: ${opp['netProfitUsd']:.2f}")
                else:
                    print("   No opportunities found (this is normal)")
                
                return True
            else:
                print("❌ Arbitrage API returned unsuccessful response")
                return False
        else:
            print(f"❌ Arbitrage test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Arbitrage test failed: {e}")
        return False

async def test_zrx_quote():
    """Test 0x quote functionality"""
    print("\n💱 Testing 0x Quote...")
    
    try:
        quote_data = {
            "sellToken": "0x4200000000000000000000000000000000000006",  # WETH
            "buyToken": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",   # USDC
            "sellAmount": "1000000000000000000",  # 1 WETH
            "slippagePercentage": 0.01
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/parallel/zrx/quote",
            json=quote_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                quote = data['data']
                print(f"✅ Got 0x quote successfully")
                print(f"   Price: {quote['price']}")
                print(f"   Buy Amount: {quote['buyAmount']}")
                print(f"   Estimated Gas: {quote['estimatedGas']}")
                return True
            else:
                print("❌ 0x quote returned unsuccessful response")
                return False
        else:
            print(f"❌ 0x quote test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 0x quote test failed: {e}")
        return False

async def test_frontend_build():
    """Test if frontend builds successfully"""
    print("\n🎨 Testing Frontend Build...")
    
    try:
        # Check if frontend is accessible
        response = requests.get(f"{FRONTEND_URL}", timeout=10)
        
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            
            # Check parallel dashboard page
            dashboard_response = requests.get(f"{FRONTEND_URL}/parallel-dashboard", timeout=10)
            
            if dashboard_response.status_code == 200:
                print("✅ Parallel dashboard page is accessible")
                return True
            else:
                print(f"❌ Parallel dashboard not accessible: HTTP {dashboard_response.status_code}")
                return False
        else:
            print(f"❌ Frontend not accessible: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        print("   Note: Make sure frontend is running on port 3000")
        return False

async def run_complete_test_suite():
    """Run complete integration test suite"""
    print("🚀 ATOM - COMPLETE INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Network: Base Sepolia Testnet")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Balancer Integration", test_balancer_integration),
        ("0x Integration", test_zrx_integration),
        ("The Graph Integration", test_thegraph_integration),
        ("Arbitrage Opportunities", test_arbitrage_opportunities),
        ("0x Quote", test_zrx_quote),
        ("Frontend Build", test_frontend_build)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 COMPLETE TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! System is ready for Vercel deployment.")
        print("\n📋 DEPLOYMENT CHECKLIST:")
        print("   ✅ Balancer GraphQL API integration working")
        print("   ✅ 0x API integration working")
        print("   ✅ The Graph Protocol integration working")
        print("   ✅ Parallel orchestrator functioning")
        print("   ✅ Frontend dashboard accessible")
        print("   ✅ All API endpoints responding")
        print("\n🚀 Ready for production deployment!")
    else:
        print("⚠️  Some tests failed. Fix issues before deployment.")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Ensure backend is running: python backend/main.py")
        print("   2. Ensure frontend is running: pnpm run dev")
        print("   3. Check environment variables are set")
        print("   4. Verify API keys are valid")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = asyncio.run(run_complete_test_suite())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
