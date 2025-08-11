#!/bin/bash

# LinkedIn Android Poster - Startup Script
echo "🚀 Starting LinkedIn Android Poster"
echo "======================================"

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    echo "❌ Please run this script from the linkedin-android-poster directory"
    exit 1
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting FastAPI backend server..."
    cd backend
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started (PID: $BACKEND_PID)"
}

# Function to start frontend  
start_frontend() {
    echo "⚛️  Starting React frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [[ ! -z "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    if [[ ! -z "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Start both servers
start_backend
sleep 3
start_frontend

echo ""
echo "🎉 Application started successfully!"
echo "======================================"
echo "📊 Dashboard: http://localhost:5173"
echo "🔗 Backend API: http://127.0.0.1:8000"
echo "📖 API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait