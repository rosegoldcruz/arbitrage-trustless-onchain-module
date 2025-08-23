#!/usr/bin/env python3
"""
Environment Variable Validation for ATOM Arbitrage System
Validates all required environment variables on startup
"""

import os
import sys
import re
from typing import List, Dict

class EnvironmentValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_required_vars(self) -> bool:
        """Validate all required environment variables"""
        required_vars = [
            'PRIVATE_KEY',
            'WALLET_ADDRESS', 
            'ATOM_CONTRACT_ADDRESS',
            'POLYGON_RPC_URL',
            'CHAIN_ID',
            'NETWORK'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.errors.append(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def validate_network_config(self) -> bool:
        """Validate network configuration is Polygon mainnet only"""
        chain_id = os.getenv('CHAIN_ID')
        network = os.getenv('NETWORK')
        
        if chain_id != '137':
            self.errors.append(f"Invalid CHAIN_ID: {chain_id}. Must be 137 (Polygon mainnet)")
            return False
            
        if network != 'polygon_mainnet':
            self.errors.append(f"Invalid NETWORK: {network}. Must be polygon_mainnet")
            return False
            
        return True
    
    def validate_addresses(self) -> bool:
        """Validate Ethereum address formats"""
        address_vars = [
            'WALLET_ADDRESS',
            'ATOM_CONTRACT_ADDRESS',
            'WETH_ADDRESS',
            'USDC_ADDRESS',
            'DAI_ADDRESS'
        ]
        
        address_pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
        
        for var in address_vars:
            addr = os.getenv(var)
            if addr and not address_pattern.match(addr):
                self.errors.append(f"Invalid address format for {var}: {addr}")
                return False
        
        return True
    
    def validate_private_key(self) -> bool:
        """Validate private key format"""
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            return True  # Already checked in required_vars
            
        # Remove 0x prefix if present
        if private_key.startswith('0x'):
            private_key = private_key[2:]
            
        if len(private_key) != 64 or not re.match(r'^[a-fA-F0-9]{64}$', private_key):
            self.errors.append("Invalid PRIVATE_KEY format. Must be 64 hex characters")
            return False
            
        return True
    
    def validate_rpc_urls(self) -> bool:
        """Validate RPC URL formats"""
        rpc_vars = ['POLYGON_RPC_URL', 'POLYGON_RPC_BACKUP', 'POLYGON_RPC_BACKUP2']
        
        for var in rpc_vars:
            url = os.getenv(var)
            if url and not (url.startswith('http://') or url.startswith('https://')):
                self.errors.append(f"Invalid RPC URL format for {var}: {url}")
                return False
        
        return True
    
    def validate_production_flags(self) -> bool:
        """Validate production configuration flags"""
        production_mode = os.getenv('PRODUCTION_MODE', 'false').lower()
        dry_run = os.getenv('DRY_RUN', 'true').lower()
        allow_mainnet = os.getenv('ALLOW_MAINNET', 'false').lower()
        
        if production_mode == 'true' and dry_run == 'true':
            self.warnings.append("PRODUCTION_MODE=true but DRY_RUN=true. This will not execute real trades.")
            
        if production_mode == 'true' and allow_mainnet != 'true':
            self.errors.append("PRODUCTION_MODE=true requires ALLOW_MAINNET=true")
            return False
            
        return True
    
    def validate_all(self) -> bool:
        """Run all validations"""
        print("🔍 Validating environment configuration...")
        
        validations = [
            self.validate_required_vars,
            self.validate_network_config,
            self.validate_addresses,
            self.validate_private_key,
            self.validate_rpc_urls,
            self.validate_production_flags
        ]
        
        all_valid = True
        for validation in validations:
            if not validation():
                all_valid = False
        
        return all_valid
    
    def print_results(self) -> None:
        """Print validation results"""
        if self.errors:
            print("\n❌ ENVIRONMENT VALIDATION FAILED:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ All environment variables validated successfully")
        elif not self.errors:
            print("✅ Environment validation passed with warnings")

def main():
    """Main validation function"""
    validator = EnvironmentValidator()
    
    if validator.validate_all():
        validator.print_results()
        print("\n🚀 Environment ready for ATOM arbitrage system")
        sys.exit(0)
    else:
        validator.print_results()
        print("\n🔧 Fix the above issues before starting the system")
        sys.exit(1)

if __name__ == "__main__":
    main()
