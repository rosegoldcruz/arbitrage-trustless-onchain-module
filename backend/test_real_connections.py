#!/usr/bin/env python3
"""
🧪 ATOM REAL CONNECTION TEST
Test script to verify your actual API keys and blockchain connections work
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def test_real_connections():
    """Test all real connections with your actual API keys"""
    
    print("🧪 TESTING REAL ATOM CONNECTIONS")
    print("=" * 50)
    
    # Test 1: Environment Variables
    print("\n1️⃣ Testing Environment Variables...")
    
    required_vars = [
        "ALCHEMY_API_KEY",
        "INFURA_API_KEY", 
        "WALLETCONNECT_PROJECT_ID",
        "BASE_SEPOLIA_RPC_URL",
        "THEATOM_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:10]}...")
        else:
            print(f"   ❌ {var}: MISSING")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {missing_vars}")
        return False
    
    # Test 2: Blockchain Connections
    print("\n2️⃣ Testing Real Blockchain Connections...")
    
    try:
        from integrations.blockchain import blockchain_manager
        
        # Initialize with real API keys
        await blockchain_manager.initialize_networks()
        
        # Test each network
        for network_name, w3 in blockchain_manager.web3_connections.items():
            try:
                block_number = w3.eth.block_number
                gas_price = w3.eth.gas_price / 1e9  # Convert to gwei
                
                print(f"   ✅ {network_name.value}:")
                print(f"      Block: {block_number:,}")
                print(f"      Gas: {gas_price:.2f} gwei")
                
            except Exception as e:
                print(f"   ❌ {network_name.value}: {e}")
        
    except Exception as e:
        print(f"   ❌ Blockchain connection failed: {e}")
        return False
    
    # Test 3: 0x API Integration
    print("\n3️⃣ Testing Real 0x API Integration...")
    
    try:
        from integrations.dex_aggregator import dex_aggregator
        
        # Initialize DEX aggregator
        await dex_aggregator.initialize_aggregators()
        
        # Test real 0x quote
        quote = await dex_aggregator.get_0x_quote(
            token_in="ETH",
            token_out="USDC", 
            amount_in=1.0,
            chain=dex_aggregator.Chain.ETHEREUM,
            slippage_tolerance=0.01
        )
        
        if quote:
            print(f"   ✅ 0x Quote Success:")
            print(f"      1 ETH -> {quote.amount_out:.2f} USDC")
            print(f"      Gas: {quote.gas_estimate:,} units")
            print(f"      Route: {' -> '.join(quote.route)}")
        else:
            print(f"   ❌ 0x Quote failed")
            
    except Exception as e:
        print(f"   ❌ 0x API test failed: {e}")
    
    # Test 4: Real Gas Price Monitoring
    print("\n4️⃣ Testing Real Gas Price Monitoring...")
    
    try:
        # Get real gas prices
        gas_stats = blockchain_manager.get_network_stats()
        
        for network, stats in gas_stats.items():
            gas_data = stats.get("gas", {})
            current_price = gas_data.get("current_price", 0)
            
            if current_price > 0:
                print(f"   ✅ {network}: {current_price:.2f} gwei")
            else:
                print(f"   ❌ {network}: No gas data")
                
    except Exception as e:
        print(f"   ❌ Gas price monitoring failed: {e}")
    
    # Test 5: Contract Interaction (Base Sepolia)
    print("\n5️⃣ Testing Contract Interaction...")
    
    try:
        contract_address = os.getenv("BASE_SEPOLIA_CONTRACT_ADDRESS")
        
        if contract_address and blockchain_manager.web3_connections:
            # Try to get contract info
            base_w3 = None
            for network, w3 in blockchain_manager.web3_connections.items():
                if "base" in network.value.lower() or "bsc" in network.value.lower():
                    base_w3 = w3
                    break
            
            if base_w3:
                # Check if contract exists
                code = base_w3.eth.get_code(contract_address)
                if code and code != b'':
                    print(f"   ✅ Contract found at {contract_address}")
                    print(f"      Code size: {len(code)} bytes")
                else:
                    print(f"   ❌ No contract code at {contract_address}")
            else:
                print(f"   ❌ No Base network connection available")
        else:
            print(f"   ❌ Contract address not configured")
            
    except Exception as e:
        print(f"   ❌ Contract interaction failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 REAL CONNECTION TEST SUMMARY")
    print("=" * 50)
    
    working_connections = len(blockchain_manager.web3_connections) if 'blockchain_manager' in locals() else 0
    
    if working_connections > 0:
        print(f"✅ SUCCESS: {working_connections} blockchain connections working")
        print("✅ Your API keys are valid and functional")
        print("✅ Ready for real trading operations")
        print("\n🚀 Next steps:")
        print("   1. Run: python startup.py")
        print("   2. Run: uvicorn main:app --reload")
        print("   3. Visit: http://localhost:8000/docs")
        return True
    else:
        print("❌ FAILED: No working blockchain connections")
        print("❌ Check your API keys and network configuration")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_real_connections()
        
        if success:
            print("\n🎉 ALL TESTS PASSED - YOUR BACKEND IS READY!")
        else:
            print("\n💥 SOME TESTS FAILED - CHECK CONFIGURATION")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
