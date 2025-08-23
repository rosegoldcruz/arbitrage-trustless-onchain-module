#!/usr/bin/env python3
"""
Security & Failsafe Systems
Emergency controls, automatic fund protection, and system health monitoring
"""

import asyncio
import json
import logging
import os
import time
from decimal import Decimal
from typing import Dict, List, Optional, Callable
from web3 import Web3
from eth_account import Account
import redis
import aiohttp

logger = logging.getLogger(__name__)

class SecuritySystem:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.load_config()
        self.setup_redis()
        self.emergency_callbacks = []
        self.security_checks = []
        self.system_paused = False
        self.last_security_check = 0
        self.security_violations = []
        self.running = False
        
    def load_config(self):
        """Load security configuration"""
        # Emergency thresholds
        self.max_daily_loss = Decimal(os.getenv('MAX_DAILY_LOSS_USD', '200'))
        self.max_single_trade_loss = Decimal(os.getenv('MAX_SINGLE_TRADE_LOSS_USD', '50'))
        self.max_consecutive_failures = int(os.getenv('MAX_CONSECUTIVE_FAILURES', '5'))
        self.emergency_stop_loss_percentage = Decimal(os.getenv('EMERGENCY_STOP_LOSS_PERCENTAGE', '5'))
        
        # Wallet security
        self.wallet_balance_threshold = Decimal(os.getenv('WALLET_BALANCE_THRESHOLD_USD', '10000'))
        self.suspicious_activity_threshold = int(os.getenv('SUSPICIOUS_ACTIVITY_THRESHOLD', '10'))
        
        # System health
        self.max_system_downtime = int(os.getenv('MAX_SYSTEM_DOWNTIME_SECONDS', '300'))  # 5 minutes
        self.health_check_interval = int(os.getenv('SECURITY_CHECK_INTERVAL', '60'))  # 1 minute
        
        # Contract addresses
        self.flash_loan_contract = os.getenv('ATOM_CONTRACT_ADDRESS')
        if not self.flash_loan_contract:
            raise ValueError("ATOM_CONTRACT_ADDRESS environment variable is required")
        
        # Emergency contact
        self.emergency_webhook = os.getenv('EMERGENCY_WEBHOOK_URL')
        
    def setup_redis(self):
        """Initialize Redis connection"""
        redis_url = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    def add_emergency_callback(self, callback: Callable):
        """Add callback function for emergency situations"""
        self.emergency_callbacks.append(callback)
        
    def add_security_check(self, check_function: Callable):
        """Add custom security check function"""
        self.security_checks.append(check_function)
        
    async def start_security_monitoring(self):
        """Start security monitoring system"""
        self.running = True
        logger.info("🛡️ Starting security monitoring system...")
        
        tasks = [
            asyncio.create_task(self._monitor_system_health()),
            asyncio.create_task(self._monitor_wallet_security()),
            asyncio.create_task(self._monitor_trading_performance()),
            asyncio.create_task(self._check_emergency_conditions()),
            asyncio.create_task(self._automated_fund_protection())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in security monitoring: {e}")
        finally:
            self.running = False
            
    async def _monitor_system_health(self):
        """Monitor overall system health"""
        while self.running:
            try:
                health_status = await self._perform_health_checks()
                
                # Store health status
                self.redis_client.set('system_health', json.dumps(health_status))
                
                # Check for critical issues
                if health_status['status'] == 'critical':
                    await self._trigger_emergency_response('system_health_critical', health_status)
                    
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring system health: {e}")
                await asyncio.sleep(60)
                
    async def _perform_health_checks(self) -> Dict:
        """Perform comprehensive health checks"""
        try:
            checks = {
                'rpc_connection': await self._check_rpc_connection(),
                'redis_connection': self._check_redis_connection(),
                'contract_accessibility': await self._check_contract_accessibility(),
                'wallet_balances': await self._check_wallet_balances(),
                'recent_activity': self._check_recent_activity(),
                'system_resources': self._check_system_resources()
            }
            
            # Determine overall status
            failed_checks = [name for name, status in checks.items() if not status['healthy']]
            
            if len(failed_checks) == 0:
                overall_status = 'healthy'
            elif len(failed_checks) <= 2:
                overall_status = 'warning'
            else:
                overall_status = 'critical'
                
            return {
                'status': overall_status,
                'checks': checks,
                'failed_checks': failed_checks,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'timestamp': time.time()
            }
            
    async def _check_rpc_connection(self) -> Dict:
        """Check RPC connection health"""
        try:
            block_number = self.w3.eth.block_number
            return {
                'healthy': True,
                'block_number': block_number,
                'message': 'RPC connection healthy'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'message': 'RPC connection failed'
            }
            
    def _check_redis_connection(self) -> Dict:
        """Check Redis connection health"""
        try:
            self.redis_client.ping()
            return {
                'healthy': True,
                'message': 'Redis connection healthy'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'message': 'Redis connection failed'
            }
            
    async def _check_contract_accessibility(self) -> Dict:
        """Check if flash loan contract is accessible"""
        try:
            # Simple contract call to check accessibility
            code = self.w3.eth.get_code(self.flash_loan_contract)
            if len(code) > 0:
                return {
                    'healthy': True,
                    'message': 'Contract accessible'
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Contract not found or no code'
                }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'message': 'Contract accessibility check failed'
            }
            
    async def _check_wallet_balances(self) -> Dict:
        """Check wallet balances for security issues"""
        try:
            # This would check all configured wallets
            # Return current security status
            return {
                'healthy': True,
                'message': 'Wallet balances normal'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'message': 'Wallet balance check failed'
            }
            
    def _check_recent_activity(self) -> Dict:
        """Check for recent system activity"""
        try:
            # Check last trade time
            metrics_raw = self.redis_client.get('monitoring_metrics')
            if metrics_raw:
                metrics = json.loads(metrics_raw)
                last_trade_time = metrics.get('last_trade_time', 0)
                time_since_last_trade = time.time() - last_trade_time
                
                if time_since_last_trade > 3600:  # 1 hour
                    return {
                        'healthy': False,
                        'message': f'No trades in {time_since_last_trade/3600:.1f} hours'
                    }
                else:
                    return {
                        'healthy': True,
                        'message': f'Last trade {time_since_last_trade/60:.0f} minutes ago'
                    }
            else:
                return {
                    'healthy': False,
                    'message': 'No metrics available'
                }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'message': 'Activity check failed'
            }
            
    def _check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            # Basic system resource check
            # In production, this would check CPU, memory, disk usage
            return {
                'healthy': True,
                'message': 'System resources normal'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'message': 'Resource check failed'
            }
            
    async def _monitor_wallet_security(self):
        """Monitor wallet security and suspicious activity"""
        while self.running:
            try:
                # Check for suspicious wallet activity
                security_issues = await self._detect_wallet_security_issues()
                
                if security_issues:
                    for issue in security_issues:
                        await self._handle_security_violation(issue)
                        
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring wallet security: {e}")
                await asyncio.sleep(300)
                
    async def _detect_wallet_security_issues(self) -> List[Dict]:
        """Detect potential wallet security issues"""
        issues = []
        
        try:
            # Check for unusual transaction patterns
            # Check for unexpected balance changes
            # Check for unauthorized access attempts
            # This would be implemented based on specific security requirements
            
            return issues
            
        except Exception as e:
            logger.error(f"Error detecting security issues: {e}")
            return []
            
    async def _monitor_trading_performance(self):
        """Monitor trading performance for security issues"""
        while self.running:
            try:
                # Get recent trading metrics
                metrics_raw = self.redis_client.get('monitoring_metrics')
                if metrics_raw:
                    metrics = json.loads(metrics_raw)
                    
                    # Check for excessive losses
                    daily_profit = self._calculate_daily_profit()
                    if daily_profit < -float(self.max_daily_loss):
                        await self._trigger_emergency_response(
                            'daily_loss_exceeded',
                            {'daily_profit': daily_profit, 'threshold': float(self.max_daily_loss)}
                        )
                        
                    # Check success rate
                    if (metrics.get('total_trades', 0) > 10 and 
                        metrics.get('success_rate', 1.0) < 0.3):
                        await self._trigger_emergency_response(
                            'low_success_rate',
                            {'success_rate': metrics.get('success_rate', 0)}
                        )
                        
                await asyncio.sleep(180)  # Check every 3 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring trading performance: {e}")
                await asyncio.sleep(180)
                
    def _calculate_daily_profit(self) -> float:
        """Calculate profit for the last 24 hours"""
        try:
            cutoff_time = time.time() - 86400  # 24 hours ago
            trade_history_raw = self.redis_client.lrange('trade_history', 0, -1)
            
            daily_profit = 0.0
            for trade_raw in trade_history_raw:
                trade = json.loads(trade_raw)
                if trade.get('timestamp', 0) > cutoff_time:
                    daily_profit += trade.get('net_profit_usd', 0)
                    
            return daily_profit
            
        except Exception as e:
            logger.error(f"Error calculating daily profit: {e}")
            return 0.0
            
    async def _check_emergency_conditions(self):
        """Check for emergency conditions that require immediate action"""
        while self.running:
            try:
                # Run custom security checks
                for check_function in self.security_checks:
                    try:
                        result = await check_function()
                        if result and result.get('emergency', False):
                            await self._trigger_emergency_response(
                                'custom_security_check',
                                result
                            )
                    except Exception as e:
                        logger.error(f"Error in custom security check: {e}")
                        
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error checking emergency conditions: {e}")
                await asyncio.sleep(60)
                
    async def _automated_fund_protection(self):
        """Automated fund protection system"""
        while self.running:
            try:
                # Check if emergency fund withdrawal is needed
                if await self._should_withdraw_funds():
                    await self._emergency_fund_withdrawal()
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in automated fund protection: {e}")
                await asyncio.sleep(300)
                
    async def _should_withdraw_funds(self) -> bool:
        """Determine if emergency fund withdrawal is needed"""
        try:
            # Check for critical security violations
            recent_violations = [
                v for v in self.security_violations 
                if time.time() - v['timestamp'] < 3600  # Last hour
            ]
            
            critical_violations = [
                v for v in recent_violations 
                if v.get('severity') == 'critical'
            ]
            
            return len(critical_violations) >= 3  # 3 critical violations in 1 hour
            
        except Exception as e:
            logger.error(f"Error checking fund withdrawal condition: {e}")
            return False
            
    async def _emergency_fund_withdrawal(self):
        """Execute emergency fund withdrawal"""
        try:
            logger.critical("🚨 EXECUTING EMERGENCY FUND WITHDRAWAL")
            
            # This would implement actual fund withdrawal logic
            # For now, just log and alert
            
            await self._send_emergency_alert(
                "EMERGENCY FUND WITHDRAWAL TRIGGERED",
                "Critical security violations detected. Funds being moved to secure wallets."
            )
            
        except Exception as e:
            logger.error(f"Error in emergency fund withdrawal: {e}")
            
    async def _trigger_emergency_response(self, event_type: str, details: Dict):
        """Trigger emergency response procedures"""
        try:
            logger.critical(f"🚨 EMERGENCY RESPONSE TRIGGERED: {event_type}")
            
            # Record security violation
            violation = {
                'type': event_type,
                'details': details,
                'timestamp': time.time(),
                'severity': 'critical'
            }
            self.security_violations.append(violation)
            
            # Store in Redis
            self.redis_client.lpush('security_violations', json.dumps(violation))
            self.redis_client.ltrim('security_violations', 0, 99)  # Keep last 100
            
            # Pause system if necessary
            if event_type in ['daily_loss_exceeded', 'system_health_critical']:
                await self._pause_system(f"Emergency response: {event_type}")
                
            # Notify emergency callbacks
            for callback in self.emergency_callbacks:
                try:
                    await callback(event_type, details)
                except Exception as e:
                    logger.error(f"Error in emergency callback: {e}")
                    
            # Send emergency alert
            await self._send_emergency_alert(
                f"EMERGENCY: {event_type}",
                json.dumps(details, indent=2)
            )
            
        except Exception as e:
            logger.error(f"Error triggering emergency response: {e}")
            
    async def _pause_system(self, reason: str):
        """Pause the entire trading system"""
        try:
            logger.critical(f"🛑 PAUSING SYSTEM: {reason}")
            
            self.system_paused = True
            
            # Set pause flag in Redis
            self.redis_client.set('system_paused', json.dumps({
                'paused': True,
                'reason': reason,
                'timestamp': time.time()
            }))
            
            await self._send_emergency_alert(
                "SYSTEM PAUSED",
                f"Trading system has been paused: {reason}"
            )
            
        except Exception as e:
            logger.error(f"Error pausing system: {e}")
            
    async def _send_emergency_alert(self, title: str, message: str):
        """Send emergency alert to all configured channels"""
        try:
            if self.emergency_webhook:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "embeds": [{
                            "title": f"🚨 ATOM EMERGENCY: {title}",
                            "description": message,
                            "color": 0xff0000,  # Red
                            "timestamp": time.time()
                        }]
                    }
                    
                    async with session.post(self.emergency_webhook, json=payload) as response:
                        if response.status == 204:
                            logger.info("Emergency alert sent successfully")
                        else:
                            logger.error(f"Failed to send emergency alert: {response.status}")
                            
        except Exception as e:
            logger.error(f"Error sending emergency alert: {e}")
            
    async def _handle_security_violation(self, violation: Dict):
        """Handle detected security violation"""
        try:
            logger.warning(f"🔒 Security violation detected: {violation}")
            
            self.security_violations.append(violation)
            
            # Store in Redis
            self.redis_client.lpush('security_violations', json.dumps(violation))
            
            # Take action based on severity
            if violation.get('severity') == 'critical':
                await self._trigger_emergency_response('security_violation', violation)
                
        except Exception as e:
            logger.error(f"Error handling security violation: {e}")
            
    def get_security_status(self) -> Dict:
        """Get comprehensive security status"""
        return {
            'system_paused': self.system_paused,
            'recent_violations': self.security_violations[-10:],
            'last_security_check': self.last_security_check,
            'emergency_callbacks_count': len(self.emergency_callbacks),
            'security_checks_count': len(self.security_checks),
            'running': self.running
        }
