"""
🧬 AEON Execution Mode Controller
Advanced Efficient Optimized Network - Execution Mode Management
"""

import json
import os
import logging
from enum import Enum
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AEONExecutionMode(Enum):
    """AEON execution modes"""
    MANUAL = "manual"           # All trades require approval
    HYBRID = "hybrid"           # Small auto, large manual  
    AUTONOMOUS = "autonomous"   # Fully autonomous execution

class AEONModeController:
    """
    🧬 AEON Mode Controller
    Manages execution mode state via simple file storage
    """
    
    def __init__(self, config_file: str = "backend/config/aeon_mode.json"):
        self.config_file = config_file
        self.current_mode = AEONExecutionMode.MANUAL  # Default to safe mode
        self._load_mode()
    
    def _load_mode(self):
        """Load execution mode from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    mode_str = data.get('execution_mode', 'manual')
                    self.current_mode = AEONExecutionMode(mode_str)
                    logger.info(f"🧬 AEON mode loaded: {self.current_mode.value}")
            else:
                self._save_mode()  # Create default file
        except Exception as e:
            logger.error(f"Failed to load AEON mode: {e}")
            self.current_mode = AEONExecutionMode.MANUAL
    
    def _save_mode(self):
        """Save execution mode to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            data = {
                'execution_mode': self.current_mode.value,
                'updated_at': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 AEON mode saved: {self.current_mode.value}")
        except Exception as e:
            logger.error(f"Failed to save AEON mode: {e}")
    
    def set_mode(self, mode: AEONExecutionMode) -> bool:
        """Set execution mode"""
        try:
            old_mode = self.current_mode
            self.current_mode = mode
            self._save_mode()
            
            logger.info(f"🔄 AEON mode changed: {old_mode.value} → {mode.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set AEON mode: {e}")
            return False
    
    def get_mode(self) -> AEONExecutionMode:
        """Get current execution mode"""
        return self.current_mode
    
    def is_manual(self) -> bool:
        """Check if in manual mode"""
        return self.current_mode == AEONExecutionMode.MANUAL
    
    def is_hybrid(self) -> bool:
        """Check if in hybrid mode"""
        return self.current_mode == AEONExecutionMode.HYBRID
    
    def is_autonomous(self) -> bool:
        """Check if in autonomous mode"""
        return self.current_mode == AEONExecutionMode.AUTONOMOUS
    
    def should_auto_execute(self, amount_usd: float, spread_bps: float) -> bool:
        """Determine if trade should auto-execute based on mode and thresholds"""
        if self.current_mode == AEONExecutionMode.MANUAL:
            return False
        
        if self.current_mode == AEONExecutionMode.AUTONOMOUS:
            return True  # Auto-execute everything (with safety checks)
        
        if self.current_mode == AEONExecutionMode.HYBRID:
            # Auto-execute small, safe trades
            return (
                amount_usd <= 100.0 and      # Small trades only
                spread_bps <= 75 and         # Not too high spread
                spread_bps >= 23             # Above minimum threshold
            )
        
        return False
    
    def get_mode_emoji(self) -> str:
        """Get emoji for current mode"""
        if self.current_mode == AEONExecutionMode.MANUAL:
            return "🔴"
        elif self.current_mode == AEONExecutionMode.HYBRID:
            return "🟡"
        elif self.current_mode == AEONExecutionMode.AUTONOMOUS:
            return "🟢"
        return "❓"
    
    def get_mode_description(self) -> str:
        """Get description of current mode"""
        if self.current_mode == AEONExecutionMode.MANUAL:
            return "All trades require manual approval"
        elif self.current_mode == AEONExecutionMode.HYBRID:
            return "Small trades auto, large trades manual"
        elif self.current_mode == AEONExecutionMode.AUTONOMOUS:
            return "Fully autonomous execution"
        return "Unknown mode"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "mode": self.current_mode.value,
            "emoji": self.get_mode_emoji(),
            "description": self.get_mode_description(),
            "is_manual": self.is_manual(),
            "is_hybrid": self.is_hybrid(),
            "is_autonomous": self.is_autonomous()
        }

# Global AEON mode controller
aeon_mode = AEONModeController()
