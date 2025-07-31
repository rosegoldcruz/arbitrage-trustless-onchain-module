#!/usr/bin/env python3
"""
🧬 AEON SYSTEM DEPLOYMENT - REAL MONEY EXECUTION
Deploy complete FLASHLOAN ARBITRAGE SYSTEM
ATOM.py + ADOM.js + atom_hybrid_bot.py + lite_scanner.js → AAVE V3 → PROFITS
"""

import os
import sys
import subprocess
import logging
import time
import json
from pathlib import Path

# 🔐 PERMANENT BACKEND IMPORT FIX
# Add current directory to Python path for backend imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'PRIVATE_KEY',
        'BASE_RPC_URL', 
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        logger.error("Please set these in your .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def deploy_smart_contracts():
    """Deploy AEON smart contracts to Base"""
    logger.info("🚀 Deploying AEON smart contracts...")
    
    try:
        # Check if contracts are already deployed
        if os.path.exists("deployments/base/BaseAtomArbitrage.json"):
            logger.info("✅ Smart contracts already deployed")
            return True
        
        # Deploy contracts using Hardhat
        result = subprocess.run([
            "npx", "hardhat", "run", "scripts/deploy-aeon-full-stack.sh", 
            "--network", "base-sepolia"
        ], capture_output=True, text=True, cwd="..")
        
        if result.returncode == 0:
            logger.info("✅ Smart contracts deployed successfully")
            return True
        else:
            logger.error(f"❌ Contract deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Contract deployment error: {e}")
        return False

def start_orchestrator():
    """Start the AEON orchestrator"""
    logger.info("🧬 Starting AEON Orchestrator...")
    
    try:
        # Start orchestrator in background
        process = subprocess.Popen([
            sys.executable, "real_orchestrator.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(3)
        
        # Check if it's still running
        if process.poll() is None:
            logger.info("✅ AEON Orchestrator started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Orchestrator failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start orchestrator: {e}")
        return None

def start_working_bots():
    """Start all 4 working bots"""
    logger.info("🤖 Starting working bots...")
    
    bot_processes = {}
    
    # Bot configurations
    bots = {
        "ATOM": {
            "script": "bots/working/ATOM.py",
            "interpreter": sys.executable
        },
        "ADOM": {
            "script": "bots/working/ADOM.js", 
            "interpreter": "node"
        },
        "AtomHybrid": {
            "script": "bots/working/atom_hybrid_bot.py",
            "interpreter": sys.executable
        },
        "LiteScanner": {
            "script": "bots/working/lite_scanner.js",
            "interpreter": "node"
        }
    }
    
    for bot_name, config in bots.items():
        try:
            logger.info(f"Starting {bot_name}...")
            
            process = subprocess.Popen([
                config["interpreter"], config["script"]
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(1)  # Give it time to start
            
            if process.poll() is None:
                bot_processes[bot_name] = process
                logger.info(f"✅ {bot_name} started successfully")
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {bot_name} failed to start: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"❌ Failed to start {bot_name}: {e}")
    
    return bot_processes

def test_telegram_integration():
    """Test Telegram notifications"""
    logger.info("📱 Testing Telegram integration...")
    
    try:
        # Add backend to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from integrations.telegram_notifier import telegram_notifier
        
        # Test connection
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(telegram_notifier.test_connection())
        loop.close()
        
        if success:
            logger.info("✅ Telegram integration working")
            return True
        else:
            logger.error("❌ Telegram integration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Telegram test error: {e}")
        return False

def main():
    """Deploy complete AEON system"""
    logger.info("🧬 AEON SYSTEM DEPLOYMENT STARTING...")
    logger.info("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Deploy smart contracts
    if not deploy_smart_contracts():
        logger.error("❌ Smart contract deployment failed - aborting")
        sys.exit(1)
    
    # Step 3: Test Telegram
    if not test_telegram_integration():
        logger.warning("⚠️ Telegram integration failed - continuing without notifications")
    
    # Step 4: Start orchestrator
    orchestrator_process = start_orchestrator()
    if not orchestrator_process:
        logger.error("❌ Orchestrator failed to start - aborting")
        sys.exit(1)
    
    # Step 5: Start working bots
    bot_processes = start_working_bots()
    
    if not bot_processes:
        logger.error("❌ No bots started successfully")
        orchestrator_process.terminate()
        sys.exit(1)
    
    # Success!
    logger.info("=" * 60)
    logger.info("🚀 AEON SYSTEM DEPLOYED SUCCESSFULLY!")
    logger.info(f"✅ Orchestrator running (PID: {orchestrator_process.pid})")
    logger.info(f"✅ {len(bot_processes)} bots running")
    
    for bot_name, process in bot_processes.items():
        logger.info(f"   • {bot_name} (PID: {process.pid})")
    
    logger.info("=" * 60)
    logger.info("🧬 AEON IS NOW HUNTING FOR FLASHLOAN ARBITRAGE OPPORTUNITIES")
    logger.info("💰 Real money, real profits, real execution")
    logger.info("⚡ AAVE V3 flashloans → Multi-DEX arbitrage → Profit extraction")
    logger.info("=" * 60)
    
    # Keep running
    try:
        while True:
            time.sleep(60)
            
            # Check if processes are still alive
            if orchestrator_process.poll() is not None:
                logger.error("❌ Orchestrator died - restarting system")
                break
                
            dead_bots = []
            for bot_name, process in bot_processes.items():
                if process.poll() is not None:
                    dead_bots.append(bot_name)
            
            if dead_bots:
                logger.warning(f"⚠️ Dead bots detected: {dead_bots}")
                
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down AEON system...")
        
        # Cleanup
        orchestrator_process.terminate()
        for process in bot_processes.values():
            process.terminate()
        
        logger.info("✅ AEON system shutdown complete")

if __name__ == "__main__":
    main()
