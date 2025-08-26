#!/usr/bin/env python3
"""
Environment Validator
Delegates to SecureConfig as single source of truth.
"""

import sys
import logging
from config.secure_config import SecureConfig

logger = logging.getLogger("env_validation")
logging.basicConfig(level=logging.INFO)


def main():
    print("🔍 Validating environment configuration...")
    try:
        cfg = SecureConfig()
        cfg.validate_all()
        print("✅ All environment variables validated successfully")
        print("🚀 Environment ready for ATOM arbitrage system")
        sys.exit(0)
    except SystemExit as e:
        # SecureConfig already logs errors
        print("❌ Environment validation failed")
        sys.exit(e.code if isinstance(e.code, int) else 1)
    except Exception as e:
        logger.exception("Unexpected error during env validation")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
