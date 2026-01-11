# WrappedGrok Setup Guide - Voice Chat AI

## Installation

### Step 1: Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install PyAudio (REQUIRED for voice chat)

**Quick Install (recommended):**
```bash
chmod +x install_audio.sh
./install_audio.sh
```

**Manual Install:**

1. **Install Homebrew** (if not installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install portaudio:**
   ```bash
   brew install portaudio
   ```

3. **Install PyAudio:**
   ```bash
   pip install pyaudio
   ```

### Step 3: Install other dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- `requests` - for HTTP requests
- `google-search-results` - for SerpAPI web search
- `SpeechRecognition` - for speech-to-text
- `pyaudio` - for microphone access
- `python-dotenv` - for loading .env file

### Step 4: Verify installation
```bash
python3 -c "import pyaudio; import speech_recognition as sr; print('Audio support ready!')"
```

## API Keys Setup

### Option 1: Use .env file (Recommended)

1. **Install python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

2. **Edit .env file:**
   ```bash
   # Edit the .env file that was created
   nano .env
   # or use your preferred editor
   ```

3. **Add your API keys:**
   ```env
   GROK_API_KEY=your-actual-grok-api-key
   SERPAPI_KEY=your-actual-serpapi-key
   ```

   Or use the setup script:
   ```bash
   ./setup_env.sh
   ```

### Option 2: Environment Variables

```bash
export GROK_API_KEY='your-xai-api-key'
export SERPAPI_KEY='your-serpapi-key'
```

## Voice Chat Usage

### Using the example script (recommended):

```bash
# Make sure .env file has your API keys
python3 example_voice_chat.py
```

### Using in your own code:

```python
from wrapped_grok import WrappedGrok
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Initialize (will raise error if audio not available)
grok = WrappedGrok(
    grok_api_key=os.getenv('GROK_API_KEY'),
    serpapi_key=os.getenv('SERPAPI_KEY'),
    silence_timeout=2.0,  # Wait 2 seconds of silence before responding
    max_response_words=10  # Max 10 words unless 'explain' keyword
)

# Start continuous voice chat
grok.voice_chat()

# Or process single voice input
response = grok.process_voice_input()
print(response)
grok.speak(response)

# Text processing also works
text_response = grok.process_input("What is the capital of France?")
print(text_response)
grok.speak(text_response)
```

## Features

- **Voice input/output**: Full voice conversation capability
- **Silence detection**: Waits for silence before responding
- **Response limits**: Max 10 words unless you say "explain"
- **Web search**: Automatically searches for factual claims
- **Interruption**: Can interrupt AI's speech by speaking
- **Violation logging**: All rule violations logged to `violations.log`

