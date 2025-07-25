---
type: "always_apply"
---

🧪 VALIDATION & TESTING
- Simulate all trades before execution (dry-run mode)
- All bot endpoints hit `/trigger`, `/deploy`, `/flash-loan`
- Logs sent to Supabase audit table
- All deployments require:
  • Contracts verified
  • Token pair approval
  • Health check API tests