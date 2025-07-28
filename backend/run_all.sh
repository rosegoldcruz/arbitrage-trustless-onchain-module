#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

echo "🔁 Starting ADOM Flashloan Engine..."
nohup python3 adom_engine.py > logs/adom_engine.log 2>&1 &

echo "📡 Starting Arbitrage Spread Watcher..."
nohup node arb_watcher.js > logs/arb_watcher.log 2>&1 &

echo "🧠 Starting AEON Orchestrator Core (Juiced)..."
nohup python3 juiced_up_orchestrator.py > logs/orchestrator.log 2>&1 &

echo "📬 Starting Telegram Alert Service..."
nohup python3 telegram_notifier.py > logs/telegram.log 2>&1 &

echo "✅ All AEON agents launched in background"
