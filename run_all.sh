#!/bin/bash
echo "🌀 Starting ATOM Arbitrage Full Stack..."

# Activate venv
source venv/bin/activate

# Install packages from proper requirements file
pip install -r backend/requirements.txt

# Run backend systems
mkdir -p logs

nohup python3 backend/startup.py > logs/startup.log 2>&1 &
nohup python3 backend/real_orchestrator.py > logs/orchestrator.log 2>&1 &
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &

echo "✅ All systems running in background"
echo "🔍 Check logs in ./logs/"
