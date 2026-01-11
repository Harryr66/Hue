#!/bin/bash
# Setup script for Next.js UI

cd "$(dirname "$0")"

echo "════════════════════════════════════════"
echo "Setting up Hue Next.js UI"
echo "════════════════════════════════════════"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo ""
echo "📦 Installing Python dependencies..."
pip install fastapi uvicorn pydantic --quiet

echo ""
echo "📦 Installing Node.js dependencies..."
cd ui-nextjs
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "✅ Node modules already installed"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run:"
echo "  Terminal 1: python3 api_server.py"
echo "  Terminal 2: cd ui-nextjs && npm run dev"
echo ""
echo "Or use: ./run_nextjs_ui.sh"


