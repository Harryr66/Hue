#!/bin/bash
# Run the Next.js UI with Python API server

cd "$(dirname "$0")"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "════════════════════════════════════════"
echo "Starting Hue Next.js UI"
echo "════════════════════════════════════════"
echo ""

echo "🚀 Starting Python API server on port 8000..."
python3 api_server.py &
API_PID=$!

echo "⏳ Waiting for API server to start..."
sleep 4

# Check if API server started
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ API server failed to start. Check if port 8000 is available."
    exit 1
fi

echo "✅ API server running (PID: $API_PID)"
echo ""
echo "🚀 Starting Next.js UI on port 9002..."
echo ""

cd ui-nextjs
npm run dev

# Cleanup on exit
trap "echo ''; echo 'Stopping servers...'; kill $API_PID 2>/dev/null; exit" INT TERM EXIT

