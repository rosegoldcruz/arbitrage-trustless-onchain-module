#!/usr/bin/env python3
"""
ATOM Production Quick Start - SECURE
Single command to start generating profits
SECURE: Environment Variables Only - NO HARDCODED SECRETS
"""

import asyncio
import logging
import os
import sys
import time
from web3 import Web3
import redis

# Add config directory to path
sys.path.append('config')
sys.path.append('bots')

from secure_config import config
from production_orchestrator import ProductionOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate environment configuration - SECURE: Environment Variables Only"""
    try:
        # Validate secure configuration
        if not config.validate_production_ready():
            logger.error("System not production ready")
            return False

        # Test Web3 connection
        polygon_rpc = config.get('polygon_rpc_url')
        if not polygon_rpc:
            logger.error("POLYGON_RPC_URL environment variable required")
            return False

        w3 = Web3(Web3.HTTPProvider(polygon_rpc))
        if not w3.is_connected():
            # Try backup RPC
            backup_rpc = config.get('polygon_rpc_backup')
            if backup_rpc:
                w3 = Web3(Web3.HTTPProvider(backup_rpc))
                if not w3.is_connected():
                    logger.error("Failed to connect to Polygon RPC (primary and backup)")
                    return False
            else:
                logger.error("Failed to connect to Polygon RPC")
                return False

        # Validate Polygon mainnet
        chain_id = w3.eth.chain_id
        if chain_id != 137:
            logger.error(f"Connected to wrong network. Expected Polygon (137), got {chain_id}")
            return False

        logger.info(f"✅ Connected to Polygon mainnet, block: {w3.eth.block_number}")

        # Test Redis connection
        redis_url = config.get('redis_url')
        if not redis_url:
            logger.error("REDIS_URL environment variable required")
            return False

        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        logger.info("✅ Redis connection successful")

        # Validate contract address
        contract_addr = config.get('flashloan_contract')
        if not contract_addr:
            logger.error("FLASHLOAN_ARB_ADDR environment variable required")
            return False

        if not w3.is_address(contract_addr):
            logger.error(f"Invalid contract address: {contract_addr}")
            return False

        # Check contract has code
        code = w3.eth.get_code(contract_addr)
        if len(code) == 0:
            logger.error(f"No code found at contract address: {contract_addr}")
            return False

        logger.info(f"✅ Contract validated at: {contract_addr}")
        return True

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False

def display_startup_info():
    """Display startup information"""
    print("\n" + "="*60)
    print("🚀 ATOM PRODUCTION ARBITRAGE SYSTEM")
    print("="*60)
    print(f"📅 Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Network: Polygon Mainnet")
    print(f"📍 Contract: {os.getenv('FLASHLOAN_ARB_ADDR')}")
    print(f"💼 Wallet: {os.getenv('TESTNET_WALLET_ADDRESS', 'Not specified')}")
    print(f"🎯 Min Profit: {os.getenv('ATOM_MIN_PROFIT_THRESHOLD', '23')} bps")
    print(f"⛽ Max Gas: {os.getenv('ATOM_MAX_GAS_PRICE', '100')} gwei")
    print("="*60)
    print("💰 TARGET PROFITS:")
    print("   Day 1-2:  $10-50   (validation)")
    print("   Week 1:   $100-500 (optimization)")
    print("   Month 1:  $500-2000+ (scaling)")
    print("="*60)
    print("📊 MONITORING:")
    print("   • Watch console for trade alerts")
    print("   • Check Discord/Telegram for notifications")
    print("   • Monitor Redis: redis-cli get production_stats")
    print("="*60)
    print("⚠️  IMPORTANT:")
    print("   • System will run continuously")
    print("   • Press Ctrl+C to stop safely")
    print("   • First profitable trade validates system")
    print("   • All configuration loaded from environment variables")
    print("   • NO HARDCODED SECRETS in source code")
    print("="*60)
    print()

async def main():
    """Main entry point"""
    print("🔍 Validating environment...")

    # Run comprehensive environment validation
    try:
        from config.env_validation import EnvironmentValidator
        validator = EnvironmentValidator()
        if not validator.validate_all():
            validator.print_results()
            print("\n❌ Environment validation failed!")
            print("Fix the above issues before starting the system")
            sys.exit(1)
        validator.print_results()
    except ImportError:
        # Fallback to basic validation
        if not validate_environment():
            print("❌ Environment validation failed!")
            print("\nPlease ensure:")
            print("1. .env file exists and is properly configured")
            print("2. PRIVATE_KEY is set with your wallet private key")
            print("3. POLYGON_RPC_URL is set to a valid Polygon RPC")
            print("4. ATOM_CONTRACT_ADDRESS is set to your deployed contract")
            print("5. CHAIN_ID=137 and NETWORK=polygon_mainnet")
            print("6. Redis is running (redis-server)")
            sys.exit(1)

    print("✅ Environment validation passed!")
    
    display_startup_info()
    
    # Initialize orchestrator
    orchestrator = ProductionOrchestrator()
    
    try:
        print("🚀 Starting ATOM Production System...")
        print("   Initializing opportunity detection...")
        print("   Initializing trade execution...")
        print("   Initializing MEV protection...")
        print("   Initializing profit monitoring...")
        print()
        print("💡 System is now LIVE and scanning for profits!")
        print("   First trade may take 1-5 minutes to appear")
        print("   Watch for '💰 OPPORTUNITY' and '✅ Arbitrage successful' messages")
        print()
        
        # Start the production system
        await orchestrator.start_production_system()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
        print("💾 Saving final statistics...")
        
        # Display final stats
        try:
            stats = orchestrator.get_system_stats()
            print("\n📊 FINAL STATISTICS:")
            print(f"   Uptime: {stats['system']['uptime_hours']:.2f} hours")
            print(f"   Opportunities: {stats['opportunities']['total_detected']}")
            print(f"   Trades: {stats['trading']['total_trades']}")
            print(f"   Success Rate: {stats['trading']['success_rate']:.1f}%")
            print(f"   Total Profit: ${stats['trading']['total_profit_usd']:.2f}")
            print(f"   Profit/Hour: ${stats['performance']['profit_per_hour']:.2f}")
        except:
            print("   (Statistics unavailable)")
            
        print("\n✅ System stopped safely")
        
    except Exception as e:
        print(f"\n❌ System error: {e}")
        logger.error(f"System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
        
    # Run the system
    asyncio.run(main())
