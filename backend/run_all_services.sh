#!/bin/bash

echo "🚀 Starting ATOM + AEON Backend Stack..."

# Activate virtualenv
cd /root/arbitrage-trustless-onchain-module
source venv/bin/activate

# Launch FastAPI backend
echo "✅ Launching FastAPI backend..."
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Launch AEON startup logic
echo "✅ Starting AEON system logic (startup.py)..."
python3 backend/startup.py &

# Launch orchestrator bot
echo "✅ Booting real orchestrator (real_orchestrator.py)..."
python3 backend/real_orchestrator.py &

echo "🟢 All core services launched in background."
