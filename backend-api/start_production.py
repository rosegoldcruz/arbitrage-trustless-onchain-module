#!/usr/bin/env python3
"""
Production startup validation for ATOM arbitrage backend.
Runs config, RPC, Redis, and contract health checks before launch.
"""

import logging
import sys
import redis
from web3 import Web3
from config.secure_config import SecureConfig
from backend_bots.rpc_manager import RPCManager

logger = logging.getLogger("start_production")
logging.basicConfig(level=logging.INFO)

def main():
    logger.info("🚀 ATOM Production Startup")
    cfg = SecureConfig()
    cfg.validate_all()

    # Wallet
    private_key = cfg.get_private_key()
    from eth_account import Account
    acct = Account.from_key(private_key)
    logger.info(f"✅ Wallet loaded: {acct.address}")

    # RPC connectivity
    rpc = RPCManager()
    for chain in ["polygon", "ethereum", "base", "arbitrum"]:
        try:
            w3 = rpc.get_web3(chain)
            block = w3.eth.block_number
            logger.info(f"✅ {chain} RPC healthy | latest block = {block}")
        except Exception as e:
            logger.error(f"❌ {chain} RPC check failed: {e}")
            sys.exit(1)

    # Redis connectivity
    try:
        redis_url = cfg.require("REDIS_URL")
        r = redis.from_url(redis_url)
        pong = r.ping()
        if pong:
            logger.info(f"✅ Redis connected: {redis_url}")
        else:
            raise Exception("Ping failed")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        sys.exit(1)

    # Flashloan contract health check
    try:
        flashloan_contract = cfg.require("ATOM_CONTRACT_ADDRESS")
        w3 = rpc.get_web3("polygon")
        code = w3.eth.get_code(Web3.to_checksum_address(flashloan_contract))
        if code == b"":
            raise Exception("No bytecode found at contract address")
        logger.info(f"✅ Flashloan contract at {flashloan_contract} is deployed")
    except Exception as e:
        logger.error(f"❌ Contract check failed: {e}")
        sys.exit(1)

    logger.info("🎯 All production checks passed. Backend ready to launch.")

if __name__ == "__main__":
    main()
