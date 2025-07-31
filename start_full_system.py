#!/usr/bin/env python3
"""
🧬 AEON FULL SYSTEM STARTUP
Start both FRONTEND and BACKEND for complete AEON system
Ready for partner demo and real money execution
"""

import os
import sys
import subprocess
import logging
import time
import signal
from pathlib import Path

# 🔐 PERMANENT BACKEND IMPORT FIX
# Add backend directory to Python path to resolve imports like 'from backend.routers import ...'
# This makes the script self-contained and immune to PYTHONPATH issues across all environments
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AEONSystemManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("🛑 Shutdown signal received - stopping AEON system...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Node.js: {result.stdout.strip()}")
            else:
                logger.error("❌ Node.js not found")
                return False
        except FileNotFoundError:
            logger.error("❌ Node.js not installed")
            return False
        
        # Check Python
        logger.info(f"✅ Python: {sys.version.split()[0]}")
        
        # Check pnpm
        try:
            result = subprocess.run(["pnpm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ pnpm: {result.stdout.strip()}")
            else:
                logger.error("❌ pnpm not found - install with: npm install -g pnpm")
                return False
        except FileNotFoundError:
            logger.error("❌ pnpm not installed - install with: npm install -g pnpm")
            return False
        
        # Check environment files
        if not os.path.exists(".env.local"):
            logger.error("❌ .env.local not found - copy from .env.example and configure")
            return False
        
        logger.info("✅ All prerequisites met")
        return True
    
    def install_dependencies(self):
        """Install all dependencies"""
        logger.info("📦 Installing dependencies...")
        
        # Install root dependencies
        logger.info("Installing root dependencies...")
        result = subprocess.run(["pnpm", "install"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"❌ Root dependency installation failed: {result.stderr}")
            return False
        
        # Install frontend dependencies
        logger.info("Installing frontend dependencies...")
        result = subprocess.run(["pnpm", "install"], cwd="frontend", capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"❌ Frontend dependency installation failed: {result.stderr}")
            return False
        
        # Install backend dependencies
        logger.info("Installing backend dependencies...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              cwd="backend", capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"❌ Backend dependency installation failed: {result.stderr}")
            return False
        
        logger.info("✅ All dependencies installed")
        return True
    
    def start_backend(self):
        """Start AEON backend system"""
        logger.info("🧬 Starting AEON Backend System...")
        
        try:
            # Start the AEON deployment script
            process = subprocess.Popen([
                sys.executable, "deploy_aeon_system.py"
            ], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes["backend"] = process
            
            # Give it time to start
            time.sleep(5)
            
            if process.poll() is None:
                logger.info("✅ AEON Backend started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Backend failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start Next.js frontend"""
        logger.info("🎨 Starting Frontend (Next.js)...")
        
        try:
            # Start Next.js dev server
            process = subprocess.Popen([
                "pnpm", "run", "dev"
            ], cwd="frontend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes["frontend"] = process
            
            # Give it time to start
            time.sleep(10)
            
            if process.poll() is None:
                logger.info("✅ Frontend started successfully")
                logger.info("🌐 Frontend available at: http://localhost:3000")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ Frontend failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False
    
    def start_fastapi_server(self):
        """Start FastAPI server"""
        logger.info("⚡ Starting FastAPI Server...")
        
        try:
            # Start FastAPI server
            process = subprocess.Popen([
                sys.executable, "main.py"
            ], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes["fastapi"] = process
            
            # Give it time to start
            time.sleep(3)
            
            if process.poll() is None:
                logger.info("✅ FastAPI server started successfully")
                logger.info("🔗 API available at: http://localhost:8000")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ FastAPI server failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start FastAPI server: {e}")
            return False
    
    def monitor_system(self):
        """Monitor all system components"""
        logger.info("👁️ Monitoring AEON system...")
        
        while self.running:
            try:
                # Check all processes
                dead_processes = []
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        dead_processes.append(name)
                
                if dead_processes:
                    logger.error(f"❌ Dead processes detected: {dead_processes}")
                    # Could implement restart logic here
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    running_count = len([p for p in self.processes.values() if p.poll() is None])
                    logger.info(f"📊 System Status: {running_count}/{len(self.processes)} processes running")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(10)
    
    def cleanup(self):
        """Cleanup all processes"""
        logger.info("🧹 Cleaning up processes...")
        
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    logger.info(f"Stopping {name}...")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ {name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ Force killing {name}...")
                        process.kill()
                        process.wait()
                        
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
        
        logger.info("✅ Cleanup complete")
    
    def run(self):
        """Run the complete AEON system"""
        logger.info("🧬 AEON FULL SYSTEM STARTUP")
        logger.info("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites not met - aborting")
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            logger.error("❌ Dependency installation failed - aborting")
            return False
        
        # Start FastAPI server first
        if not self.start_fastapi_server():
            logger.error("❌ FastAPI server failed - aborting")
            return False
        
        # Start backend system
        if not self.start_backend():
            logger.error("❌ Backend system failed - aborting")
            return False
        
        # Start frontend
        if not self.start_frontend():
            logger.error("❌ Frontend failed - aborting")
            return False
        
        # Success!
        logger.info("=" * 60)
        logger.info("🚀 AEON FULL SYSTEM RUNNING!")
        logger.info("🌐 Frontend: http://localhost:3000")
        logger.info("🔗 API: http://localhost:8000")
        logger.info("🧬 Backend: AEON Flashloan Arbitrage System")
        logger.info("💰 Ready for real money execution")
        logger.info("=" * 60)
        
        # Monitor system
        self.monitor_system()
        
        return True

def main():
    """Main entry point"""
    manager = AEONSystemManager()
    success = manager.run()
    
    if not success:
        logger.error("❌ AEON system startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
