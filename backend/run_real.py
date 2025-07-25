#!/usr/bin/env python3
"""
🚀 ATOM REAL SYSTEM RUNNER
Run the ATOM backend with REAL blockchain connections and API integrations
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def run_real_atom_system():
    """Run the ATOM system with real connections"""
    
    print("🚀 STARTING REAL ATOM FINTECH PLATFORM")
    print("=" * 60)
    
    try:
        # Verify environment
        required_vars = ["ALCHEMY_API_KEY", "BASE_SEPOLIA_RPC_URL", "THEATOM_API_KEY"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            print(f"❌ Missing environment variables: {missing}")
            print("Please check your .env file")
            return False
        
        print("✅ Environment variables loaded")
        
        # Import and initialize real systems
        print("\n🔧 Initializing Real Systems...")
        
        # 1. Blockchain connections
        print("  📡 Connecting to blockchains...")
        from integrations.blockchain import blockchain_manager
        await blockchain_manager.initialize_networks()
        
        connected_networks = len(blockchain_manager.web3_connections)
        print(f"  ✅ Connected to {connected_networks} blockchain networks")
        
        # 2. DEX aggregators
        print("  🔄 Initializing DEX aggregators...")
        from integrations.dex_aggregator import dex_aggregator
        await dex_aggregator.initialize_aggregators()
        print(f"  ✅ Initialized {len(dex_aggregator.aggregators)} DEX aggregators")
        
        # 3. Flash loan providers
        print("  ⚡ Setting up flash loan providers...")
        from integrations.flashloan_providers import flash_loan_manager
        await flash_loan_manager.initialize_providers()
        print(f"  ✅ Connected to {len(flash_loan_manager.providers)} flash loan providers")
        
        # 4. Trading engine
        print("  🎯 Starting trading engine...")
        from core.trading_engine import trading_engine
        await trading_engine.start_engine()
        print("  ✅ Trading engine operational")
        
        # 5. AI agents
        print("  🤖 Initializing AI agents...")
        from core.orchestrator import master_orchestrator
        await master_orchestrator.initialize_agents()
        print(f"  ✅ {len(master_orchestrator.agents)} AI agents online")
        
        # 6. MEV protection
        print("  🛡️ Activating MEV protection...")
        from core.mev_protection import mev_protection
        await mev_protection.initialize_protection()
        print("  ✅ MEV protection active")
        
        print("\n" + "=" * 60)
        print("🎉 ATOM PLATFORM FULLY OPERATIONAL!")
        print("=" * 60)
        
        # Display system status
        print("\n📊 REAL-TIME SYSTEM STATUS:")
        print("-" * 40)
        
        # Blockchain status
        for network, w3 in blockchain_manager.web3_connections.items():
            try:
                block = w3.eth.block_number
                gas = w3.eth.gas_price / 1e9
                print(f"  🔗 {network.value}: Block {block:,}, Gas {gas:.1f} gwei")
            except:
                print(f"  ❌ {network.value}: Connection error")
        
        # Trading status
        opportunities = trading_engine.get_current_opportunities()
        performance = trading_engine.get_performance_metrics()
        print(f"  💰 Opportunities: {len(opportunities)}")
        print(f"  📈 Success Rate: {performance['success_rate']*100:.1f}%")
        print(f"  💵 Total Profit: ${performance['total_profit']:.2f}")
        
        # Agent status
        agent_status = master_orchestrator.get_system_status()
        print(f"  🤖 Active Agents: {agent_status['global_metrics']['active_agents']}")
        print(f"  ⚡ Total Operations: {agent_status['global_metrics']['total_operations']}")
        
        print("\n🌐 API ENDPOINTS:")
        print("-" * 40)
        print("  📖 Documentation: http://localhost:8000/docs")
        print("  🏠 System Status: http://localhost:8000/")
        print("  📊 Analytics: http://localhost:8000/analytics/performance")
        print("  🛡️ Risk Management: http://localhost:8000/risk/portfolio-risk")
        print("  ⚡ Flash Loans: http://localhost:8000/flash-loan/quote")
        
        print("\n🚀 TO START THE API SERVER:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
        # Keep systems running
        print("\n⏳ Systems running... Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(10)
                
                # Show live updates every 10 seconds
                opportunities = len(trading_engine.get_current_opportunities())
                active_trades = len(trading_engine.get_active_trades())
                
                print(f"  💡 Live: {opportunities} opportunities, {active_trades} active trades")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down systems...")
            
            # Graceful shutdown
            await trading_engine.stop_engine()
            for agent in master_orchestrator.agents.values():
                await agent.stop()
            
            print("✅ All systems stopped gracefully")
            return True
        
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"\n💥 System error: {e}")
        return False

async def test_real_quote():
    """Quick test of real 0x quote"""
    print("\n🧪 Testing Real 0x Quote...")
    
    try:
        from integrations.dex_aggregator import dex_aggregator
        await dex_aggregator.initialize_aggregators()
        
        quote = await dex_aggregator.get_0x_quote(
            token_in="ETH",
            token_out="USDC",
            amount_in=1.0,
            chain=dex_aggregator.Chain.ETHEREUM,
            slippage_tolerance=0.01
        )
        
        if quote:
            print(f"✅ Real Quote: 1 ETH = {quote.amount_out:.2f} USDC")
            print(f"   Gas: {quote.gas_estimate:,} units @ {quote.gas_price:.1f} gwei")
            print(f"   Route: {' -> '.join(quote.route)}")
        else:
            print("❌ Quote failed")
            
    except Exception as e:
        print(f"❌ Quote test error: {e}")

async def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Just test a quote
        await test_real_quote()
    else:
        # Run full system
        await run_real_atom_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
