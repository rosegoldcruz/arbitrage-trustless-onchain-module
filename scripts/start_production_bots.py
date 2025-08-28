#!/usr/bin/env python3
"""
🚀 ATOM Production Bot Startup Script
Starts all production bots with robust RPC management and monitoring
"""

import os
import sys
import time
import logging
import threading
import signal
from typing import List
import subprocess

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend-bots'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionBotManager:
    """
    Production bot manager with health monitoring and automatic restarts
    """
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True
        self.health_check_interval = 30  # seconds
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.shutdown()
    
    def validate_environment(self) -> bool:
        """Validate required environment variables"""
        logger.info("⚙️ Validating environment configuration...")
        
        required_vars = [
            'POLYGON_RPC_URL',
            'POLYGON_RPC_BACKUP', 
            'POLYGON_RPC_BACKUP2',
            'CHAINLINK_ETH_USD',
            'CHAINLINK_MATIC_USD',
            'CHAINLINK_USDC_USD',
            'CHAINLINK_DAI_USD',
            'CHAINLINK_USDT_USD',
            'PRIVATE_KEY',
            'ATOM_CONTRACT_ADDRESS',
            'REDIS_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        logger.info("✅ All required environment variables configured")
        return True
    
    def test_infrastructure(self) -> bool:
        """Test infrastructure components"""
        logger.info("🧪 Testing infrastructure components...")
        
        try:
            # Test RPC manager
            from backend_bots.rpc_manager import RPCManager
            
            rpc_manager = RPCManager()
            w3 = getattr(rpc_manager, "web3", None) or rpc_manager.get_web3()
            
            # Test connectivity
            chain_id = w3.eth.chain_id
            if chain_id != 137:
                logger.error(f"❌ Wrong network: {chain_id} (expected 137)")
                return False
            
            logger.info(f"✅ Connected to Polygon mainnet (Chain {chain_id})")
            
            # Test price feeds
            from price_utils import get_price_feed
            
            price_feed = get_price_feed()
            health = price_feed.health_check()
            healthy_feeds = sum(health.values())
            total_feeds = len(health)
            
            if healthy_feeds == 0:
                logger.error("❌ No healthy price feeds")
                return False
            
            logger.info(f"✅ Price feeds: {healthy_feeds}/{total_feeds} healthy")
            
            # Test Redis
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            logger.info("✅ Redis connection successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Infrastructure test failed: {e}")
            return False
    
    def start_bot(self, script_path: str, name: str) -> subprocess.Popen:
        """Start a bot process"""
        logger.info(f"🚀 Starting {name}...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(process)
            logger.info(f"✅ Started {name} (PID: {process.pid})")
            
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            raise
    
    def start_all_bots(self):
        """Start all production bots"""
        logger.info("🚀 Starting all production bots...")
        
        bot_configs = [
            {
                'script': '../bots/production_opportunity_detector.py',
                'name': 'Opportunity Detector'
            },
            {
                'script': '../bots/production_trade_executor.py', 
                'name': 'Trade Executor'
            },
            {
                'script': '../backend-bots/prometheus_metrics.py',
                'name': 'Metrics Server'
            }
        ]
        
        for config in bot_configs:
            script_path = os.path.join(os.path.dirname(__file__), config['script'])
            if os.path.exists(script_path):
                try:
                    self.start_bot(script_path, config['name'])
                except Exception as e:
                    logger.error(f"❌ Failed to start {config['name']}: {e}")
            else:
                logger.warning(f"⚠️ Script not found: {script_path}")
        
        logger.info(f"🎉 Started {len(self.processes)} bot processes")
    
    def monitor_processes(self):
        """Monitor bot processes and restart if needed"""
        logger.info("🏥 Starting process health monitor...")
        
        while self.running:
            try:
                for i, process in enumerate(self.processes[:]):  # Copy list to avoid modification during iteration
                    if process.poll() is not None:  # Process has terminated
                        logger.warning(f"⚠️ Process {process.pid} has terminated (exit code: {process.returncode})")
                        
                        # Remove from list
                        self.processes.remove(process)
                        
                        # TODO: Implement restart logic here if needed
                        logger.info("🔄 Process restart logic not implemented yet")
                
                # Log current status
                active_processes = len([p for p in self.processes if p.poll() is None])
                logger.info(f"📊 Active processes: {active_processes}/{len(self.processes)}")
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(5)
    
    def shutdown(self):
        """Graceful shutdown of all processes"""
        logger.info("🛑 Shutting down all processes...")
        
        self.running = False
        
        for process in self.processes:
            if process.poll() is None:  # Still running
                logger.info(f"🛑 Terminating process {process.pid}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ Process {process.pid} terminated gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Force killing process {process.pid}...")
                    process.kill()
                    process.wait()
        
        logger.info("✅ All processes shut down")
    
    def run(self):
        """Main run loop"""
        logger.info("🚀 ATOM Production Bot Manager Starting...")
        logger.info("=" * 60)
        
        # Validate environment
        if not self.validate_environment():
            logger.error("❌ Environment validation failed")
            return False
        
        # Test infrastructure
        if not self.test_infrastructure():
            logger.error("❌ Infrastructure test failed")
            return False
        
        # Start bots
        self.start_all_bots()
        
        if not self.processes:
            logger.error("❌ No processes started")
            return False
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        logger.info("🎉 ATOM Production System is running!")
        logger.info("   Press Ctrl+C to shutdown gracefully")
        logger.info("=" * 60)
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        
        self.shutdown()
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATOM Production Bot Manager')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate environment and infrastructure')
    parser.add_argument('--test-only', action='store_true',
                       help='Only run infrastructure tests')
    
    args = parser.parse_args()
    
    manager = ProductionBotManager()
    
    if args.validate_only:
        success = manager.validate_environment()
        exit(0 if success else 1)
    elif args.test_only:
        success = manager.validate_environment() and manager.test_infrastructure()
        exit(0 if success else 1)
    else:
        success = manager.run()
        exit(0 if success else 1)

if __name__ == '__main__':
    main()
