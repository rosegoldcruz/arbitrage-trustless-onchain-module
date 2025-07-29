#!/usr/bin/env python3
"""
Startup script for the Real Orchestrator
Handles environment setup and graceful startup/shutdown
"""

import os
import sys
import signal
import logging
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from real_orchestrator import RealOrchestrator

def setup_environment():
    """Setup environment and check prerequisites"""
    print("🔧 Setting up environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Check required files exist
    required_files = [
        "orchestrator_config.json",
        "bots/ATOM.py",
        "bots/ADOM.js"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file missing: {file_path}")
            sys.exit(1)
    
    # Create required directories
    directories = [
        "comm/commands",
        "comm/results", 
        "comm/heartbeats",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Check Node.js for ADOM bot
    try:
        import subprocess
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js not found - required for ADOM bot")
            sys.exit(1)
        print(f"✅ Node.js version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found - required for ADOM bot")
        sys.exit(1)
    
    # Check required Python packages
    required_packages = ["requests", "psutil"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        sys.exit(1)
    
    print("✅ Environment setup complete")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    if 'orchestrator' in globals():
        orchestrator.stop()
    sys.exit(0)

def main():
    """Main startup function"""
    print("🚀 Starting Real Arbitrage Orchestrator")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/startup.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Create and start orchestrator
        global orchestrator
        orchestrator = RealOrchestrator("orchestrator_config.json")
        
        print("✅ Orchestrator initialized")
        print("📊 Starting bot coordination...")
        print("🔍 Monitoring DEX APIs for opportunities...")
        print("⚡ Real-time arbitrage execution active")
        print("\nPress Ctrl+C to stop\n")
        
        # Start orchestrator (blocking)
        orchestrator.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.exception("Fatal error in orchestrator")
        sys.exit(1)
    finally:
        if 'orchestrator' in globals():
            orchestrator.stop()
        print("👋 Orchestrator shutdown complete")

if __name__ == "__main__":
    main()
