# Next.js UI Setup Instructions

## Quick Start

### Step 1: Install Dependencies

Run the setup script:
```bash
cd /Users/harry/Desktop/HUE
./setup_nextjs.sh
```

Or manually:
```bash
# Install Python dependencies
pip install fastapi uvicorn pydantic

# Install Node.js dependencies
cd ui-nextjs
npm install
cd ..
```

### Step 2: Verify .env File

Make sure your `.env` file has:
```
GROK_API_KEY=your-actual-key
SERPAPI_KEY=your-actual-key
ELEVENLABS_API_KEY=your-actual-key (optional)
```

### Step 3: Run the Application

**Option A: Use the run script (recommended)**
```bash
./run_nextjs_ui.sh
```

**Option B: Run manually in two terminals**

Terminal 1 - Python API server:
```bash
cd /Users/harry/Desktop/HUE
python3 api_server.py
```

Terminal 2 - Next.js UI:
```bash
cd /Users/harry/Desktop/HUE/ui-nextjs
npm run dev
```

## Access

- **UI**: http://localhost:9002
- **API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/health

## Troubleshooting

**Terminal not accepting input:**
- Press `Ctrl+C` to stop any running processes
- Make sure no other process is using ports 8000 or 9002
- Check if processes are still running: `lsof -i :8000` or `lsof -i :9002`

**API server won't start:**
- Check if `.env` file has correct API keys
- Verify Python dependencies: `pip list | grep fastapi`
- Check port availability: `lsof -i :8000`

**Next.js won't start:**
- Check if `node_modules` exists: `ls ui-nextjs/node_modules`
- Reinstall: `cd ui-nextjs && rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

**Can't connect to API:**
- Make sure Python API server is running first
- Check CORS settings in `api_server.py`
- Verify API is responding: `curl http://localhost:8000/health`


