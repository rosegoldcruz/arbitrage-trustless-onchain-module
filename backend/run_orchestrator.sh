#!/bin/bash

# Real Arbitrage Orchestrator Startup Script
# No fake quantum bullshit - just working bot coordination

echo "🚀 REAL ARBITRAGE ORCHESTRATOR STARTUP"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "orchestrator_config.json" ]; then
    echo "❌ orchestrator_config.json not found"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required, found $python_version"
    exit 1
fi

# Check Node.js for ADOM bot
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found - required for ADOM bot"
    exit 1
fi

node_version=$(node --version)
echo "✅ Node.js version: $node_version"

# Install Python dependencies if needed
echo "🔧 Checking Python dependencies..."
pip3 install -q requests psutil

# Install Node.js dependencies for ADOM bot
if [ -f "bots/package.json" ]; then
    echo "🔧 Installing Node.js dependencies..."
    cd bots
    npm install --silent
    cd ..
fi

# Create required directories
echo "📁 Creating communication directories..."
mkdir -p comm/commands
mkdir -p comm/results
mkdir -p comm/heartbeats
mkdir -p logs

# Set environment variables if .env exists
if [ -f ".env" ]; then
    echo "🔑 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if bots exist
if [ ! -f "bots/ATOM.py" ]; then
    echo "❌ ATOM.py bot not found"
    exit 1
fi

if [ ! -f "bots/ADOM.js" ]; then
    echo "❌ ADOM.js bot not found"
    exit 1
fi

echo "✅ All prerequisites checked"
echo ""
echo "🎯 Starting Real Orchestrator..."
echo "   - ATOM.py (Python arbitrage bot)"
echo "   - ADOM.js (Node.js MEV bot)"
echo "   - Real DEX API scanning"
echo "   - File-based bot communication"
echo "   - SQLite performance tracking"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the orchestrator
python3 start_orchestrator.py

echo ""
echo "👋 Orchestrator shutdown complete"
