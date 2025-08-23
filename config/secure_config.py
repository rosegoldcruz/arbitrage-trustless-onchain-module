#!/usr/bin/env python3
"""
Secure Configuration Loader - Environment Variables Only
NO HARDCODED SECRETS - PRODUCTION READY
"""

import os
import logging
from typing import Dict, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class SecureConfig:
    """Secure configuration loader with environment variable enforcement"""
    
    def __init__(self):
        self.config = self._load_secure_config()
        self._validate_polygon_mainnet()
        
    def _load_secure_config(self) -> Dict:
        """Load all configuration from environment variables"""
        config = {
            # Network Configuration - POLYGON MAINNET ONLY
            'network': os.getenv('NETWORK', 'polygon_mainnet'),
            'chain_id': int(os.getenv('CHAIN_ID', '137')),
            'polygon_rpc_url': os.getenv('POLYGON_RPC_URL'),
            'polygon_rpc_backup': os.getenv('POLYGON_RPC_BACKUP'),
            'polygon_rpc_backup2': os.getenv('POLYGON_RPC_BACKUP2'),
            
            # Wallet Configuration
            'private_key': os.getenv('PRIVATE_KEY'),
            'wallet_address': os.getenv('TESTNET_WALLET_ADDRESS'),
            
            # Contract Addresses
            'flashloan_contract': os.getenv('FLASHLOAN_ARB_ADDR'),
            'atom_contract': os.getenv('ATOM_CONTRACT_ADDRESS'),
            
            # AAVE V3 Polygon
            'aave_pool_provider': os.getenv('AAVE_POOL_ADDRESSES_PROVIDER'),
            'aave_pool_address': os.getenv('AAVE_POOL_ADDRESS'),
            
            # DEX Addresses
            'uniswap_v3_router': os.getenv('UNISWAP_V3_ROUTER'),
            'uniswap_v3_quoter': os.getenv('UNISWAP_V3_QUOTER'),
            'quickswap_router': os.getenv('QUICKSWAP_ROUTER'),
            'sushiswap_router': os.getenv('SUSHISWAP_ROUTER'),
            'balancer_vault': os.getenv('BALANCER_VAULT'),
            
            # Token Addresses
            'weth_address': os.getenv('WETH_ADDRESS'),
            'usdc_address': os.getenv('USDC_ADDRESS'),
            'usdt_address': os.getenv('USDT_ADDRESS'),
            'dai_address': os.getenv('DAI_ADDRESS'),
            'wmatic_address': os.getenv('WMATIC_ADDRESS'),
            
            # Trading Parameters
            'min_trade_size_usd': Decimal(os.getenv('MIN_TRADE_SIZE_USD', '25000.00')),
            'min_profit_threshold_bps': int(os.getenv('MIN_PROFIT_THRESHOLD_BPS', '35')),
            'min_trade_profit_usd': Decimal(os.getenv('MIN_TRADE_PROFIT_USD', '87.50')),
            'target_net_profit': Decimal(os.getenv('TARGET_NET_PROFIT_PER_TRADE', '100.00')),
            'max_trade_size_usd': Decimal(os.getenv('MAX_TRADE_SIZE_USD', '100000.00')),
            'max_slippage_bps': int(os.getenv('MAX_SLIPPAGE_BPS', '300')),
            
            # Gas Configuration
            'max_gas_cost_usd': Decimal(os.getenv('MAX_GAS_COST_USD', '10.00')),
            'max_gas_price': int(os.getenv('ATOM_MAX_GAS_PRICE', '200')),
            'gas_price_multiplier': Decimal(os.getenv('GAS_PRICE_MULTIPLIER', '1.2')),
            'max_gas_limit': int(os.getenv('MAX_GAS_LIMIT', '600000')),
            'priority_fee_gwei': int(os.getenv('PRIORITY_FEE_GWEI', '5')),
            
            # AAVE Configuration
            'aave_flash_loan_fee_bps': int(os.getenv('AAVE_FLASH_LOAN_FEE_BPS', '9')),
            
            # Bot Configuration
            'scan_interval': int(os.getenv('ATOM_SCAN_INTERVAL', '1000')) / 1000,
            'opportunity_scan_interval': int(os.getenv('OPPORTUNITY_SCAN_INTERVAL_MS', '500')) / 1000,
            'execution_timeout': int(os.getenv('ATOM_EXECUTION_TIMEOUT', '8000')) / 1000,
            'retry_attempts': int(os.getenv('ATOM_RETRY_ATTEMPTS', '1')),
            'max_concurrent_trades': int(os.getenv('ATOM_MAX_CONCURRENT_TRADES', '1')),
            
            # API Keys
            'the_graph_api_key': os.getenv('THE_GRAPH_API_KEY'),
            'the_graph_studio_url': os.getenv('THE_GRAPH_STUDIO_URL'),
            
            # Redis Configuration
            'redis_url': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
            'redis_host': os.getenv('REDIS_HOST', '127.0.0.1'),
            'redis_port': int(os.getenv('REDIS_PORT', '6379')),
            'redis_db': int(os.getenv('REDIS_DB', '0')),
            
            # MEV Protection
            'use_flashbots_protect': os.getenv('USE_FLASHBOTS_PROTECT', 'true').lower() == 'true',
            'flashbots_protect_rpc': os.getenv('FLASHBOTS_PROTECT_RPC'),
            'private_mempool_enabled': os.getenv('PRIVATE_MEMPOOL_ENABLED', 'true').lower() == 'true',
            
            # Risk Management
            'max_daily_loss_usd': Decimal(os.getenv('MAX_DAILY_LOSS_USD', '1000.00')),
            'max_single_trade_loss_usd': Decimal(os.getenv('MAX_SINGLE_TRADE_LOSS_USD', '250.00')),
            'emergency_stop_loss_usd': Decimal(os.getenv('EMERGENCY_STOP_LOSS_USD', '2500.00')),
            'circuit_breaker_enabled': os.getenv('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true',
            
            # Profit Targets
            'daily_profit_target_usd': Decimal(os.getenv('DAILY_PROFIT_TARGET_USD', '500')),
            'weekly_profit_target_usd': Decimal(os.getenv('WEEKLY_PROFIT_TARGET_USD', '3500')),
            'monthly_profit_target_usd': Decimal(os.getenv('MONTHLY_PROFIT_TARGET_USD', '15000')),
            
            # Alert Configuration
            'enable_discord_alerts': os.getenv('ENABLE_DISCORD_ALERTS', 'true').lower() == 'true',
            'enable_telegram_alerts': os.getenv('ENABLE_TELEGRAM_ALERTS', 'true').lower() == 'true',
            'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),
            
            # Production Flags
            'production_mode': os.getenv('PRODUCTION_MODE', 'true').lower() == 'true',
            'enable_trading': os.getenv('ENABLE_TRADING', 'true').lower() == 'true',
            'dry_run': os.getenv('DRY_RUN', 'false').lower() == 'true',
        }
        
        return config
        
    def _validate_polygon_mainnet(self):
        """Validate Polygon mainnet configuration"""
        # Enforce Polygon mainnet only
        if self.config['chain_id'] != 137:
            raise ValueError(f"Invalid chain ID {self.config['chain_id']}. System configured for Polygon mainnet (137) only.")
            
        if self.config['network'] != 'polygon_mainnet':
            raise ValueError(f"Invalid network {self.config['network']}. System configured for polygon_mainnet only.")
            
        # Validate required environment variables
        required_vars = [
            'private_key', 'flashloan_contract', 'polygon_rpc_url',
            'aave_pool_provider', 'uniswap_v3_router', 'quickswap_router',
            'weth_address', 'usdc_address', 'wmatic_address'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not self.config.get(var):
                missing_vars.append(var.upper())
                
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
            
        # Validate Polygon addresses
        polygon_addresses = {
            'AAVE_POOL_ADDRESSES_PROVIDER': '0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb',
            'UNISWAP_V3_ROUTER': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
            'QUICKSWAP_ROUTER': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
            'WETH_ADDRESS': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
            'USDC_ADDRESS': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
            'WMATIC_ADDRESS': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'
        }
        
        for env_var, expected_addr in polygon_addresses.items():
            config_key = env_var.lower()
            if self.config.get(config_key) and self.config[config_key].lower() != expected_addr.lower():
                logger.warning(f"{env_var} address mismatch. Expected: {expected_addr}, Got: {self.config[config_key]}")
                
        logger.info("✅ Polygon mainnet configuration validated")
        
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
        
    def get_tokens(self) -> Dict[str, str]:
        """Get token addresses"""
        return {
            'WETH': self.config['weth_address'],
            'USDC': self.config['usdc_address'],
            'USDT': self.config['usdt_address'],
            'DAI': self.config['dai_address'],
            'WMATIC': self.config['wmatic_address']
        }
        
    def get_dex_routers(self) -> Dict[str, str]:
        """Get DEX router addresses"""
        return {
            'uniswap_v3': self.config['uniswap_v3_router'],
            'quickswap': self.config['quickswap_router'],
            'sushiswap': self.config['sushiswap_router'],
            'balancer': self.config['balancer_vault']
        }
        
    def validate_production_ready(self) -> bool:
        """Validate system is production ready"""
        checks = [
            self.config['production_mode'],
            self.config['enable_trading'],
            not self.config['dry_run'],
            self.config['chain_id'] == 137,
            self.config['private_key'] is not None,
            self.config['flashloan_contract'] is not None
        ]
        
        if all(checks):
            logger.info("✅ System validated as production ready")
            return True
        else:
            logger.error("❌ System not production ready")
            return False

# Global configuration instance
config = SecureConfig()
