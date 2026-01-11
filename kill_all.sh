#!/bin/bash
# Kill all Hue-related processes

echo "Killing all Hue processes..."

# Kill processes on specific ports
for port in 8000 8501 9002; do
    lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null
done

# Kill by process name
pkill -f "streamlit" 2>/dev/null
pkill -f "api_server" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null

echo "✅ All processes killed. Terminal should be free now."


