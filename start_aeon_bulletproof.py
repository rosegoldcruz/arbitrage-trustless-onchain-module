#!/usr/bin/env python3
"""
🧬 AEON BULLETPROOF STARTUP - GUARANTEED DIGITALOCEAN COMPATIBILITY
Permanent fix for all import issues - works on any server, any environment
NO PYTHONPATH REQUIRED - SELF-CONTAINED IMPORT RESOLUTION
"""

import os
import sys
import subprocess
import logging
import time

# 🔐 BULLETPROOF IMPORT FIX - WORKS ON ANY DIGITALOCEAN DROPLET
current_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "backend"))

# Add ALL necessary paths to ensure imports work in ANY environment
paths_to_add = [
    backend_dir,
    current_dir,
    os.path.join(backend_dir, "core"),
    os.path.join(backend_dir, "integrations"),
    os.path.join(backend_dir, "routers"),
    os.path.join(backend_dir, "bots", "working"),
    os.path.join(backend_dir, "bots"),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if we're in the right environment"""
    logger.info("🔍 Checking AEON environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required")
        return False
    
    # Check critical directories
    if not os.path.exists(backend_dir):
        logger.error(f"❌ Backend directory not found: {backend_dir}")
        return False
    
    # Check critical files
    critical_files = [
        os.path.join(backend_dir, "main.py"),
        os.path.join(backend_dir, "real_orchestrator.py"),
    ]
    
    for file_path in critical_files:
        if not os.path.exists(file_path):
            logger.error(f"❌ Critical file missing: {file_path}")
            return False
    
    logger.info("✅ Environment check passed")
    return True

def install_backend_dependencies():
    """Install backend Python dependencies"""
    logger.info("📦 Installing backend dependencies...")
    
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    if not os.path.exists(requirements_file):
        logger.warning("⚠️ requirements.txt not found - skipping dependency installation")
        return True
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], capture_output=True, text=True, cwd=backend_dir)
        
        if result.returncode == 0:
            logger.info("✅ Backend dependencies installed")
            return True
        else:
            logger.error(f"❌ Dependency installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Dependency installation error: {e}")
        return False

def start_fastapi_server():
    """Start FastAPI server with bulletproof imports"""
    logger.info("⚡ Starting FastAPI server...")
    
    try:
        # Set environment variables for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = ':'.join(paths_to_add)
        
        # Start FastAPI server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], cwd=backend_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(8)
        
        if process.poll() is None:
            logger.info("✅ FastAPI server started on http://0.0.0.0:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ FastAPI failed to start:")
            logger.error(f"STDOUT: {stdout.decode()}")
            logger.error(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"❌ FastAPI startup error: {e}")
        return None

def start_orchestrator():
    """Start AEON orchestrator"""
    logger.info("🧬 Starting AEON orchestrator...")
    
    try:
        # Set environment variables for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = ':'.join(paths_to_add)
        
        # Start orchestrator
        process = subprocess.Popen([
            sys.executable, "real_orchestrator.py"
        ], cwd=backend_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(5)
        
        if process.poll() is None:
            logger.info("✅ AEON orchestrator started")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ Orchestrator failed to start:")
            logger.error(f"STDOUT: {stdout.decode()}")
            logger.error(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Orchestrator startup error: {e}")
        return None

def test_imports():
    """Test critical imports"""
    logger.info("🧪 Testing critical imports...")
    
    try:
        # Test FastAPI import
        from fastapi import FastAPI
        logger.info("✅ FastAPI import: SUCCESS")
    except ImportError as e:
        logger.error(f"❌ FastAPI import: FAILED - {e}")
        return False
    
    try:
        # Test uvicorn import
        import uvicorn
        logger.info("✅ Uvicorn import: SUCCESS")
    except ImportError as e:
        logger.error(f"❌ Uvicorn import: FAILED - {e}")
        return False
    
    # Test backend imports (if available)
    try:
        sys.path.insert(0, backend_dir)
        from routers import health
        logger.info("✅ Backend router imports: SUCCESS")
    except ImportError as e:
        logger.warning(f"⚠️ Backend router imports: {e}")
    
    return True

def main():
    """Main startup function"""
    logger.info("🧬 AEON BULLETPROOF STARTUP")
    logger.info("=" * 60)
    logger.info(f"Current directory: {current_dir}")
    logger.info(f"Backend directory: {backend_dir}")
    logger.info(f"Python version: {sys.version}")
    logger.info("=" * 60)
    
    # Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        logger.error("❌ Import test failed")
        sys.exit(1)
    
    # Install dependencies
    if not install_backend_dependencies():
        logger.warning("⚠️ Dependency installation failed - continuing anyway")
    
    processes = {}
    
    try:
        # Start FastAPI server
        fastapi_process = start_fastapi_server()
        if fastapi_process:
            processes["fastapi"] = fastapi_process
        else:
            logger.error("❌ FastAPI startup failed")
            sys.exit(1)
        
        # Start orchestrator
        orchestrator_process = start_orchestrator()
        if orchestrator_process:
            processes["orchestrator"] = orchestrator_process
        else:
            logger.warning("⚠️ Orchestrator startup failed - API only mode")
        
        # Success message
        logger.info("=" * 60)
        logger.info("🚀 AEON BACKEND SYSTEM STARTED!")
        logger.info("🔗 API Server: http://0.0.0.0:8000")
        logger.info("📖 API Docs: http://0.0.0.0:8000/docs")
        
        if "orchestrator" in processes:
            logger.info("🧬 Orchestrator: Running")
        
        logger.info("=" * 60)
        logger.info("💰 AEON is ready for arbitrage execution!")
        logger.info("🌐 Access from any IP on port 8000")
        logger.info("Press Ctrl+C to stop all services")
        logger.info("=" * 60)
        
        # Keep running and monitor
        while True:
            time.sleep(30)
            
            # Check if FastAPI is still alive
            if "fastapi" in processes and processes["fastapi"].poll() is not None:
                logger.error("❌ FastAPI died - system critical failure")
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
                    logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
        
        logger.info("✅ AEON system stopped")

if __name__ == "__main__":
    main()
