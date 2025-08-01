"""
ATOM Backend Routers Package
Arbitrage Trustless On-Chain Module

This package contains all FastAPI routers for the ATOM arbitrage system.
Each router handles specific functionality and endpoints.
"""

# Import all router modules to make them available when importing from this package
try:
    # Use absolute imports to avoid relative import issues
    import agent
    import analytics
    import arbitrage
    import contact
    import deploy
    import flashloan
    import health
    import institutional
    import parallel_dashboard
    import risk
    import stats
    import telegram
    import tokens
    import trades
    import zeroex

    # List all available routers for easy reference
    __all__ = [
        'agent',
        'analytics',
        'arbitrage',
        'contact',
        'deploy',
        'flashloan',
        'health',
        'institutional',
        'parallel_dashboard',
        'risk',
        'stats',
        'telegram',
        'tokens',
        'trades',
        'zeroex'
    ]

    print("SUCCESS: All ATOM routers imported successfully")

except ImportError as e:
    print(f"ERROR: Router import error: {e}")
    # Re-raise the error so it's visible during startup
    raise
