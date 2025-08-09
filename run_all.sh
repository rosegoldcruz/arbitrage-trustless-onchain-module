#!/bin/bash
echo "🚀 ATOM - LEAN MEAN ARBITRAGE MACHINE"
echo "====================================="

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create logs directory
mkdir -p logs

echo "🔥 Starting ATOM Core Systems..."

# Start FastAPI Backend (Dashboard API)
echo "📡 Starting Dashboard API..."
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!

# Start Real Orchestrator (Master Bot Controller)
echo "🧠 Starting Master Orchestrator..."
nohup python3 backend/real_orchestrator.py > logs/orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!

# Start Startup Services (Bot Initialization)
echo "⚡ Starting Bot Services..."
nohup python3 backend/startup.py > logs/startup.log 2>&1 &
STARTUP_PID=$!

echo ""
echo "✅ ATOM SYSTEMS ONLINE!"
echo "====================================="
echo "🌐 Dashboard API: https://api.aeoninvestmentstechnologies.com"
echo "📊 API Docs: https://api.aeoninvestmentstechnologies.com/docs"
echo "📈 Health Check: https://api.aeoninvestmentstechnologies.com/health"
echo ""
echo "🤖 Process IDs:"
echo "   API: $API_PID"
echo "   Orchestrator: $ORCHESTRATOR_PID"
echo "   Startup: $STARTUP_PID"
echo ""
echo "🔍 Monitor logs: tail -f logs/*.log"
echo "🛑 Stop all: pkill -f 'uvicorn|orchestrator|startup'"
