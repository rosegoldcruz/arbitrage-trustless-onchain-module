#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

echo "Starting ATOM bot..."
nohup python3 ATOM.py > logs/atom.log 2>&1 &

echo "Starting ADOM engine..."
nohup python3 adom_engine.py > logs/adom.log 2>&1 &

echo "Starting Master Orchestrator..."
nohup python3 master_agent_orchestrator.py > logs/orchestrator.log 2>&1 &

echo "✅ All agents launched in background"
