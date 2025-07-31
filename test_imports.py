#!/usr/bin/env python3
"""
🧪 Test Backend Import Resolution
Verify that all backend imports work correctly after the permanent fix
"""

import os
import sys

# 🔐 PERMANENT BACKEND IMPORT FIX
# Add backend directory to Python path to resolve imports like 'from backend.routers import ...'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_backend_imports():
    """Test all critical backend imports"""
    print("🧪 Testing Backend Import Resolution...")
    print("=" * 50)
    
    # Test 1: Core AEON imports
    try:
        from backend.core.aeon_execution_mode import aeon_mode, AEONExecutionMode
        print("✅ AEON execution mode imports: SUCCESS")
    except ImportError as e:
        print(f"❌ AEON execution mode imports: FAILED - {e}")
    
    # Test 2: Trading engine
    try:
        from backend.core.trading_engine import trading_engine
        print("✅ Trading engine imports: SUCCESS")
    except ImportError as e:
        print(f"❌ Trading engine imports: FAILED - {e}")
    
    # Test 3: Telegram integration
    try:
        from backend.integrations.telegram_notifier import telegram_notifier
        print("✅ Telegram notifier imports: SUCCESS")
    except ImportError as e:
        print(f"❌ Telegram notifier imports: FAILED - {e}")
    
    # Test 4: Flashloan providers
    try:
        from backend.integrations.flashloan_providers import flashloan_manager
        print("✅ Flashloan providers imports: SUCCESS")
    except ImportError as e:
        print(f"❌ Flashloan providers imports: FAILED - {e}")
    
    # Test 5: DEX aggregator
    try:
        from backend.integrations.dex_aggregator import dex_aggregator
        print("✅ DEX aggregator imports: SUCCESS")
    except ImportError as e:
        print(f"❌ DEX aggregator imports: FAILED - {e}")
    
    # Test 6: Router imports
    try:
        from backend.routers.telegram import router as telegram_router
        print("✅ Telegram router imports: SUCCESS")
    except ImportError as e:
        print(f"❌ Telegram router imports: FAILED - {e}")
    
    try:
        from backend.routers.arbitrage import router as arbitrage_router
        print("✅ Arbitrage router imports: SUCCESS")
    except ImportError as e:
        print(f"❌ Arbitrage router imports: FAILED - {e}")
    
    # Test 7: Working bots
    try:
        from backend.bots.working.config import get_atom_config
        print("✅ Bot config imports: SUCCESS")
    except ImportError as e:
        print(f"❌ Bot config imports: FAILED - {e}")
    
    print("=" * 50)
    print("🧪 Import testing complete!")

def test_system_paths():
    """Test system path configuration"""
    print("\n🔍 System Path Analysis:")
    print("=" * 50)
    
    current_dir = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.abspath(os.path.join(current_dir, "backend"))
    
    print(f"Current directory: {current_dir}")
    print(f"Backend directory: {backend_dir}")
    print(f"Backend exists: {os.path.exists(backend_dir)}")
    
    print("\nPython sys.path entries:")
    for i, path in enumerate(sys.path[:10]):  # Show first 10 entries
        print(f"  {i}: {path}")
    
    print("=" * 50)

def test_file_structure():
    """Test critical file structure"""
    print("\n📁 File Structure Check:")
    print("=" * 50)
    
    critical_files = [
        "backend/main.py",
        "backend/real_orchestrator.py", 
        "backend/core/trading_engine.py",
        "backend/core/aeon_execution_mode.py",
        "backend/integrations/telegram_notifier.py",
        "backend/integrations/flashloan_providers.py",
        "backend/routers/telegram.py",
        "backend/routers/arbitrage.py",
        "backend/bots/working/ATOM.py",
        "backend/bots/working/ADOM.js",
        "backend/bots/working/atom_hybrid_bot.py",
        "backend/bots/working/config.py"
    ]
    
    for file_path in critical_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
    
    print("=" * 50)

def main():
    """Run all import tests"""
    print("🧬 AEON BACKEND IMPORT RESOLUTION TEST")
    print("Testing permanent import fixes...")
    
    test_system_paths()
    test_file_structure()
    test_backend_imports()
    
    print("\n🎯 SUMMARY:")
    print("If all imports show ✅ SUCCESS, the backend is ready to run!")
    print("If any show ❌ FAILED, check the error messages above.")
    print("\n🚀 Next step: Run 'python start_full_system.py' to start AEON!")

if __name__ == "__main__":
    main()
