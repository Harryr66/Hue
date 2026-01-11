# Quick Test Instructions - Next.js UI

## Your terminal should be free now. Follow these steps:

### Step 1: Install Dependencies (ONE TIME ONLY)

```bash
cd /Users/harry/Desktop/HUE

# Install Python dependencies
pip install fastapi uvicorn pydantic

# Install Node.js dependencies  
cd ui-nextjs
npm install
cd ..
```

### Step 2: Run in TWO TERMINALS

**Open Terminal 1:**
```bash
cd /Users/harry/Desktop/HUE
python3 api_server.py
```
**Keep this terminal open** - You should see: `Uvicorn running on http://0.0.0.0:8000`

**Open Terminal 2 (NEW TERMINAL WINDOW):**
```bash
cd /Users/harry/Desktop/HUE/ui-nextjs
npm run dev
```
**Keep this terminal open** - You should see: `Ready on http://localhost:9002`

### Step 3: Open Browser

Go to: **http://localhost:9002**

## That's it!

The UI should be working. If you see errors, check:
- Is the Python API server running in Terminal 1?
- Are API keys set in `.env`?
- Did `npm install` complete successfully?

## To Stop:

Press `Ctrl+C` in both terminals.


