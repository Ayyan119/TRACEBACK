#!/bin/bash
# ==============================================================================
# TRACEBACK AI — Unified Startup Script
# Starts both FastAPI Backend (port 8000) and Next.js Frontend (port 3000) simultaneously
# ==============================================================================

echo "🚀 Starting TRACEBACK AI Engine..."

# 1. Start FastAPI Backend in background
echo "📦 Launching FastAPI Backend on http://localhost:8000..."
(cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

# 2. Start Next.js Frontend
echo "💻 Launching Next.js Frontend on http://localhost:3000..."
(source ~/.nvm/nvm.sh && nvm use 22 && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "✅ TRACEBACK is running!"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend:  http://localhost:8000/api/v1/health"
echo "   - Press Ctrl+C to stop both servers."
echo ""

# Handle graceful shutdown on Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" EXIT INT TERM

wait
