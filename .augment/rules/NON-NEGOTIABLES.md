---
type: "always_apply"
---

# 🚫 NON-NEGOTIABLE EXECUTION RULES (AUGMENT ONLY)

These rules are hardwired into the ATOM system.  
They are for the executor only. No assumptions, no exceptions.

- ❌ Never use `npm install` — always use `pnpm` to preserve dependency integrity
- ❌ Never commit any `.env*` file or API keys under any name, format, or folder
- ❌ Never deploy frontend to Vercel unless all pages pass:
  - ✅ TypeScript strict mode
  - ✅ ESLint (no warnings or errors)
  - ✅ Zod schema validation (end-to-end)
- ❌ Never allow a trade or route to execute if the arbitrage simulation fails or returns incomplete data
- ❌ Never launch or maintain bot processes outside daemon protection (PM2 or systemd only)

These are mandatory in all environments.  
Augment is not allowed to bypass, ignore, rewrite, or relax any of these rules.
