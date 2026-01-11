# Testing Instructions

## 🚀 Web UI (Recommended - Easiest)

### Quick Start:
```bash
cd /Users/harry/Desktop/HUE
source venv/bin/activate
pip install streamlit
streamlit run app.py
```

**Or use the script:**
```bash
./run_ui.sh
```

**What happens:**
- Browser opens automatically at `http://localhost:8501`
- Web interface loads
- Click "Initialize WrappedGrok" in sidebar
- Type messages and chat!

**Features:**
- ✅ Text chat interface
- ✅ Chat history
- ✅ Settings (silence timeout, max words)
- ✅ Violations log viewer
- ✅ API key status checker
- ✅ Speak responses button

---

## Quick Test (5 minutes)

### Step 1: Test API Connection
Open your terminal and run:

```bash
cd /Users/harry/Desktop/HUE
source venv/bin/activate
python3 test_grok_api.py
```

**✅ Success looks like:**
```
✅ Loaded .env file using python-dotenv (override=True)
✅ API Key found: xai-i...D7z9B (length: 84 chars)
🔍 Testing model: grok-3
  Status Code: 200
  ✅ SUCCESS! Model 'grok-3' works!
  Response: Hello! How can I help...
```

**❌ If it fails:** Check that your API key in `.env` is correct and you have credits at https://console.x.ai

---

### Step 2: Test Voice Chat
Run this command:

```bash
python3 example_voice_chat.py
```

**What happens:**
1. Script loads (shows "Voice Chat Ready")
2. **Say something** (it's listening!)
3. Wait 2 seconds after you stop speaking
4. AI processes and responds
5. AI speaks the response back to you

**What to say:**
- "Hello" - Simple test
- "What is Python explain" - Gets longer response
- "exit" - Ends the chat

**Expected behavior:**
- ✅ Waits for silence before responding
- ✅ Limits responses to 10 words (unless you say "explain")
- ✅ Searches web for factual claims
- ✅ Speaks response out loud
- ✅ Can be interrupted by speaking while AI is talking

---

## Troubleshooting

**Problem: "API key not found"**
```bash
# Check your .env file
cat .env | grep GROK_API_KEY
# Should show: GROK_API_KEY=xai-...
```

**Problem: "Audio not available"**
```bash
# Make sure PyAudio is installed
pip install pyaudio
# If that fails, install portaudio first:
brew install portaudio
pip install pyaudio
```

**Problem: "Cannot connect to API"**
- Check your internet connection
- Verify API key is correct at https://console.x.ai
- Make sure you have credits in your xAI account

**Problem: "Microphone not working"**
- Grant microphone permissions in System Settings
- Check microphone is not muted
- Try: System Settings → Privacy & Security → Microphone

---

## Full Feature Test

Run each of these to test all features:

1. **Silence Detection:**
   - Say: "Hello" → Wait → Should wait 2 seconds before responding

2. **Word Limit:**
   - Say: "What is Python" → Should get max 10 words
   - Say: "Explain what is Python" → Should get longer response

3. **Web Search:**
   - Say: "What is the latest version of Python" → Should search web

4. **Interruption:**
   - Start voice chat, let AI speak, then speak yourself → AI should stop immediately

5. **Exit:**
   - Say: "exit" or "quit" → Should end gracefully

---

## Check Logs

View violation logs:
```bash
tail -20 violations.log
```

This shows all rule violations and errors.

