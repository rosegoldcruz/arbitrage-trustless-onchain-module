---
type: "always_apply"
---

📊 DASHBOARD RULES (ATOM UI v2)

- Display real-time bot status:
  • Active / Inactive / Failed
  • Live heartbeat every 5 sec
- Trigger execution manually:
  • Flashloan or spot
  • JSON payloads displayed
  • Log output visualized (stdout)
- Show strategy modes:
  • Flash Loan, MEV Defense, Triangle, Spread
  • Mode selector dropdown
- Wallet connection (Clerk + injected Web3):
  • Use Clerk auth + injected Metamask for tx signing
  • No Web3Auth modal — must reflect branding
- Show real-time trade metrics:
  • spreadBps %
  • ROI % (after gas)
  • Slippage risk estimate
- Visual blocks for:
  • Trade paths (token A → B → C)
  • Gas simulator (live chain or estimated)
  • Execution confirmation (tx hash + status)
- Toggle auto-mode:
  • Checkbox: “Enable Auto-Arbitrage”
  • Show cooldown settings (min X seconds between trades)
