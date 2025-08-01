#!/usr/bin/env python3
"""
🌐 AEON PUBLIC API LAUNCHER
Starts FastAPI backend with public access for Vercel → DigitalOcean connection
Ensures 0.0.0.0 host binding for external access
"""

import os
import sys
import logging

# 🔐 PERMANENT BACKEND IMPORT FIX FOR PUBLIC DEPLOYMENT
current_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "backend"))

# Add ALL necessary paths for public deployment
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

def main():
    """Start FastAPI with public access"""
    logger.info("🌐 AEON PUBLIC API LAUNCHER")
    logger.info("=" * 60)
    logger.info("🔥 Starting FastAPI for PUBLIC ACCESS")
    logger.info("🌐 Vercel → DigitalOcean connection enabled")
    logger.info("=" * 60)

    try:
        # Change to backend directory
        os.chdir(backend_dir)

        # Import FastAPI app and uvicorn
        from main import app
        import uvicorn

        logger.info("✅ FastAPI app imported successfully")
        logger.info("🚀 Starting server on 0.0.0.0:8000...")
        logger.info("🔥 PUBLIC HOST BINDING - External access enabled")

        # Start FastAPI with public host binding
        # This is the key fix for Vercel → DigitalOcean connection
        uvicorn.run(
            app,
            host="0.0.0.0",  # 🔥 PUBLIC ACCESS - allows external connections
            port=8000,
            log_level="info",
            access_log=True,
            reload=False  # Disable reload for production
        )

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're in the correct directory and dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
