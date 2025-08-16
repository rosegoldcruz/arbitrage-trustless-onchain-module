#!/usr/bin/env python3
"""
Test script for /api/execute-trade endpoint
Tests all authentication methods and trade strategies
"""

import requests
import json
import hmac
import hashlib
import time
from datetime import datetime

# Configuration
API_BASE = "https://api.aeoninvestmentstechnologies.com"
# API_BASE = "http://localhost:8000"  # For local testing

def test_api_key_auth():
    """Test API key authentication"""
    print("🔑 Testing API Key Authentication...")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "atom_api_key_production"
    }
    
    payload = {
        "strategy": "atom",
        "token_pair": "WETH/USDC",
        "amount": 100.0,
        "mode": "auto",
        "slippage": 0.005,
        "min_profit_bps": 25,
        "webhook_id": "test_api_key_001"
    }
    
    response = requests.post(f"{API_BASE}/api/execute-trade", 
                           headers=headers, 
                           json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_signature_auth():
    """Test HMAC signature authentication"""
    print("\n🔐 Testing Signature Authentication...")
    
    webhook_secret = "atom_webhook_secret_2024"
    timestamp = str(int(time.time()))
    
    payload = {
        "strategy": "adom",
        "token_pair": "USDC/DAI",
        "amount": 250.0,
        "mode": "auto",
        "slippage": 0.003,
        "min_profit_bps": 30,
        "webhook_id": "test_signature_001"
    }
    
    body = json.dumps(payload)
    signature = hmac.new(
        webhook_secret.encode(),
        f"{timestamp}.{body}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
        "X-Timestamp": timestamp
    }
    
    response = requests.post(f"{API_BASE}/api/execute-trade", 
                           headers=headers, 
                           json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_triangular_strategy():
    """Test triangular arbitrage strategy"""
    print("\n🔺 Testing Triangular Strategy...")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "atom_api_key_production"
    }
    
    payload = {
        "strategy": "triangular",
        "token_pair": "DAI/GHO",
        "amount": 500.0,
        "mode": "auto",
        "slippage": 0.008,
        "min_profit_bps": 35,
        "webhook_id": "test_triangular_001"
    }
    
    response = requests.post(f"{API_BASE}/api/execute-trade", 
                           headers=headers, 
                           json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_invalid_auth():
    """Test invalid authentication"""
    print("\n❌ Testing Invalid Authentication...")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "invalid_key"
    }
    
    payload = {
        "strategy": "atom",
        "token_pair": "WETH/USDC",
        "amount": 100.0
    }
    
    response = requests.post(f"{API_BASE}/api/execute-trade", 
                           headers=headers, 
                           json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401

def test_invalid_strategy():
    """Test invalid strategy"""
    print("\n❌ Testing Invalid Strategy...")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "atom_api_key_production"
    }
    
    payload = {
        "strategy": "invalid_strategy",
        "token_pair": "WETH/USDC",
        "amount": 100.0
    }
    
    response = requests.post(f"{API_BASE}/api/execute-trade", 
                           headers=headers, 
                           json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

if __name__ == "__main__":
    print("🚀 Testing /api/execute-trade endpoint")
    print(f"API Base: {API_BASE}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    results = []
    results.append(("API Key Auth", test_api_key_auth()))
    results.append(("Signature Auth", test_signature_auth()))
    results.append(("Triangular Strategy", test_triangular_strategy()))
    results.append(("Invalid Auth", test_invalid_auth()))
    results.append(("Invalid Strategy", test_invalid_strategy()))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nOverall: {passed_count}/{len(results)} tests passed")
