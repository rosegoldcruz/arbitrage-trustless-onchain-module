---
type: "always_apply"
---

🧠 RULES FOR ATOM-BASED ARBITRAGE ENGINE (v2)

- All bots must run as 24/7 daemons (PM2 or systemd)
- Arbitrage math must be validated against:
  • Balancer weighted pool math (asymmetric pools)
  • Curve StableSwap virtual price formulas
  • 0x, Uniswap v3, and 1inch spreads (real-time)
- All routes must enforce: 
  • spreadBps > 23bps 
  • ROI after gas > 0.25%
- Flashloan and spot routes must simulate:
  • Virtual price
  • Slippage per leg
  • Gas per route
  • Net ROI across full path
- Token path support (Base Sepolia):
  • WETH → USDC → GHO → DAI
  • GHO → DAI → USDC → WETH
- Smart contracts must support:
  • FlashLoanExecutor.sol (Base-compatible)
  • Dynamic DEX router detection (per trade)
  • Modular AEONMath.sol logic
- All strategies must include:
  • Pre-trade simulation
  • Post-trade audit logging
  • Telegram or dashboard notifications
- Execution modes:
  • ATOM = Spot-only arb (non-flashloan)
  • ADOM = Flashloan multi-hop arb
  • ARCHANGEL = Emergency fallback execution agent (optional)
