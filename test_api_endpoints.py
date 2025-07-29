#!/usr/bin/env python3
"""
Test script for FastAPI backend endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            try:
                result = response.json()
                if isinstance(result, dict) and len(result) > 0:
                    print(f"   Response keys: {list(result.keys())}")
                elif isinstance(result, list):
                    print(f"   Response: List with {len(result)} items")
                else:
                    print(f"   Response: {str(result)[:100]}...")
            except:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint} - Connection error: {e}")
        return False

def test_all_endpoints():
    """Test all available API endpoints"""
    print("🧪 Testing FastAPI Backend Endpoints...")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    test_results = []
    
    # Health check endpoints
    print("\n🏥 Health Check Endpoints:")
    test_results.append(test_endpoint("GET", "/"))
    test_results.append(test_endpoint("GET", "/health"))
    test_results.append(test_endpoint("GET", "/health/detailed"))
    
    # Agent endpoints
    print("\n🤖 Agent Endpoints:")
    test_results.append(test_endpoint("GET", "/agent/status"))
    test_results.append(test_endpoint("POST", "/agent/deploy", {"strategy": "test"}))
    
    # Arbitrage endpoints
    print("\n⚡ Arbitrage Endpoints:")
    test_results.append(test_endpoint("POST", "/arbitrage/trigger", {
        "token_triple": ["DAI", "USDC", "GHO"],
        "amount": 1000,
        "min_profit_bps": 23
    }))
    test_results.append(test_endpoint("GET", "/arbitrage/opportunities"))
    test_results.append(test_endpoint("GET", "/arbitrage/history"))
    
    # Flash loan endpoints
    print("\n💰 Flash Loan Endpoints:")
    test_results.append(test_endpoint("POST", "/flash-loan/execute", {
        "token": "DAI",
        "amount": 1000,
        "strategy": "triangular"
    }))
    test_results.append(test_endpoint("GET", "/flash-loan/status"))
    
    # Analytics endpoints
    print("\n📊 Analytics Endpoints:")
    test_results.append(test_endpoint("GET", "/analytics/performance"))
    test_results.append(test_endpoint("GET", "/analytics/profit"))
    test_results.append(test_endpoint("GET", "/analytics/gas"))
    
    # Token endpoints
    print("\n🪙 Token Endpoints:")
    test_results.append(test_endpoint("GET", "/tokens/prices"))
    test_results.append(test_endpoint("GET", "/tokens/balances"))
    
    # Stats endpoints
    print("\n📈 Stats Endpoints:")
    test_results.append(test_endpoint("GET", "/stats/summary"))
    test_results.append(test_endpoint("GET", "/stats/bots"))
    
    # 0x integration endpoints
    print("\n🔄 0x Integration Endpoints:")
    test_results.append(test_endpoint("GET", "/0x/quote", expected_status=422))  # Missing params
    test_results.append(test_endpoint("GET", "/0x/price"))
    
    # Risk endpoints
    print("\n⚠️  Risk Endpoints:")
    test_results.append(test_endpoint("GET", "/risk/assessment"))
    test_results.append(test_endpoint("GET", "/risk/limits"))
    
    # Contact endpoints
    print("\n📞 Contact Endpoints:")
    test_results.append(test_endpoint("POST", "/contact/submit", {
        "name": "Test User",
        "email": "test@example.com",
        "message": "Test message"
    }))
    
    # Calculate results
    passed = sum(test_results)
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 API endpoints test PASSED!")
        return True
    else:
        print("❌ API endpoints test FAILED!")
        return False

if __name__ == "__main__":
    success = test_all_endpoints()
    exit(0 if success else 1)
