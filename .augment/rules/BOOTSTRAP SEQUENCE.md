---
type: "always_apply"
---

✅ BOOTSTRAP SEQUENCE
```bash
pnpm install
cp .env.example .env.local
# Populate all required secrets
pnpm run dev (frontend)
python agents/atom/main.py (backend test)
```