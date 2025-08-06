---
type: "always_apply"
---

# 🧪 VALIDATION & DEPLOYMENT (PRODUCTION-ONLY MODE)

ATOM never runs in testing mode.  
This system is **production-first, profit-locked, and money-motivated.**

All code, all logic, all executions happen **live** — or not at all.

---

## ✅ EXECUTION REQUIREMENTS (NO EXCEPTIONS)

- All trades must be simulated before execution
  - ✅ ROI after gas must be positive
  - ✅ Slippage per leg must be within 0.5%
  - ✅ SpreadBps must exceed 23bps

- Every trade simulation is a **live route**, not a test.
  - No “dry-run” mode allowed
  - Simulation is for validation — not for preview

- Every trade must use production-calibrated endpoints:
  - `/trigger` — spot arb
  - `/deploy` — initialize agents
  - `/flash-loan` — ADOM logic trigger

- All executions must be logged to Supabase:
  - ✅ Strategy ID
  - ✅ ROI %
  - ✅ Slippage %
  - ✅ Execution status
  - ✅ Tx hash

---

## 🔐 DEPLOYMENT RULES

- ✅ Smart contracts must be verified on Basescan
- ✅ Token approvals must be granted before trade execution
- ✅ Health check endpoints (`/health`) must return 200 OK before allowing any bot to run

---

## 🚫 HARD BANS

- ❌ No testnets beyond Base Sepolia
- ❌ No `--dry-run` parameters allowed anywhere in the bot stack
- ❌ No deployments using mock tokens, fake pairs, or staging configs
- ❌ No sandboxed or simulated arbitrage logic

---

## 💵 PHILOSOPHY

> We get money.  
> We are money.  
> But we love humanity — and that means we ship real tools that work for real people.

This engine exists to move real capital — not to pretend, not to demo, and not to sandbox.

There is **only production.**
There is **only execution.**
There is **only ATOM.**
