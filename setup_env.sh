#!/bin/bash
# Setup script to create .env file from template

echo "=== Setting up .env file ==="

if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Create .env file
cat > .env << 'EOF'
# WrappedGrok API Keys
# Get your Grok API key from: https://console.x.ai
GROK_API_KEY=your-grok-api-key-here

# Get your SerpAPI key from: https://serpapi.com/
SERPAPI_KEY=your-serpapi-key-here

# Optional: ElevenLabs API key for better TTS voice (get from https://elevenlabs.io/)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
EOF

echo "✅ Created .env file"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file: nano .env (or use your preferred editor)"
echo "2. Replace 'your-grok-api-key-here' with your actual Grok API key"
echo "3. Replace 'your-serpapi-key-here' with your actual SerpAPI key"
echo "4. (Optional) Replace 'your-elevenlabs-api-key-here' with your ElevenLabs API key for better voice"
echo ""
echo "Get your API keys:"
echo "  - Grok: https://console.x.ai"
echo "  - SerpAPI: https://serpapi.com/"
echo "  - ElevenLabs (optional): https://elevenlabs.io/ - for natural-sounding TTS voice"

