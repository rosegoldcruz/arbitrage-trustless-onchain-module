---
type: "always_apply"
---

S# ⚙️ RULES FOR ATOM-BASED ARBITRAGE ENGINE (v3)

This is the canonical rulebook for all arbitrage logic in the ATOM system.  
These rules are non-negotiable, strictly enforced, and universally applied across all agents.

---

## 🛠 BOT & DAEMON REQUIREMENTS

- All arbitrage agents must run as **24/7 daemons** (PM2 or systemd only)
- No bots may be run manually except through dashboard triggers
- **Auto-restart** and **health checks** must be enforced on crash

---

## 🧮 MATH VALIDATION REQUIREMENTS

All arbitrage logic must be validated against:

- ✅ **Balancer weighted pool math** (including asymmetric 80/20, 98/2 pools)
- ✅ **Curve StableSwap virtual price invariant**
- ✅ **DEX spread APIs**:
  - 0x Swap API
  - Uniswap v3 quote endpoint
  - 1inch Aggregator spreads

Redundant checks are expected.  
Validation must be applied **before every simulated trade.**

---

## 💸 SPREAD, ROI, AND SLIPPAGE THRESHOLDS

- Minimum `spreadBps` = **23bps**
- Minimum projected **ROI after gas** = **0.25%**
- Slippage must be calculated **per route leg**, not globally
- Route is invalid if:
  - ROI ≤ gas cost
  - Slippage exceeds 0.5%
  - Spread ≤ 23bps

---

## 🧪 SIMULATION REQUIREMENTS

Every strategy — spot or flashloan — must simulate:

- Curve or Balancer **virtual price**
- Slippage **per hop**
- Estimated gas usage **per route**
- Net ROI = `(output - input - gas) / input`

Simulation is required **before execution**.  
Trades without simulation are discarded.

---

## 🔗 SUPPORTED TOKEN ROUTES (Base Sepolia)

- `WETH → USDC → GHO → DAI`
- `GHO → DAI → USDC → WETH`
- `USDC → DAI → GHO → WETH`
- Expandable via config — default to 4-token triangular cycles

---

## 🧾 CONTRACT REQUIREMENTS

Each trade must pass through smart contracts with:

- ✅ `FlashLoanExecutor.sol` (Base-compatible)
- ✅ Dynamic DEX router detection (Uniswap, Balancer, Curve)
- ✅ Full modular logic from `AEONMath.sol`
- ✅ Route execution via flashloan or spot — depending on agent

---

## 🚨 STRATEGY STRUCTURE (MANDATORY)

Each trade strategy (spot or flashloan) must include:

- 🔁 **Pre-trade simulation** (ROI, slippage, gas)
- 🧾 **Post-trade audit log** to Supabase (status, tx hash, ROI)
- 🔔 **Dashboard notification only** — Telegram is disabled

---

## 🚦 EXECUTION MODES

- **ATOM** = Spot arbitrage only (WETH-based pairs, multi-hop)
- **ADOM** = Flashloan-capable, high-gas multi-leg arbitrage
- **ARCHANGEL** = Emergency fallback executor (only activates if ATOM & ADOM fail)

Agents may never switch modes unless explicitly configured to.

---

## 🔐 FINAL ENFORCEMENTS

- ❌ No Telegram. All alerts, trade feedback, and status logs must be sent to the dashboard.
- ❌ No test routes. All strategies must simulate before going live.
- ❌ No soft thresholds. All logic must hard reject trades below system thresholds.
- ✅ Only production deployments. No staging forks allowed in arbitrage logic.
- ✅ Every route must be monitored via backend `/health` endpoint and Supabase sync.

---

🔒 All rul
