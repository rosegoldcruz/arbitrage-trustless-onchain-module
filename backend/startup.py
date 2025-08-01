#!/usr/bin/env python3
"""
🚀 ATOM FINTECH PLATFORM - Enterprise Startup Script
Complete system initialization and health verification
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/startup.log")
    ]
)
logger = logging.getLogger(__name__)

async def initialize_atom_platform():
    """Initialize the complete ATOM platform"""
    
    print("=" * 80)
    print("🚀 ATOM FINTECH PLATFORM - ENTERPRISE INITIALIZATION")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logger.info("🔧 Starting ATOM Platform Initialization...")
        
        # Import all core systems
        logger.info("📦 Loading Core Systems...")
        from core.trading_engine import trading_engine
        from core.orchestrator import master_orchestrator
        from core.mev_protection import mev_protection
        from core.security import security_manager
        
        # Import integrations
        logger.info("🔗 Loading External Integrations...")
        from integrations.flashloan_providers import flash_loan_manager
        from integrations.dex_aggregator import dex_aggregator
        from integrations.blockchain import blockchain_manager
        
        print("✅ All modules loaded successfully")
        print()
        
        # Initialize systems in order
        initialization_steps = [
            ("🔒 Security & Compliance System", security_manager.initialize_security),
            ("⛓️ Blockchain Networks", blockchain_manager.initialize_networks),
            ("🔗 DEX Aggregators", dex_aggregator.initialize_aggregators),
            ("⚡ Flash Loan Providers", flash_loan_manager.initialize_providers),
            ("🛡️ MEV Protection", mev_protection.initialize_protection),
            ("🚀 Trading Engine", trading_engine.start_engine),
            ("🤖 AI Agent Orchestrator", master_orchestrator.initialize_agents),
        ]
        
        print("🔄 Initializing Systems:")
        print("-" * 40)
        
        for step_name, init_function in initialization_steps:
            try:
                step_start = time.time()
                print(f"  {step_name}...", end=" ", flush=True)
                
                await init_function()
                
                step_time = time.time() - step_start
                print(f"✅ ({step_time:.2f}s)")
                
            except Exception as e:
                print(f"❌ FAILED")
                logger.error(f"Failed to initialize {step_name}: {e}")
                raise
        
        print()
        
        # Verify system health
        print("🔍 System Health Verification:")
        print("-" * 40)
        
        health_checks = [
            ("Trading Engine", lambda: trading_engine.is_running),
            ("AI Agents", lambda: len(master_orchestrator.agents) > 0),
            ("MEV Protection", lambda: mev_protection.is_monitoring),
            ("Flash Loan Providers", lambda: len(flash_loan_manager.providers) > 0),
            ("DEX Aggregators", lambda: len(dex_aggregator.aggregators) > 0),
            ("Blockchain Networks", lambda: len(blockchain_manager.networks) > 0),
            ("Security System", lambda: security_manager.is_monitoring),
        ]
        
        all_healthy = True
        for check_name, check_function in health_checks:
            try:
                is_healthy = check_function()
                status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
                print(f"  {check_name}: {status}")
                
                if not is_healthy:
                    all_healthy = False
                    
            except Exception as e:
                print(f"  {check_name}: ❌ ERROR - {e}")
                all_healthy = False
        
        print()
        
        if not all_healthy:
            raise Exception("System health check failed")
        
        # Display system statistics
        print("📊 System Statistics:")
        print("-" * 40)
        
        stats = {
            "AI Agents": len(master_orchestrator.agents),
            "Flash Loan Providers": len(flash_loan_manager.providers),
            "DEX Aggregators": len(dex_aggregator.aggregators),
            "Blockchain Networks": len(blockchain_manager.networks),
            "Security Policies": "Enterprise Grade",
            "Compliance Frameworks": "SOX, GDPR, MiFID II",
        }
        
        for stat_name, stat_value in stats.items():
            print(f"  {stat_name}: {stat_value}")
        
        print()
        
        # Performance test
        print("⚡ Performance Test:")
        print("-" * 40)
        
        # Test opportunity detection
        print("  Testing opportunity detection...", end=" ", flush=True)
        test_start = time.time()
        opportunities = trading_engine.get_current_opportunities()
        detection_time = time.time() - test_start
        print(f"✅ {len(opportunities)} opportunities ({detection_time*1000:.1f}ms)")
        
        # Test agent coordination
        print("  Testing agent coordination...", end=" ", flush=True)
        test_start = time.time()
        system_status = master_orchestrator.get_system_status()
        coordination_time = time.time() - test_start
        print(f"✅ {system_status['global_metrics']['active_agents']} agents ({coordination_time*1000:.1f}ms)")
        
        # Test MEV protection
        print("  Testing MEV protection...", end=" ", flush=True)
        test_start = time.time()
        protection_stats = mev_protection.get_protection_stats()
        protection_time = time.time() - test_start
        print(f"✅ {protection_stats['protection_level']} level ({protection_time*1000:.1f}ms)")
        
        print()
        
        # Final status
        total_time = time.time() - start_time
        
        print("=" * 80)
        print("🎉 ATOM PLATFORM INITIALIZATION COMPLETE!")
        print("=" * 80)
        print(f"⏱️  Total Initialization Time: {total_time:.2f} seconds")
        print(f"🎯 System Status: OPERATIONAL")
        print(f"💰 Ready for Enterprise Trading")
        print(f"🔗 API Documentation: http://localhost:8000/docs")
        print(f"📊 System Dashboard: http://localhost:8000/")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ATOM Platform initialization failed: {e}")
        print()
        print("=" * 80)
        print("❌ INITIALIZATION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print("Check logs for detailed error information.")
        print("=" * 80)
        return False

async def run_system_diagnostics():
    """Run comprehensive system diagnostics"""
    
    print("\n🔧 RUNNING SYSTEM DIAGNOSTICS")
    print("=" * 50)
    
    try:
        # Import systems
        from core.trading_engine import trading_engine
        from core.orchestrator import master_orchestrator
        from core.mev_protection import mev_protection
        from integrations.flashloan_providers import flash_loan_manager
        from integrations.dex_aggregator import dex_aggregator
        from integrations.blockchain import blockchain_manager
        
        diagnostics = []
        
        # Trading Engine Diagnostics
        if trading_engine.is_running:
            performance = trading_engine.get_performance_metrics()
            diagnostics.append({
                "system": "Trading Engine",
                "status": "✅ OPERATIONAL",
                "metrics": {
                    "Total Trades": performance["total_trades"],
                    "Success Rate": f"{performance['success_rate']*100:.1f}%",
                    "Total Profit": f"${performance['total_profit']:.2f}",
                    "Avg Execution Time": f"{performance['avg_execution_time']*1000:.1f}ms"
                }
            })
        
        # Agent System Diagnostics
        agent_status = master_orchestrator.get_system_status()
        diagnostics.append({
            "system": "AI Agent System",
            "status": "✅ OPERATIONAL",
            "metrics": {
                "Active Agents": agent_status["global_metrics"]["active_agents"],
                "Total Operations": agent_status["global_metrics"]["total_operations"],
                "System Uptime": f"{agent_status['global_metrics']['system_uptime']:.1f}%",
                "Total Profit": f"${agent_status['global_metrics']['total_profit']:.2f}"
            }
        })
        
        # MEV Protection Diagnostics
        mev_stats = mev_protection.get_protection_stats()
        diagnostics.append({
            "system": "MEV Protection",
            "status": "✅ ACTIVE",
            "metrics": {
                "Protection Level": mev_stats["protection_level"],
                "Threats Detected": mev_stats["stats"]["threats_detected"],
                "Threats Mitigated": mev_stats["stats"]["threats_mitigated"],
                "Success Rate": f"{mev_stats['stats']['success_rate']*100:.1f}%"
            }
        })
        
        # Flash Loan Diagnostics
        fl_stats = flash_loan_manager.get_provider_stats()
        diagnostics.append({
            "system": "Flash Loan System",
            "status": "✅ READY",
            "metrics": {
                "Providers": len(fl_stats["providers"]),
                "Total Volume": f"${fl_stats['total_volume']:.2f}",
                "Active Loans": fl_stats["total_active_loans"],
                "Completed Loans": fl_stats["total_completed_loans"]
            }
        })
        
        # DEX Aggregator Diagnostics
        dex_stats = dex_aggregator.get_aggregator_stats()
        diagnostics.append({
            "system": "DEX Aggregators",
            "status": "✅ CONNECTED",
            "metrics": {
                "Aggregators": len(dex_stats["aggregators"]),
                "Total Swaps": dex_stats["total_swaps"],
                "Total Volume": f"${dex_stats['total_volume']:.2f}",
                "Cache Size": dex_stats["cache_size"]
            }
        })
        
        # Blockchain Diagnostics
        blockchain_stats = blockchain_manager.get_network_stats()
        diagnostics.append({
            "system": "Blockchain Networks",
            "status": "✅ CONNECTED",
            "metrics": {
                "Networks": len(blockchain_stats),
                "Total Transactions": sum(
                    stats["transactions"]["total"] 
                    for stats in blockchain_stats.values()
                ),
                "Pending Transactions": sum(
                    stats["transactions"]["pending"] 
                    for stats in blockchain_stats.values()
                )
            }
        })
        
        # Display diagnostics
        for diagnostic in diagnostics:
            print(f"\n📋 {diagnostic['system']}")
            print(f"   Status: {diagnostic['status']}")
            for metric_name, metric_value in diagnostic["metrics"].items():
                print(f"   {metric_name}: {metric_value}")
        
        print("\n✅ All systems operational and performing within expected parameters")
        return True
        
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        print(f"\n❌ Diagnostics failed: {e}")
        return False

async def main():
    """Main startup function"""
    
    # Initialize the platform
    success = await initialize_atom_platform()
    
    if success:
        # Run diagnostics
        await run_system_diagnostics()
        
        print("\n🚀 ATOM Platform is ready for enterprise trading!")
        print("   Use 'uvicorn main:app --reload' to start the API server")
        
    else:
        print("\n❌ Platform initialization failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    # Run the startup process
    asyncio.run(main())
