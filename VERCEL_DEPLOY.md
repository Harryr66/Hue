# Deploying to Vercel

## Quick Setup

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy from the ui-nextjs directory**:
   ```bash
   cd ui-nextjs
   vercel
   ```

3. **Follow the prompts**:
   - Link to existing project or create new
   - Set project settings
   - Add environment variables (see below)

## Environment Variables

Add these in Vercel Dashboard → Project Settings → Environment Variables:

### Required:
- `NEXT_PUBLIC_API_URL` - Your deployed Python API URL (e.g., `https://your-api.railway.app` or `https://your-api.render.com`)
- `API_URL` - Same as above (used by server-side routes)

### Optional (if using Firebase client-side):
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- etc.

## Important: Python API Server

**Vercel only hosts Next.js/Node.js**. Your Python FastAPI server needs to be deployed separately:

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Select your repo, choose the root directory
4. Railway will detect Python and install dependencies
5. Set environment variables in Railway dashboard
6. Railway provides a URL like `https://your-app.railway.app`

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
6. Set environment variables

### Option 3: Fly.io
1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Run `fly launch` in project root
3. Follow prompts
4. Set environment variables with `fly secrets set`

## After Deploying Python API

1. Get your API URL (e.g., `https://your-api.railway.app`)
2. Update Vercel environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-api.railway.app`
   - `API_URL=https://your-api.railway.app`
3. Redeploy Vercel app or wait for automatic redeploy

## Testing Locally Before Deploy

1. Create `.env.local` in `ui-nextjs`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   API_URL=http://localhost:8000
   ```

2. Run both servers:
   ```bash
   # Terminal 1: Python API
   cd /Users/harry/Desktop/HUE
   python3 api_server.py
   
   # Terminal 2: Next.js
   cd ui-nextjs
   npm run dev
   ```

## Deploy Commands

**First time:**
```bash
cd ui-nextjs
vercel
```

**Update existing:**
```bash
cd ui-nextjs
vercel --prod
```

**Or use GitHub integration:**
- Push to GitHub
- Connect repo in Vercel dashboard
- Auto-deploys on push to main branch

