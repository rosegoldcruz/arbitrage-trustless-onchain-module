---
type: "always_apply"
---

🧠 RULES FOR ATOM-BASED ARBITRAGE ENGINE
- All bots must run as 24/7 daemons (PM2 or systemd)
- All arbitrage math validated against:
  • Balancer weighted pool math
  • Curve StableSwap formulas
  • 0x, Uniswap, 1inch API spreads
- All routes must enforce spreadBps > 23bps
- Token path examples (Base Sepolia): WETH → USDC → GHO → DAI
- Smart contracts must include:
  • FlashLoanExecutor
  • Dynamic DEX router detection
  • Slippage, gas, and ROI simulation logic