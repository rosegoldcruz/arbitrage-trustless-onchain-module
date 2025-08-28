#!/bin/bash
set -euo pipefail

# Health check script for ATOM Backend API
DOMAIN=${1:-"127.0.0.1:8000"}
PROTOCOL=${2:-"http"}

echo "🏥 Health checking ATOM Backend API at ${PROTOCOL}://${DOMAIN}"

# Basic health check
echo "1. Basic health endpoint..."
curl -fsS "${PROTOCOL}://${DOMAIN}/health" | jq .

# API endpoints
echo "2. MEV latest..."
curl -fsS "${PROTOCOL}://${DOMAIN}/mev/latest" | head -n 5

echo "3. Triangular range..."
curl -fsS "${PROTOCOL}://${DOMAIN}/triangular/range?count=5" | jq .

echo "✅ All health checks passed!"