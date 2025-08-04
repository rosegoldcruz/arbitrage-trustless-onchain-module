#!/bin/bash

echo "🚀 LAUNCHING FULL AEON + ATOM STACK"
echo "==================================="

cd /root/arbitrage-trustless-onchain-module || exit 1
source venv/bin/activate

# Launch FastAPI backend + AEON core
echo "🔧 Starting backend and AEON logic..."
./run_all_services.sh

# Run orchestrator engine (ATOM + ADOM)
echo ""
echo "🤖 Booting real orchestrator and bots..."
./run_orchestrator.sh

echo ""
echo "✅ All services launched — AEON is live."
