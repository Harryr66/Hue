#!/bin/bash
# Deploy Next.js UI to Vercel

cd "$(dirname "$0")"

echo "════════════════════════════════════════"
echo "🚀 Deploying Hue UI to Vercel"
echo "════════════════════════════════════════"
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install with: npm install -g vercel"
    exit 1
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "⚠️  Not logged in to Vercel. Run: vercel login"
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Vercel CLI ready"
echo ""

# Check for environment variables file
if [ ! -f ".env.local" ] && [ ! -f ".env" ]; then
    echo "⚠️  No .env.local file found"
    echo "   Create one with: NEXT_PUBLIC_API_URL=your-api-url"
    echo "   Or set environment variables in Vercel dashboard after deployment"
    echo ""
fi

echo "📦 Deploying to Vercel..."
echo ""

# Deploy (first time will ask questions, subsequent deploys use settings)
vercel "$@"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Don't forget to:"
echo "   1. Set NEXT_PUBLIC_API_URL in Vercel dashboard if not in .env.local"
echo "   2. Deploy your Python API server separately (Railway/Render/Fly.io)"
echo "   3. Update environment variables with your production API URL"
echo ""

