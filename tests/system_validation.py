#!/usr/bin/env python3
"""
Complete System Validation Tests
Comprehensive validation covering all 6 test requirements
"""

import asyncio
import json
import logging
import os
import sys
import time
from decimal import Decimal
from typing import Dict, List, Tuple
import redis
from web3 import Web3
import aiohttp

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.opportunity_detector import OpportunityDetector
from bots.trade_executor import TradeExecutor
from bots.monitoring_system import MonitoringSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemValidator:
    def __init__(self):
        self.load_config()
        self.setup_connections()
        self.test_results = {}
        
    def load_config(self):
        """Load test configuration"""
        self.polygon_rpc = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
        self.redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.flash_loan_contract = os.getenv('FLASH_LOAN_CONTRACT', '0x34d560b34d3dB2671260092AbAcbA05399121E9a')
        
    def setup_connections(self):
        """Setup test connections"""
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        
    async def run_comprehensive_validation(self) -> Dict:
        """Run all validation tests"""
        logger.info("🧪 Starting comprehensive system validation...")
        
        tests = [
            ("Infrastructure Connectivity", self.test_infrastructure_connectivity),
            ("Price Feed Integration", self.test_price_feed_integration),
            ("DEX Integration", self.test_dex_integration),
            ("Opportunity Detection", self.test_opportunity_detection),
            ("Trade Execution Simulation", self.test_trade_execution_simulation),
            ("System Health Monitoring", self.test_system_health_monitoring),
            ("Security Systems", self.test_security_systems),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        results = {}
        overall_success = True
        
        for test_name, test_function in tests:
            logger.info(f"Running test: {test_name}")
            try:
                result = await test_function()
                results[test_name] = result
                
                if result['success']:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                    overall_success = False
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
                results[test_name] = {'success': False, 'error': str(e)}
                overall_success = False
                
        # Generate final report
        report = {
            'overall_success': overall_success,
            'test_results': results,
            'timestamp': time.time(),
            'summary': self._generate_summary(results)
        }
        
        return report
        
    async def test_infrastructure_connectivity(self) -> Dict:
        """Test 1: Infrastructure connectivity"""
        try:
            # Test Polygon RPC
            block_number = self.w3.eth.block_number
            if block_number == 0:
                return {'success': False, 'error': 'Invalid block number from RPC'}
                
            # Test Redis
            self.redis_client.ping()
            
            # Test contract accessibility
            contract_code = self.w3.eth.get_code(self.flash_loan_contract)
            if len(contract_code) == 0:
                return {'success': False, 'error': 'Flash loan contract not found'}
                
            return {
                'success': True,
                'details': {
                    'block_number': block_number,
                    'redis_connected': True,
                    'contract_accessible': True
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_price_feed_integration(self) -> Dict:
        """Test 2: Price feed integration"""
        try:
            # Test DEX API endpoints
            dex_endpoints = {
                'uniswap_v3': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3-polygon',
                'quickswap': 'https://api.thegraph.com/subgraphs/name/sameepsi/quickswap06',
                'sushiswap': 'https://api.thegraph.com/subgraphs/name/sushiswap/exchange-polygon'
            }
            
            results = {}
            
            for dex_name, endpoint in dex_endpoints.items():
                try:
                    async with aiohttp.ClientSession() as session:
                        query = '{ _meta { block { number } } }'
                        async with session.post(endpoint, json={'query': query}, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                results[dex_name] = {
                                    'accessible': True,
                                    'block_number': data.get('data', {}).get('_meta', {}).get('block', {}).get('number', 0)
                                }
                            else:
                                results[dex_name] = {'accessible': False, 'status': response.status}
                except Exception as e:
                    results[dex_name] = {'accessible': False, 'error': str(e)}
                    
            accessible_count = sum(1 for r in results.values() if r.get('accessible', False))
            
            return {
                'success': accessible_count >= 2,  # At least 2 DEXs accessible
                'details': {
                    'dex_results': results,
                    'accessible_count': accessible_count
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_dex_integration(self) -> Dict:
        """Test 3: DEX integration"""
        try:
            # Test DEX router contracts
            dex_routers = {
                'uniswap_v3': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'quickswap': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
                'sushiswap': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'
            }
            
            results = {}
            
            for dex_name, router_address in dex_routers.items():
                try:
                    code = self.w3.eth.get_code(router_address)
                    results[dex_name] = {
                        'contract_exists': len(code) > 0,
                        'address': router_address
                    }
                except Exception as e:
                    results[dex_name] = {'contract_exists': False, 'error': str(e)}
                    
            accessible_count = sum(1 for r in results.values() if r.get('contract_exists', False))
            
            return {
                'success': accessible_count >= 3,  # All 3 DEX routers accessible
                'details': {
                    'router_results': results,
                    'accessible_count': accessible_count
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_opportunity_detection(self) -> Dict:
        """Test 4: Opportunity detection"""
        try:
            # Initialize opportunity detector
            detector = OpportunityDetector()
            
            # Test price fetching
            weth = detector.tokens['WETH']
            usdc = detector.tokens['USDC']
            amount = int(1 * 10**18)  # 1 WETH
            
            # Test Uniswap V3 price
            uniswap_price = await detector.get_uniswap_v3_price(weth, usdc, amount)
            
            # Test QuickSwap price
            quickswap_price = await detector.get_v2_price(detector.quickswap_router, weth, usdc, amount)
            
            success = (uniswap_price is not None and uniswap_price > 0 and
                      quickswap_price is not None and quickswap_price > 0)
            
            return {
                'success': success,
                'details': {
                    'uniswap_v3_price': uniswap_price,
                    'quickswap_price': quickswap_price,
                    'price_difference': abs(uniswap_price - quickswap_price) if success else 0
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_trade_execution_simulation(self) -> Dict:
        """Test 5: Trade execution simulation (dry run)"""
        try:
            # Create mock opportunity
            mock_opportunity = {
                'token_a': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',  # WETH
                'token_b': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',  # USDC
                'token_c': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',  # WMATIC
                'token_a_name': 'WETH',
                'token_b_name': 'USDC',
                'token_c_name': 'WMATIC',
                'dex_a': 'uniswap_v3',
                'dex_b': 'quickswap',
                'dex_c': 'sushiswap',
                'amount_in': int(0.1 * 10**18),  # 0.1 WETH
                'profit_bps': 50,  # 0.5% profit
                'timestamp': time.time()
            }
            
            # Test trade validation (without actual execution)
            executor = TradeExecutor()
            
            # Test gas estimation
            gas_cost = executor.estimate_gas_cost()
            
            # Test parameter encoding
            params = executor.encode_arbitrage_params(mock_opportunity)
            
            success = (gas_cost > 0 and params is not None)
            
            return {
                'success': success,
                'details': {
                    'gas_cost_estimated': gas_cost,
                    'parameters_encoded': params is not None,
                    'mock_opportunity_valid': True
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_system_health_monitoring(self) -> Dict:
        """Test 6: System health monitoring"""
        try:
            # Test monitoring system
            monitoring = MonitoringSystem()
            
            # Test metrics collection
            await monitoring._collect_metrics()
            
            # Test Redis storage
            metrics = self.redis_client.get('monitoring_metrics')
            metrics_valid = metrics is not None
            
            if metrics_valid:
                metrics_data = json.loads(metrics)
                required_fields = ['system_start_time', 'total_trades', 'total_profit_usd']
                fields_present = all(field in metrics_data for field in required_fields)
            else:
                fields_present = False
                
            return {
                'success': metrics_valid and fields_present,
                'details': {
                    'metrics_stored': metrics_valid,
                    'required_fields_present': fields_present,
                    'monitoring_system_initialized': True
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_security_systems(self) -> Dict:
        """Test 7: Security systems"""
        try:
            # Test emergency thresholds
            max_daily_loss = Decimal(os.getenv('MAX_DAILY_LOSS_USD', '200'))
            max_single_loss = Decimal(os.getenv('MAX_SINGLE_TRADE_LOSS_USD', '50'))
            
            # Test wallet configuration
            wallet_count = 0
            for i in range(1, 6):
                private_key = os.getenv(f'WALLET_PRIVATE_KEY_{i}')
                if private_key and private_key != f'YOUR_ROTATION_WALLET_{i}_PRIVATE_KEY_HERE':
                    wallet_count += 1
                    
            return {
                'success': wallet_count >= 1 and max_daily_loss > 0 and max_single_loss > 0,
                'details': {
                    'configured_wallets': wallet_count,
                    'max_daily_loss': float(max_daily_loss),
                    'max_single_loss': float(max_single_loss),
                    'security_thresholds_set': True
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def test_performance_metrics(self) -> Dict:
        """Test 8: Performance metrics"""
        try:
            # Test performance calculation
            start_time = time.time()
            
            # Simulate some operations
            for _ in range(100):
                self.redis_client.ping()
                
            end_time = time.time()
            operation_time = end_time - start_time
            
            # Test if system can handle required throughput
            operations_per_second = 100 / operation_time
            required_ops_per_second = 10  # Minimum required
            
            return {
                'success': operations_per_second >= required_ops_per_second,
                'details': {
                    'operations_per_second': operations_per_second,
                    'required_ops_per_second': required_ops_per_second,
                    'performance_adequate': operations_per_second >= required_ops_per_second
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate test summary"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r.get('success', False))
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'overall_status': 'PASS' if passed_tests == total_tests else 'FAIL'
        }

async def main():
    """Run system validation"""
    validator = SystemValidator()
    
    print("🚀 ATOM Arbitrage System - Comprehensive Validation")
    print("=" * 60)
    
    report = await validator.run_comprehensive_validation()
    
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    summary = report['summary']
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")
    
    if report['overall_success']:
        print("\n✅ SYSTEM VALIDATION PASSED")
        print("🚀 System is ready for production deployment!")
    else:
        print("\n❌ SYSTEM VALIDATION FAILED")
        print("⚠️ Please fix the issues before deploying to production.")
        
    # Save detailed report
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\n📄 Detailed report saved to: validation_report.json")
    
    return 0 if report['overall_success'] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
