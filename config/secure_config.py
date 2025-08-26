#!/usr/bin/env python3
"""
SecureConfig
Centralized configuration loader with strict environment enforcement.
Covers core RPCs, MEV defense, DEX routers, and token addresses.
"""

import os
import sys
import logging
from typing import Dict
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# Load .env.production
# ------------------------------------------------------------------------------
load_dotenv(dotenv_path=".env.production")

logger = logging.getLogger("secure_config")
logging.basicConfig(level=logging.INFO)


class SecureConfig:
    def __init__(self):
        self.env = os.environ
        # Run initial validation immediately
        self.validate_all()

        self.chain_ids = {
            "polygon": 137,
            "ethereum": 1,
            "base": 8453,
            "arbitrum": 42161,
        }

    # --------------------------------------------------------------------------
    # Require util
    # --------------------------------------------------------------------------
    def require(self, key: str) -> str:
        val = self.env.get(key)
        if not val:
            logger.critical(f"❌ Missing required env var: {key}")
            sys.exit(1)
        return val

    # --------------------------------------------------------------------------
    # Core validation
    # --------------------------------------------------------------------------
    def validate_core(self):
        required = [
            "PRIVATE_KEY",
            "CLERK_SECRET_KEY",
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
            "POLYGON_RPC_URL",
            "POLYGON_RPC_BACKUP",
            "POLYGON_RPC_BACKUP2",
            "ETHEREUM_RPC_URL",
            "BASE_RPC_URL",
            "ARBITRUM_RPC_URL",
        ]
        for key in required:
            self.require(key)

    # --------------------------------------------------------------------------
    # MEV defense config
    # --------------------------------------------------------------------------
    def validate_mev_defense(self):
        required = [
            "POLYGON_WSS_URL",
            "FLASHBOTS_RPC_URL",
            "ZEROX_API_KEY",
            "ZRX_API_URL",
            "ZRX_GASLESS_API_URL",
        ]
        for key in required:
            self.require(key)

    def get_mev_config(self) -> Dict[str, str]:
        return {
            "polygon_wss": self.require("POLYGON_WSS_URL"),
            "flashbots_rpc": self.require("FLASHBOTS_RPC_URL"),
            "zerox_api_key": self.require("ZEROX_API_KEY"),
            "zerox_api_url": self.require("ZRX_API_URL"),
            "zerox_gasless_api_url": self.require("ZRX_GASLESS_API_URL"),
        }

    # --------------------------------------------------------------------------
    # DEX Routers + Token addresses
    # --------------------------------------------------------------------------
    def validate_dex_and_tokens(self):
        required = [
            # Routers
            "UNISWAP_V3_ROUTER",
            "QUICKSWAP_ROUTER",
            "SUSHISWAP_ROUTER",
            "BALANCER_VAULT",
            "UNISWAP_V3_QUOTER",
            # Tokens
            "WETH_ADDRESS",
            "USDC_ADDRESS",
            "USDT_ADDRESS",
            "DAI_ADDRESS",
            "WMATIC_ADDRESS",
        ]
        for key in required:
            self.require(key)

    def get_dex_routers(self) -> Dict[str, str]:
        return {
            "uniswap_v3_router": self.require("UNISWAP_V3_ROUTER"),
            "quickswap_router": self.require("QUICKSWAP_ROUTER"),
            "sushiswap_router": self.require("SUSHISWAP_ROUTER"),
            "balancer_vault": self.require("BALANCER_VAULT"),
            "uniswap_v3_quoter": self.require("UNISWAP_V3_QUOTER"),
        }

    def get_token_addresses(self) -> Dict[str, str]:
        return {
            "weth": self.require("WETH_ADDRESS"),
            "usdc": self.require("USDC_ADDRESS"),
            "usdt": self.require("USDT_ADDRESS"),
            "dai": self.require("DAI_ADDRESS"),
            "wmatic": self.require("WMATIC_ADDRESS"),
        }

    # --------------------------------------------------------------------------
    # RPC URLs
    # --------------------------------------------------------------------------
    def get_rpc_url(self, chain: str) -> str:
        if chain not in ["polygon", "ethereum", "base", "arbitrum"]:
            logger.critical(f"❌ Unknown chain requested: {chain}")
            sys.exit(1)
        mapping = {
            "polygon": "POLYGON_RPC_URL",
            "ethereum": "ETHEREUM_RPC_URL",
            "base": "BASE_RPC_URL",
            "arbitrum": "ARBITRUM_RPC_URL",
        }
        return self.require(mapping[chain])

    # --------------------------------------------------------------------------
    # Keys / Wallet
    # --------------------------------------------------------------------------
    def get_private_key(self) -> str:
        return self.require("PRIVATE_KEY")

    # --------------------------------------------------------------------------
    # Validate all
    # --------------------------------------------------------------------------
    def validate_all(self) -> bool:
        self.validate_core()
        self.validate_mev_defense()
        self.validate_dex_and_tokens()
        logger.info("✅ All configuration validated successfully.")
        return True
