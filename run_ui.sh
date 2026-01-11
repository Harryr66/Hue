#!/bin/bash
# Quick script to run the Streamlit UI

echo "=== Starting WrappedGrok UI ==="
echo ""
echo "Make sure:"
echo "1. Virtual environment is activated: source venv/bin/activate"
echo "2. Dependencies are installed: pip install -r requirements.txt"
echo "3. .env file has your API keys"
echo ""
echo "Starting Streamlit app..."
echo "The UI will open in your browser automatically"
echo "Press Ctrl+C to stop"
echo ""

streamlit run app.py


