#!/usr/bin/env python3
"""
Example usage of WrappedGrok for voice chat.
Run this script to start a voice conversation with the AI.
"""

import os
from pathlib import Path

# Try to load from .env file (optional)
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    # Fallback: manually parse .env file
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ Loaded .env file manually (python-dotenv not installed)")
        except Exception as e:
            print(f"⚠️  Could not load .env file manually: {e}")
    else:
        print("Note: python-dotenv not installed. Install with: pip install python-dotenv")
        print("You can still use environment variables: export GROK_API_KEY='your-key'")

from wrapped_grok import WrappedGrok

def main():
    # Load environment variables from .env file if available
    if DOTENV_AVAILABLE:
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path, override=True)  # Force override shell env vars
            print(f"✅ Loaded environment variables from {env_path} (override=True)")
        else:
            print(f"⚠️  .env file not found at {env_path}")
            print("Run ./setup_env.sh to create .env file, or set environment variables:")
            print("  export GROK_API_KEY='your-key'")
            print("  export SERPAPI_KEY='your-key'")
    else:
        # Fallback: manually parse .env file and override
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()  # Overwrites existing
                print(f"✅ Loaded .env file manually (override=True)")
            except Exception as e:
                print(f"⚠️  Could not load .env file: {e}")
        else:
            print("⚠️  python-dotenv not installed and .env file not found")
    
    # Get API keys from environment variables
    grok_api_key = os.getenv('GROK_API_KEY')
    serpapi_key = os.getenv('SERPAPI_KEY')
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')  # Optional - for better TTS
    
    # Check for placeholder API keys
    placeholder_patterns = ['your-grok', 'your-xai', 'your-serpapi', 'placeholder', 'example']
    
    if not grok_api_key or any(pattern in grok_api_key.lower() for pattern in placeholder_patterns):
        print("\n❌ ERROR: GROK_API_KEY not set or still using placeholder value")
        print(f"   Current value: {grok_api_key[:30] if grok_api_key else 'NOT SET'}...")
        print("\n📝 To fix:")
        print("1. Get your API key from: https://console.x.ai")
        print("   - Sign in or create an account")
        print("   - Navigate to 'API Keys' section")
        print("   - Click 'Create API Key'")
        print("   - Copy the key (it's shown only once!)")
        print("2. Edit .env file:")
        print("   nano .env")
        print("3. Replace the placeholder:")
        print("   GROK_API_KEY=xai-your-actual-api-key-here")
        print("   (No quotes, no spaces around the = sign)")
        print("4. Save and try again")
        return
    
    if not serpapi_key or any(pattern in serpapi_key.lower() for pattern in placeholder_patterns):
        print("\n❌ ERROR: SERPAPI_KEY not set or still using placeholder value")
        print(f"   Current value: {serpapi_key[:30] if serpapi_key else 'NOT SET'}...")
        print("\n📝 To fix:")
        print("1. Get your API key from: https://serpapi.com/")
        print("   - Sign in or create an account")
        print("   - Go to your dashboard")
        print("   - Copy your API key")
        print("2. Edit .env file:")
        print("   nano .env")
        print("3. Replace the placeholder:")
        print("   SERPAPI_KEY=your-actual-serpapi-key-here")
        return
    
    print("Initializing WrappedGrok...")
    try:
        grok = WrappedGrok(
            grok_api_key=grok_api_key,
            serpapi_key=serpapi_key,
            silence_timeout=2.0,  # Wait 2 seconds of silence before responding
            max_response_words=20,  # Max 20 words unless 'explain' keyword (increased from 10)
            explain_keyword='explain',
            elevenlabs_api_key=elevenlabs_api_key,  # Optional - for better TTS voice
            elevenlabs_voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel - clear female voice
            use_elevenlabs=elevenlabs_api_key is not None  # Use ElevenLabs if key provided
        )
        
        print("\n=== Voice Chat Ready ===")
        print("The AI will:")
        print("  - Wait for silence before responding")
        print("  - Limit responses to 10 words (unless you say 'explain')")
        print("  - Search the web for factual claims")
        print("  - Stop speaking if you interrupt with English input")
        print("\nSay 'exit', 'quit', 'goodbye', or 'stop' to end the chat")
        print("Say 'explain' in your question to get longer responses\n")
        
        # Start voice chat
        grok.voice_chat(exit_phrases=['exit', 'quit', 'goodbye', 'stop', 'end'])
        
    except RuntimeError as e:
        print(f"\nError: {e}")
        print("\nTo fix:")
        print("1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("2. Install portaudio: brew install portaudio")
        print("3. Install PyAudio: pip install pyaudio")
        print("\nOr run: ./install_audio.sh")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nCheck that:")
        print("- All dependencies are installed: pip install -r requirements.txt")
        print("- API keys are set correctly")
        print("- Microphone permissions are granted")
    
    print("\nVoice chat ended.")

if __name__ == "__main__":
    main()

