#!/bin/bash
# Script to help add Firebase service account key path to .env

echo "════════════════════════════════════════"
echo "🔑 Firebase Service Account Key Setup"
echo "════════════════════════════════════════"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating it..."
    touch .env
fi

# Get the path to the JSON file
echo "📁 Where did you save the Firebase service account JSON file?"
echo "   (It should be in this directory: /Users/harry/Desktop/HUE/)"
echo ""
read -p "Enter the full path to the JSON file: " json_path

# Verify file exists
if [ ! -f "$json_path" ]; then
    echo "❌ File not found: $json_path"
    echo ""
    echo "Please:"
    echo "1. Save the JSON file in your project directory"
    echo "2. Run this script again"
    exit 1
fi

# Check if FIREBASE_SERVICE_ACCOUNT_PATH already exists in .env
if grep -q "FIREBASE_SERVICE_ACCOUNT_PATH" .env; then
    echo ""
    echo "⚠️  FIREBASE_SERVICE_ACCOUNT_PATH already exists in .env"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old line
        sed -i '' '/FIREBASE_SERVICE_ACCOUNT_PATH/d' .env
        echo "FIREBASE_SERVICE_ACCOUNT_PATH=$json_path" >> .env
        echo "✅ Updated FIREBASE_SERVICE_ACCOUNT_PATH in .env"
    else
        echo "Keeping existing value"
    fi
else
    # Add to .env
    echo "" >> .env
    echo "# Firebase Service Account Key" >> .env
    echo "FIREBASE_SERVICE_ACCOUNT_PATH=$json_path" >> .env
    echo "✅ Added FIREBASE_SERVICE_ACCOUNT_PATH to .env"
fi

echo ""
echo "════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Install firebase-admin: pip install firebase-admin"
echo "2. Test it: python3 api_server.py"
echo "   You should see: ✅ Using Firebase Firestore"
echo ""


