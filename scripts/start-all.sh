#!/bin/bash
# 🚀 ATOM/AEON Complete System Startup Script (Linux/Mac)
# Starts frontend, backend, and bots in the correct order

echo "🧬 ATOM/AEON System Startup"
echo "=============================="

# Check if required tools are installed
echo "🔍 Checking dependencies..."

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js not found. Please install Node.js"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
elif command -v python &> /dev/null; then
    echo "✅ Python: $(python --version)"
else
    echo "❌ Python not found. Please install Python"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    echo "✅ npm: $(npm --version)"
else
    echo "❌ npm not found. Please install Node.js"
    exit 1
fi

echo ""
echo "🚀 Starting ATOM/AEON System..."

# Start Backend (FastAPI)
echo "📡 Starting Backend..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start Frontend (Next.js)
echo "🌐 Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 10

# Start ATOM Bot (Node.js)
echo "🤖 Starting ATOM Bot..."
cd bots
npm run atom &
ATOM_PID=$!

# Start ADOM Engine (Python)
echo "🐍 Starting ADOM Engine..."
python3 adom_engine.py &
ADOM_PID=$!
cd ..

echo ""
echo "✅ ATOM/AEON System Started!"
echo "=============================="
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend: http://128.199.95.97:8000"
echo "📊 API Docs: http://128.199.95.97:8000/docs"
echo "📈 Monitor: http://localhost:3000/monitor"
echo ""
echo "🤖 Process IDs:"
echo "   Backend: $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo "   ATOM Bot: $ATOM_PID"
echo "   ADOM Engine: $ADOM_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and kill all processes
trap 'echo "🛑 Stopping all services..."; kill $BACKEND_PID $FRONTEND_PID $ATOM_PID $ADOM_PID; exit' INT

# Wait for all processes
wait
