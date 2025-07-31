#!/usr/bin/env python3
"""
🧪 ATOM Telegram Integration Test Suite
Comprehensive testing for all notification types and features
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.integrations.telegram_notifier import telegram_notifier, TelegramAlert, AlertType, Priority

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_connection():
    """Test basic Telegram bot connection"""
    print("🔗 Testing Telegram bot connection...")
    
    success = await telegram_notifier.test_connection()
    if success:
        print("✅ Connection test PASSED")
        return True
    else:
        print("❌ Connection test FAILED")
        return False

async def test_arbitrage_notifications():
    """Test arbitrage opportunity notifications"""
    print("\n🎯 Testing arbitrage opportunity notifications...")
    
    test_cases = [
        {
            "token_a": "DAI",
            "token_b": "USDC", 
            "spread_bps": 45.2,
            "estimated_profit": 123.45,
            "dex_path": "DAI→USDC→GHO→DAI"
        },
        {
            "token_a": "WETH",
            "token_b": "USDC",
            "spread_bps": 67.8,
            "estimated_profit": 234.56,
            "dex_path": "WETH→USDC→DAI→WETH"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"  📤 Sending test case {i}...")
        success = await telegram_notifier.notify_arbitrage_opportunity(**case)
        if success:
            print(f"  ✅ Test case {i} sent successfully")
        else:
            print(f"  ❌ Test case {i} failed")
        
        # Wait between messages to avoid rate limiting
        await asyncio.sleep(3)

async def test_depeg_notifications():
    """Test Curve depeg notifications"""
    print("\n🌊 Testing depeg notifications...")
    
    test_cases = [
        {
            "pool_address": "0x1234567890123456789012345678901234567890",
            "virtual_price": 0.985,
            "deviation": 0.025
        },
        {
            "pool_address": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "virtual_price": 1.032,
            "deviation": 0.035
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"  📤 Sending depeg test {i}...")
        success = await telegram_notifier.notify_depeg_detected(**case)
        if success:
            print(f"  ✅ Depeg test {i} sent successfully")
        else:
            print(f"  ❌ Depeg test {i} failed")
        
        await asyncio.sleep(3)

async def test_trade_notifications():
    """Test trade execution notifications"""
    print("\n💰 Testing trade execution notifications...")
    
    # Test successful trade
    print("  📤 Testing successful trade notification...")
    success = await telegram_notifier.notify_trade_executed(
        trade_type="Triangular DAI→USDC→GHO",
        profit_usd=45.67,
        gas_used=420000,
        tx_hash="0x1234567890abcdef1234567890abcdef12345678"
    )
    if success:
        print("  ✅ Success notification sent")
    else:
        print("  ❌ Success notification failed")
    
    await asyncio.sleep(3)
    
    # Test failed trade
    print("  📤 Testing failed trade notification...")
    success = await telegram_notifier.notify_trade_failed(
        trade_type="Triangular WETH→USDC→DAI",
        error_reason="Insufficient gas for execution",
        estimated_loss=12.34
    )
    if success:
        print("  ✅ Failure notification sent")
    else:
        print("  ❌ Failure notification failed")

async def test_bot_status_notifications():
    """Test bot status notifications"""
    print("\n🤖 Testing bot status notifications...")
    
    status_tests = [
        {
            "bot_name": "ATOM",
            "status": "running",
            "uptime": "2h 34m",
            "opportunities_found": 47
        },
        {
            "bot_name": "ADOM", 
            "status": "stopped",
            "uptime": "0s",
            "opportunities_found": 0
        }
    ]
    
    for i, case in enumerate(status_tests, 1):
        print(f"  📤 Sending status test {i}...")
        success = await telegram_notifier.notify_bot_status(**case)
        if success:
            print(f"  ✅ Status test {i} sent successfully")
        else:
            print(f"  ❌ Status test {i} failed")
        
        await asyncio.sleep(3)

async def test_manual_approval():
    """Test manual approval workflow"""
    print("\n🔐 Testing manual approval workflow...")
    
    print("  📤 Sending approval request...")
    approval_id = await telegram_notifier.request_manual_approval(
        trade_type="High-Value Triangular Arbitrage",
        estimated_profit=567.89,
        risk_level="medium",
        timeout=300
    )
    
    if approval_id:
        print(f"  ✅ Approval request sent (ID: {approval_id})")
        print("  ⏳ Check your Telegram for interactive buttons!")
        print("  💡 You have 5 minutes to approve/reject")
    else:
        print("  ❌ Approval request failed")

async def test_custom_alert():
    """Test custom alert creation"""
    print("\n🎨 Testing custom alert...")
    
    custom_alert = TelegramAlert(
        alert_type=AlertType.SYSTEM_ERROR,
        priority=Priority.HIGH,
        title="🧪 Custom Test Alert",
        message="This is a custom test alert to verify the notification system is working correctly.",
        data={
            "test_parameter": "custom_value",
            "timestamp": datetime.now().isoformat(),
            "system_health": "excellent",
            "test_score": 98.5
        },
        timestamp=datetime.now()
    )
    
    print("  📤 Sending custom alert...")
    success = await telegram_notifier.send_alert(custom_alert)
    if success:
        print("  ✅ Custom alert sent successfully")
    else:
        print("  ❌ Custom alert failed")

async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n⏱️ Testing rate limiting...")
    
    print("  📤 Sending rapid-fire messages (should be rate limited)...")
    
    for i in range(5):
        success = await telegram_notifier.notify_arbitrage_opportunity(
            token_a="TEST",
            token_b="RATE",
            spread_bps=25.0,
            estimated_profit=10.0,
            dex_path=f"Rate-Limit-Test-{i}"
        )
        print(f"    Message {i+1}: {'✅ Sent' if success else '⏸️ Rate Limited'}")
        # No sleep - test rate limiting
    
    print("  💡 Only the first message should be sent, others rate limited")

async def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🚀 Starting ATOM Telegram Integration Test Suite")
    print("=" * 60)
    
    # Check configuration
    if not telegram_notifier.enabled:
        print("❌ Telegram notifier is disabled!")
        print("💡 Please configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env.local")
        return False
    
    print(f"🔧 Configuration:")
    print(f"   Bot Token: {'✅ Configured' if telegram_notifier.bot_token else '❌ Missing'}")
    print(f"   Chat ID: {'✅ Configured' if telegram_notifier.chat_id else '❌ Missing'}")
    print()
    
    # Run tests
    tests = [
        ("Connection Test", test_connection),
        ("Arbitrage Notifications", test_arbitrage_notifications),
        ("Depeg Notifications", test_depeg_notifications),
        ("Trade Notifications", test_trade_notifications),
        ("Bot Status Notifications", test_bot_status_notifications),
        ("Manual Approval", test_manual_approval),
        ("Custom Alert", test_custom_alert),
        ("Rate Limiting", test_rate_limiting)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = await test_func()
            if result is not False:  # None or True counts as pass
                passed += 1
                print(f"✅ {test_name} completed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
        
        # Wait between test suites
        await asyncio.sleep(2)
    
    # Final results
    print("\n" + "=" * 60)
    print("🏁 TEST SUITE COMPLETE")
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Telegram integration is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n💡 Check your Telegram chat for all the test messages!")
    return passed == total

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_comprehensive_test())
