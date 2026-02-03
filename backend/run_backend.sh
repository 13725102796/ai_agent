#!/bin/bash
PORT=8000

# Function to check and kill process on port
check_and_kill_port() {
    local pid=$(lsof -t -i:$PORT)
    if [ -n "$pid" ]; then
        echo "⚠️  Port $PORT is occupied by PID $pid. Killing it..."
        kill -9 $pid
        echo "✅  Process killed."
    else
        echo "✅  Port $PORT is free."
    fi
}

echo "🚀 Preparing to start Backend Server..."
check_and_kill_port

echo "🔥 Starting Uvicorn server..."
# Using --reload for development allows auto-restart on code changes
uvicorn main:app --port $PORT --reload
