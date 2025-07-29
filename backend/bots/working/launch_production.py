#!/usr/bin/env python3
"""
PRODUCTION LAUNCHER FOR ATOM BOT ECOSYSTEM
Launches all connected bots with REAL DEX integrations
"""

import asyncio
import logging
import subprocess
import sys
import os
import time
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))
from config import validate_production_config, get_atom_config, get_adom_config, get_hybrid_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_bots.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PRODUCTION_LAUNCHER')

class ProductionLauncher:
    """Launches and manages production bot ecosystem"""
    
    def __init__(self):
        self.processes = {}
        self.is_running = False
        
    async def start_production_ecosystem(self):
        """Start the complete production bot ecosystem"""
        logger.info("🚀 STARTING PRODUCTION ATOM BOT ECOSYSTEM")
        logger.info("=" * 60)
        
        # Validate configuration
        if not validate_production_config():
            logger.error("❌ Configuration validation failed!")
            return False
        
        self.is_running = True
        
        try:
            # Start bots in sequence
            await self._start_atom_bot()
            await asyncio.sleep(2)
            
            await self._start_adom_bot()
            await asyncio.sleep(2)
            
            await self._start_hybrid_bot()
            await asyncio.sleep(2)
            
            # Start monitoring
            await self._monitor_ecosystem()
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            logger.error(f"❌ Production ecosystem error: {e}")
        finally:
            await self._shutdown_ecosystem()
    
    async def _start_atom_bot(self):
        """Start ATOM Python bot with REAL DEX integration"""
        logger.info("🔁 Starting ATOM Bot (Python + DEX Aggregator)")
        
        try:
            # Import and start ATOM bot
            from ATOM import ATOMBot, ATOMConfig
            
            config = get_atom_config()
            atom_config = ATOMConfig(
                rpc_url=config.rpc_url,
                wss_url=config.wss_url,
                chain_id=config.chain_id,
                private_key=config.private_key,
                contract_address=config.arbitrage_bot_address,
                min_spread_bps=config.min_spread_bps,
                max_gas_price=config.max_gas_price,
                min_profit_usd=config.min_profit_usd,
                max_trade_size=config.max_trade_size,
                scan_interval=config.scan_interval,
                execution_timeout=config.execution_timeout,
                retry_attempts=config.retry_attempts,
                theatom_api_key=config.theatom_api_key,
                alchemy_api_key=config.alchemy_api_key
            )
            
            atom_bot = ATOMBot(atom_config)
            
            # Start ATOM bot in background task
            self.processes['atom'] = asyncio.create_task(atom_bot.start())
            logger.info("✅ ATOM Bot started with REAL DEX connections")
            
        except Exception as e:
            logger.error(f"❌ Failed to start ATOM bot: {e}")
    
    async def _start_adom_bot(self):
        """Start ADOM Node.js bot with smart contract integration"""
        logger.info("🔄 Starting ADOM Bot (Node.js + Smart Contracts)")
        
        try:
            # Start ADOM bot as subprocess
            adom_config = get_adom_config()
            
            # Write config to temporary file for Node.js bot
            import json
            config_file = Path(__file__).parent / 'adom_config.json'
            with open(config_file, 'w') as f:
                json.dump(adom_config, f, indent=2)
            
            # Start ADOM process
            process = subprocess.Popen(
                ['node', 'ADOM.js', str(config_file)],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['adom'] = process
            logger.info("✅ ADOM Bot started with smart contract integration")
            
        except Exception as e:
            logger.error(f"❌ Failed to start ADOM bot: {e}")
    
    async def _start_hybrid_bot(self):
        """Start hybrid bot with full DEX aggregator integration"""
        logger.info("⚡ Starting Hybrid Bot (Off-chain + On-chain)")
        
        try:
            from atom_hybrid_bot import AtomHybridBot
            
            hybrid_bot = AtomHybridBot()
            
            # Start hybrid bot in background task
            self.processes['hybrid'] = asyncio.create_task(hybrid_bot.monitor_and_execute())
            logger.info("✅ Hybrid Bot started with full DEX aggregator")
            
        except Exception as e:
            logger.error(f"❌ Failed to start hybrid bot: {e}")
    
    async def _monitor_ecosystem(self):
        """Monitor the health of all bots"""
        logger.info("📊 Starting ecosystem monitoring...")
        
        while self.is_running:
            try:
                # Check bot health
                healthy_bots = 0
                total_bots = len(self.processes)
                
                for bot_name, process in self.processes.items():
                    if isinstance(process, asyncio.Task):
                        if not process.done():
                            healthy_bots += 1
                        elif process.exception():
                            logger.error(f"❌ {bot_name} bot crashed: {process.exception()}")
                    elif isinstance(process, subprocess.Popen):
                        if process.poll() is None:  # Still running
                            healthy_bots += 1
                        else:
                            logger.error(f"❌ {bot_name} bot process terminated")
                
                # Log ecosystem health
                if healthy_bots == total_bots:
                    logger.info(f"💚 Ecosystem healthy: {healthy_bots}/{total_bots} bots running")
                else:
                    logger.warning(f"⚠️  Ecosystem degraded: {healthy_bots}/{total_bots} bots running")
                
                # Wait before next health check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _shutdown_ecosystem(self):
        """Gracefully shutdown all bots"""
        logger.info("🛑 Shutting down production ecosystem...")
        
        self.is_running = False
        
        # Stop all processes
        for bot_name, process in self.processes.items():
            try:
                if isinstance(process, asyncio.Task):
                    process.cancel()
                    try:
                        await process
                    except asyncio.CancelledError:
                        pass
                elif isinstance(process, subprocess.Popen):
                    process.terminate()
                    process.wait(timeout=10)
                
                logger.info(f"✅ {bot_name} bot stopped")
                
            except Exception as e:
                logger.error(f"❌ Error stopping {bot_name} bot: {e}")
        
        logger.info("🏁 Production ecosystem shutdown complete")

async def main():
    """Main production launcher"""
    print("🤖 ATOM PRODUCTION BOT ECOSYSTEM")
    print("=" * 50)
    print("🔗 REAL DEX Integrations:")
    print("   ✅ 0x Protocol")
    print("   ✅ 1inch")
    print("   ✅ ParaSwap")
    print("   ✅ Balancer")
    print("   ✅ Curve")
    print("   ✅ Uniswap")
    print("=" * 50)
    
    launcher = ProductionLauncher()
    await launcher.start_production_ecosystem()

if __name__ == "__main__":
    asyncio.run(main())
