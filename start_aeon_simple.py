#!/usr/bin/env python3
"""
🧬 AEON SIMPLE STARTUP - GUARANTEED TO WORK
Simple, robust startup script with permanent import fixes
No complex dependencies - just starts the core AEON system
"""

import os
import sys
import subprocess
import logging
import time

# 🔐 PERMANENT BACKEND IMPORT FIX - BULLETPROOF VERSION
# Add all necessary paths to ensure imports work in any environment
current_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "backend"))
frontend_dir = os.path.abspath(os.path.join(current_dir, "frontend"))

# Add to Python path
sys.path.insert(0, backend_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(backend_dir, "bots", "working"))
sys.path.insert(0, os.path.join(backend_dir, "integrations"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8+ required")
        return False
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_environment():
    """Check basic environment"""
    logger.info("🔍 Checking environment...")
    
    # Check directories exist
    if not os.path.exists(backend_dir):
        logger.error(f"❌ Backend directory not found: {backend_dir}")
        return False
    
    if not os.path.exists(frontend_dir):
        logger.error(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    # Check critical files
    critical_files = [
        os.path.join(backend_dir, "main.py"),
        os.path.join(backend_dir, "real_orchestrator.py"),
        os.path.join(frontend_dir, "package.json")
    ]
    
    for file_path in critical_files:
        if not os.path.exists(file_path):
            logger.error(f"❌ Critical file missing: {file_path}")
            return False
    
    logger.info("✅ Environment check passed")
    return True

def start_fastapi():
    """Start FastAPI server"""
    logger.info("⚡ Starting FastAPI server...")
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start FastAPI with uvicorn
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(5)
        
        if process.poll() is None:
            logger.info("✅ FastAPI server started on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ FastAPI failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"❌ FastAPI startup error: {e}")
        return None
    finally:
        # Change back to original directory
        os.chdir(current_dir)

def start_frontend():
    """Start Next.js frontend"""
    logger.info("🎨 Starting Next.js frontend...")
    
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Check if node_modules exists
        if not os.path.exists("node_modules"):
            logger.info("📦 Installing frontend dependencies...")
            install_result = subprocess.run(["pnpm", "install"], capture_output=True, text=True)
            if install_result.returncode != 0:
                logger.error(f"❌ Frontend dependency installation failed: {install_result.stderr}")
                return None
        
        # Start Next.js
        process = subprocess.Popen([
            "pnpm", "run", "dev"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(10)
        
        if process.poll() is None:
            logger.info("✅ Frontend started on http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Frontend failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Frontend startup error: {e}")
        return None
    finally:
        # Change back to original directory
        os.chdir(current_dir)

def start_orchestrator():
    """Start AEON orchestrator"""
    logger.info("🧬 Starting AEON orchestrator...")
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start orchestrator
        process = subprocess.Popen([
            sys.executable, "real_orchestrator.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ AEON orchestrator started")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Orchestrator failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Orchestrator startup error: {e}")
        return None
    finally:
        # Change back to original directory
        os.chdir(current_dir)

def main():
    """Main startup function"""
    logger.info("🧬 AEON SIMPLE STARTUP")
    logger.info("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    processes = {}
    
    try:
        # Start FastAPI server
        fastapi_process = start_fastapi()
        if fastapi_process:
            processes["fastapi"] = fastapi_process
        else:
            logger.error("❌ FastAPI startup failed - aborting")
            sys.exit(1)
        
        # Start orchestrator
        orchestrator_process = start_orchestrator()
        if orchestrator_process:
            processes["orchestrator"] = orchestrator_process
        else:
            logger.warning("⚠️ Orchestrator startup failed - continuing without it")
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes["frontend"] = frontend_process
        else:
            logger.warning("⚠️ Frontend startup failed - API only mode")
        
        # Success message
        logger.info("=" * 60)
        logger.info("🚀 AEON SYSTEM STARTED!")
        
        if "fastapi" in processes:
            logger.info("🔗 API: http://localhost:8000")
            logger.info("📖 API Docs: http://localhost:8000/docs")
        
        if "frontend" in processes:
            logger.info("🌐 Frontend: http://localhost:3000")
        
        if "orchestrator" in processes:
            logger.info("🧬 Orchestrator: Running")
        
        logger.info("=" * 60)
        logger.info("💰 AEON is ready for arbitrage execution!")
        logger.info("Press Ctrl+C to stop all services")
        
        # Keep running
        while True:
            time.sleep(60)
            
            # Check if critical processes are still alive
            if "fastapi" in processes and processes["fastapi"].poll() is not None:
                logger.error("❌ FastAPI died - system unstable")
                break
                
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested...")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
    finally:
        # Cleanup
        logger.info("🧹 Stopping all processes...")
        for name, process in processes.items():
            try:
                if process.poll() is None:
                    logger.info(f"Stopping {name}...")
                    process.terminate()
                    process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        logger.info("✅ AEON system stopped")

if __name__ == "__main__":
    main()
