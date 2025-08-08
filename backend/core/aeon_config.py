"""
🧬 AEON Configuration System
Advanced Efficient Optimized Network - Core Configuration Management
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

class ExecutionMode(Enum):
    """AEON execution modes"""
    AUTO = "auto"           # Fully autonomous execution
    MANUAL = "manual"       # Manual approval required for all trades
    HYBRID = "hybrid"       # Auto for small trades, manual for large ones

class RiskLevel(Enum):
    """AEON risk tolerance levels"""
    CONSERVATIVE = "conservative"  # 23-30bps, max $100 trades
    MODERATE = "moderate"         # 23-50bps, max $500 trades  
    AGGRESSIVE = "aggressive"     # 23-100bps, max $2000 trades

@dataclass
class AEONConfig:
    """
    🧬 AEON - Advanced Efficient Optimized Network Configuration
    The core brain of the arbitrage system
    """
    
    # === EXECUTION CONTROL ===
    execution_mode: ExecutionMode = ExecutionMode.MANUAL
    auto_trade_enabled: bool = False
    manual_approval_required: bool = True
    
    # === RISK MANAGEMENT ===
    risk_level: RiskLevel = RiskLevel.MODERATE
    min_spread_bps: int = 23                    # Minimum 23bps threshold
    max_spread_bps: int = 500                   # Maximum spread (safety)
    max_trade_amount_usd: float = 500.0         # Maximum trade size
    max_daily_trades: int = 50                  # Daily trade limit
    max_daily_volume_usd: float = 10000.0       # Daily volume limit
    
    # === AUTO-TRADE THRESHOLDS ===
    auto_trade_min_spread_bps: int = 30         # Higher threshold for auto
    auto_trade_max_amount_usd: float = 100.0    # Smaller amounts for auto
    auto_trade_min_confidence: float = 85.0     # Minimum confidence %
    
    # === MANUAL APPROVAL TRIGGERS ===
    manual_approval_amount_usd: float = 200.0   # Require approval above this
    manual_approval_spread_bps: int = 75        # Require approval above this spread
    manual_approval_timeout_seconds: int = 300  # 5 minute approval timeout
    
    # === CIRCUIT BREAKERS ===
    circuit_breaker_enabled: bool = True
    max_consecutive_failures: int = 5           # Stop after 5 failures
    cooldown_after_failure_minutes: int = 15   # Wait 15min after failures
    emergency_stop_loss_percent: float = 5.0   # Emergency stop at 5% loss
    
    # === NOTIFICATION PREFERENCES ===
    notify_all_opportunities: bool = False      # Only notify on execution by default
    notify_auto_trades: bool = True             # Notify when auto-executing
    notify_manual_requests: bool = True         # Notify when approval needed
    notify_failures: bool = True                # Always notify failures
    
    # === ADVANCED SETTINGS ===
    gas_price_limit_gwei: int = 50             # Max gas price
    slippage_tolerance_bps: int = 50           # 0.5% max slippage
    price_staleness_seconds: int = 30          # Max price age
    
    # === METADATA ===
    created_at: str = ""
    updated_at: str = ""
    version: str = "2.0.0"

class AEONConfigManager:
    """
    🧬 AEON Configuration Manager
    Handles loading, saving, and updating AEON system configuration
    """
    
    def __init__(self, config_path: str = "backend/config/aeon_config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[AEONConfig] = None
        self._load_config()

    @classmethod
    def parse_file(cls, config_path: str) -> AEONConfig:
        """Parse AEON config from file"""
        manager = cls(config_path)
        return manager.get_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Convert string enums back to enum objects
                if 'execution_mode' in data:
                    data['execution_mode'] = ExecutionMode(data['execution_mode'])
                if 'risk_level' in data:
                    data['risk_level'] = RiskLevel(data['risk_level'])
                
                self._config = AEONConfig(**data)
                logger.info(f"✅ AEON config loaded from {self.config_path}")
            else:
                self._config = AEONConfig()
                self._config.created_at = datetime.now().isoformat()
                self._save_config()
                logger.info("🆕 Created new AEON config with defaults")
                
        except Exception as e:
            logger.error(f"Failed to load AEON config: {e}")
            self._config = AEONConfig()
            self._config.created_at = datetime.now().isoformat()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            if self._config:
                self._config.updated_at = datetime.now().isoformat()
                
                # Convert to dict and handle enums
                data = asdict(self._config)
                data['execution_mode'] = self._config.execution_mode.value
                data['risk_level'] = self._config.risk_level.value
                
                with open(self.config_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"💾 AEON config saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save AEON config: {e}")
    
    @property
    def config(self) -> AEONConfig:
        """Get current configuration"""
        return self._config or AEONConfig()
    
    def update_execution_mode(self, mode: ExecutionMode) -> bool:
        """Update execution mode and related settings"""
        try:
            self._config.execution_mode = mode
            
            if mode == ExecutionMode.AUTO:
                self._config.auto_trade_enabled = True
                self._config.manual_approval_required = False
                logger.info("🤖 AEON switched to AUTONOMOUS mode")
                
            elif mode == ExecutionMode.MANUAL:
                self._config.auto_trade_enabled = False
                self._config.manual_approval_required = True
                logger.info("👤 AEON switched to MANUAL mode")
                
            elif mode == ExecutionMode.HYBRID:
                self._config.auto_trade_enabled = True
                self._config.manual_approval_required = True  # For large trades
                logger.info("🔄 AEON switched to HYBRID mode")
            
            self._save_config()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update execution mode: {e}")
            return False
    
    def update_risk_level(self, risk_level: RiskLevel) -> bool:
        """Update risk level and adjust thresholds"""
        try:
            self._config.risk_level = risk_level
            
            if risk_level == RiskLevel.CONSERVATIVE:
                self._config.max_spread_bps = 30
                self._config.max_trade_amount_usd = 100.0
                self._config.auto_trade_max_amount_usd = 50.0
                
            elif risk_level == RiskLevel.MODERATE:
                self._config.max_spread_bps = 75
                self._config.max_trade_amount_usd = 500.0
                self._config.auto_trade_max_amount_usd = 100.0
                
            elif risk_level == RiskLevel.AGGRESSIVE:
                self._config.max_spread_bps = 150
                self._config.max_trade_amount_usd = 2000.0
                self._config.auto_trade_max_amount_usd = 200.0
            
            self._save_config()
            logger.info(f"⚡ AEON risk level updated to {risk_level.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update risk level: {e}")
            return False
    
    def should_auto_execute(self, spread_bps: float, amount_usd: float, confidence: float) -> bool:
        """Determine if trade should be auto-executed"""
        if not self._config.auto_trade_enabled:
            return False
        
        # Check all auto-trade criteria
        checks = [
            spread_bps >= self._config.auto_trade_min_spread_bps,
            amount_usd <= self._config.auto_trade_max_amount_usd,
            confidence >= self._config.auto_trade_min_confidence,
            spread_bps <= self._config.max_spread_bps  # Safety check
        ]
        
        return all(checks)
    
    def requires_manual_approval(self, spread_bps: float, amount_usd: float) -> bool:
        """Determine if trade requires manual approval"""
        if self._config.execution_mode == ExecutionMode.MANUAL:
            return True
        
        if self._config.execution_mode == ExecutionMode.AUTO:
            return False
        
        # HYBRID mode - check thresholds
        return (
            amount_usd > self._config.manual_approval_amount_usd or
            spread_bps > self._config.manual_approval_spread_bps
        )
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current AEON status summary"""
        return {
            "execution_mode": self._config.execution_mode.value,
            "auto_trade_enabled": self._config.auto_trade_enabled,
            "risk_level": self._config.risk_level.value,
            "min_spread_bps": self._config.min_spread_bps,
            "max_trade_amount_usd": self._config.max_trade_amount_usd,
            "circuit_breaker_enabled": self._config.circuit_breaker_enabled,
            "last_updated": self._config.updated_at,
            "version": self._config.version
        }
    
    def export_config(self) -> Dict[str, Any]:
        """Export full configuration"""
        data = asdict(self._config)
        data['execution_mode'] = self._config.execution_mode.value
        data['risk_level'] = self._config.risk_level.value
        return data
    
    def import_config(self, config_data: Dict[str, Any]) -> bool:
        """Import configuration from dict"""
        try:
            # Validate and convert enums
            if 'execution_mode' in config_data:
                config_data['execution_mode'] = ExecutionMode(config_data['execution_mode'])
            if 'risk_level' in config_data:
                config_data['risk_level'] = RiskLevel(config_data['risk_level'])
            
            self._config = AEONConfig(**config_data)
            self._save_config()
            logger.info("📥 AEON configuration imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False

# Global AEON configuration manager
aeon_config = AEONConfigManager()
