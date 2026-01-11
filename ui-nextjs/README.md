# Hue Next.js UI

This is the Next.js UI for Hue, integrated with the WrappedGrok backend.

## Setup

1. Install Python dependencies (in root HUE directory):
```bash
pip install fastapi uvicorn pydantic
```

2. Install Node.js dependencies:
```bash
cd ui-nextjs
npm install
```

3. Make sure your `.env` file in the root HUE directory has:
```
GROK_API_KEY=your-actual-key
SERPAPI_KEY=your-actual-key
ELEVENLABS_API_KEY=your-actual-key (optional)
```

## Running

### Option 1: Use the run script (recommended)
From the root HUE directory:
```bash
./run_nextjs_ui.sh
```

### Option 2: Run manually

Terminal 1 - Start Python API server:
```bash
python3 api_server.py
```

Terminal 2 - Start Next.js UI:
```bash
cd ui-nextjs
npm run dev
```

The UI will be available at http://localhost:9002

## Integration

The UI calls the Python FastAPI server at `http://localhost:8000/api/chat` which uses `WrappedGrok` for processing.

## Features

- Dark/Light theme support with your specified color schemes
- Hue persona ring with animated gradient
- Chat interface with conversation history in sidebar
- Voice mode toggle
- Text input with send button

