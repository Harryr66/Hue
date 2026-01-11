# Connect to GitHub

## Quick Setup

### 1. Initialize Git Repository

```bash
cd /Users/harry/Desktop/HUE
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: Hue AI Assistant with Next.js UI and Python API"
```

### 4. Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click **"New repository"** (or go to https://github.com/new)
3. Repository name: `hue` (or your preferred name)
4. Description: "AI Assistant with Grok API, Next.js UI, and Firebase"
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

### 5. Connect Local Repository to GitHub

After creating the repo, GitHub will show you commands. Use these:

```bash
git remote add origin https://github.com/YOUR_USERNAME/hue.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Install GitHub CLI (if not installed)
# macOS: brew install gh

# Login to GitHub
gh auth login

# Create repo and push
cd /Users/harry/Desktop/HUE
gh repo create hue --public --source=. --remote=origin --push
```

## Important Files Already in .gitignore

- `.env` files (environment variables)
- `firebase-service-account.json` (sensitive keys)
- `node_modules/` (dependencies)
- `venv/` (Python virtual environment)
- `*.db` (database files)
- `.next/` (Next.js build files)

**Make sure to add environment variables in:**
- Vercel dashboard (for deployment)
- Railway/Render/Fly.io dashboard (for Python API)
- GitHub Secrets (if using GitHub Actions)

## After Pushing to GitHub

1. **Deploy to Vercel from GitHub:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import from GitHub
   - Select your `hue` repository
   - Root Directory: `ui-nextjs`
   - Add environment variables
   - Deploy

2. **Deploy Python API:**
   - Railway: Connect GitHub repo, select root directory
   - Render: Connect GitHub repo, select root directory
   - Fly.io: Use `fly launch` with GitHub integration

## Troubleshooting

**"Repository not found":**
- Check repository name matches
- Make sure you're logged in: `gh auth login` or use HTTPS with token

**"Permission denied":**
- Use SSH keys: `git remote set-url origin git@github.com:USERNAME/hue.git`
- Or use GitHub Personal Access Token for HTTPS

**"Large files":**
- If you have large files, consider Git LFS
- Or add them to .gitignore

