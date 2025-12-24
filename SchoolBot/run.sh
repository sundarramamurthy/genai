#!/bin/bash

# Ensure we are in the project directory
cd "$(dirname "$0")"

# Check for venv
if [ ! -d "venv" ]; then
    echo "Error: 'venv' directory not found. Please run ./start.sh first to setup."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping SchoolBot..."
    kill -- -$$ 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT

echo "🚀 Starting SchoolBot Server..."
python app.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

echo "🚇 Starting Ngrok Tunnel..."
python start_tunnel.py &
TUNNEL_PID=$!

echo ""
echo "✅ SchoolBot is running!"
echo "👉 Copy the Ngrok URL above and update your Twilio Sandbox settings."
echo "⌨️  Press Ctrl+C to stop everything."
echo ""

# Wait for processes
wait
