"""
ATOM Validation Engine - Mandatory Pre-Trade Validation
Enforces .augment/rules/ requirements:
- spread_bps >= 23
- ROI after gas >= 0.25%
- slippage per leg <= 0.5%
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

@dataclass
class TradeValidationParams:
    spread_bps: float
    roi_after_gas: float
    slippage_per_leg: float
    gas_cost_usd: float
    profit_usd: float
    amount_usd: float
    token_pair: str
    dex_path: List[str]

class ValidationEngine:
    """
    Enforces mandatory validation rules before any trade execution
    """
    
    # MANDATORY THRESHOLDS (from .augment/rules/)
    MIN_SPREAD_BPS = 23.0          # 0.23% minimum spread
    MIN_ROI_AFTER_GAS = 0.25       # 0.25% minimum ROI after gas
    MAX_SLIPPAGE_PER_LEG = 0.5     # 0.5% maximum slippage per leg
    
    def __init__(self):
        self.validation_history = []
        self.health_status = {
            "contracts": False,
            "rpc": False,
            "external_apis": False,
            "last_check": None
        }
    
    async def validate_trade_parameters(self, params: TradeValidationParams) -> ValidationResult:
        """
        Mandatory pre-trade validation - MUST pass all checks
        """
        errors = []
        warnings = []
        metrics = {}
        
        logger.info(f"🔍 Validating trade: {params.token_pair}")
        
        # 1. SPREAD VALIDATION (MANDATORY)
        if params.spread_bps < self.MIN_SPREAD_BPS:
            errors.append(
                f"Spread {params.spread_bps:.2f}bps below minimum {self.MIN_SPREAD_BPS}bps"
            )
        else:
            logger.info(f"✅ Spread validation passed: {params.spread_bps:.2f}bps")
        
        # 2. ROI AFTER GAS VALIDATION (MANDATORY)
        if params.roi_after_gas < self.MIN_ROI_AFTER_GAS:
            errors.append(
                f"ROI after gas {params.roi_after_gas:.3f}% below minimum {self.MIN_ROI_AFTER_GAS}%"
            )
        else:
            logger.info(f"✅ ROI validation passed: {params.roi_after_gas:.3f}%")
        
        # 3. SLIPPAGE PER LEG VALIDATION (MANDATORY)
        if params.slippage_per_leg > self.MAX_SLIPPAGE_PER_LEG:
            errors.append(
                f"Slippage per leg {params.slippage_per_leg:.3f}% exceeds maximum {self.MAX_SLIPPAGE_PER_LEG}%"
            )
        else:
            logger.info(f"✅ Slippage validation passed: {params.slippage_per_leg:.3f}%")
        
        # 4. PROFIT VALIDATION
        if params.profit_usd <= 0:
            errors.append("Profit must be positive")
        elif params.profit_usd < 1.0:
            warnings.append(f"Low profit: ${params.profit_usd:.2f}")
        
        # 5. GAS COST VALIDATION
        if params.gas_cost_usd >= params.profit_usd:
            errors.append(
                f"Gas cost ${params.gas_cost_usd:.2f} exceeds profit ${params.profit_usd:.2f}"
            )
        
        # 6. DEX PATH VALIDATION
        if len(params.dex_path) == 0:
            errors.append("DEX path cannot be empty")
        elif len(params.dex_path) > 5:
            warnings.append(f"Long DEX path ({len(params.dex_path)} hops) may increase slippage")
        
        # Calculate validation metrics
        metrics = {
            "spread_bps": params.spread_bps,
            "roi_after_gas": params.roi_after_gas,
            "slippage_per_leg": params.slippage_per_leg,
            "profit_to_gas_ratio": params.profit_usd / max(params.gas_cost_usd, 0.01),
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "dex_path_length": len(params.dex_path)
        }
        
        # Store validation result
        result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
        
        self.validation_history.append({
            "timestamp": datetime.now(timezone.utc),
            "token_pair": params.token_pair,
            "result": result,
            "params": params
        })
        
        # Log validation result
        if result.valid:
            logger.info(f"✅ Trade validation PASSED for {params.token_pair}")
            if warnings:
                logger.warning(f"⚠️ Warnings: {'; '.join(warnings)}")
        else:
            logger.error(f"❌ Trade validation FAILED for {params.token_pair}")
            logger.error(f"   Errors: {'; '.join(errors)}")
        
        return result
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Comprehensive health check before allowing any execution
        """
        logger.info("🏥 Running comprehensive health checks...")
        
        health_results = {}
        
        # 1. Contract Health Check
        health_results["contracts"] = await self._check_contracts_health()
        
        # 2. RPC Health Check
        health_results["rpc"] = await self._check_rpc_health()
        
        # 3. External APIs Health Check
        health_results["external_apis"] = await self._check_external_apis_health()
        
        # Update health status
        self.health_status.update(health_results)
        self.health_status["last_check"] = datetime.now(timezone.utc)
        
        all_healthy = all(health_results.values())
        
        if all_healthy:
            logger.info("✅ All health checks passed")
        else:
            failed_checks = [k for k, v in health_results.items() if not v]
            logger.error(f"❌ Health check failures: {', '.join(failed_checks)}")
        
        return health_results
    
    async def _check_contracts_health(self) -> bool:
        """Check deployed contract health"""
        try:
            # Import Web3 executor to check contracts
            from .web3_executor import web3_executor
            
            # Check if contracts are loaded
            if not web3_executor.contracts:
                logger.error("❌ No contracts loaded")
                return False
            
            # Check contract balances
            for name, contract in web3_executor.contracts.items():
                try:
                    balance = web3_executor.get_contract_balance(name)
                    if balance is None:
                        logger.warning(f"⚠️ Could not get balance for {name}")
                    else:
                        logger.info(f"✅ {name} balance: {balance:.4f} ETH")
                except Exception as e:
                    logger.error(f"❌ Error checking {name}: {e}")
                    return False
            
            logger.info("✅ Contract health check passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Contract health check failed: {e}")
            return False
    
    async def _check_rpc_health(self) -> bool:
        """Check RPC endpoint health"""
        try:
            from .web3_executor import web3_executor
            
            # Check connection
            if not web3_executor.w3.is_connected():
                logger.error("❌ RPC not connected")
                return False
            
            # Check latest block
            latest_block = web3_executor.w3.eth.block_number
            if latest_block == 0:
                logger.error("❌ RPC returning invalid block number")
                return False
            
            # Check gas price
            gas_price = web3_executor.w3.eth.gas_price
            if gas_price == 0:
                logger.error("❌ RPC returning invalid gas price")
                return False
            
            logger.info(f"✅ RPC health check passed (block: {latest_block}, gas: {gas_price})")
            return True
            
        except Exception as e:
            logger.error(f"❌ RPC health check failed: {e}")
            return False
    
    async def _check_external_apis_health(self) -> bool:
        """Check external API health (0x, Chainlink, etc.)"""
        try:
            import aiohttp
            import os
            
            # Check 0x API
            zrx_api_url = os.getenv("ZRX_API_URL", "https://api.0x.org")
            theatom_api_key = os.getenv("THEATOM_API_KEY")
            
            if not theatom_api_key:
                logger.error("❌ THEATOM_API_KEY not configured")
                return False
            
            async with aiohttp.ClientSession() as session:
                # Test 0x API health
                try:
                    headers = {"0x-api-key": theatom_api_key}
                    async with session.get(f"{zrx_api_url}/swap/v1/sources", headers=headers, timeout=10) as response:
                        if response.status != 200:
                            logger.error(f"❌ 0x API unhealthy: {response.status}")
                            return False
                        logger.info("✅ 0x API health check passed")
                except Exception as e:
                    logger.error(f"❌ 0x API health check failed: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ External API health check failed: {e}")
            return False
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        if not self.validation_history:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
        
        total = len(self.validation_history)
        passed = sum(1 for v in self.validation_history if v["result"].valid)
        failed = total - passed
        pass_rate = passed / total if total > 0 else 0.0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "last_validation": self.validation_history[-1]["timestamp"].isoformat() if self.validation_history else None
        }
    
    def is_system_healthy(self) -> bool:
        """Check if system is healthy enough for execution"""
        return all([
            self.health_status.get("contracts", False),
            self.health_status.get("rpc", False),
            self.health_status.get("external_apis", False)
        ])

# Global validation engine instance
validation_engine = ValidationEngine()
