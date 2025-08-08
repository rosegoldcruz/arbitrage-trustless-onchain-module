"""
DEPRECATED: This file has been moved to backend/config/bots.py
Import from there instead.
"""

# Temporary compatibility imports
from backend.config.bots import AtomConfig, AdomConfig

def get_atom_config():
    """DEPRECATED: Use AtomConfig.from_env() instead"""
    return AtomConfig.from_env().to_dict()

def get_adom_config():
    """DEPRECATED: Use AdomConfig.from_env() instead"""
    return AdomConfig.from_env().to_dict()

def validate_production_config():
    """DEPRECATED: Use AtomConfig.validate() instead"""
    try:
        AtomConfig.from_env().validate()
        AdomConfig.from_env().validate()
        return True
    except Exception:
        return False
