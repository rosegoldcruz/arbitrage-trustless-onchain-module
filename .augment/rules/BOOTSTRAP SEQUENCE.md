---
type: "agent_requested"
description: "Example description"
---
# 📦 1. Install dependencies (always use pnpm)
pnpm install

# 🛠 2. Copy environment file and configure secrets
cp .env.example .env.local
# 👉 Edit `.env.local` and add API keys, contract addresses, etc.

# 🌐 3. Launch frontend (Vercel local preview)
pnpm run dev

# 🔁 4. Start backend bots + API server
python backend/startup.py     # Master orchestrator
# or (if using combined launch)
./run_all.sh                  # Full production system

# ✅ 5. Confirm system is alive
# - http://localhost:3000       → Frontend
# - http://localhost:8000/docs  → FastAPI backend
# - Bots logging to terminal or logs/

# 🧠 6. Deploy frontend to Vercel (production)
# - Commit + push main
# - Vercel auto-deploys via GitHub

# 🌐 7. Point frontend to live backend
# Example: Set API_URL = https://api.aeoninvestmentstechnologies.com

# 🎯 Done. You're live.
