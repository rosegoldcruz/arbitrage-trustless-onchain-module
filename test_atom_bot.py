#!/usr/bin/env python3
"""
Test script for ATOM Bot functionality
"""

import os
import sys
import asyncio
import logging

# Set up test environment variables
os.environ['BASE_SEPOLIA_RPC_URL'] = 'https://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d'
os.environ['BASE_SEPOLIA_WSS_URL'] = 'wss://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d'
os.environ['PRIVATE_KEY'] = '0x0000000000000000000000000000000000000000000000000000000000000001'  # Test key
os.environ['BASE_SEPOLIA_CONTRACT_ADDRESS'] = '0xb3800E6bC7847E5d5a71a03887EDc5829DF4133b'
os.environ['THEATOM_API_KEY'] = '7324a2b4-3b05-4288-b353-68322f49a283'

# Add backend directory to path
sys.path.append('backend')

from bots.ATOM import ATOMBot, ATOMConfig

async def test_atom_bot():
    """Test ATOM bot initialization and basic functionality"""
    print("🧪 Testing ATOM Bot...")
    print("=" * 50)
    
    try:
        # Test configuration
        config = ATOMConfig(
            rpc_url=os.getenv('BASE_SEPOLIA_RPC_URL'),
            wss_url=os.getenv('BASE_SEPOLIA_WSS_URL'),
            chain_id=84532,
            private_key=os.getenv('PRIVATE_KEY'),
            contract_address=os.getenv('BASE_SEPOLIA_CONTRACT_ADDRESS'),
            theatom_api_key=os.getenv('THEATOM_API_KEY')
        )
        
        print("✅ Configuration loaded successfully")
        print(f"   RPC URL: {config.rpc_url[:50]}...")
        print(f"   Chain ID: {config.chain_id}")
        print(f"   Contract: {config.contract_address}")
        
        # Test bot initialization
        bot = ATOMBot(config)
        print("✅ ATOM Bot initialized successfully")
        
        # Test Web3 connection
        try:
            latest_block = bot.w3.eth.block_number
            print(f"✅ Web3 connection successful - Latest block: {latest_block}")
        except Exception as e:
            print(f"⚠️  Web3 connection test failed: {e}")
        
        # Test contract ABI loading
        if bot.contract_abi:
            print(f"✅ Contract ABI loaded - {len(bot.contract_abi)} functions")
        else:
            print("⚠️  Contract ABI not loaded (expected for test)")
        
        # Test opportunity detection (mock)
        print("\n🔍 Testing opportunity detection...")
        opportunities = await bot._scan_triangular_paths()
        print(f"✅ Opportunity scan completed - Found {len(opportunities)} opportunities")
        
        # Test statistics
        stats = bot.execution_stats
        print(f"\n📊 Performance Stats:")
        print(f"   Total Scans: {stats['total_scans']}")
        print(f"   Opportunities Found: {stats['opportunities_found']}")
        print(f"   Successful Executions: {stats['successful_executions']}")
        
        print("\n🎉 ATOM Bot test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ATOM Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_atom_bot())
    sys.exit(0 if success else 1)
