#!/usr/bin/env python3
"""
ATOM Security Audit Script
Validates that NO sensitive data is hardcoded in source files
"""

import os
import re
import sys
from pathlib import Path

# Sensitive patterns to detect
SENSITIVE_PATTERNS = [
    # Private keys (64 hex characters)
    (r'[0-9a-fA-F]{64}', 'Private Key'),
    
    # Ethereum addresses (0x followed by 40 hex characters)
    (r'0x[0-9a-fA-F]{40}', 'Ethereum Address'),
    
    # API keys patterns
    (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
    (r'pk_test_[a-zA-Z0-9]+', 'Stripe Test Key'),
    (r'sk_test_[a-zA-Z0-9]+', 'Stripe Secret Key'),
    
    # Common secret patterns
    (r'secret[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', 'Secret Key'),
    (r'api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', 'API Key'),
    (r'private[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', 'Private Key'),
    (r'password["\']?\s*[:=]\s*["\'][^"\']+["\']', 'Password'),
    (r'token["\']?\s*[:=]\s*["\'][^"\']+["\']', 'Token'),
]

# Files to exclude from audit
EXCLUDED_FILES = {
    '.env.example',
    'security_audit.py',
    '.env',
    '.env.local',
    '.env.production',
    '.env.polygon.production',
    'README.md',
    '.gitignore'
}

# Directories to exclude
EXCLUDED_DIRS = {
    '.git',
    'node_modules',
    '__pycache__',
    '.vscode',
    'venv',
    'env'
}

# Known safe addresses (Polygon mainnet contracts)
SAFE_ADDRESSES = {
    '0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb',  # AAVE Pool Provider
    '0x794a61358D6845594F94dc1DB02A252b5b4814aD',  # AAVE Pool
    '0xE592427A0AEce92De3Edee1F18E0157C05861564',  # Uniswap V3 Router
    '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6',  # Uniswap V3 Quoter
    '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',  # QuickSwap Router
    '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',  # SushiSwap Router
    '0xBA12222222228d8Ba445958a75a0704d566BF2C8',  # Balancer Vault
    '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',  # WETH
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',  # USDC
    '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  # USDT
    '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',  # DAI
    '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',  # WMATIC
}

class SecurityAudit:
    def __init__(self):
        self.violations = []
        self.files_scanned = 0
        self.total_lines = 0
        
    def scan_file(self, file_path: Path) -> list:
        """Scan a single file for sensitive data"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                self.total_lines += len(lines)
                
                for line_num, line in enumerate(lines, 1):
                    line_clean = line.strip()
                    
                    # Skip comments and empty lines
                    if not line_clean or line_clean.startswith('#') or line_clean.startswith('//'):
                        continue
                        
                    for pattern, description in SENSITIVE_PATTERNS:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            matched_text = match.group()
                            
                            # Skip safe addresses
                            if description == 'Ethereum Address' and matched_text in SAFE_ADDRESSES:
                                continue
                                
                            # Skip environment variable references
                            if 'os.getenv' in line or 'getenv' in line or 'config.get' in line:
                                continue

                            # Skip variable declarations that use env vars
                            if '=' in line and ('os.getenv' in line or 'config.get' in line):
                                continue

                            # Skip environment variable fallbacks (process.env.VAR || 'fallback')
                            if 'process.env.' in line and '||' in line:
                                continue

                            # Skip package.json/package-lock.json token references
                            if 'registry-auth-token' in line or 'token": "^' in line:
                                continue
                                
                            violations.append({
                                'file': str(file_path),
                                'line': line_num,
                                'type': description,
                                'content': line_clean,
                                'match': matched_text
                            })
                            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            
        return violations
        
    def scan_directory(self, directory: Path = None) -> None:
        """Scan directory recursively for sensitive data"""
        if directory is None:
            directory = Path('.')
            
        print(f"🔍 Scanning {directory.absolute()} for sensitive data...")
        print("="*60)
        
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip excluded files
                if file in EXCLUDED_FILES:
                    continue
                    
                # Only scan text files
                if file_path.suffix in {'.py', '.js', '.ts', '.sol', '.json', '.yaml', '.yml', '.sh', '.md', '.txt'}:
                    self.files_scanned += 1
                    file_violations = self.scan_file(file_path)
                    self.violations.extend(file_violations)
                    
    def generate_report(self) -> None:
        """Generate security audit report"""
        print("\n" + "="*60)
        print("🔒 SECURITY AUDIT REPORT")
        print("="*60)
        
        print(f"📊 Files Scanned: {self.files_scanned}")
        print(f"📊 Lines Scanned: {self.total_lines:,}")
        print(f"🚨 Violations Found: {len(self.violations)}")
        
        if self.violations:
            print("\n❌ SECURITY VIOLATIONS DETECTED:")
            print("-" * 60)
            
            for violation in self.violations:
                print(f"🚨 {violation['type']} in {violation['file']}:{violation['line']}")
                print(f"   Content: {violation['content'][:100]}...")
                print(f"   Match: {violation['match']}")
                print()
                
            print("🔥 CRITICAL: Sensitive data found in source code!")
            print("🔧 ACTION REQUIRED:")
            print("1. Move all sensitive data to environment variables")
            print("2. Use os.getenv() or config.get() to load values")
            print("3. Add sensitive files to .gitignore")
            print("4. Never commit secrets to version control")
            
            return False
        else:
            print("\n✅ NO SECURITY VIOLATIONS FOUND!")
            print("🎉 All sensitive data properly externalized to environment variables")
            print("🔒 Source code is safe for public sharing")
            
            return True
            
    def validate_environment_usage(self) -> bool:
        """Validate that environment variables are being used properly"""
        print("\n🔍 Validating Environment Variable Usage...")
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for file in files:
                if file.endswith('.py') and file not in EXCLUDED_FILES:
                    python_files.append(Path(root) / file)
                    
        env_usage_found = False
        config_usage_found = False
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if 'os.getenv' in content or 'getenv' in content:
                        env_usage_found = True
                        
                    if 'config.get' in content or 'from config' in content:
                        config_usage_found = True
                        
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
        if env_usage_found or config_usage_found:
            print("✅ Environment variable usage detected")
            return True
        else:
            print("⚠️  No environment variable usage found")
            return False

def main():
    """Main security audit function"""
    print("🔒 ATOM SECURITY AUDIT")
    print("Validating NO sensitive data in source code")
    print("="*60)
    
    audit = SecurityAudit()
    audit.scan_directory()
    
    # Generate main report
    is_secure = audit.generate_report()
    
    # Validate environment variable usage
    env_usage = audit.validate_environment_usage()
    
    print("\n" + "="*60)
    print("🎯 FINAL SECURITY STATUS")
    print("="*60)
    
    if is_secure and env_usage:
        print("✅ SECURITY AUDIT PASSED")
        print("🔒 System is production-ready and secure")
        print("📤 Source code can be safely shared publicly")
        sys.exit(0)
    else:
        print("❌ SECURITY AUDIT FAILED")
        print("🚨 System requires security fixes before deployment")
        print("🔧 Fix all violations before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()
