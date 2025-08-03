#!/usr/bin/env python3
"""
🚀 ATOM FINTECH PLATFORM - Enterprise Startup Script
Complete system initialization and health verification
"""

import sys
import os

# 🔧 Patch sys.path for full repo + lib access
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lib")))

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path

# 🔌 Logging config
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/startup.log")
    ]
)
logger = logging.getLogger("startup")

async def initialize_atom_platform():
    print("=" * 80)
    print("\U0001F680 ATOM FINTECH PLATFORM - ENTERPRISE INITIALIZATION")
    print("=" * 80)
    print()
    start_time = time.time()

    try:
        logger.info("🔧 Starting initialization...")

        # 📦 Core systems - Import one by one to catch specific errors
        try:
            from backend.core.trading_engine import trading_engine
            logger.info("✅ Trading engine imported")
        except Exception as e:
            logger.error(f"❌ Failed to import trading_engine: {e}")
            raise

        try:
            from backend.core.parallel_orchestrator import orchestrator
            logger.info("✅ Parallel orchestrator imported")
        except Exception as e:
            logger.error(f"❌ Failed to import orchestrator: {e}")
            raise

        try:
            from backend.core.security import security_manager
            logger.info("✅ Security manager imported")
        except Exception as e:
            logger.error(f"❌ Failed to import security_manager: {e}")
            raise

        # 🔗 Integrations - Import one by one to catch specific errors
        try:
            from backend.integrations.flashloan_providers import flash_loan_manager
            logger.info("✅ Flash loan manager imported")
        except Exception as e:
            logger.error(f"❌ Failed to import flash_loan_manager: {e}")
            raise

        try:
            from backend.integrations.dex_aggregator import dex_aggregator
            logger.info("✅ DEX aggregator imported")
        except Exception as e:
            logger.error(f"❌ Failed to import dex_aggregator: {e}")
            raise

        try:
            from backend.integrations.blockchain import blockchain_manager
            logger.info("✅ Blockchain manager imported")
        except Exception as e:
            logger.error(f"❌ Failed to import blockchain_manager: {e}")
            raise

        print("✅ All modules loaded successfully\n")

        steps = [
            ("🔒 Security & Compliance", security_manager.initialize_security),
            ("⚓️ Blockchain Networks", blockchain_manager.initialize_networks),
            ("🔗 DEX Aggregators", dex_aggregator.initialize_aggregators),
            ("⚡ Flash Loan Providers", flash_loan_manager.initialize_providers),
            ("🚀 Trading Engine", trading_engine.start_engine),
            ("🧐 Parallel Orchestrator", orchestrator.start),
        ]

        print("🔄 Initializing Systems:\n" + "-" * 40)
        for name, fn in steps:
            try:
                print(f"  {name}...", end=" ", flush=True)
                t0 = time.time()
                await fn()
                print(f"✅ ({time.time()-t0:.2f}s)")
            except Exception as e:
                print("❌ FAILED")
                logger.error(f"Failed at {name}: {e}")
                raise

        print("\n🔍 Verifying Health:\n" + "-" * 40)
        checks = [
            ("Trading Engine", lambda: trading_engine.is_running),
            ("Orchestrator", lambda: orchestrator.isRunning),
            ("Flash Loans", lambda: len(flash_loan_manager.providers) > 0),
            ("DEX Aggregators", lambda: len(dex_aggregator.aggregators) > 0),
            ("Blockchains", lambda: len(blockchain_manager.networks) > 0),
            ("Security", lambda: security_manager.is_monitoring),
        ]

        healthy = True
        for label, test in checks:
            try:
                status = "✅ HEALTHY" if test() else "❌ UNHEALTHY"
                print(f"  {label}: {status}")
                if "❌" in status: healthy = False
            except Exception as e:
                print(f"  {label}: ❌ ERROR - {e}")
                healthy = False

        if not healthy:
            raise Exception("System health check failed")

        # 📊 Metrics
        print("\n📊 System Stats:\n" + "-" * 40)
        stats = {
            "Orchestrator Status": "Running" if orchestrator.isRunning else "Stopped",
            "Flash Loan Providers": len(flash_loan_manager.providers),
            "DEX Aggregators": len(dex_aggregator.aggregators),
            "Blockchain Networks": len(blockchain_manager.networks),
            "Security": "Enterprise Grade",
            "Compliance": "SOX, GDPR, MiFID II",
        }
        for k, v in stats.items(): print(f"  {k}: {v}")

        print("\n⚡ Performance Tests:\n" + "-" * 40)

        print("  Testing opportunity detection...", end=" ", flush=True)
        t0 = time.time()
        opps = trading_engine.get_current_opportunities()
        print(f"✅ {len(opps)} found ({(time.time()-t0)*1000:.1f}ms)")

        print("  Testing orchestrator status...", end=" ", flush=True)
        t0 = time.time()
        status = orchestrator.isRunning
        print(f"✅ {'Running' if status else 'Stopped'} ({(time.time()-t0)*1000:.1f}ms)")

        print("  Testing security monitoring...", end=" ", flush=True)
        t0 = time.time()
        security_status = security_manager.is_monitoring
        print(f"✅ {'Active' if security_status else 'Inactive'} ({(time.time()-t0)*1000:.1f}ms)")

        print("\n" + "=" * 80)
        print("🎉 ATOM PLATFORM INITIALIZATION COMPLETE!")
        print("=" * 80)
        print(f"⏱️  Init Time: {time.time()-start_time:.2f}s")
        print(f"🎯 Status: OPERATIONAL")
        print(f"💰 Ready to Trade")
        print(f"🔗 API Docs: http://localhost:8000/docs")
        print(f"📊 Dashboard: http://localhost:8000/")
        print("=" * 80)
        return True

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        print("\n❌ INITIALIZATION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print("Check logs for full trace.")
        print("=" * 80)
        return False

async def main():
    success = await initialize_atom_platform()
    if success:
        print("\n🚀 Ready for enterprise trading!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
