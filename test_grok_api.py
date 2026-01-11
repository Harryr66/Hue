#!/usr/bin/env python3
"""
Test script to diagnose Grok API connection issues.
"""

import os
import sys
from pathlib import Path

# Try to load from .env file
env_path = Path(__file__).parent / '.env'
print(f"📁 Looking for .env file at: {env_path}")
print(f"   File exists: {env_path.exists()}")

try:
    from dotenv import load_dotenv
    # Force load from .env file, overriding any shell environment variables
    result = load_dotenv(env_path, override=True)
    if result:
        print(f"✅ Loaded .env file using python-dotenv (override=True)")
    else:
        print(f"⚠️  dotenv.load_dotenv() returned False - file may be empty or keys not found")
except ImportError:
    print("⚠️  python-dotenv not installed, manually loading .env file...")
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value  # This overwrites existing env vars
                        print(f"   Loaded: {key}={value[:10]}... (from line {line_num}, override=True)")
            print("✅ Loaded .env file manually")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("❌ .env file not found")

import requests

def test_grok_api():
    print("\n🔍 Checking for GROK_API_KEY...")
    
    # Also check what's directly in .env file
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        print(f"\n📄 Reading .env file directly...")
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GROK_API_KEY=') and not line.startswith('#'):
                        key_from_file = line.split('=', 1)[1].strip()
                        print(f"   Key in .env file: {key_from_file[:15]}...{key_from_file[-10:] if len(key_from_file) > 25 else ''} (length: {len(key_from_file)})")
                        break
        except Exception as e:
            print(f"   ⚠️  Could not read .env file: {e}")
    
    grok_api_key = os.getenv('GROK_API_KEY')
    
    if grok_api_key:
        print(f"   Key from environment: {grok_api_key[:15]}...{grok_api_key[-10:] if len(grok_api_key) > 25 else ''} (length: {len(grok_api_key)})")
    else:
        print("   ❌ Key not found in environment")
    
    if not grok_api_key:
        print("❌ ERROR: GROK_API_KEY not set")
        print("\n📝 To fix:")
        print("1. Edit .env file: nano .env")
        print("2. Replace 'your-grok-api-key-here' with your actual API key")
        print("3. Get your API key from: https://console.x.ai")
        return False
    
    # Check for placeholder values
    placeholder_patterns = [
        'your-grok-api-key-here',
        'your-grok',
        'your-xai',
        'placeholder',
        'example',
        'xxx',
        'test'
    ]
    
    key_lower = grok_api_key.lower()
    is_placeholder = any(pattern in key_lower for pattern in placeholder_patterns) or len(grok_api_key) < 20
    
    if is_placeholder:
        print("❌ ERROR: GROK_API_KEY appears to be a placeholder or too short")
        print(f"   Current value: {grok_api_key[:15]}...")
        print("\n📝 To fix:")
        print("1. Get your API key from: https://console.x.ai")
        print("   - Sign in or create an account")
        print("   - Go to API Keys section")
        print("   - Create a new API key")
        print("2. Edit .env file: nano .env")
        print("3. Replace the placeholder with your actual key:")
        print("   GROK_API_KEY=xai-your-actual-api-key-here")
        print("4. Make sure there are no spaces or quotes around the key")
        return False
    
    # Show masked API key for confirmation
    if len(grok_api_key) > 15:
        masked = f"{grok_api_key[:5]}...{grok_api_key[-5:]}"
    else:
        masked = f"{grok_api_key[:3]}...{grok_api_key[-3:]}"
    print(f"✅ API Key found: {masked} (length: {len(grok_api_key)} chars)")
    
    # Test different endpoints and models (grok-3 is the current model)
    api_url = "https://api.x.ai/v1/chat/completions"
    models = ["grok-3", "grok-beta", "grok-2", "grok-vision-beta", "grok"]
    
    headers = {
        "Authorization": f"Bearer {grok_api_key}",
        "Content-Type": "application/json"
    }
    
    test_message = {
        "model": None,  # Will be set for each attempt
        "messages": [
            {"role": "user", "content": "Say hello"}
        ]
    }
    
    print(f"\nTesting API endpoint: {api_url}")
    print("=" * 60)
    
    for model in models:
        print(f"\n🔍 Testing model: {model}")
        test_message["model"] = model
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=test_message,
                timeout=10
            )
            
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"  ✅ SUCCESS! Model '{model}' works!")
                print(f"  Response: {content[:100]}...")
                return True
            elif response.status_code == 401:
                print(f"  ❌ Unauthorized (401): Invalid API key")
                print(f"  Response: {response.text[:200]}")
                return False
            elif response.status_code == 400:
                error_text = response.text
                print(f"  ⚠️  Bad Request (400)")
                print(f"  Response: {error_text[:300]}")
                if "model" in error_text.lower() and "invalid" in error_text.lower():
                    print(f"  → Model '{model}' not available, trying next...")
                    continue
                else:
                    return False
            elif response.status_code == 404:
                print(f"  ❌ Not Found (404): Endpoint doesn't exist")
                print(f"  Response: {response.text[:200]}")
                return False
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ Connection Error: Cannot reach {api_url}")
            print(f"  Error: {e}")
            return False
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout: API request took too long")
            return False
        except Exception as e:
            print(f"  ❌ Unexpected Error: {type(e).__name__}: {e}")
            return False
    
    print("\n❌ All models failed. Check your API key and account status at https://console.x.ai")
    return False

if __name__ == "__main__":
    print("=== Grok API Diagnostic Test ===\n")
    success = test_grok_api()
    sys.exit(0 if success else 1)

