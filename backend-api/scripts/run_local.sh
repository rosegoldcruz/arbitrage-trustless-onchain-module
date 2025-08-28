#!/bin/bash
set -euo pipefail

# Local development runner for ATOM Backend API
echo "🚀 Starting ATOM Backend API in local development mode..."

# Check if .env.production exists
if [[ ! -f ".env.production" ]]; then
    echo "❌ Missing .env.production file"
    echo "Please create .env.production with required environment variables"
    exit 1
fi

# Load environment variables
echo "📋 Loading environment from .env.production..."
set -a
source ./.env.production
set +a

# Override for local development
export ENV=development
export REDIS_HOST=${REDIS_HOST:-127.0.0.1}
export REDIS_PORT=${REDIS_PORT:-6379}
export REDIS_DB=${REDIS_DB:-0}
export STREAM_NAMESPACE=${STREAM_NAMESPACE:-atom}

# Start the server
echo "🎯 Starting uvicorn server..."
uvicorn backend_api.main:app --reload --loop uvloop --http h11 --host 127.0.0.1 --port 8000