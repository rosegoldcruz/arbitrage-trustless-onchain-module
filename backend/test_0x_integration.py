#!/usr/bin/env python3
"""
🧪 Test script for 0x.org API integration
Tests the THEATOM_API_KEY and various endpoints
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from routers.zeroex import make_0x_request, get_headers
import httpx

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

THEATOM_API_KEY = os.getenv("THEATOM_API_KEY")
ZRX_API_URL = os.getenv("ZRX_API_URL", "https://api.0x.org")

async def test_api_key():
    """Test if the API key is valid"""
    print("🔑 Testing API Key...")
    
    if not THEATOM_API_KEY:
        print("❌ THEATOM_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {THEATOM_API_KEY[:8]}...")
    
    try:
        headers = get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ZRX_API_URL}/swap/v1/sources",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                print("✅ API Key is valid and working!")
                return True
            else:
                print(f"❌ API Key validation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

async def test_supported_tokens():
    """Test fetching supported tokens"""
    print("\n🪙 Testing Supported Tokens...")
    
    try:
        url = f"{ZRX_API_URL}/swap/v1/tokens"
        params = {"chainId": 1}  # Ethereum mainnet
        
        data = await make_0x_request(url, params)
        
        if data and "records" in data:
            tokens = data["records"][:5]  # First 5 tokens
            print(f"✅ Found {len(data['records'])} supported tokens")
            print("Sample tokens:")
            for token in tokens:
                print(f"  - {token['symbol']}: {token['name']} ({token['address'][:10]}...)")
            return True
        else:
            print("❌ No tokens found in response")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching tokens: {e}")
        return False

async def test_liquidity_sources():
    """Test fetching liquidity sources"""
    print("\n💧 Testing Liquidity Sources...")
    
    try:
        url = f"{ZRX_API_URL}/swap/v1/sources"
        params = {"chainId": 1}
        
        data = await make_0x_request(url, params)
        
        if data and "sources" in data:
            sources = data["sources"]
            print(f"✅ Found {len(sources)} liquidity sources")
            print("Available sources:")
            for source in sources[:10]:  # First 10 sources
                print(f"  - {source}")
            return True
        else:
            print("❌ No sources found in response")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching sources: {e}")
        return False

async def test_price_quote():
    """Test getting a price quote"""
    print("\n💰 Testing Price Quote...")
    
    try:
        url = f"{ZRX_API_URL}/swap/v1/price"
        params = {
            "sellToken": "ETH",
            "buyToken": "USDC",
            "sellAmount": "1000000000000000000"  # 1 ETH in wei
        }
        
        data = await make_0x_request(url, params)
        
        if data and "price" in data:
            price = float(data["price"])
            estimated_gas = data.get("estimatedGas", "N/A")
            
            print(f"✅ Price quote successful!")
            print(f"  - 1 ETH = {price:.2f} USDC")
            print(f"  - Estimated gas: {estimated_gas}")
            print(f"  - Sell amount: {data.get('sellAmount', 'N/A')}")
            print(f"  - Buy amount: {data.get('buyAmount', 'N/A')}")
            return True
        else:
            print("❌ No price data in response")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return False

async def test_swap_quote():
    """Test getting a full swap quote"""
    print("\n🔄 Testing Swap Quote...")
    
    try:
        url = f"{ZRX_API_URL}/swap/v1/quote"
        params = {
            "sellToken": "ETH",
            "buyToken": "USDC",
            "sellAmount": "1000000000000000000",  # 1 ETH in wei
            "slippagePercentage": "0.01",  # 1%
            "skipValidation": "true"
        }
        
        data = await make_0x_request(url, params)
        
        if data and "price" in data:
            price = float(data["price"])
            guaranteed_price = float(data.get("guaranteedPrice", data["price"]))
            gas_estimate = data.get("gas", "N/A")
            protocol_fee = data.get("protocolFee", "0")
            
            print(f"✅ Swap quote successful!")
            print(f"  - Price: {price:.6f}")
            print(f"  - Guaranteed price: {guaranteed_price:.6f}")
            print(f"  - Gas estimate: {gas_estimate}")
            print(f"  - Protocol fee: {protocol_fee} wei")
            print(f"  - Allowance target: {data.get('allowanceTarget', 'N/A')[:10]}...")
            
            # Show liquidity sources
            sources = data.get("sources", [])
            if sources:
                print(f"  - Liquidity sources ({len(sources)}):")
                for source in sources[:3]:  # First 3 sources
                    proportion = float(source.get("proportion", 0)) * 100
                    print(f"    * {source.get('name', 'Unknown')}: {proportion:.1f}%")
            
            return True
        else:
            print("❌ No quote data in response")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching swap quote: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting 0x.org API Integration Tests")
    print("=" * 50)
    
    tests = [
        ("API Key Validation", test_api_key),
        ("Supported Tokens", test_supported_tokens),
        ("Liquidity Sources", test_liquidity_sources),
        ("Price Quote", test_price_quote),
        ("Swap Quote", test_swap_quote),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! 0x.org integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API key and network connectivity.")
    
    return passed == total

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🚀 Ready to integrate 0x.org into ATOM platform!")
    else:
        print("\n🔧 Please fix the issues above before proceeding.")
    
    sys.exit(0 if success else 1)
